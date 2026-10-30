"""Pruebas del rendimiento de los productos ('un galon rinde 21 m2 a 2 manos'): se configura por presentacion en el
panel, se muestra en las tarjetas, la ficha y el selector, y el pedido lleva el total (m2 x cantidad).

Se ejecutan contra una base SQLite temporal, nunca contra la base real, y sin enviar correos:

    python -m unittest test_rendimiento -v
"""
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

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import Presentation, Product, ProductYield, QuoteItem, QuoteRequest, SiteConfig  # noqa: E402
from models import format_m2, yield_label  # noqa: E402

app.config['TESTING'] = True
CLIENTE = {'name': 'Cliente de prueba', 'document': '12345678', 'phone': '987654321'}


class SyncThread:
    """Ejecuta el envio del correo en el acto para poder inspeccionarlo."""
    def __init__(self, target, args=(), kwargs=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


class FormatoTest(unittest.TestCase):
    def test_metros_sin_ceros_de_mas(self):
        self.assertEqual([format_m2(x) for x in (21.0, 10.5, 31.25, 0.1 * 3, 1250.0)], ['21', '10.5', '31.25', '0.3', '1250'])

    def test_mano_en_singular(self):
        self.assertEqual(yield_label(63, 2), '63 m² a 2 manos')
        self.assertEqual(yield_label(10.5, 1), '10.5 m² a 1 mano')


class RendimientoTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            QuoteItem.query.delete()
            QuoteRequest.query.delete()
            SiteConfig.set('notify_email', 'destino@example.com')
            db.session.commit()
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        self.s = uuid.uuid4().hex[:6].upper()
        with app.app_context():
            self.gl = self.presentacion('1GL')
            self.balde = self.presentacion('4GL')

    def presentacion(self, name):
        p = Presentation.query.filter_by(name=name).first()
        if not p:
            p = Presentation(name=name, slug=name.lower())
            db.session.add(p)
            db.session.commit()
        return p.id

    def crear_pintura(self, rendimientos=None):
        """Pintura en 1GL y 4GL; rendimientos: {presentation_id: (m2, manos)}."""
        with app.app_context():
            p = Product(name=f'LATEX {self.s}', sku=f'SKU{self.s}', is_active=True,
                        presentations=[db.session.get(Presentation, self.gl), db.session.get(Presentation, self.balde)])
            db.session.add(p)
            db.session.flush()
            for pres_id, (m2, coats) in (rendimientos or {}).items():
                db.session.add(ProductYield(product_id=p.id, presentation_id=pres_id, area_m2=m2, coats=coats))
            db.session.commit()
            return p.id

    def editar(self, pid, **campos):
        data = {'name': f'LATEX {self.s}', 'presentation_ids': [self.gl, self.balde], **campos}
        return self.client.post(f'/admin/productos/{pid}/editar', data=data, follow_redirects=True)

    def rendimientos(self, pid):
        with app.app_context():
            return {y.presentation_id: (y.area_m2, y.coats) for y in ProductYield.query.filter_by(product_id=pid)}

    # ---------- panel ----------

    def test_el_panel_guarda_el_rendimiento_de_cada_presentacion(self):
        pid = self.crear_pintura()
        self.editar(pid, **{f'yield_m2_{self.gl}': '21', f'yield_coats_{self.gl}': '2',
                            f'yield_m2_{self.balde}': '84,5', f'yield_coats_{self.balde}': '2'})
        self.assertEqual(self.rendimientos(pid), {self.gl: (21.0, 2), self.balde: (84.5, 2)})
        html = self.client.get(f'/admin/productos/{pid}/editar').get_data(as_text=True)
        self.assertIn(f'name="yield_m2_{self.gl}" value="21"', html)
        self.assertIn(f'name="yield_m2_{self.balde}" value="84.5"', html)

    def test_sin_datos_no_guarda_rendimiento_y_una_fila_incompleta_se_avisa(self):
        pid = self.crear_pintura({self.gl: (21, 2)})
        html = self.editar(pid, **{f'yield_m2_{self.gl}': '', f'yield_coats_{self.gl}': '',
                                   f'yield_m2_{self.balde}': '84', f'yield_coats_{self.balde}': ''}).get_data(as_text=True)
        self.assertEqual(self.rendimientos(pid), {})
        self.assertIn('El rendimiento de 4GL necesita', html)

    def test_quitar_una_presentacion_quita_su_rendimiento(self):
        pid = self.crear_pintura({self.gl: (21, 2), self.balde: (84, 2)})
        self.editar(pid, presentation_ids=[self.gl], **{f'yield_m2_{self.gl}': '21', f'yield_coats_{self.gl}': '2',
                                                       f'yield_m2_{self.balde}': '84', f'yield_coats_{self.balde}': '2'})
        self.assertEqual(self.rendimientos(pid), {self.gl: (21.0, 2)})

    def test_producto_sin_presentaciones_usa_el_rendimiento_por_unidad(self):
        resp = self.client.post('/admin/productos/nuevo', data={'name': f'SELLADOR {self.s}', 'yield_m2_0': '30',
                                                                'yield_coats_0': '1'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        with app.app_context():
            pid = Product.query.filter_by(name=f'SELLADOR {self.s}').one().id
        self.assertEqual(self.rendimientos(pid), {None: (30.0, 1)})

    def test_los_campos_vacios_no_se_muestran_ni_se_guardan_como_none(self):
        pid = self.crear_pintura()
        html = self.client.get(f'/admin/productos/{pid}/editar').get_data(as_text=True)
        self.assertNotIn('>None</textarea>', html)
        self.assertNotIn('value="None"', html)
        self.editar(pid, description='', technical_description='  ', video_url='')
        with app.app_context():
            p = db.session.get(Product, pid)
            self.assertEqual((p.description, p.technical_description, p.video_url), (None, None, None))

    # ---------- tarjeta, selector y ficha ----------

    def test_la_tarjeta_muestra_el_rendimiento_de_la_presentacion_mas_chica(self):
        self.crear_pintura({self.balde: (84, 2), self.gl: (21, 2)})
        html = re.sub(r'\s+', ' ', self.client.get('/productos', query_string={'q': self.s}).get_data(as_text=True))
        self.assertIn('Rinde <strong>21 m²</strong> por 1GL a 2 manos', html)

    def test_sin_rendimiento_la_tarjeta_no_lo_muestra(self):
        self.crear_pintura()
        self.assertNotIn('pcr-yield', self.client.get('/productos', query_string={'q': self.s}).get_data(as_text=True))

    def test_el_selector_y_la_ficha_reciben_el_rendimiento_de_cada_presentacion(self):
        pid = self.crear_pintura({self.gl: (21, 2)})
        datos = self.client.get(f'/api/producto/{pid}/opciones').get_json()
        self.assertEqual({p['name']: p['yield'] for p in datos['presentations']},
                         {'1GL': {'m2': 21.0, 'coats': 2}, '4GL': None})
        html = self.client.get(f'/producto/{pid}').get_data(as_text=True)
        self.assertEqual(json.loads(re.search(r'const YIELDS = (\{.*?\});', html).group(1)), {str(self.gl): {'m2': 21.0, 'coats': 2}})
        self.assertIn('id="detailYield"', html)

    # ---------- pedido ----------

    def cotizar(self, items):
        enviados = []
        with mock.patch('app.send_async_email', lambda _app, datos: enviados.append(datos)), \
                mock.patch('app.threading', types.SimpleNamespace(Thread=SyncThread)), \
                mock.patch.dict(app.config, {'MAIL_USERNAME': 'prueba@example.com'}):
            resp = self.client.post('/api/cotizacion', json={**CLIENTE, 'items': items})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        return resp.get_json()['quote_id'], enviados

    def test_el_pedido_lleva_el_rendimiento_total_calculado_por_el_servidor(self):
        pid = self.crear_pintura({self.gl: (21, 2)})
        qid, enviados = self.cotizar([
            {'product_id': pid, 'quantity': 3, 'presentation': '1GL', 'yield_m2': 999},   # el navegador no decide el total
            {'product_id': pid, 'quantity': 2, 'presentation': '4GL'},                    # 4GL sin rendimiento
        ])
        with app.app_context():
            items = [(i.presentation, i.yield_m2, i.yield_coats, i.yield_text)
                     for i in QuoteItem.query.filter_by(quote_id=qid).order_by(QuoteItem.id)]
        self.assertEqual(items, [('1GL', 63.0, 2, '63 m² a 2 manos'), ('4GL', None, None, '')])
        self.assertIn('Presentación: 1GL x 3 - Rendimiento: 63 m² a 2 manos', enviados[0]['body'])
        panel = self.client.get(f'/admin/solicitudes/{qid}').get_data(as_text=True)
        self.assertIn('Rendimiento: <strong>63 m² a 2 manos</strong>', panel)

    def test_producto_sin_presentaciones_rinde_por_unidad(self):
        with app.app_context():
            p = Product(name=f'SELLADOR {self.s}', sku=f'S{self.s}', is_active=True)
            db.session.add(p)
            db.session.flush()
            db.session.add(ProductYield(product_id=p.id, presentation_id=None, area_m2=12.5, coats=1))
            db.session.commit()
            pid = p.id
        qid, _ = self.cotizar([{'product_id': pid, 'quantity': 4}])
        with app.app_context():
            self.assertEqual(QuoteItem.query.filter_by(quote_id=qid).one().yield_text, '50 m² a 1 mano')


if __name__ == '__main__':
    unittest.main()
