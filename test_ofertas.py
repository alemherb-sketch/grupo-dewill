"""Pruebas de la seccion OFERTAS (debajo de Marcas en la portada) y de su modulo en el panel de administracion.

Se ejecutan contra una base SQLite temporal y una carpeta de subidas temporal, nunca contra las reales:

    python -m unittest test_ofertas -v
"""
import io
import os
import re
import tempfile
import unittest
import uuid

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from PIL import Image  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from app import app, db, _clean_offer_link  # noqa: E402
from models import AdminUser, Brand, Offer, SiteConfig  # noqa: E402

app.config['TESTING'] = True
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='dewill_uploads_')

PASSWORD = 'Clave-segura-1'


def png(color='red', size=(1200, 400)):
    """Un PNG real (las subidas se validan con Pillow)."""
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, 'PNG')
    buf.seek(0)
    return buf


def make_user(username, permissions):
    with app.app_context():
        user = AdminUser(username=username, is_active=True, is_admin=False)
        user.set_password(PASSWORD)
        user.set_permissions(permissions)
        db.session.add(user)
        db.session.commit()


class CleanOfferLinkTest(unittest.TestCase):
    def test_acepta_rutas_del_sitio_y_direcciones_web(self):
        self.assertEqual(_clean_offer_link('/productos?cat=pinturas'), '/productos?cat=pinturas')
        self.assertEqual(_clean_offer_link('https://wa.me/51999999999'), 'https://wa.me/51999999999')
        self.assertEqual(_clean_offer_link('http://ejemplo.com/oferta'), 'http://ejemplo.com/oferta')
        self.assertEqual(_clean_offer_link('  /contacto  '), '/contacto')

    def test_sin_esquema_se_asume_https(self):
        self.assertEqual(_clean_offer_link('www.ejemplo.com/oferta'), 'https://www.ejemplo.com/oferta')
        self.assertEqual(_clean_offer_link('wa.me/51999999999'), 'https://wa.me/51999999999')

    def test_vacio_es_sin_enlace(self):
        self.assertEqual(_clean_offer_link(''), '')
        self.assertEqual(_clean_offer_link('   '), '')
        self.assertEqual(_clean_offer_link(None), '')

    def test_rechaza_lo_que_no_es_un_enlace_seguro(self):
        for malo in ('javascript:alert(1)', 'JaVaScRiPt:alert(1)', '//malo.com', 'data:text/html,hola', 'una oferta',
                     'https://a.com/con espacios', 'mailto:alguien@ejemplo.com', 'x' * 301):
            self.assertIsNone(_clean_offer_link(malo), malo)


class OfertasTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            Offer.query.delete()
            SiteConfig.set('disabled_pages', '')     # otras suites comparten esta base
            SiteConfig.set('maintenance_mode', '')
            db.session.commit()
        self.client = app.test_client()
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})
        self.sufijo = uuid.uuid4().hex[:6]

    # ---------- utilidades ----------

    def crear(self, title='', link='', order=0, active=True, image=None, client=None):
        data = {'action': 'create', 'title': title, 'link_url': link, 'order': str(order),
                'image': (image or png(), 'banner.png')}
        if active:
            data['is_active'] = 'on'
        return (client or self.client).post('/admin/ofertas', data=data, content_type='multipart/form-data',
                                            follow_redirects=True).get_data(as_text=True)

    def ofertas(self):
        with app.app_context():
            return [(o.title, o.link_url, o.order, o.is_active) for o in Offer.query.order_by(Offer.order, Offer.id).all()]

    def portada(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def seccion(self, html):
        """HTML de la seccion OFERTAS de la portada ('' si no se muestra)."""
        m = re.search(r'<section class="section offers-section" id="ofertas">.*?</section>', html, re.S)
        return m.group(0) if m else ''

    # ---------- panel: crear, editar, eliminar ----------

    def test_crear_una_oferta_guarda_la_imagen_y_los_datos(self):
        html = self.crear(title='Descuento en pinturas', link='/productos', order=3)
        self.assertIn('Oferta creada', html)
        self.assertEqual(self.ofertas(), [('Descuento en pinturas', '/productos', 3, True)])
        with app.app_context():
            image_url = Offer.query.one().image_url
        self.assertTrue(image_url.startswith('uploads/offers/'))
        self.assertTrue(os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'offers', os.path.basename(image_url))))

    def test_crear_sin_imagen_se_rechaza(self):
        resp = self.client.post('/admin/ofertas', data={'action': 'create', 'title': 'Sin imagen'},
                                content_type='multipart/form-data', follow_redirects=True)
        self.assertIn('Sube la imagen de la oferta', resp.get_data(as_text=True))
        self.assertEqual(self.ofertas(), [])

    def test_un_archivo_que_no_es_imagen_se_rechaza(self):
        falso = io.BytesIO(b'esto no es una imagen')
        html = self.crear(title='Falsa', image=falso)
        self.assertIn('No se pudo usar la imagen', html)
        pdf = self.client.post('/admin/ofertas', data={'action': 'create', 'image': (png(), 'oferta.pdf')},
                               content_type='multipart/form-data', follow_redirects=True).get_data(as_text=True)
        self.assertIn('No se pudo usar la imagen', pdf)
        self.assertEqual(self.ofertas(), [])

    def test_un_enlace_peligroso_se_rechaza_y_no_se_crea_la_oferta(self):
        html = self.crear(title='Mala', link='javascript:alert(1)')
        self.assertIn('El enlace no es válido', html)
        self.assertEqual(self.ofertas(), [])

    def test_el_enlace_sin_esquema_se_guarda_con_https(self):
        self.crear(title='Web', link='www.ejemplo.com/oferta')
        self.assertEqual(self.ofertas(), [('Web', 'https://www.ejemplo.com/oferta', 0, True)])

    def test_el_orden_se_limita_a_un_rango_razonable(self):
        self.crear(title='Enorme', order=10 ** 12)
        self.assertEqual(self.ofertas()[0][2], 9999)

    def test_editar_sin_imagen_nueva_conserva_la_anterior(self):
        self.crear(title='Original', link='/productos')
        with app.app_context():
            oferta = Offer.query.one()
            oid, imagen = oferta.id, oferta.image_url
        resp = self.client.post('/admin/ofertas', data={'action': 'update', 'id': str(oid), 'title': 'Cambiada',
                                                        'link_url': '', 'order': '7'},
                                content_type='multipart/form-data', follow_redirects=True)
        self.assertIn('Oferta actualizada', resp.get_data(as_text=True))
        # sin la casilla marcada la oferta queda inactiva
        self.assertEqual(self.ofertas(), [('Cambiada', '', 7, False)])
        with app.app_context():
            self.assertEqual(Offer.query.one().image_url, imagen)

    def test_editar_con_imagen_nueva_la_reemplaza(self):
        self.crear(title='Original')
        with app.app_context():
            oferta = Offer.query.one()
            oid, imagen = oferta.id, oferta.image_url
        self.client.post('/admin/ofertas', data={'action': 'update', 'id': str(oid), 'title': 'Original', 'is_active': 'on',
                                                 'image': (png('blue'), 'nueva.png')},
                         content_type='multipart/form-data', follow_redirects=True)
        with app.app_context():
            self.assertNotEqual(Offer.query.one().image_url, imagen)
            self.assertTrue(Offer.query.one().image_url.endswith('.png'))

    def test_eliminar_una_oferta(self):
        self.crear(title='Para borrar')
        with app.app_context():
            oid = Offer.query.one().id
        html = self.client.post('/admin/ofertas', data={'action': 'delete', 'id': str(oid)}, follow_redirects=True).get_data(as_text=True)
        self.assertIn('Oferta eliminada', html)
        self.assertEqual(self.ofertas(), [])

    def test_editar_o_eliminar_una_oferta_inexistente_no_falla(self):
        for accion in ('update', 'delete'):
            html = self.client.post('/admin/ofertas', data={'action': accion, 'id': '99999'},
                                    content_type='multipart/form-data', follow_redirects=True).get_data(as_text=True)
            self.assertIn('La oferta no existe', html)

    def test_el_listado_muestra_las_ofertas_en_orden(self):
        self.crear(title='Segunda', order=2)
        self.crear(title='Primera', order=1)
        html = self.client.get('/admin/ofertas').get_data(as_text=True)
        self.assertIn('2 ofertas registradas', html)
        self.assertLess(html.index('Primera'), html.index('Segunda'))

    def test_el_listado_vacio_invita_a_crear_la_primera(self):
        html = self.client.get('/admin/ofertas').get_data(as_text=True)
        self.assertIn('Aún no hay ofertas', html)

    # ---------- panel: permisos ----------

    def test_el_modulo_aparece_en_el_menu_y_en_el_formulario_de_usuarios(self):
        self.assertIn('/admin/ofertas', self.client.get('/admin/').get_data(as_text=True))
        self.assertIn('Ofertas', self.client.get('/admin/usuarios/nuevo').get_data(as_text=True))

    def test_sin_permiso_no_hay_acceso_ni_enlace_en_el_menu(self):
        nombre = f'sin_{self.sufijo}'
        make_user(nombre, {'banners': 'manage'})
        otro = app.test_client()
        otro.post('/admin/login', data={'username': nombre, 'password': PASSWORD})
        self.assertEqual(otro.get('/admin/ofertas').status_code, 403)
        self.assertNotIn('/admin/ofertas', otro.get('/admin/banners').get_data(as_text=True))

    def test_solo_ver_permite_consultar_pero_no_guardar(self):
        nombre = f'lector_{self.sufijo}'
        make_user(nombre, {'ofertas': 'view'})
        otro = app.test_client()
        otro.post('/admin/login', data={'username': nombre, 'password': PASSWORD})
        self.assertEqual(otro.get('/admin/ofertas').status_code, 200)
        resp = otro.post('/admin/ofertas', data={'action': 'create', 'image': (png(), 'x.png')}, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(self.ofertas(), [])

    def test_gestionar_permite_crear(self):
        nombre = f'gestor_{self.sufijo}'
        make_user(nombre, {'ofertas': 'manage'})
        otro = app.test_client()
        otro.post('/admin/login', data={'username': nombre, 'password': PASSWORD})
        self.assertIn('Oferta creada', self.crear(title='Del gestor', client=otro))

    def test_el_panel_exige_iniciar_sesion(self):
        anonimo = app.test_client()
        self.assertEqual(anonimo.get('/admin/ofertas').status_code, 302)
        self.assertEqual(anonimo.post('/admin/ofertas', data={'action': 'delete', 'id': '1'}).status_code, 302)

    # ---------- portada ----------

    def test_sin_ofertas_la_seccion_no_se_muestra(self):
        self.assertEqual(self.seccion(self.portada()), '')

    def test_solo_las_ofertas_activas_se_muestran_en_orden(self):
        self.crear(title='Tercera', order=3)
        self.crear(title='Primera', order=1)
        self.crear(title='Oculta', order=2, active=False)
        seccion = self.seccion(self.portada())
        self.assertNotEqual(seccion, '')
        self.assertNotIn('Oculta', seccion)
        self.assertLess(seccion.index('Primera'), seccion.index('Tercera'))
        self.assertEqual(seccion.count('class="offer-banner"'), 2)

    def test_si_todas_estan_inactivas_la_seccion_se_oculta(self):
        self.crear(title='Una', active=False)
        self.assertEqual(self.seccion(self.portada()), '')

    def test_la_seccion_va_debajo_de_marcas_y_antes_de_ventajas(self):
        with app.app_context():
            db.session.add(Brand(name=f'Marca {self.sufijo}', slug=f'marca-{self.sufijo}'))
            db.session.commit()
        self.crear(title='Oferta de prueba')
        html = self.portada()
        self.assertLess(html.index('brands-section'), html.index('id="ofertas"'))
        self.assertLess(html.index('id="ofertas"'), html.index('id="por-que"'))

    def test_el_titulo_de_la_seccion_es_ofertas(self):
        self.crear(title='Una')
        self.assertIn('<span class="gradient-text">Ofertas</span>', self.seccion(self.portada()))

    def test_las_ofertas_van_sueltas_una_debajo_de_otra_sin_carrusel(self):
        for n in range(3):
            self.crear(title=f'Oferta {n}', order=n)
        seccion = self.seccion(self.portada())
        self.assertIn('class="offers-list"', seccion)
        self.assertEqual(seccion.count('class="offer-banner"'), 3)
        for carrusel in ('offers-carousel', 'offers-track', 'offers-nav', 'offers-dot', 'aria-roledescription'):
            self.assertNotIn(carrusel, seccion)

    def test_solo_la_primera_oferta_se_carga_de_inmediato(self):
        for n in range(3):
            self.crear(title=f'Oferta {n}', order=n)
        imagenes = re.findall(r'<img [^>]*>', self.seccion(self.portada()))
        self.assertEqual(len(imagenes), 3)
        self.assertNotIn('loading="lazy"', imagenes[0])
        self.assertTrue(all('loading="lazy"' in img for img in imagenes[1:]))

    def test_el_titulo_es_el_texto_alternativo_y_sin_titulo_se_numera(self):
        self.crear(title='Descuento en pinturas', order=1)
        self.crear(title='', order=2)
        seccion = self.seccion(self.portada())
        self.assertIn('alt="Descuento en pinturas"', seccion)
        self.assertIn('alt="Oferta 2"', seccion)

    def test_los_enlaces_internos_y_externos(self):
        self.crear(title='Interna', link='/productos', order=1)
        self.crear(title='Externa', link='https://wa.me/51999999999', order=2)
        self.crear(title='Sin enlace', order=3)
        seccion = self.seccion(self.portada())
        self.assertIn('<a href="/productos">', seccion)
        self.assertIn('<a href="https://wa.me/51999999999" target="_blank" rel="noopener">', seccion)
        self.assertEqual(seccion.count('<a href='), 2, 'la oferta sin enlace no es un enlace')

    def test_la_imagen_se_sirve_desde_la_carpeta_de_ofertas(self):
        self.crear(title='Con imagen')
        self.assertRegex(self.seccion(self.portada()), r'src="/static/uploads/offers/banner_\d+\.png"')


if __name__ == '__main__':
    unittest.main()
