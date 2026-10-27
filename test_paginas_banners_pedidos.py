"""Pruebas de: paginas habilitables, banners por pagina, formulario de pedidos (DNI/RUC) e iconos sociales.

Se ejecutan contra una base SQLite temporal y una carpeta de subidas temporal, nunca contra las reales:

    python -m unittest test_paginas_banners_pedidos -v
"""
import io
import os
import tempfile
import unittest
from unittest import mock

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test_paginas.db').replace(os.sep, '/')

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import AdminUser, PageBanner, Product, QuoteRequest, SiteConfig  # noqa: E402

app.config['TESTING'] = True
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='dewill_uploads_')

PASSWORD = 'Clave-segura-1'
PAGES_PUBLICAS = {'nosotros': '/nosotros', 'productos': '/productos', 'galeria': '/galeria',
                  'ambientes': '/galeria/ambientes', 'blog': '/blog', 'contacto': '/contacto'}


def make_user(username, **fields):
    permissions = fields.pop('permissions', {})
    with app.app_context():
        user = AdminUser(username=username, is_active=True, is_admin=fields.pop('is_admin', False), **fields)
        user.set_password(PASSWORD)
        user.set_permissions(permissions)
        db.session.add(user)
        db.session.commit()


def png_bytes(color='red', size=(40, 20)):
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', size, color).save(buf, 'PNG')
    buf.seek(0)
    return buf


class BaseTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            AdminUser.query.filter(AdminUser.username != 'admin').delete()
            PageBanner.query.delete()
            QuoteRequest.query.delete()
            SiteConfig.query.filter(SiteConfig.key.in_(['disabled_pages', 'notify_email', 'facebook', 'youtube'])).delete(
                synchronize_session=False)
            db.session.commit()
        self.visitor = app.test_client()
        self.admin = app.test_client()
        self.admin.post('/admin/login', data={'username': 'admin', 'password': 'admin123'})

    def save_settings(self, enabled, client=None, **extra):
        """Envia el formulario de Configuracion con solo estas paginas habilitadas."""
        data = {'pages_form': '1', 'pages_enabled': list(enabled), **extra}
        return (client or self.admin).post('/admin/configuracion', data=data)

    def html(self, url, client=None):
        resp = (client or self.visitor).get(url)
        return resp.status_code, resp.get_data(as_text=True)


