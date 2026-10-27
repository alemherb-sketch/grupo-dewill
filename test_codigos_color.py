"""Pruebas del codigo de los colores ('AMARILLO LIMON #41'): importacion desde Excel, selector de la
ficha del producto y cotizacion.

Se ejecutan contra una base SQLite temporal, nunca contra la base real, y sin enviar correos:

    python -m unittest test_codigos_color -v
"""
import io
import os
import tempfile
import types
import unittest
import uuid
from unittest import mock

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from openpyxl import Workbook  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from app import app, db  # noqa: E402
from models import Product, ProductSpec, Presentation, QuoteItem, QuoteRequest, SiteConfig  # noqa: E402
from models import split_color_code, color_label  # noqa: E402

app.config['TESTING'] = True

HEADERS = ['Codigo', 'Categoria', 'Sub Categoria', 'Marca', 'Producto', 'Color', 'Presentacion']
HEADERS_SIN_CODIGO = HEADERS[1:]   # el formato del Excel de LINEA DECORATIVA: sin SKU
CLIENTE = {'name': 'Cliente de prueba', 'document': '12345678', 'phone': '987654321'}


def xlsx(headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


class SyncThread:
    """Ejecuta el envio del correo en el acto para poder inspeccionarlo."""
    def __init__(self, target, args=(), kwargs=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


class SplitColorCodeTest(unittest.TestCase):
    def test_separa_nombre_y_codigo(self):
        casos = {
            'AMARILLO LIMON #41': ('AMARILLO LIMON', '41'),
            'AZUL HONDA #310': ('AZUL HONDA', '310'),
            'MEDIUM GRAY (GRIS MEDIUM) #23': ('MEDIUM GRAY (GRIS MEDIUM)', '23'),
            'ROJO#103': ('ROJO', '103'),
            '  AZUL CLARO  #  35  ': ('AZUL CLARO', '35'),
            'VERDE #1 CLARO #7': ('VERDE #1 CLARO', '7'),
        }
        for texto, esperado in casos.items():
            self.assertEqual(split_color_code(texto), esperado, texto)

    def test_el_codigo_es_texto_y_conserva_el_cero(self):
        self.assertEqual(split_color_code('ANTICORROSIVO GRIS #08'), ('ANTICORROSIVO GRIS', '08'))

    def test_sin_codigo_no_cambia_el_texto(self):
        self.assertEqual(split_color_code('BLANCO HUMO'), ('BLANCO HUMO', None))
        self.assertEqual(split_color_code('  CASTAÑO '), ('CASTAÑO', None))
        self.assertEqual(split_color_code(''), ('', None))
        self.assertEqual(split_color_code(None), ('', None))

    def test_un_hex_suelto_no_es_un_color_con_codigo(self):
        self.assertEqual(split_color_code('#FF0000'), ('#FF0000', None))

    def test_etiqueta(self):
        self.assertEqual(color_label('AMARILLO LIMON', '41'), 'AMARILLO LIMON #41')
        self.assertEqual(color_label('AMARILLO LIMON', None), 'AMARILLO LIMON')
        self.assertEqual(color_label('AMARILLO LIMON', ''), 'AMARILLO LIMON')


class ColoresConCodigoTest(unittest.TestCase):
    def setUp(self):
        # partir de un estado conocido: otras suites que comparten esta base pueden dejar cotizaciones (y items
        # huerfanos con ids repetidos) o un correo de aviso vacio, y entonces no se enviaria ningun correo
        with app.app_context():
            QuoteItem.query.delete()
            QuoteRequest.query.delete()
            SiteConfig.set('notify_email', 'destino@example.com')
            db.session.commit()
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        # un producto y una marca propios de cada prueba, para no depender del orden
        self.sufijo = uuid.uuid4().hex[:6].upper()
        self.sku = f'TC-{self.sufijo}'
        self.marca = f'MARCA {self.sufijo}'
        self.producto = f'PINTURA SPRAY {self.sufijo}'

    # ---------- utilidades ----------

    def fila(self, color, presentacion='400ML', sku=None, producto=None, marca=None):
        return [sku or self.sku, 'LINEA DECORATIVA', 'PINTURA SPRAY', marca or self.marca,
                producto or self.producto, color, presentacion]

    def importar(self, headers, rows):
        resp = self.client.post('/admin/productos/importar', data={'excel_file': (xlsx(headers, rows), 'colores.xlsx')},
                                content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def producto_creado(self):
        return Product.query.filter_by(sku=self.sku).one()

    def cotizar(self, items):
        """Envia una cotizacion y devuelve (respuesta, correos que se habrian enviado)."""
        enviados = []
        with mock.patch('app.send_async_email', lambda _app, datos: enviados.append(datos)), \
                mock.patch('app.threading', types.SimpleNamespace(Thread=SyncThread)), \
                mock.patch.dict(app.config, {'MAIL_USERNAME': 'prueba@example.com', 'MAIL_NOTIFY_TO': 'destino@example.com'}):
            resp = self.client.post('/api/cotizacion', json={**CLIENTE, 'items': items})
        return resp, enviados

    def importar_spray(self):
        self.importar(HEADERS, [self.fila('AMARILLO LIMON #41'), self.fila('ANTICORROSIVO GRIS #08'), self.fila('NEGRO')])
        with app.app_context():
            p = self.producto_creado()
            return p.id, Presentation.query.filter_by(name='400ML').one().id

    # ---------- importacion ----------

    def test_el_importador_guarda_el_codigo_aparte_del_nombre(self):
        self.importar(HEADERS, [self.fila('AMARILLO LIMON #41'), self.fila('ANTICORROSIVO GRIS #08'), self.fila('NEGRO')])
        with app.app_context():
            p = self.producto_creado()
            vinculos = {lk.color_name: (lk.color_code, lk.label) for lk in p.presentation_colors}
            self.assertEqual(vinculos, {
                'AMARILLO LIMON': ('41', 'AMARILLO LIMON #41'),
                'ANTICORROSIVO GRIS': ('08', 'ANTICORROSIVO GRIS #08'),
                'NEGRO': (None, 'NEGRO'),
            })
            especificaciones = {s.value for s in p.specs if s.key == 'Color'}
            self.assertEqual(especificaciones, {'AMARILLO LIMON', 'ANTICORROSIVO GRIS', 'NEGRO'})

    def test_excel_sin_columna_codigo_actualiza_los_productos_existentes(self):
        # el producto ya estaba cargado, sin codigos
        self.importar(HEADERS, [self.fila('AMARILLO LIMON'), self.fila('NEGRO')])
        # y llega el Excel de LINEA DECORATIVA: sin SKU, con los codigos dentro del color
        mensaje = self.importar(HEADERS_SIN_CODIGO, [
            self.fila('AMARILLO LIMON #41')[1:],
            self.fila('NEGRO')[1:],
            self.fila('ROJO #103', producto=f'PRODUCTO NUEVO {self.sufijo}', marca=f'MARCA NUEVA {self.sufijo}')[1:],
        ])
        self.assertIn('no tiene la columna Codigo', mensaje)
        with app.app_context():
            p = self.producto_creado()
            self.assertEqual({lk.color_name: lk.color_code for lk in p.presentation_colors},
                             {'AMARILLO LIMON': '41', 'NEGRO': None})
            self.assertEqual(Product.query.filter_by(name=f'PRODUCTO NUEVO {self.sufijo}').count(), 0, 'sin SKU no se crean productos')

    def test_sin_sku_no_se_crean_marcas_nuevas(self):
        from models import Brand
        self.importar(HEADERS_SIN_CODIGO, [self.fila('ROJO #103')[1:]])
        with app.app_context():
            self.assertEqual(Brand.query.filter_by(name=self.marca).count(), 0)

    def test_la_especificacion_con_el_formato_antiguo_se_reemplaza(self):
        self.importar(HEADERS, [self.fila('ROJO')])
        with app.app_context():
            p = self.producto_creado()
            db.session.add(ProductSpec(product_id=p.id, key='Color', value='ROJO #103'))   # asi quedaba antes
            db.session.commit()
        self.importar(HEADERS, [self.fila('ROJO #103')])
        with app.app_context():
            valores = sorted(s.value for s in self.producto_creado().specs if s.key == 'Color')
            self.assertEqual(valores, ['ROJO'])

    def test_una_fila_vacia_no_toca_nada(self):
        mensaje = self.importar(HEADERS, [self.fila('NEGRO'), [None] * len(HEADERS)])
        self.assertIn('1 omitidos', mensaje)

    # ---------- selector de color de la ficha ----------

    def test_api_de_colores_devuelve_codigo_y_etiqueta(self):
        pid, pres_id = self.importar_spray()
        datos = self.client.get(f'/api/producto/{pid}/colores?pres_id={pres_id}').get_json()
        por_nombre = {c['name']: c for c in datos}
        self.assertEqual(por_nombre['AMARILLO LIMON']['code'], '41')
        self.assertEqual(por_nombre['AMARILLO LIMON']['label'], 'AMARILLO LIMON #41')
        self.assertEqual(por_nombre['ANTICORROSIVO GRIS']['label'], 'ANTICORROSIVO GRIS #08')
        self.assertIsNone(por_nombre['NEGRO']['code'])
        self.assertEqual(por_nombre['NEGRO']['label'], 'NEGRO')

    def test_la_ficha_muestra_el_codigo_bajo_cada_color(self):
        pid, _ = self.importar_spray()
        html = self.client.get(f'/producto/{pid}').get_data(as_text=True)
        self.assertIn('data-label="AMARILLO LIMON #41"', html)
        self.assertIn('title="AMARILLO LIMON #41"', html)
        self.assertIn('<span class="color-swatch-code">#41</span>', html)
        self.assertIn('<span class="color-swatch-code">#08</span>', html)
        self.assertIn('data-label="NEGRO"', html)

    # ---------- cotizacion ----------

    def test_la_cotizacion_envia_el_color_con_su_codigo(self):
        pid, _ = self.importar_spray()
        resp, enviados = self.cotizar([
            {'product_id': pid, 'quantity': 2, 'color': 'AMARILLO LIMON #41', 'presentation': '400ML'},   # ya con codigo
            {'product_id': pid, 'quantity': 1, 'color': 'ANTICORROSIVO GRIS', 'presentation': '400ML'},   # solo el nombre
            {'product_id': pid, 'quantity': 1, 'color': 'NEGRO', 'presentation': '400ML'},                # sin codigo
            {'product_id': pid, 'quantity': 1},                                                           # sin color
        ])
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        with app.app_context():
            items = QuoteItem.query.filter_by(quote_id=resp.get_json()['quote_id']).order_by(QuoteItem.id).all()
            self.assertEqual([i.color for i in items],
                             ['AMARILLO LIMON #41', 'ANTICORROSIVO GRIS #08', 'NEGRO', None])
        self.assertEqual(len(enviados), 1)
        cuerpo = enviados[0]['body']
        self.assertIn('Color: AMARILLO LIMON #41', cuerpo)
        self.assertIn('Color: ANTICORROSIVO GRIS #08', cuerpo)
        self.assertIn('Color: NEGRO ', cuerpo)

    def test_el_codigo_no_se_duplica_con_colores_guardados_con_el_formato_antiguo(self):
        # colores importados antes de que existieran los codigos: el nombre trae el '#' y no hay codigo aparte
        self.importar(HEADERS, [self.fila('SOLO NOMBRE')])
        with app.app_context():
            p = self.producto_creado()
            lk = p.presentation_colors[0]
            lk.color_name, lk.color_code = 'ROJO #103', None
            db.session.commit()
            pid = p.id
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'color': 'ROJO #103'}])
        with app.app_context():
            item = QuoteItem.query.filter_by(quote_id=resp.get_json()['quote_id']).one()
            self.assertEqual(item.color, 'ROJO #103')

    def test_un_color_inexistente_se_envia_tal_cual(self):
        pid, _ = self.importar_spray()
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'color': 'COLOR QUE NO EXISTE'}])
        with app.app_context():
            self.assertEqual(QuoteItem.query.filter_by(quote_id=resp.get_json()['quote_id']).one().color, 'COLOR QUE NO EXISTE')

    def test_el_panel_muestra_el_color_con_su_codigo(self):
        pid, _ = self.importar_spray()
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'color': 'AMARILLO LIMON'}])
        html = self.client.get(f"/admin/solicitudes/{resp.get_json()['quote_id']}").get_data(as_text=True)
        self.assertIn('AMARILLO LIMON #41', html)


if __name__ == '__main__':
    unittest.main()
