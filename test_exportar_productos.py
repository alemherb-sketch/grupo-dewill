"""Pruebas de Admin > Productos > Exportar Excel: el catalogo en un .xlsx con la hoja Productos (una fila por variante, en el
formato del importador) y la hoja Detalle (una fila por producto, solo de consulta).

Se ejecutan contra una base SQLite temporal, nunca contra la real:

    python -m unittest test_exportar_productos -v
"""
import io
import os
import re
import tempfile
import unittest
import uuid

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test_exportar.db').replace(os.sep, '/')

from openpyxl import Workbook, load_workbook  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from import_template import IMPORT_COLUMNS  # noqa: E402
from models import (AdminUser, Brand, Category, Presentation, Product, ProductSpec, ProductYield,  # noqa: E402
                    SubCategory)
from product_export import DETAIL_COLUMNS, DETAIL_SHEET  # noqa: E402

app.config['TESTING'] = True

XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
HEADERS = ['Codigo', 'Categoria', 'Sub Categoria', 'Marca', 'Producto', 'Color', 'Presentacion']
PASSWORD = 'Clave-segura-1'
PASSWORD_HASH = generate_password_hash(PASSWORD)


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


def make_user(username, permissions):
    with app.app_context():
        user = AdminUser(username=username, is_active=True, is_admin=False, password_hash=PASSWORD_HASH)
        user.set_permissions(permissions)
        db.session.add(user)
        db.session.commit()


def login(username, password=PASSWORD):
    client = app.test_client()
    assert client.post('/admin/login', data={'username': username, 'password': password}).status_code == 302
    return client