class PaginasHabilitablesTest(BaseTest):
    def test_por_defecto_todas_las_paginas_estan_disponibles(self):
        for url in PAGES_PUBLICAS.values():
            self.assertEqual(self.html(url)[0], 200, url)
        _, home = self.html('/')
        for url in ('/nosotros', '/productos', '/galeria', '/galeria/ambientes', '/blog', '/contacto'):
            self.assertIn(f'href="{url}"', home, url)

    def test_deshabilitar_blog_lo_oculta_a_los_visitantes(self):
        self.save_settings(set(PAGES_PUBLICAS) - {'blog'})
        status, body = self.html('/blog')
        self.assertEqual(status, 404)
        self.assertIn('no está disponible por el momento', body)
        self.assertEqual(self.html('/blog/un-articulo')[0], 404)
        # Sale del menu principal y del pie de pagina
        _, home = self.html('/')
        self.assertNotIn('href="/blog"', home)
        # El resto del sitio no se afecta
        for key, url in PAGES_PUBLICAS.items():
            if key != 'blog':
                self.assertEqual(self.html(url)[0], 200, url)

    def test_el_administrador_con_sesion_sigue_viendo_la_pagina_con_un_aviso(self):
        self.save_settings(set(PAGES_PUBLICAS) - {'blog'})
        status, body = self.html('/blog', client=self.admin)
        self.assertEqual(status, 200)
        self.assertIn('está deshabilitada', body)
        # Una pagina habilitada no muestra el aviso
        self.assertNotIn('está deshabilitada', self.html('/nosotros', client=self.admin)[1])

    def test_volver_a_habilitar_restaura_la_pagina(self):
        self.save_settings(set(PAGES_PUBLICAS) - {'blog'})
        self.assertEqual(self.html('/blog')[0], 404)
        self.save_settings(set(PAGES_PUBLICAS))
        self.assertEqual(self.html('/blog')[0], 200)
        self.assertIn('href="/blog"', self.html('/')[1])

    def test_un_formulario_sin_el_bloque_de_paginas_no_las_modifica(self):
        self.save_settings(set(PAGES_PUBLICAS) - {'blog'})
        self.admin.post('/admin/configuracion', data={'phone': '123'})   # formulario desactualizado, sin 'pages_form'
        self.assertEqual(self.html('/blog')[0], 404)

    def test_las_claves_desconocidas_se_ignoran_e_inicio_nunca_se_deshabilita(self):
        self.save_settings({'nosotros'})
        with app.app_context():
            stored = SiteConfig.get('disabled_pages')
        self.assertEqual(set(stored.split(',')), {'productos', 'galeria', 'ambientes', 'blog', 'contacto'})
        self.assertEqual(self.html('/')[0], 200)
        with app.app_context():
            SiteConfig.set('disabled_pages', 'inicio,blog,no-existe')
        self.assertEqual(self.html('/')[0], 200)
        self.assertEqual(self.html('/blog')[0], 404)

    def test_deshabilitar_productos_oculta_el_catalogo_y_la_cotizacion(self):
        self.save_settings(set(PAGES_PUBLICAS) - {'productos'})
        self.assertEqual(self.html('/productos')[0], 404)
        self.assertEqual(self.html('/producto/1')[0], 404)
        for url in ('/api/productos/search?q=pintura', '/api/producto/1/colores'):
            resp = self.visitor.get(url)
            self.assertEqual(resp.status_code, 404, url)
            self.assertFalse(resp.get_json()['success'])
        resp = self.visitor.post('/api/cotizacion', json={'items': [{'product_id': 1}], 'name': 'Ana'})
        self.assertEqual(resp.status_code, 404)
        _, home = self.html('/')
        self.assertIn('class="no-catalog"', home)
        self.assertNotIn('href="/productos', home)
        self.assertNotIn('Líneas de', home)   # seccion de categorias del Inicio

    def test_solo_quien_gestiona_la_configuracion_puede_cambiar_las_paginas(self):
        make_user('editor', permissions={'banners': 'manage'})
        editor = app.test_client()
        editor.post('/admin/login', data={'username': 'editor', 'password': PASSWORD})
        resp = self.save_settings(set(), client=editor)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(self.html('/blog')[0], 200)


