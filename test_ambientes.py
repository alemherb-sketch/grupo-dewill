"""Pruebas del enlace de las imagenes de Ambientes a un producto: se elige en el panel (Admin > Ambientes) y al hacer
clic en la imagen del modal se abre la ficha del producto.

Se ejecutan contra una base SQLite temporal, nunca contra la base real:

    python -m unittest test_ambientes -v
"""
import os
import tempfile
import unittest
import uuid

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import AmbientCategory, AmbientImage, Product, SiteConfig  # noqa: E402

app.config['TESTING'] = True


class EnlaceAmbientesTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            SiteConfig.set('disabled_pages', '')
            db.session.commit()
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        s = uuid.uuid4().hex[:6]
        with app.app_context():
            self.producto = self.crear_producto(f'DURALATEX {s}')
            self.otro = self.crear_producto(f'SATINADO {s}')
            self.nombre = f'Sala {s}'
            a = AmbientCategory(name=self.nombre, slug=f'sala-{s}', type='room', area='interior')
            db.session.add(a)
            db.session.flush()
            imgs = [AmbientImage(category_id=a.id, image_url=f'uploads/ambientes/{s}-{n}.jpg', order=n) for n in range(2)]
            db.session.add_all(imgs)
            db.session.commit()
            self.ambiente, self.imagenes = a.id, [i.id for i in imgs]

    def crear_producto(self, name, active=True):
        p = Product(name=name, sku=uuid.uuid4().hex[:10], is_active=active)
        db.session.add(p)
        db.session.flush()
        return p.id

    def guardar(self, **enlaces):
        data = {'name': self.nombre, 'type': 'room', 'area': 'interior', 'order': '0', **enlaces}
        resp = self.client.post(f'/admin/ambientes/{self.ambiente}/editar', data=data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def enlaces(self):
        with app.app_context():
            return [db.session.get(AmbientImage, i).product_id for i in self.imagenes]

    def api(self):
        return [img['product'] for img in self.client.get(f'/api/ambientes/{self.ambiente}').get_json()['images']]

    # ---------- panel ----------

    def test_el_panel_guarda_el_producto_de_cada_imagen(self):
        img1, img2 = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto), f'image_product_{img2}': ''})
        self.assertEqual(self.enlaces(), [self.producto, None])
        html = self.client.get(f'/admin/ambientes/{self.ambiente}/editar').get_data(as_text=True)
        self.assertRegex(html, rf'<option value="{self.producto}"[^>]* selected>')
        self.assertIn(f'name="image_product_{img2}"', html)
        # el buscador (sobre la misma lista) muestra el producto enlazado
        combo = html[html.index(f'data-select="imgProduct{img1}"'):html.index(f'name="image_product_{img1}"')]
        self.assertRegex(combo, r'class="form-input product-combo-input" value="DURALATEX ')

    def test_quitar_el_enlace_y_un_producto_inexistente(self):
        img1, img2 = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto), f'image_product_{img2}': str(self.otro)})
        self.guardar(**{f'image_product_{img1}': '', f'image_product_{img2}': '999999'})
        self.assertEqual(self.enlaces(), [None, None])

    def test_un_formulario_sin_el_campo_no_borra_el_enlace(self):
        img1, _ = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto)})
        self.guardar()   # p. ej. un formulario viejo en otra pestana
        self.assertEqual(self.enlaces()[0], self.producto)

    # ---------- modal de la pagina Ambientes ----------

    def test_el_modal_recibe_el_enlace_de_cada_imagen(self):
        img1, _ = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto)})
        enlace, sin_enlace = self.api()
        self.assertEqual(enlace['id'], self.producto)
        self.assertEqual(enlace['url'], f'/producto/{self.producto}')
        self.assertTrue(enlace['name'].startswith('DURALATEX'))
        self.assertIsNone(sin_enlace)

    def test_producto_inactivo_no_se_enlaza(self):
        img1, _ = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto)})
        with app.app_context():
            db.session.get(Product, self.producto).is_active = False
            db.session.commit()
        self.assertEqual(self.api(), [None, None])

    def test_con_la_pagina_productos_deshabilitada_no_hay_enlaces(self):
        img1, _ = self.imagenes
        self.guardar(**{f'image_product_{img1}': str(self.producto)})
        with app.app_context():
            SiteConfig.set('disabled_pages', 'productos')
            db.session.commit()
        self.assertEqual(self.api(), [None, None])

    def test_la_pagina_arma_el_enlace_en_el_modal(self):
        html = self.client.get('/galeria/ambientes').get_data(as_text=True)
        self.assertIn('ambient-slide-link', html)


if __name__ == '__main__':
    unittest.main()
