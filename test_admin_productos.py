"""Pruebas del contador de la lista de productos del panel (Admin > Productos).

Se ejecutan contra una base SQLite temporal, nunca contra la base real:

    python -m unittest test_admin_productos -v
"""
import os
import re
import tempfile
import unittest
import uuid

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import Product  # noqa: E402

app.config['TESTING'] = True


def text(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


class ContadorProductosTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        self.sufijo = uuid.uuid4().hex[:8].upper()

    def crear(self, n, active=True, featured=False):
        with app.app_context():
            for _ in range(n):
                db.session.add(Product(name=f'PRODUCTO {self.sufijo} {uuid.uuid4().hex[:6]}', sku=uuid.uuid4().hex[:12],
                                       is_active=active, is_featured=featured))
            db.session.commit()

    def lista(self, **params):
        """(texto del contador, texto de toda la pagina) de Admin > Productos."""
        html = self.client.get('/admin/productos', query_string=params).get_data(as_text=True)
        m = re.search(r'<div class="gallery-summary">(.*?)<div class="admin-toolbar">', html, re.S)
        self.assertIsNotNone(m, 'la lista debe mostrar el contador sobre la barra de busqueda')
        return text(m.group(1)), text(html)

    def test_sin_filtros_cuenta_todo_el_catalogo(self):
        self.crear(2)
        with app.app_context():
            total = Product.query.count()
            activos = Product.query.filter(Product.is_active.is_(True)).count()
            destacados = Product.query.filter(Product.is_featured.is_(True)).count()
        resumen, pagina = self.lista()
        self.assertIn(f'{total} Productos', resumen)
        self.assertIn(f'{activos} Activo', resumen)
        self.assertIn(f'{total - activos} Inactivo', resumen)
        self.assertIn(f'{destacados} Destacado', resumen)
        self.assertIn(f'Mostrando 1–{min(total, 20)} de {total}', pagina)

    def test_con_busqueda_cuenta_los_resultados_y_sus_estados(self):
        self.crear(2, active=True, featured=True)
        self.crear(1, active=False)
        with app.app_context():
            total = Product.query.count()
        resumen, pagina = self.lista(q=self.sufijo)
        self.assertEqual(resumen, f'3 Resultados de {total} 2 Activos 1 Inactivo 2 Destacados')
        self.assertIn('Mostrando 1–3 de 3', pagina)

    def test_busqueda_sin_resultados(self):
        resumen, pagina = self.lista(q='NO-EXISTE-' + self.sufijo)
        self.assertTrue(resumen.startswith('0 Resultados de '), resumen)
        self.assertIn('Ningún producto coincide con la búsqueda.', pagina)
        self.assertNotIn('Mostrando', pagina)

    def test_el_tramo_sigue_la_pagina(self):
        self.crear(23)
        self.assertIn('Mostrando 1–20 de 23', self.lista(q=self.sufijo)[1])
        self.assertIn('Mostrando 21–23 de 23', self.lista(q=self.sufijo, page=2)[1])


if __name__ == '__main__':
    unittest.main()