class BannersPorPaginaTest(BaseTest):
    def post_banner(self, page, image=None, **fields):
        data = {'action': 'save_page', 'page': page, **fields}
        if image is not None:
            data['image'] = (image, 'banner.png')
        return self.admin.post('/admin/banners', data=data, content_type='multipart/form-data', follow_redirects=True)

    def banner_row(self, page):
        with app.app_context():
            row = PageBanner.query.filter_by(page=page).first()
            return None if row is None else {c: getattr(row, c) for c in
                                             ('image_url', 'image2_url', 'badge', 'title', 'subtitle', 'description', 'is_active')}

    def test_sin_personalizar_cada_pagina_muestra_su_banner_original(self):
        _, productos = self.html('/productos')
        self.assertIn('assets/banner_productos_new.png', productos)
        self.assertIn('Nuestros <span class="hl-primary">Productos</span>', productos)
        self.assertIn('assets/banner_comunidad.png', self.html('/galeria')[1])
        self.assertIn('assets/banner_contacto.png', self.html('/contacto')[1])
        self.assertIn('assets/blog_bg.png', self.html('/blog')[1])
        _, ambientes = self.html('/galeria/ambientes')
        self.assertIn('assets/ambiente_sala.png', ambientes)
        self.assertIn('assets/ambiente_dormitorio.png', ambientes)
        self.assertIn('Galería de<br><span class="text-red">Ambientes</span>', ambientes)
        _, nosotros = self.html('/nosotros')
        self.assertIn('assets/local_foto.jpeg', nosotros)
        self.assertIn('Sobre<br><span class="text-red">Nosotros</span>', nosotros)

    def test_guardar_imagen_y_textos_nuevos(self):
        resp = self.post_banner('productos', image=png_bytes(), title='Todo en *pinturas*\nal mejor precio', subtitle='Ofertas <b>de temporada</b>',
                                is_active='on')
        self.assertIn('Banner de Productos guardado', resp.get_data(as_text=True))
        row = self.banner_row('productos')
        self.assertTrue(row['image_url'].startswith('uploads/banners/'))
        self.assertTrue(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], row['image_url'][len('uploads/'):])))
        _, body = self.html('/productos')
        self.assertIn(row['image_url'], body)
        self.assertNotIn('assets/banner_productos_new.png', body)
        self.assertIn('Todo en <span class="hl-primary">pinturas</span><br>al mejor precio', body)
        # El HTML escrito por el administrador se muestra como texto, no se ejecuta
        self.assertIn('Ofertas &lt;b&gt;de temporada&lt;/b&gt;', body)
        self.assertNotIn('<b>de temporada</b>', body)

    def test_guardar_sin_cambios_no_crea_una_personalizacion(self):
        # El formulario llega con los valores de fabrica: no hay nada que guardar
        self.post_banner('productos', title='Nuestros *Productos*', subtitle='Pinturas de alta calidad para cada necesidad.', is_active='on')
        self.assertIsNone(self.banner_row('productos'))

    def test_un_archivo_que_no_es_imagen_se_rechaza_y_no_cambia_el_banner(self):
        self.post_banner('productos', image=png_bytes(), is_active='on')
        guardada = self.banner_row('productos')['image_url']
        self.assertIsNotNone(guardada)
        for contenido, nombre in ((b'esto no es una imagen', 'falso.png'), (b'%PDF-1.4', 'doc.pdf'), (b'MZ\x90\x00', 'programa.exe')):
            resp = self.admin.post('/admin/banners', data={'action': 'save_page', 'page': 'productos', 'is_active': 'on',
                                                           'image': (io.BytesIO(contenido), nombre)},
                                   content_type='multipart/form-data', follow_redirects=True)
            self.assertIn('No se pudo usar la imagen', resp.get_data(as_text=True), nombre)
            self.assertEqual(self.banner_row('productos')['image_url'], guardada, nombre)
        self.assertIn(guardada, self.html('/productos')[1])

    def test_volver_a_la_imagen_original_y_restaurar_todo(self):
        self.post_banner('blog', image=png_bytes(), title='Mi *blog*', is_active='on')
        self.assertIsNotNone(self.banner_row('blog')['image_url'])
        self.post_banner('blog', title='Mi *blog*', is_active='on', image_reset='1')
        row = self.banner_row('blog')
        self.assertIsNone(row['image_url'])
        self.assertEqual(row['title'], 'Mi *blog*')
        self.assertIn('assets/blog_bg.png', self.html('/blog')[1])
        self.admin.post('/admin/banners', data={'action': 'reset_page', 'page': 'blog'})
        self.assertIsNone(self.banner_row('blog'))
        self.assertIn('Consejos, ideas y <span class="gradient-text">soluciones</span>', self.html('/blog')[1])

    def test_ocultar_el_banner_de_una_pagina(self):
        self.post_banner('contacto')   # sin 'is_active': se oculta
        self.assertFalse(self.banner_row('contacto')['is_active'])
        self.assertNotIn('contact-hero-static', self.html('/contacto')[1])
        self.post_banner('contacto', is_active='on')
        self.assertIn('contact-hero-static', self.html('/contacto')[1])

    def test_la_cabecera_de_nosotros_no_se_puede_ocultar(self):
        self.post_banner('nosotros', title='Quiénes *somos*', subtitle='', description='')
        _, body = self.html('/nosotros')
        self.assertIn('about-hero-model', body)
        self.assertIn('Quiénes <span class="text-red">somos</span>', body)
        self.assertNotIn('about-hero-subtitle', body)   # un texto vacio no se muestra
        self.assertTrue(self.banner_row('nosotros')['is_active'])

    def test_ambientes_admite_dos_imagenes(self):
        self.admin.post('/admin/banners', data={'action': 'save_page', 'page': 'ambientes', 'is_active': 'on',
                                                'image': (png_bytes('blue'), 'izq.png'), 'image2': (png_bytes('green'), 'der.png')},
                        content_type='multipart/form-data')
        row = self.banner_row('ambientes')
        self.assertIn('izq', row['image_url'])
        self.assertIn('der', row['image2_url'])
        _, body = self.html('/galeria/ambientes')
        self.assertIn(row['image_url'], body)
        self.assertIn(row['image2_url'], body)

    def test_la_pagina_del_panel_lista_todas_las_pestanas(self):
        status, body = self.html('/admin/banners', client=self.admin)
        self.assertEqual(status, 200)
        for label in ('Inicio', 'Nosotros', 'Productos', 'Galería', 'Ambientes', 'Blog', 'Contacto'):
            self.assertIn(label, body)
        for key in PAGES_PUBLICAS:
            self.assertEqual(self.html(f'/admin/banners?pagina={key}', client=self.admin)[0], 200, key)
        self.assertEqual(self.html('/admin/banners?pagina=inventada', client=self.admin)[0], 200)

    def test_una_pagina_inexistente_se_rechaza(self):
        resp = self.admin.post('/admin/banners', data={'action': 'save_page', 'page': 'inventada'}, follow_redirects=True)
        self.assertIn('La página elegida no existe', resp.get_data(as_text=True))
        with app.app_context():
            self.assertEqual(PageBanner.query.count(), 0)

    def test_permisos_del_modulo_banners(self):
        make_user('lector', permissions={'banners': 'view'})
        make_user('sin_acceso', permissions={'blog': 'manage'})
        lector, sin_acceso = app.test_client(), app.test_client()
        lector.post('/admin/login', data={'username': 'lector', 'password': PASSWORD})
        sin_acceso.post('/admin/login', data={'username': 'sin_acceso', 'password': PASSWORD})
        self.assertEqual(lector.get('/admin/banners?pagina=blog').status_code, 200)
        self.assertEqual(lector.post('/admin/banners', data={'action': 'save_page', 'page': 'blog', 'title': 'x'}).status_code, 403)
        self.assertEqual(sin_acceso.get('/admin/banners').status_code, 403)
        self.assertIsNone(self.banner_row('blog'))

    def test_filtro_banner_text(self):
        render = app.jinja_env.from_string("{{ t|banner_text('x') }}")
        self.assertEqual(render.render(t='Hola *mundo*\nfin'), 'Hola <span class="x">mundo</span><br>fin')
        self.assertEqual(render.render(t='<script>alert(1)</script> *a*'), '&lt;script&gt;alert(1)&lt;/script&gt; <span class="x">a</span>')
        self.assertEqual(render.render(t='5 * 3 y 2 * 4'), '5 <span class="x"> 3 y 2 </span> 4')   # los asteriscos sueltos en pares resaltan
        self.assertEqual(render.render(t='un * solo'), 'un * solo')
        self.assertEqual(render.render(t=None), '')


