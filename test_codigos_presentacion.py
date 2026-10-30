"""Pruebas del Codigo de cada variante (presentacion + color): importacion desde Excel, ficha del producto y cotizacion.

El Excel trae un Codigo por fila (esa presentacion y ese color). Se guarda por variante, la ficha muestra el de lo que
elige el cliente y la solicitud de cotizacion lo envia.

Se ejecutan contra una base SQLite temporal, nunca contra la base real, y sin enviar correos:

    python -m unittest test_codigos_presentacion -v
"""
import io
import json
import os
import re
import tempfile
import types
import unittest
import uuid
from unittest import mock

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from openpyxl import Workbook  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from app import app, db  # noqa: E402
from models import PaintColor, Product, ProductVariantCode, Presentation, QuoteItem, QuoteRequest, SiteConfig  # noqa: E402
from models import find_variant_code  # noqa: E402

app.config['TESTING'] = True

HEADERS = ['Codigo', 'Categoria', 'Sub Categoria', 'Marca', 'Producto', 'Color', 'Presentacion']
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


class VarianteStub:
    def __init__(self, presentation_id, color_name, code):
        self.presentation_id, self.color_name, self.code = presentation_id, color_name, code


class FindVariantCodeTest(unittest.TestCase):
    def test_prefiere_la_combinacion_exacta_y_cae_a_la_mas_general(self):
        codes = [VarianteStub(1, 'AZUL', 'A'), VarianteStub(1, '', 'B'), VarianteStub(None, 'AZUL', 'C'), VarianteStub(None, '', 'D')]
        self.assertEqual(find_variant_code(codes, 1, 'azul'), 'A')       # presentacion + color
        self.assertEqual(find_variant_code(codes, 1, 'ROJO'), 'B')       # presentacion (el color no tiene codigo propio)
        self.assertEqual(find_variant_code(codes, 2, 'AZUL'), 'C')       # solo color
        self.assertEqual(find_variant_code(codes, 2, 'ROJO'), 'D')       # solo el producto
        self.assertEqual(find_variant_code(codes, None, ''), 'D')

    def test_sin_codigos_devuelve_none(self):
        self.assertIsNone(find_variant_code([], 1, 'AZUL'))
        self.assertIsNone(find_variant_code([VarianteStub(1, 'AZUL', 'A')], 2, 'ROJO'))

    def test_ignora_mayusculas_y_espacios_del_color(self):
        self.assertEqual(find_variant_code([VarianteStub(1, ' Azul ', 'A')], 1, 'AZUL'), 'A')


