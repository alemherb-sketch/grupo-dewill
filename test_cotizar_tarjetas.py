"""Pruebas de cotizar desde las tarjetas del catalogo: el selector de presentacion, color y cantidad que abre COTIZAR.

Las tarjetas piden las opciones del producto a /api/producto/<id>/opciones y agregan a Mi Cotizacion lo que elige
el cliente; la solicitud llega al panel con el color, la presentacion y el codigo de esa variante.

Se ejecutan contra una base SQLite temporal, nunca contra la base real, y sin enviar correos:

    python -m unittest test_cotizar_tarjetas -v
"""
import io
import os
import tempfile
import unittest
import uuid
from unittest import mock

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from openpyxl import Workbook  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from app import app, db  # noqa: E402
from models import Product, ProductPresentationColor, QuoteItem, QuoteRequest, SiteConfig  # noqa: E402

app.config['TESTING'] = True

HEADERS = ['Codigo', 'Categoria', 'Sub Categoria', 'Marca', 'Producto', 'Color', 'Presentacion']
CLIENTE = {'name': 'Cliente de prueba', 'document': '12345678', 'phone': '987654321'}


def xlsx(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


class CotizarDesdeTarjetasTest(unittest.TestCase):
    def setUp(self):
        # otras suites que comparten esta base pueden dejar cotizaciones, paginas deshabilitadas o un correo de aviso
        with app.app_context():
            QuoteItem.query.delete()
            QuoteRequest.query.delete()
            SiteConfig.set('notify_email', '')
            SiteConfig.set('disabled_pages', '')
            db.session.commit()
        self.admin = app.test_client()
        self.admin.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        self.client = app.test_client()   # visitante sin sesion
        sufijo = uuid.uuid4().hex[:6].upper()
        self.marca = f'MARCA {sufijo}'
        self.esmalte = f'ESMALTE {sufijo}'
        self.brocha = f'BROCHA {sufijo}'
        self.s = sufijo

    def importar(self, rows):
        resp = self.admin.post('/admin/productos/importar', data={'excel_file': (xlsx(rows), 'tarjetas.xlsx')},
                               content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def cargar_esmalte(self):
        """1GL en AZUL y ROJO #103; 1/4GL solo en ROJO #103."""
        self.importar([
            [f'E1{self.s}', 'PINTURAS', 'ESMALTES', self.marca, self.esmalte, 'AZUL', '1GL'],
            [f'E2{self.s}', 'PINTURAS', 'ESMALTES', self.marca, self.esmalte, 'ROJO #103', '1GL'],
            [f'E3{self.s}', 'PINTURAS', 'ESMALTES', self.marca, self.esmalte, 'ROJO #103', '1/4GL'],
        ])
        return self.producto_id(self.esmalte)

    def producto_id(self, nombre):
        with app.app_context():
            return Product.query.filter_by(name=nombre).one().id

    def opciones(self, pid, client=None):
        resp = (client or self.client).get(f'/api/producto/{pid}/opciones')
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        return resp.get_json()

    # ---------- opciones del producto ----------

    def test_cada_presentacion_trae_solo_sus_colores_con_codigo(self):
        datos = self.opciones(self.cargar_esmalte())
        self.assertEqual(datos['name'], self.esmalte)
        self.assertEqual(datos['brand'], self.marca)
        colores = {p['name']: [c['label'] for c in p['colors']] for p in datos['presentations']}
        self.assertEqual(colores, {'1GL': ['AZUL', 'ROJO #103'], '1/4GL': ['ROJO #103']})
        rojo = datos['presentations'][1]['colors'][0]
        self.assertEqual((rojo['name'], rojo['code']), ('ROJO', '103'))

    def test_incluye_los_codigos_de_cada_variante(self):
        datos = self.opciones(self.cargar_esmalte())
        ids = {p['name']: p['id'] for p in datos['presentations']}
        self.assertEqual({(c['p'], c['c']): c['code'] for c in datos['codes']}, {
            (ids['1GL'], 'AZUL'): f'E1{self.s}', (ids['1GL'], 'ROJO'): f'E2{self.s}', (ids['1/4GL'], 'ROJO'): f'E3{self.s}'})

    def test_sin_colores_vinculados_cada_presentacion_usa_los_colores_del_producto(self):
        pid = self.cargar_esmalte()
        with app.app_context():
            ProductPresentationColor.query.filter_by(product_id=pid).delete()
            db.session.commit()
        datos = self.opciones(pid)
        generales = sorted(c['name'] for c in datos['colors'])
        self.assertEqual(generales, ['AZUL', 'ROJO'])
        for pres in datos['presentations']:
            self.assertEqual(sorted(c['name'] for c in pres['colors']), generales)

    def test_producto_sin_presentaciones_ni_colores(self):
        self.importar([[f'B1{self.s}', 'HERRAMIENTAS', 'BROCHAS', self.marca, self.brocha, None, None]])
        datos = self.opciones(self.producto_id(self.brocha))
        self.assertEqual((datos['presentations'], datos['colors']), ([], []))
        self.assertEqual(datos['codes'], [{'p': None, 'c': '', 'code': f'B1{self.s}'}])

    def test_producto_inactivo_o_inexistente_no_tiene_opciones(self):
        pid = self.cargar_esmalte()
        with app.app_context():
            db.session.get(Product, pid).is_active = False
            db.session.commit()
        self.assertEqual(self.client.get(f'/api/producto/{pid}/opciones').status_code, 404)
        self.assertEqual(self.client.get('/api/producto/999999/opciones').status_code, 404)

    def test_con_el_catalogo_deshabilitado_no_responde(self):
        pid = self.cargar_esmalte()
        with app.app_context():
            SiteConfig.set('disabled_pages', 'productos')
            db.session.commit()
        self.assertEqual(self.client.get(f'/api/producto/{pid}/opciones').status_code, 404)

    # ---------- tarjetas ----------

    def test_las_tarjetas_abren_el_selector_con_el_color_o_la_presentacion_tocados(self):
        pid = self.cargar_esmalte()
        html = self.client.get('/productos', query_string={'q': self.esmalte}).get_data(as_text=True)
        self.assertIn(f'data-product-id="{pid}"', html)
        self.assertIn('data-quote-color="AZUL"', html)
        self.assertIn('>1/4GL</button>', html)
        self.assertIn('class="pcr-btn-quote" data-quote-open', html)
        self.assertNotIn('onclick="addToQuote(', html, 'COTIZAR ya no agrega sin elegir color ni presentacion')
        self.assertIn('id="quoteOptions"', html)

    def test_el_nombre_con_comillas_no_rompe_la_tarjeta(self):
        # antes el nombre iba dentro de un onclick="addToQuote(..., '{{ nombre }}')" y un apostrofo lo cortaba
        nombre = f"ESMALTE D'ORO \"PRO\" {self.s}"
        self.importar([[f'Q1{self.s}', 'PINTURAS', 'ESMALTES', self.marca, nombre, 'AZUL', '1GL']])
        html = self.client.get('/productos', query_string={'q': self.s}).get_data(as_text=True)
        self.assertIn(f'data-product-id="{self.producto_id(nombre)}"', html)
        self.assertIn(f'<h3 class="pcr-title">ESMALTE D&#39;ORO &#34;PRO&#34; {self.s}</h3>', html)
        self.assertEqual(self.opciones(self.producto_id(nombre))['name'], nombre)

    # ---------- cotizacion ----------

    def test_lo_elegido_en_el_selector_llega_al_panel(self):
        pid = self.cargar_esmalte()
        # lo que envia el selector: el color con su codigo y el nombre de la presentacion
        with mock.patch.dict(app.config, {'MAIL_USERNAME': ''}):
            resp = self.client.post('/api/cotizacion', json={**CLIENTE, 'items': [
                {'product_id': pid, 'quantity': 3, 'color': 'ROJO #103', 'presentation': '1/4GL'}]})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        qid = resp.get_json()['quote_id']
        with app.app_context():
            item = QuoteItem.query.filter_by(quote_id=qid).one()
            self.assertEqual((item.presentation, item.color, item.code, item.quantity),
                             ('1/4GL', 'ROJO #103', f'E3{self.s}', 3))
        panel = self.admin.get(f'/admin/solicitudes/{qid}').get_data(as_text=True)
        for texto in ('ROJO #103', '1/4GL', f'E3{self.s}'):
            self.assertIn(texto, panel)


if __name__ == '__main__':
    unittest.main()