class FormularioDePedidosTest(BaseTest):
    def setUp(self):
        super().setUp()
        # Sin usuario de correo configurado la app no intenta enviar avisos (nunca se manda correo real desde las pruebas)
        patcher = mock.patch.dict(app.config, {'MAIL_USERNAME': ''})
        patcher.start()
        self.addCleanup(patcher.stop)
        with app.app_context():
            product = Product.query.filter_by(sku='T-001').first()
            if product is None:
                product = Product(name='Pintura de prueba', sku='T-001', is_active=True)
                db.session.add(product)
                db.session.commit()
            self.product_id = product.id

    def payload(self, **overrides):
        data = {'name': 'Juan Pérez', 'document': '12345678', 'phone': '987654321', 'email': '', 'company': '', 'message': '',
                'items': [{'product_id': self.product_id, 'quantity': 2}]}
        data.update(overrides)
        return data

    def send(self, **overrides):
        return self.visitor.post('/api/cotizacion', json=self.payload(**overrides))

    def quotes(self):
        with app.app_context():
            return [{'name': q.client_name, 'document': q.client_document, 'phone': q.client_phone, 'email': q.client_email,
                     'company': q.client_company, 'message': q.message} for q in QuoteRequest.query.order_by(QuoteRequest.id)]

    def test_pedido_con_dni_y_celular_sin_email_ni_mensaje(self):
        resp = self.send()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])
        self.assertEqual(self.quotes(), [{'name': 'Juan Pérez', 'document': '12345678', 'phone': '987654321', 'email': '',
                                          'company': '', 'message': ''}])

    def test_pedido_con_ruc_email_y_mensaje(self):
        resp = self.send(document='20123456789', phone='+51 912-345-678', email='ventas@empresa.pe', company='Empresa SAC',
                         message='Cotizar por mayor')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.quotes()[0], {'name': 'Juan Pérez', 'document': '20123456789', 'phone': '912345678',
                                            'email': 'ventas@empresa.pe', 'company': 'Empresa SAC', 'message': 'Cotizar por mayor'})

    def test_dni_o_ruc_es_obligatorio_y_debe_tener_8_u_11_digitos(self):
        for document in ('', '1234567', '123456789', '123456789012', 'abcdefgh'):
            resp = self.send(document=document)
            self.assertEqual(resp.status_code, 400, document)
            self.assertIn('DNI', resp.get_json()['error'])
        self.assertEqual(self.send(document='1234-5678').status_code, 200)   # separadores se ignoran
        self.assertEqual(len(self.quotes()), 1)

    def test_el_celular_es_obligatorio_y_debe_ser_peruano(self):
        for phone in ('', '12345', '887654321', '98765432', '9876543210'):
            resp = self.send(phone=phone)
            self.assertEqual(resp.status_code, 400, phone)
            self.assertIn('celular', resp.get_json()['error'])
        self.assertEqual(self.quotes(), [])

    def test_el_email_es_opcional_pero_si_se_escribe_debe_ser_valido(self):
        self.assertEqual(self.send(email='').status_code, 200)
        self.assertEqual(self.send(email='ana@correo.com').status_code, 200)
        resp = self.send(email='ana@')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('correo', resp.get_json()['error'])
        self.assertEqual(len(self.quotes()), 2)

    def test_el_nombre_y_los_productos_siguen_siendo_obligatorios(self):
        self.assertEqual(self.send(name='  ').status_code, 400)
        resp = self.send(items=[])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_json()['error'], 'No hay productos')
        self.assertEqual(self.visitor.post('/api/cotizacion', data='{no es json', content_type='application/json').status_code, 400)
        self.assertEqual(self.quotes(), [])

    def test_el_correo_de_aviso_incluye_el_dni_o_ruc_y_el_celular(self):
        with app.app_context():
            SiteConfig.set('notify_email', 'ventas@example.com')
        # El hilo que enviaria el correo se sustituye por un doble: solo se inspecciona el cuerpo del mensaje
        with mock.patch.dict(app.config, {'MAIL_USERNAME': 'aviso@example.com'}), mock.patch('app.threading.Thread') as thread:
            self.send(document='20123456789', phone='912345678')
            self.send()
        bodies = [call.kwargs['args'][1]['body'] for call in thread.call_args_list]
        self.assertIn('RUC: 20123456789', bodies[0])
        self.assertIn('Celular: 912345678', bodies[0])
        self.assertIn('Email: No especificado', bodies[0])
        self.assertIn('DNI: 12345678', bodies[1])
        self.assertIn('Pintura de prueba', bodies[1])

    def test_el_panel_muestra_dni_ruc_y_celular(self):
        self.send(document='20123456789', phone='912345678', email='ventas@empresa.pe')
        self.send()
        with app.app_context():
            ids = [q.id for q in QuoteRequest.query.order_by(QuoteRequest.id)]
        _, detail = self.html(f'/admin/solicitudes/{ids[0]}', client=self.admin)
        self.assertIn('RUC:', detail)
        self.assertIn('20123456789', detail)
        self.assertIn('https://wa.me/51912345678', detail)   # el celular de 9 digitos se enlaza con el prefijo de Peru
        _, detail = self.html(f'/admin/solicitudes/{ids[1]}', client=self.admin)
        self.assertIn('DNI:', detail)
        self.assertIn('No especificado', detail)   # email vacio
        self.assertEqual(self.html('/admin/solicitudes', client=self.admin)[0], 200)
        self.assertEqual(self.html('/admin/', client=self.admin)[0], 200)

    def test_las_solicitudes_anteriores_sin_dni_siguen_abriendo(self):
        with app.app_context():
            quote = QuoteRequest(client_name='Antiguo', client_phone='+51 977 585 654', client_email='a@b.com')
            db.session.add(quote)
            db.session.commit()
            qid = quote.id
        status, detail = self.html(f'/admin/solicitudes/{qid}', client=self.admin)
        self.assertEqual(status, 200)
        self.assertIn('DNI / RUC:', detail)
        self.assertIn('https://wa.me/51977585654', detail)

    def test_el_formulario_publico_tiene_los_campos_nuevos(self):
        _, home = self.html('/')
        for field_id in ('clientName', 'clientDocument', 'clientPhone', 'clientEmail', 'clientMessage'):
            self.assertIn(f'id="{field_id}"', home)
        self.assertIn('placeholder="DNI / RUC *"', home)
        self.assertIn('placeholder="Celular *"', home)
        self.assertIn('placeholder="Email (opcional)"', home)
        self.assertIn('placeholder="Mensaje (opcional)"', home)