class CodigosPorVarianteTest(unittest.TestCase):
    def setUp(self):
        # otras suites que comparten esta base pueden dejar cotizaciones (y items huerfanos) o un correo de aviso vacio
        with app.app_context():
            QuoteItem.query.delete()
            QuoteRequest.query.delete()
            SiteConfig.set('notify_email', 'destino@example.com')
            db.session.commit()
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        self.sufijo = uuid.uuid4().hex[:6].upper()
        self.marca = f'MARCA {self.sufijo}'
        self.brocha = f'BROCHA {self.sufijo}'
        self.pintura = f'LATEX {self.sufijo}'

    # ---------- utilidades ----------

    def fila(self, codigo, producto, color=None, presentacion=None):
        return [codigo, 'HERRAMIENTAS', 'BROCHAS', self.marca, producto, color, presentacion]

    def importar(self, rows, headers=HEADERS):
        resp = self.client.post('/admin/productos/importar', data={'excel_file': (xlsx(headers, rows), 'codigos.xlsx')},
                                content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def cargar_brochas(self):
        """Producto solo con presentaciones: un codigo por tamano."""
        return self.importar([
            self.fila(f'4975{self.sufijo}', self.brocha, presentacion='1 1/2 PLG'),
            self.fila(f'4470{self.sufijo}', self.brocha, presentacion='1 PLG'),
            self.fila(f'0571{self.sufijo}', self.brocha, presentacion='2 PLG'),
        ])

    def cargar_pintura(self):
        """Producto con presentaciones y colores: un codigo por presentacion + color."""
        return self.importar([
            self.fila(f'P1{self.sufijo}', self.pintura, 'AZUL', '1GL'),
            self.fila(f'P2{self.sufijo}', self.pintura, 'AZUL', '4GL'),
            self.fila(f'P3{self.sufijo}', self.pintura, 'ROJO #103', '1GL'),
            self.fila(f'P4{self.sufijo}', self.pintura, 'ROJO #103', '4GL'),
        ])

    def producto(self, nombre):
        return Product.query.filter_by(name=nombre).one()

    def codigos(self, nombre):
        """{(presentacion, color): codigo} del producto."""
        with app.app_context():
            p = self.producto(nombre)
            nombres = {x.id: x.name for x in Presentation.query.all()}
            return {(nombres.get(c.presentation_id), c.color_name): c.code for c in p.variant_codes}

    def cotizar(self, items):
        """Envia una cotizacion y devuelve (respuesta, correos que se habrian enviado)."""
        enviados = []
        with mock.patch('app.send_async_email', lambda _app, datos: enviados.append(datos)), \
                mock.patch('app.threading', types.SimpleNamespace(Thread=SyncThread)), \
                mock.patch.dict(app.config, {'MAIL_USERNAME': 'prueba@example.com', 'MAIL_NOTIFY_TO': 'destino@example.com'}):
            resp = self.client.post('/api/cotizacion', json={**CLIENTE, 'items': items})
        return resp, enviados

    def items_guardados(self, resp):
        with app.app_context():
            return [(i.presentation, i.color, i.code) for i in
                    QuoteItem.query.filter_by(quote_id=resp.get_json()['quote_id']).order_by(QuoteItem.id).all()]

    # ---------- importacion ----------

    def test_guarda_un_codigo_por_presentacion(self):
        mensaje = self.cargar_brochas()
        s = self.sufijo
        self.assertEqual(self.codigos(self.brocha),
                         {('1 1/2 PLG', ''): f'4975{s}', ('1 PLG', ''): f'4470{s}', ('2 PLG', ''): f'0571{s}'})
        self.assertIn('3 códigos de presentación y color guardados', mensaje)

    def test_guarda_un_codigo_por_presentacion_y_color_con_el_nombre_limpio(self):
        self.cargar_pintura()
        s = self.sufijo
        self.assertEqual(self.codigos(self.pintura), {
            ('1GL', 'AZUL'): f'P1{s}', ('4GL', 'AZUL'): f'P2{s}',
            ('1GL', 'ROJO'): f'P3{s}', ('4GL', 'ROJO'): f'P4{s}',   # 'ROJO #103': el #103 es el codigo del color, no parte del nombre
        })

    def test_conserva_los_ceros_a_la_izquierda(self):
        self.importar([self.fila('0571', self.brocha + ' Z', presentacion='1 PLG')])
        with app.app_context():
            self.assertEqual(self.producto(self.brocha + ' Z').sku, '0571')
            self.assertEqual([c.code for c in self.producto(self.brocha + ' Z').variant_codes], ['0571'])

    def test_fila_sin_presentacion_ni_color_es_el_codigo_del_producto(self):
        self.importar([self.fila(f'5168{self.sufijo}', self.brocha)])
        self.assertEqual(self.codigos(self.brocha), {(None, ''): f'5168{self.sufijo}'})

    def test_el_sku_de_un_producto_nuevo_es_el_codigo_de_su_primera_fila(self):
        self.cargar_brochas()
        with app.app_context():
            self.assertEqual(self.producto(self.brocha).sku, f'4975{self.sufijo}')

    def test_reimportar_reemplaza_los_codigos_del_producto(self):
        self.cargar_brochas()
        s = self.sufijo
        # llega el Excel corregido: cambia el codigo de 1 PLG y ya no trae 2 PLG
        self.importar([self.fila(f'4975{s}', self.brocha, presentacion='1 1/2 PLG'),
                       self.fila(f'9999{s}', self.brocha, presentacion='1 PLG')])
        self.assertEqual(self.codigos(self.brocha), {('1 1/2 PLG', ''): f'4975{s}', ('1 PLG', ''): f'9999{s}'})

    def test_un_excel_sin_columna_codigo_no_borra_los_codigos(self):
        self.cargar_brochas()
        mensaje = self.importar([[ 'HERRAMIENTAS', 'BROCHAS', self.marca, self.brocha, None, '1 PLG']], headers=HEADERS[1:])
        self.assertIn('no tiene la columna Codigo', mensaje)
        self.assertEqual(len(self.codigos(self.brocha)), 3)

    def test_no_toca_los_codigos_de_otros_productos(self):
        self.cargar_brochas()
        self.cargar_pintura()
        self.cargar_brochas()
        self.assertEqual(len(self.codigos(self.pintura)), 4)

    def test_al_borrar_el_producto_se_borran_sus_codigos(self):
        self.cargar_brochas()
        with app.app_context():
            p = self.producto(self.brocha)
            pid = p.id
            db.session.delete(p)
            db.session.commit()
            self.assertEqual(ProductVariantCode.query.filter_by(product_id=pid).count(), 0)

    # ---------- ficha del producto ----------

    def codigos_de_la_ficha(self, nombre):
        with app.app_context():
            pid = self.producto(nombre).id
        html = self.client.get(f'/producto/{pid}').get_data(as_text=True)
        found = re.search(r'const VARIANT_CODES = (\[.*?\]);', html)
        self.assertIsNotNone(found, 'la ficha debe incluir los codigos de las variantes')
        return json.loads(found.group(1)), html

    def test_la_ficha_incluye_los_codigos_para_elegir_por_presentacion_y_color(self):
        self.cargar_pintura()
        datos, html = self.codigos_de_la_ficha(self.pintura)
        with app.app_context():
            ids = {p.name: p.id for p in Presentation.query.filter(Presentation.name.in_(['1GL', '4GL'])).all()}
        s = self.sufijo
        self.assertEqual({(d['p'], d['c']): d['code'] for d in datos},
                         {(ids['1GL'], 'AZUL'): f'P1{s}', (ids['4GL'], 'AZUL'): f'P2{s}',
                          (ids['1GL'], 'ROJO'): f'P3{s}', (ids['4GL'], 'ROJO'): f'P4{s}'})
        self.assertIn('id="skuLine"', html)

    def test_la_ficha_sin_codigos_conserva_el_sku(self):
        self.importar([self.fila('SKU-' + self.sufijo, self.brocha, presentacion='1 PLG')], headers=HEADERS)
        with app.app_context():
            ProductVariantCode.query.delete()
            db.session.commit()
        datos, html = self.codigos_de_la_ficha(self.brocha)
        self.assertEqual(datos, [])
        self.assertIn(f'SKU: SKU-{self.sufijo}', html)

    # ---------- cotizacion ----------

    def test_la_cotizacion_envia_el_codigo_de_la_presentacion_elegida(self):
        self.cargar_brochas()
        s = self.sufijo
        with app.app_context():
            pid = self.producto(self.brocha).id
        resp, enviados = self.cotizar([
            {'product_id': pid, 'quantity': 2, 'presentation': '1 PLG'},
            {'product_id': pid, 'quantity': 1, 'presentation': '2 PLG'},
        ])
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertEqual(self.items_guardados(resp), [('1 PLG', None, f'4470{s}'), ('2 PLG', None, f'0571{s}')])
        cuerpo = enviados[0]['body']
        self.assertIn(f'(Código: 4470{s}) - Presentación: 1 PLG x 2', cuerpo)
        self.assertIn(f'(Código: 0571{s}) - Presentación: 2 PLG x 1', cuerpo)
        self.assertNotIn('SKU:', cuerpo, 'el codigo de la variante reemplaza al SKU general')

    def test_la_cotizacion_envia_el_codigo_segun_color_y_presentacion(self):
        self.cargar_pintura()
        s = self.sufijo
        with app.app_context():
            pid = self.producto(self.pintura).id
        resp, enviados = self.cotizar([
            {'product_id': pid, 'quantity': 1, 'presentation': '1GL', 'color': 'AZUL'},
            {'product_id': pid, 'quantity': 1, 'presentation': '4GL', 'color': 'AZUL'},
            {'product_id': pid, 'quantity': 1, 'presentation': '4GL', 'color': 'ROJO #103'},   # el color ya viaja con su codigo
            {'product_id': pid, 'quantity': 1, 'presentation': '1GL', 'color': 'ROJO'},        # solo el nombre: el servidor completa #103
        ])
        self.assertEqual(self.items_guardados(resp), [
            ('1GL', 'AZUL', f'P1{s}'), ('4GL', 'AZUL', f'P2{s}'),
            ('4GL', 'ROJO #103', f'P4{s}'), ('1GL', 'ROJO #103', f'P3{s}')])
        self.assertIn(f'(Código: P4{s}) - Color: ROJO #103 - Presentación: 4GL', enviados[0]['body'])

    def test_el_servidor_ignora_un_codigo_enviado_por_el_navegador(self):
        self.cargar_brochas()
        with app.app_context():
            pid = self.producto(self.brocha).id
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'presentation': '1 PLG', 'code': 'FALSO'}])
        self.assertEqual(self.items_guardados(resp), [('1 PLG', None, f'4470{self.sufijo}')])

    def test_sin_codigos_cargados_se_envia_el_sku_como_antes(self):
        self.importar([self.fila('SKU-' + self.sufijo, self.brocha, presentacion='1 PLG')])
        with app.app_context():
            ProductVariantCode.query.delete()
            db.session.commit()
            pid = self.producto(self.brocha).id
        resp, enviados = self.cotizar([{'product_id': pid, 'quantity': 1, 'presentation': '1 PLG'}])
        self.assertEqual(self.items_guardados(resp), [('1 PLG', None, None)])
        self.assertIn(f'(SKU: SKU-{self.sufijo}) - Presentación: 1 PLG', enviados[0]['body'])

    def test_una_presentacion_que_no_es_del_producto_no_recibe_codigo_de_otra(self):
        self.cargar_brochas()
        with app.app_context():
            pid = self.producto(self.brocha).id
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'presentation': '9 PLG'}])
        self.assertEqual(self.items_guardados(resp), [('9 PLG', None, None)])

    def test_el_panel_muestra_el_codigo_de_cada_item(self):
        self.cargar_brochas()
        with app.app_context():
            pid = self.producto(self.brocha).id
        resp, _ = self.cotizar([{'product_id': pid, 'quantity': 1, 'presentation': '1 PLG'}])
        html = self.client.get(f"/admin/solicitudes/{resp.get_json()['quote_id']}").get_data(as_text=True)
        self.assertIn(f'4470{self.sufijo}', html)
        self.assertIn('Código:', html)

    # ---------- SKU general y buscador ----------

    def test_la_ficha_con_codigos_no_muestra_el_sku_general(self):
        # el SKU general seria el codigo de otra variante: solo se muestra el codigo de lo que se elige
        self.cargar_pintura()
        _, html = self.codigos_de_la_ficha(self.pintura)
        self.assertNotIn(f'SKU: P1{self.sufijo}', html)
        self.assertIn('id="skuLine" style="display:none"', html)

    def test_el_buscador_encuentra_el_producto_por_cualquier_codigo(self):
        self.cargar_pintura()
        codigo = f'P4{self.sufijo}'   # 4GL ROJO: no es el SKU del producto (ese es P1, el de su primera fila)
        anonimo = app.test_client()
        self.assertIn(self.pintura, anonimo.get('/productos', query_string={'q': codigo}).get_data(as_text=True))
        self.assertIn(self.pintura, [p['name'] for p in anonimo.get('/api/productos/search', query_string={'q': codigo}).get_json()])
        self.assertIn(self.pintura, self.client.get('/admin/productos', query_string={'q': codigo}).get_data(as_text=True))

    # ---------- variantes en Editar Producto: presentacion + color + codigo ----------

    def tabla_de_variantes(self, nombre):
        """[(presentacion, color, codigo)] de la tabla del formulario, en orden ('Sin presentación' si no tiene)."""
        with app.app_context():
            pid = self.producto(nombre).id
        html = self.client.get(f'/admin/productos/{pid}/editar').get_data(as_text=True)
        cuerpo = html[html.index('<tbody id="variantRows">'):html.index('</tbody>', html.index('<tbody id="variantRows">'))]
        filas = []
        for tr in re.findall(r'<tr class="variant-row".*?</tr>', cuerpo, re.S):
            pres = re.search(r'<option value="[^"]*" selected>([^<]*)</option>', tr).group(1)
            color = re.search(r'name="vc_color\[\]" value="([^"]*)"', tr).group(1)
            codigo = re.search(r'name="vc_code\[\]" value="([^"]*)"', tr).group(1)
            filas.append((pres, color, codigo))
        return pid, html, filas

    def ids(self, *nombres):
        with app.app_context():
            return {p.name: p.id for p in Presentation.query.filter(Presentation.name.in_(nombres)).all()}

    def guardar_variantes(self, pid, filas, presentaciones, **extra):
        """Envia el formulario de edicion con la tabla de variantes: filas = [(presentation_id, color, codigo)]."""
        data = {'name': 'x', 'is_active': 'on', 'presentation_ids': presentaciones, 'variants_present': '1',
                'vc_pres[]': [str(p) if p else '' for p, _, _ in filas], 'vc_color[]': [c for _, c, _ in filas],
                'vc_code[]': [code for _, _, code in filas], **extra}
        with app.app_context():
            data['name'] = db.session.get(Product, pid).name
        resp = self.client.post(f'/admin/productos/{pid}/editar', data=data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def variantes(self, nombre):
        """Lo guardado: ({(presentacion, color): (codigo de fabrica, hex)}, {(presentacion, color): codigo}, [colores])."""
        with app.app_context():
            p = self.producto(nombre)
            nombres = {x.id: x.name for x in Presentation.query.all()}
            enlaces = {(nombres[lk.presentation_id], lk.color_name): (lk.color_code, lk.hex_code) for lk in p.presentation_colors}
            codigos = {(nombres.get(c.presentation_id), c.color_name): c.code for c in p.variant_codes}
            colores = sorted(s.value for s in p.specs if s.key.lower() == 'color')
            return enlaces, codigos, colores

    def filas_de_pintura(self):
        """Las 4 variantes de cargar_pintura tal como las envia el formulario."""
        i, s = self.ids('1GL', '4GL'), self.sufijo
        return i, [(i['1GL'], 'AZUL', f'P1{s}'), (i['4GL'], 'AZUL', f'P2{s}'),
                   (i['1GL'], 'ROJO #103', f'P3{s}'), (i['4GL'], 'ROJO #103', f'P4{s}')]

    def test_el_formulario_muestra_cada_variante_con_su_codigo(self):
        self.cargar_pintura()
        _, html, filas = self.tabla_de_variantes(self.pintura)
        s = self.sufijo
        self.assertEqual(sorted(filas), sorted([('1GL', 'AZUL', f'P1{s}'), ('4GL', 'AZUL', f'P2{s}'),
                                                ('1GL', 'ROJO #103', f'P3{s}'), ('4GL', 'ROJO #103', f'P4{s}')]))
        self.assertIn('4 variantes · 4 con código', html)
        self.assertIn('id="variantAdd"', html)
        self.assertIn('id="variantRowTemplate"', html)

    def test_la_tabla_de_variantes_reemplaza_el_bloque_de_colores(self):
        # los colores ya no se repiten en Especificaciones: se agregan y editan en la tabla de variantes
        self.cargar_pintura()
        _, html, _ = self.tabla_de_variantes(self.pintura)
        self.assertIn('Variantes: presentación, color y código</h3>', html)
        self.assertNotIn('color-specs', html)
        self.assertNotIn('Colores del producto', html)
        especificaciones = html[html.index('id="specsContainer"'):html.index('id="variantEditor"')]
        self.assertNotIn('value="Color"', especificaciones)
        self.assertLess(html.index('id="variantEditor"'), html.index('class="form-actions"'))

    def test_guardar_sin_cambios_no_altera_las_variantes(self):
        self.cargar_pintura()
        antes = self.variantes(self.pintura)
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        self.guardar_variantes(pid, filas, [i['1GL'], i['4GL']])
        self.assertEqual(self.variantes(self.pintura), antes)
        self.assertEqual(antes[0][('1GL', 'ROJO')][0], '103')   # el codigo de fabrica sigue en su color

    def test_agregar_una_variante_con_un_color_nuevo(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        s = self.sufijo
        self.guardar_variantes(pid, filas + [(i['4GL'], f'  verde   lima {s.lower()} #77 ', f'N1{s}')], [i['1GL'], i['4GL']])
        enlaces, codigos, colores = self.variantes(self.pintura)
        self.assertEqual(enlaces[('4GL', f'VERDE LIMA {s}')], ('77', '#cccccc'))   # nombre limpio, en mayusculas, y su codigo de fabrica
        self.assertNotIn(('1GL', f'VERDE LIMA {s}'), enlaces)
        self.assertEqual(codigos[('4GL', f'VERDE LIMA {s}')], f'N1{s}')
        self.assertEqual(colores, ['AZUL', 'ROJO', f'VERDE LIMA {s}'])
        # la web la ofrece en esa presentacion, con su codigo
        opciones = app.test_client().get(f'/api/producto/{pid}/opciones').get_json()
        cuatro = next(p for p in opciones['presentations'] if p['name'] == '4GL')
        self.assertIn(f'VERDE LIMA {s} #77', [c['label'] for c in cuatro['colors']])
        self.assertIn({'p': i['4GL'], 'c': f'VERDE LIMA {s}', 'code': f'N1{s}'}, opciones['codes'])
        _, _, tabla = self.tabla_de_variantes(self.pintura)
        self.assertIn(('4GL', f'VERDE LIMA {s} #77', f'N1{s}'), tabla)

    def test_cambiar_el_color_y_el_codigo_de_una_variante(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        s = self.sufijo
        filas[0] = (i['1GL'], 'CELESTE #5', f'C1{s}')   # antes: 1GL AZUL P1
        filas[3] = (i['4GL'], 'ROJO #104', f'P4{s}')    # otro codigo de fabrica
        self.guardar_variantes(pid, filas, [i['1GL'], i['4GL']])
        enlaces, codigos, colores = self.variantes(self.pintura)
        self.assertEqual(set(enlaces), {('1GL', 'CELESTE'), ('4GL', 'AZUL'), ('1GL', 'ROJO'), ('4GL', 'ROJO')})
        self.assertEqual(enlaces[('1GL', 'CELESTE')][0], '5')
        self.assertEqual(enlaces[('4GL', 'ROJO')][0], '104')
        self.assertEqual(codigos, {('1GL', 'CELESTE'): f'C1{s}', ('4GL', 'AZUL'): f'P2{s}',
                                   ('1GL', 'ROJO'): f'P3{s}', ('4GL', 'ROJO'): f'P4{s}'})
        self.assertEqual(colores, ['AZUL', 'CELESTE', 'ROJO'])

    def test_quitar_variantes_borra_su_color_y_su_codigo(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        self.guardar_variantes(pid, filas[:2], [i['1GL'], i['4GL']])   # sin las filas de ROJO
        enlaces, codigos, colores = self.variantes(self.pintura)
        self.assertEqual(set(enlaces), {('1GL', 'AZUL'), ('4GL', 'AZUL')})
        self.assertEqual(set(codigos), {('1GL', 'AZUL'), ('4GL', 'AZUL')})
        self.assertEqual(colores, ['AZUL'])

    def test_una_fila_sin_codigo_conserva_el_color(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        filas[1] = (i['4GL'], 'AZUL', '')
        self.guardar_variantes(pid, filas, [i['1GL'], i['4GL']])
        enlaces, codigos, _ = self.variantes(self.pintura)
        self.assertIn(('4GL', 'AZUL'), enlaces)
        self.assertNotIn(('4GL', 'AZUL'), codigos)

    def test_quitar_una_presentacion_quita_sus_variantes(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        self.guardar_variantes(pid, filas, [i['1GL']])   # el formulario aun trae las filas de 4GL
        enlaces, codigos, colores = self.variantes(self.pintura)
        self.assertEqual(set(enlaces), {('1GL', 'AZUL'), ('1GL', 'ROJO')})
        self.assertEqual(set(codigos), {('1GL', 'AZUL'), ('1GL', 'ROJO')})
        self.assertEqual(colores, ['AZUL', 'ROJO'])

    def test_variantes_repetidas_se_guardan_una_vez(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        html = self.guardar_variantes(pid, filas + [(i['1GL'], 'azul', 'OTRO')], [i['1GL'], i['4GL']])
        self.assertIn('Variantes repetidas (se guardaron una sola vez): AZUL en 1GL.', html)
        self.assertEqual(self.variantes(self.pintura)[1][('1GL', 'AZUL')], f'P1{self.sufijo}')

    def test_las_filas_vacias_no_se_guardan(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        antes = self.variantes(self.pintura)
        self.guardar_variantes(pid, filas + [(i['1GL'], '  ', ''), (None, '', '')], [i['1GL'], i['4GL']])
        self.assertEqual(self.variantes(self.pintura), antes)

    def test_un_formulario_sin_la_tabla_no_toca_las_variantes(self):
        # p. ej. una pestana abierta con el formulario anterior (traia vc_present y los colores como especificaciones)
        self.cargar_pintura()
        antes = self.variantes(self.pintura)
        pid = self.tabla_de_variantes(self.pintura)[0]
        with app.app_context():
            ids = [p.id for p in self.producto(self.pintura).presentations]
        self.client.post(f'/admin/productos/{pid}/editar', data={
            'name': self.pintura, 'presentation_ids': ids, 'vc_present': '1', 'vc_pres[]': [str(ids[0])],
            'vc_color[]': ['AZUL'], 'vc_code[]': ['VIEJO'], 'spec_key[]': ['Color'], 'spec_value[]': ['AZUL']},
            follow_redirects=True)
        self.assertEqual(self.variantes(self.pintura), antes)

    def test_un_color_escrito_en_especificaciones_pasa_a_las_variantes(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        self.guardar_variantes(pid, filas, [i['1GL'], i['4GL']],
                               **{'spec_key[]': ['Color', 'Acabado', 'color'], 'spec_value[]': ['negro', 'Mate', 'AZUL']})
        enlaces, _, colores = self.variantes(self.pintura)
        self.assertEqual(colores, ['AZUL', 'NEGRO', 'ROJO'])   # AZUL ya estaba: no se repite
        self.assertEqual(len(enlaces), 4)
        with app.app_context():
            otras = [(s.key, s.value) for s in self.producto(self.pintura).specs if s.key.lower() != 'color']
        self.assertEqual(otras, [('Acabado', 'Mate')])
        _, _, tabla = self.tabla_de_variantes(self.pintura)
        self.assertIn(('Sin presentación', 'NEGRO', ''), tabla)

    def test_las_demas_especificaciones_se_guardan_aparte(self):
        self.cargar_pintura()
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        for _ in range(2):   # guardar dos veces no duplica nada
            self.guardar_variantes(pid, filas, [i['1GL'], i['4GL']],
                                   **{'spec_key[]': ['Acabado'], 'spec_value[]': ['Satinado']})
        with app.app_context():
            specs = sorted((s.key, s.value) for s in self.producto(self.pintura).specs)
        self.assertEqual(specs, [('Acabado', 'Satinado'), ('Color', 'AZUL'), ('Color', 'ROJO')])

    def test_conserva_el_tono_y_usa_el_conocido_para_un_color_nuevo(self):
        self.cargar_pintura()
        s = self.sufijo
        otro = f'ESMALTE {s}'
        self.importar([self.fila(f'E1{s}', otro, f'MORADO {s}', '1GL')])
        with app.app_context():
            self.producto(self.pintura).presentation_colors[0].hex_code = '#123456'
            primero = self.producto(self.pintura).presentation_colors[0]
            clave = (primero.presentation_id, primero.color_name)
            self.producto(otro).presentation_colors[0].hex_code = '#654321'
            db.session.add(PaintColor(name=f'Turquesa {s}', hex_code='#00aaaa'))
            db.session.commit()
            nombre_pres = db.session.get(Presentation, clave[0]).name
        pid = self.tabla_de_variantes(self.pintura)[0]
        i, filas = self.filas_de_pintura()
        self.guardar_variantes(pid, filas + [(i['1GL'], f'MORADO {s}', ''), (i['1GL'], f'TURQUESA {s}', ''),
                                             (i['1GL'], f'INVENTADO {s}', '')], [i['1GL'], i['4GL']])
        enlaces = self.variantes(self.pintura)[0]
        self.assertEqual(enlaces[(nombre_pres, clave[1])][1], '#123456')   # el tono que tenia
        self.assertEqual(enlaces[('1GL', f'MORADO {s}')][1], '#654321')   # el de otro producto
        self.assertEqual(enlaces[('1GL', f'TURQUESA {s}')][1], '#00aaaa')   # el de la paleta
        self.assertEqual(enlaces[('1GL', f'INVENTADO {s}')][1], '#cccccc')

    def test_la_tabla_sugiere_los_colores_conocidos(self):
        self.cargar_pintura()
        with app.app_context():
            db.session.add(PaintColor(name=f'Arena {self.sufijo}', hex_code='#d8c8a0'))
            db.session.commit()
        _, html, _ = self.tabla_de_variantes(self.pintura)
        sugerencias = html[html.index('<datalist id="variantColorNames">'):html.index('</datalist>')]
        self.assertIn('<option value="ROJO #103">', sugerencias)
        self.assertIn(f'<option value="ARENA {self.sufijo}">', sugerencias)
        self.assertIn(f'"ARENA {self.sufijo}": "#d8c8a0"', html)   # su tono para la muestra de la fila

    def test_producto_sin_presentaciones_tiene_una_fila_para_su_codigo(self):
        self.importar([self.fila(f'U{self.sufijo}', self.brocha)])
        pid, html, filas = self.tabla_de_variantes(self.brocha)
        self.assertEqual(filas, [('Sin presentación', '', f'U{self.sufijo}')])
        self.guardar_variantes(pid, [(None, '', f'V{self.sufijo}')], [])
        self.assertEqual(self.codigos(self.brocha), {(None, ''): f'V{self.sufijo}'})

    def test_producto_sin_presentaciones_con_colores(self):
        self.importar([self.fila(f'U{self.sufijo}', self.brocha)])
        pid = self.tabla_de_variantes(self.brocha)[0]
        s = self.sufijo
        self.guardar_variantes(pid, [(None, '', f'U{s}'), (None, 'BLANCO #1', f'B{s}')], [])
        enlaces, codigos, colores = self.variantes(self.brocha)
        self.assertEqual(enlaces, {})   # sin presentacion no hay enlace: el color es del producto
        self.assertEqual(codigos, {(None, ''): f'U{s}', (None, 'BLANCO'): f'B{s}'})
        self.assertEqual(colores, ['BLANCO'])
        _, _, tabla = self.tabla_de_variantes(self.brocha)
        self.assertEqual(tabla, [('Sin presentación', '', f'U{s}'), ('Sin presentación', 'BLANCO', f'B{s}')])

    def test_nuevo_producto_con_variantes(self):
        html = self.client.get('/admin/productos/nuevo').get_data(as_text=True)
        self.assertIn('Aún no hay variantes', html)
        self.assertIn('name="variants_present"', html)
        self.cargar_pintura()   # crea las presentaciones 1GL y 4GL
        i, s = self.ids('1GL', '4GL'), self.sufijo
        nombre = f'NUEVO {s}'
        resp = self.client.post('/admin/productos/nuevo', data={
            'name': nombre, 'sku': f'SKU{s}', 'is_active': 'on', 'presentation_ids': [i['1GL'], i['4GL']],
            'variants_present': '1', 'vc_pres[]': [str(i['1GL']), str(i['4GL'])], 'vc_color[]': [f'GRIS {s} #9', f'GRIS {s} #9'],
            'vc_code[]': [f'G1{s}', f'G4{s}'], 'spec_key[]': ['Acabado'], 'spec_value[]': ['Mate']}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        enlaces, codigos, colores = self.variantes(nombre)
        self.assertEqual(enlaces, {('1GL', f'GRIS {s}'): ('9', '#cccccc'), ('4GL', f'GRIS {s}'): ('9', '#cccccc')})
        self.assertEqual(codigos, {('1GL', f'GRIS {s}'): f'G1{s}', ('4GL', f'GRIS {s}'): f'G4{s}'})
        self.assertEqual(colores, [f'GRIS {s}'])

    # ---------- presentaciones con fraccion ----------

    def test_12_plg_no_se_confunde_con_1_2_plg(self):
        # slugify quita la barra: '1/2 PLG' y '12 PLG' darian el mismo slug '12-plg'
        rodillo = f'RODILLO {self.sufijo}'
        self.importar([self.fila(f'B{self.sufijo}', self.brocha, presentacion='1/2 PLG'),
                       self.fila(f'R{self.sufijo}', rodillo, presentacion='12 PLG')])
        with app.app_context():
            self.assertEqual([p.name for p in self.producto(self.brocha).presentations], ['1/2 PLG'])
            self.assertEqual([p.name for p in self.producto(rodillo).presentations], ['12 PLG'])
            doce = Presentation.query.filter_by(name='12 PLG').one()
            self.assertNotEqual(doce.slug, Presentation.query.filter_by(name='1/2 PLG').one().slug)
        # un segundo Excel con las mismas filas reutiliza cada presentacion por su nombre
        self.importar([self.fila(f'R{self.sufijo}', rodillo, presentacion='12 PLG')])
        with app.app_context():
            self.assertEqual(Presentation.query.filter_by(name='12 PLG').count(), 1)
            self.assertEqual(self.codigos(rodillo), {('12 PLG', ''): f'R{self.sufijo}'})


if __name__ == '__main__':
    unittest.main()