class ExportarProductosTest(unittest.TestCase):
    def setUp(self):
        self.client = login('admin', 'admin123')
        s = self.s = uuid.uuid4().hex[:6].upper()
        self.categoria, self.subcategoria, self.marca = f'CATEGORIA {s}', f'SUB {s}', f'MARCA {s}'
        self.pintura, self.brocha, self.cinta = f'LATEX {s}', f'BROCHA {s}', f'CINTA {s}'
        self.importar([
            [f'0883{s}', self.categoria, self.subcategoria, self.marca, self.pintura, 'AZUL #41', '1GL'],
            [f'0884{s}', self.categoria, self.subcategoria, self.marca, self.pintura, 'AZUL #41', '4GL'],
            [f'0885{s}', self.categoria, self.subcategoria, self.marca, self.pintura, 'ROJO', '1GL'],
            [f'0886{s}', self.categoria, self.subcategoria, self.marca, self.pintura, 'ROJO', '4GL'],
            [f'4470{s}', self.categoria, self.subcategoria, self.marca, self.brocha, None, '1 PLG'],
            [f'4975{s}', self.categoria, self.subcategoria, self.marca, self.brocha, None, '1 1/2 PLG'],
            [f'0771{s}', self.categoria, self.subcategoria, self.marca, self.cinta, None, None],
        ])

    # ---------- utilidades ----------

    def importar(self, rows, buf=None, client=None):
        resp = (client or self.client).post(
            '/admin/productos/importar', data={'excel_file': (buf or xlsx(HEADERS, rows), 'productos.xlsx')},
            content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Importación completada', resp.get_data(as_text=True))

    def exportar(self, **params):
        params = {'q': self.s, **params}
        resp = self.client.get('/admin/productos/exportar', query_string={k: v for k, v in params.items() if v is not None})
        self.assertEqual(resp.status_code, 200)
        return resp

    def libro(self, resp):
        return load_workbook(io.BytesIO(resp.data))

    def filas(self, ws):
        return [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]

    def hoja_productos(self, **params):
        return self.filas(self.libro(self.exportar(**params))['Productos'])

    def crear(self, name, **fields):
        with app.app_context():
            ids = {'category_id': Category.query.filter_by(name=self.categoria).one().id,
                   'subcategory_id': SubCategory.query.filter_by(name=self.subcategoria).one().id,
                   'brand_id': Brand.query.filter_by(name=self.marca).one().id}
            product = Product(name=name, **{**ids, **fields})
            db.session.add(product)
            db.session.commit()
            return product.id

    def producto(self, nombre):
        return Product.query.filter_by(name=nombre).one()

    def foto(self):
        """Lo que importa de los productos de la prueba, por nombre: presentaciones, colores con su codigo, codigos y SKU."""
        with app.app_context():
            fotos = {}
            for p in Product.query.filter(Product.name.like(f'%{self.s}')).all():
                nombres = {x.id: x.name for x in Presentation.query.all()}
                fotos[p.name] = {
                    'sku': p.sku,
                    'presentaciones': sorted(x.name for x in p.presentations),
                    'colores': sorted((nombres[lk.presentation_id], lk.color_name, lk.color_code) for lk in p.presentation_colors),
                    'codigos': sorted((nombres.get(vc.presentation_id, ''), vc.color_name, vc.code) for vc in p.variant_codes),
                    'especificaciones': sorted((sp.key, sp.value) for sp in p.specs),
                }
            return fotos

    # ---------- el archivo ----------

    def test_descarga_un_xlsx_con_la_fecha_en_el_nombre(self):
        resp = self.exportar()
        self.assertEqual(resp.mimetype, XLSX)
        self.assertRegex(resp.headers['Content-Disposition'],
                         r'^attachment; filename=productos-grupo-dewill-\d{4}-\d{2}-\d{2}\.xlsx$')
        wb = self.libro(resp)
        self.assertEqual(wb.sheetnames, ['Productos', DETAIL_SHEET])
        self.assertEqual(wb.active.title, 'Productos')   # se abre en la hoja que se importa

    def test_la_hoja_productos_tiene_una_fila_por_variante_en_el_formato_del_importador(self):
        s, c, sc, m = self.s, self.categoria, self.subcategoria, self.marca
        ws = self.libro(self.exportar())['Productos']
        self.assertEqual([cell.value for cell in ws[1]], IMPORT_COLUMNS)
        self.assertEqual(self.filas(ws), [
            [f'4975{s}', c, sc, m, self.brocha, None, '1 1/2 PLG'],
            [f'4470{s}', c, sc, m, self.brocha, None, '1 PLG'],
            [f'0771{s}', c, sc, m, self.cinta, None, None],
            [f'0883{s}', c, sc, m, self.pintura, 'AZUL #41', '1GL'],
            [f'0885{s}', c, sc, m, self.pintura, 'ROJO', '1GL'],
            [f'0884{s}', c, sc, m, self.pintura, 'AZUL #41', '4GL'],
            [f'0886{s}', c, sc, m, self.pintura, 'ROJO', '4GL'],
        ])

    def test_los_codigos_son_texto_y_conservan_los_ceros(self):
        ws = self.libro(self.exportar())['Productos']
        codigos = [row[0] for row in ws.iter_rows(min_row=2)]
        self.assertTrue(all(c.data_type == 's' and c.number_format == '@' for c in codigos))
        self.assertTrue(all(c.value.startswith(('0', '4')) for c in codigos))   # 0883..., 4470...: no se vuelven numeros
        self.assertEqual(ws.auto_filter.ref, f'A1:G{len(codigos) + 1}')
        self.assertEqual(ws.freeze_panes, 'A2')

    def test_un_producto_sin_variantes_sale_con_su_sku(self):
        self.crear(f'TIJERA {self.s}', sku=f'T-{self.s}')
        fila = next(f for f in self.hoja_productos() if f[4] == f'TIJERA {self.s}')
        self.assertEqual(fila, [f'T-{self.s}', self.categoria, self.subcategoria, self.marca, f'TIJERA {self.s}', None, None])

    def test_con_presentaciones_sin_codigo_no_se_inventan_codigos(self):
        pid = self.crear(f'RODILLO {self.s}', sku=f'R-{self.s}')
        with app.app_context():
            p = db.session.get(Product, pid)
            p.presentations = list(Presentation.query.filter(Presentation.name.in_(['1GL', '4GL'])).all())
            db.session.commit()
        filas = [f for f in self.hoja_productos() if f[4] == f'RODILLO {self.s}']
        self.assertEqual([(f[0], f[6]) for f in filas], [(None, '1GL'), (None, '4GL')])

    def test_un_color_sin_presentacion_sale_en_su_fila(self):
        pid = self.crear(f'BARNIZ {self.s}', sku=f'B-{self.s}')
        with app.app_context():
            db.session.add(ProductSpec(product_id=pid, key='Color', value='NEGRO'))
            db.session.commit()
        filas = [f for f in self.hoja_productos() if f[4] == f'BARNIZ {self.s}']
        self.assertEqual([(f[0], f[5], f[6]) for f in filas], [(None, 'NEGRO', None)])

    def test_el_orden_es_categoria_subcategoria_marca_y_nombre(self):
        s = self.s
        self.importar([[f'9001{s}', f'AAA {s}', f'ZZZ {s}', f'MARCA {s}', f'PEGAMENTO {s}', None, None],
                       [f'9002{s}', f'AAA {s}', f'BBB {s}', f'MARCA {s}', f'ZETA {s}', None, None],
                       [f'9003{s}', f'AAA {s}', f'BBB {s}', f'MARCA {s}', f'alfa {s}', None, None]])
        orden = []
        for fila in self.hoja_productos():
            clave = (fila[1], fila[2], fila[4])
            if not orden or orden[-1] != clave:
                orden.append(clave)
        self.assertEqual(orden, [(f'AAA {s}', f'BBB {s}', f'alfa {s}'), (f'AAA {s}', f'BBB {s}', f'ZETA {s}'),
                                 (f'AAA {s}', f'ZZZ {s}', f'PEGAMENTO {s}'),
                                 (self.categoria, self.subcategoria, self.brocha), (self.categoria, self.subcategoria, self.cinta),
                                 (self.categoria, self.subcategoria, self.pintura)])

    # ---------- hoja Detalle ----------

    def test_la_hoja_detalle_tiene_una_fila_por_producto(self):
        s = self.s
        with app.app_context():
            pres = {p.name: p.id for p in Presentation.query.filter(Presentation.name.in_(['1GL', '4GL'])).all()}
            pintura_id = self.producto(self.pintura).id
            db.session.add_all([ProductYield(product_id=pintura_id, presentation_id=pres['1GL'], area_m2=21, coats=2),
                                ProductYield(product_id=pintura_id, presentation_id=pres['4GL'], area_m2=84, coats=2)])
            db.session.commit()
        esmalte_id = self.crear(f'ESMALTE {s}', sku=f'E{s}', is_active=False, is_featured=True,
                                description='Esmalte sintético', technical_description='Secado: 4 h')
        ws = self.libro(self.exportar())[DETAIL_SHEET]
        self.assertEqual([cell.value for cell in ws[1]], DETAIL_COLUMNS)
        detalle = {fila[1]: dict(zip(DETAIL_COLUMNS, fila)) for fila in self.filas(ws)}
        self.assertEqual(list(detalle), [self.brocha, self.cinta, f'ESMALTE {s}', self.pintura])   # el mismo orden de Productos
        pintura = detalle[self.pintura]
        self.assertEqual((pintura['MARCA'], pintura['CATEGORIA'], pintura['SUBCATEGORIA'], pintura['ESTADO'], pintura['DESTACADO']),
                         (self.marca, self.categoria, self.subcategoria, 'Activo', 'No'))
        self.assertEqual((pintura['PRESENTACIONES'], pintura['COLORES'], pintura['VARIANTES'], pintura['VARIANTES CON CODIGO']),
                         ('1GL, 4GL', 2, 4, 4))
        self.assertEqual(pintura['RENDIMIENTO'], '1GL: 21 m² a 2 manos; 4GL: 84 m² a 2 manos')
        self.assertEqual(pintura['SKU'], f'0883{s}')
        esmalte = detalle[f'ESMALTE {s}']
        self.assertEqual((esmalte['ID'], esmalte['ESTADO'], esmalte['DESTACADO'], esmalte['SKU'], esmalte['DESCRIPCION'],
                          esmalte['DESCRIPCION TECNICA'], esmalte['RENDIMIENTO'], esmalte['VARIANTES'],
                          esmalte['VARIANTES CON CODIGO']),
                         (esmalte_id, 'Inactivo', 'Sí', f'E{s}', 'Esmalte sintético', 'Secado: 4 h', None, 1, 1))   # su SKU es su codigo
        brocha = detalle[self.brocha]
        self.assertEqual((brocha['PRESENTACIONES'], brocha['COLORES'], brocha['VARIANTES']), ('1 1/2 PLG, 1 PLG', 0, 2))

    def test_el_rendimiento_de_un_producto_sin_presentaciones_es_el_de_su_unidad(self):
        pid = self.crear(f'SELLADOR {self.s}', sku=f'S-{self.s}')
        with app.app_context():
            db.session.add(ProductYield(product_id=pid, presentation_id=None, area_m2=10.5, coats=1))
            db.session.commit()
        ws = self.libro(self.exportar())[DETAIL_SHEET]
        fila = next(f for f in self.filas(ws) if f[1] == f'SELLADOR {self.s}')
        self.assertEqual(fila[DETAIL_COLUMNS.index('RENDIMIENTO')], '10.5 m² a 1 mano')

    def test_la_hoja_detalle_no_se_toma_por_la_hoja_de_productos(self):
        # sus encabezados no son los del importador: si el libro se guarda mirando el Detalle, se importa igual la hoja Productos
        antes = self.foto()
        wb = self.libro(self.exportar())
        wb.active = wb.worksheets.index(wb[DETAIL_SHEET])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        self.importar(None, buf=buf)
        self.assertEqual(self.foto(), antes)

    # ---------- filtros de la lista ----------

    def test_sin_filtros_baja_todo_el_catalogo(self):
        self.crear(f'INACTIVO {self.s}', sku=f'I-{self.s}', is_active=False)
        wb = self.libro(self.exportar(q=None))
        nombres = {f[4] for f in self.filas(wb['Productos'])}
        self.assertTrue({self.pintura, self.brocha, self.cinta, f'INACTIVO {self.s}'} <= nombres)
        with app.app_context():   # una fila de Detalle por producto del catalogo, tambien los inactivos
            self.assertEqual({f[0] for f in self.filas(wb[DETAIL_SHEET])}, {p.id for p in Product.query.all()})

    def test_respeta_la_busqueda_de_la_lista(self):
        s = self.s
        self.assertEqual({f[4] for f in self.hoja_productos(q=self.pintura)}, {self.pintura})
        self.assertEqual({f[4] for f in self.hoja_productos(q=f'0884{s}')}, {self.pintura})   # por el codigo de una variante
        self.assertEqual({f[4] for f in self.hoja_productos(q=f'4470{s}')}, {self.brocha})
        self.assertEqual(self.hoja_productos(q=f'no existe {s} nada'), [])

    def test_respeta_la_categoria_de_la_lista(self):
        s = self.s
        self.importar([[f'8001{s}', f'OTRA CATEGORIA {s}', f'OTRA SUB {s}', f'MARCA {s}', f'OTRO {s}', None, None]])
        with app.app_context():
            cat_id = Category.query.filter_by(name=self.categoria).one().id
        self.assertEqual({f[4] for f in self.hoja_productos(cat=str(cat_id))}, {self.pintura, self.brocha, self.cinta})
        self.assertEqual({f[4] for f in self.hoja_productos(cat=None)} - {f'OTRO {s}'},
                         {self.pintura, self.brocha, self.cinta})
        # una categoria que no es un numero se ignora (la lista del panel tampoco se rompe)
        self.assertEqual(len(self.hoja_productos(cat='abc')), len(self.hoja_productos()))
        self.assertEqual(self.client.get('/admin/productos', query_string={'cat': 'abc', 'q': s}).status_code, 200)

    # ---------- caracteres raros ----------

    def test_un_texto_con_caracteres_de_control_o_que_empieza_por_igual_no_rompe_el_archivo(self):
        s = self.s
        self.crear(f'=SUMA(1;1) {s}', sku=f'X-{s}', description='linea uno\x0b linea dos\x01')
        wb = self.libro(self.exportar())
        celda = next(row[4] for row in wb['Productos'].iter_rows(min_row=2) if (row[4].value or '').endswith(s) and row[4].value.startswith('='))
        self.assertEqual((celda.value, celda.data_type), (f'=SUMA(1;1) {s}', 's'))   # texto, no formula
        detalle = self.filas(wb[DETAIL_SHEET])
        fila = next(f for f in detalle if f[1] == f'=SUMA(1;1) {s}')
        self.assertEqual(fila[DETAIL_COLUMNS.index('DESCRIPCION')], 'linea uno linea dos')

    # ---------- ida y vuelta con el importador ----------

    def test_importar_lo_exportado_no_cambia_nada(self):
        antes = self.foto()
        self.assertEqual(sorted(antes), sorted([self.pintura, self.brocha, self.cinta]))
        self.importar(None, buf=io.BytesIO(self.exportar().data))
        self.assertEqual(self.foto(), antes)
        self.assertEqual(antes[self.pintura]['colores'], [('1GL', 'AZUL', '41'), ('1GL', 'ROJO', None),
                                                          ('4GL', 'AZUL', '41'), ('4GL', 'ROJO', None)])

    def test_lo_que_se_corrige_en_el_excel_exportado_se_importa(self):
        s = self.s
        wb = self.libro(self.exportar())
        ws = wb['Productos']
        for row in ws.iter_rows(min_row=2):
            if row[0].value == f'0885{s}':
                row[0].value = f'NUEVO{s}'   # otro codigo para 1GL ROJO
            if row[0].value == f'0886{s}':
                row[5].value = 'ROJO TEJA #103'   # color con codigo de fabrica
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        self.importar(None, buf=buf)
        pintura = self.foto()[self.pintura]
        self.assertIn(('1GL', 'ROJO', f'NUEVO{s}'), pintura['codigos'])
        self.assertIn(('4GL', 'ROJO TEJA', f'0886{s}'), pintura['codigos'])
        self.assertIn(('4GL', 'ROJO TEJA', '103'), pintura['colores'])

    # ---------- permisos y pantallas ----------

    def test_permisos_de_la_exportacion(self):
        self.assertEqual(app.test_client().get('/admin/productos/exportar').status_code, 302)   # sin sesion: al login
        make_user(f'sin{self.s}', {'blog': 'manage'})
        self.assertEqual(login(f'sin{self.s}').get('/admin/productos/exportar').status_code, 403)
        make_user(f'lector{self.s}', {'productos': 'view'})   # consultar el modulo basta para bajar el Excel
        resp = login(f'lector{self.s}').get('/admin/productos/exportar', query_string={'q': self.s})
        self.assertEqual((resp.status_code, resp.mimetype), (200, XLSX))

    def test_la_lista_ofrece_el_boton_con_la_busqueda_y_la_categoria(self):
        html = self.client.get('/admin/productos').get_data(as_text=True)
        self.assertIn('href="/admin/productos/exportar"', html)
        self.assertIn('Exportar Excel', html)
        self.assertIn('todo el catálogo', html)
        html = self.client.get('/admin/productos', query_string={'q': self.s, 'cat': '3'}).get_data(as_text=True)
        self.assertIn(f'href="/admin/productos/exportar?q={self.s}&amp;cat=3"', html)
        self.assertRegex(html, r'title="Descarga en Excel los \d+ productos? de esta búsqueda"')

    def test_la_pagina_de_importar_explica_como_editar_lo_exportado(self):
        html = re.sub(r'\s+', ' ', self.client.get('/admin/productos/importar').get_data(as_text=True))
        self.assertIn('Exportar Excel', html)
        self.assertIn('«Detalle» es solo de consulta', html)


if __name__ == '__main__':
    unittest.main()