class IconosSocialesTest(BaseTest):
    def test_los_iconos_se_muestran_con_la_clase_de_su_marca(self):
        _, home = self.html('/')
        for network in ('facebook', 'instagram', 'youtube', 'linkedin'):
            self.assertIn(f'social-icon--{network}', home)
        _, contacto = self.html('/contacto')
        self.assertIn('social-icon--tiktok', contacto)

    def test_sin_url_el_icono_se_ve_igual_y_con_url_enlaza_al_perfil(self):
        self.assertIn('<a href="#" class="social-icon social-icon--facebook"', self.html('/')[1])
        self.admin.post('/admin/configuracion', data={'facebook': 'https://facebook.com/dewill', 'youtube': 'javascript:alert(1)'})
        _, home = self.html('/')
        self.assertIn('<a href="https://facebook.com/dewill" class="social-icon social-icon--facebook"', home)
        self.assertIn('target="_blank" rel="noopener noreferrer"', home)
        # Una URL que no sea http(s) nunca llega al enlace
        self.assertNotIn('javascript:alert', home)
        self.assertIn('<a href="#" class="social-icon social-icon--youtube"', home)

    def test_la_configuracion_guarda_youtube_y_linkedin(self):
        self.admin.post('/admin/configuracion', data={'youtube': 'https://youtube.com/@dewill', 'linkedin': 'https://linkedin.com/company/dewill'})
        _, home = self.html('/')
        self.assertIn('href="https://youtube.com/@dewill"', home)
        self.assertIn('href="https://linkedin.com/company/dewill"', home)


if __name__ == '__main__':
    unittest.main()
