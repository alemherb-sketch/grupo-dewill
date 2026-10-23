"""Pruebas del modulo de usuarios y permisos del panel.

Se ejecutan contra una base SQLite temporal, nunca contra la base real:

    python -m unittest test_usuarios -v
"""
import os
import tempfile
import unittest

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import AdminUser  # noqa: E402

app.config['TESTING'] = True

PASSWORD = 'Clave-segura-1'


# Importante: no mantener un contexto de aplicacion abierto durante las peticiones del cliente de pruebas.
# Flask-Login guarda el usuario en `g`, y un contexto compartido filtraria la sesion de un cliente a otro.

def make_user(username, password=PASSWORD, **fields):
    """Crea un usuario y devuelve su id."""
    permissions = fields.pop('permissions', {})
    with app.app_context():
        user = AdminUser(username=username, is_active=fields.pop('is_active', True),
                         is_admin=fields.pop('is_admin', False), **fields)
        user.set_password(password)
        user.set_permissions(permissions)
        db.session.add(user)
        db.session.commit()
        return user.id


def state(username):
    """Foto del usuario guardado en la base (None si no existe)."""
    with app.app_context():
        user = AdminUser.query.filter_by(username=username).first()
        if user is None:
            return None
        return {'id': user.id, 'full_name': user.full_name, 'is_admin': user.is_admin, 'is_active': user.is_active,
                'permissions': user.get_permissions(), 'password_ok': user.check_password,
                'level': user.level, 'can': user.can}


def update_user(username, **fields):
    with app.app_context():
        user = AdminUser.query.filter_by(username=username).one()
        for key, value in fields.items():
            setattr(user, key, value)
        db.session.commit()


class UsuariosPermisosTest(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            AdminUser.query.filter(AdminUser.username != 'admin').delete()
            db.session.commit()
        self.client = app.test_client()

    def login(self, username, password=PASSWORD, client=None):
        return (client or self.client).post('/admin/login', data={'username': username, 'password': password})

    def login_admin(self):
        return self.login('admin', 'admin123')

    # ---------- arranque ----------

    def test_admin_inicial_es_administrador(self):
        admin = state('admin')
        self.assertTrue(admin['is_admin'] and admin['is_active'])
        resp = self.login_admin()
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/admin/'))

    # ---------- control de acceso por modulo ----------

    def test_solo_ver_permite_leer_pero_no_guardar(self):
        make_user('lector', permissions={'productos': 'view'})
        self.login('lector')
        self.assertEqual(self.client.get('/admin/productos').status_code, 200)
        resp = self.client.post('/admin/productos/1/eliminar')
        self.assertEqual(resp.status_code, 403)
        self.assertIn('solo puede consultar', resp.get_data(as_text=True))

    def test_gestionar_permite_escribir(self):
        make_user('gestor', permissions={'marcas': 'manage'})
        self.login('gestor')
        self.assertEqual(self.client.get('/admin/marcas').status_code, 200)
        self.assertNotEqual(self.client.post('/admin/marcas', data={'action': 'ninguna'}).status_code, 403)

    def test_modulo_sin_permiso_devuelve_403_y_no_aparece_en_el_menu(self):
        make_user('ventas', permissions={'productos': 'view'})
        self.login('ventas')
        self.assertEqual(self.client.get('/admin/solicitudes').status_code, 403)
        html = self.client.get('/admin/productos').get_data(as_text=True)
        self.assertIn('Productos', html)
        self.assertNotIn('/admin/solicitudes', html)
        self.assertNotIn('/admin/usuarios', html)

    def test_cada_sesion_ve_solo_sus_permisos(self):
        """Dos clientes con permisos distintos no se contaminan entre si."""
        make_user('uno', permissions={'productos': 'view'})
        make_user('dos', permissions={'banners': 'view'})
        otro = app.test_client()
        self.login('uno')
        self.login('dos', client=otro)
        self.assertEqual(self.client.get('/admin/productos').status_code, 200)
        self.assertEqual(self.client.get('/admin/banners').status_code, 403)
        self.assertEqual(otro.get('/admin/banners').status_code, 200)
        self.assertEqual(otro.get('/admin/productos').status_code, 403)

    def test_aviso_de_solo_lectura(self):
        make_user('lector', permissions={'productos': 'view', 'marcas': 'manage'})
        self.login('lector')
        self.assertIn('readonly-notice', self.client.get('/admin/productos').get_data(as_text=True))
        self.assertNotIn('readonly-notice', self.client.get('/admin/marcas').get_data(as_text=True))

    def test_dashboard_oculta_datos_de_clientes_sin_permiso_de_solicitudes(self):
        make_user('panel', permissions={'dashboard': 'view'})
        self.login('panel')
        html = self.client.get('/admin/').get_data(as_text=True)
        self.assertNotIn('Últimas Solicitudes', html)
        self.assertNotIn('Nuevo Producto', html)

    def test_rutas_de_admin_sin_sesion_redirigen_al_login(self):
        for path in ('/admin/', '/admin/productos', '/admin/usuarios', '/admin/cuenta'):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 302, path)
            self.assertIn('/admin/login', resp.headers['Location'])

    def test_usuario_sin_permisos_aterriza_en_mi_cuenta(self):
        make_user('vacio')
        resp = self.login('vacio')
        self.assertTrue(resp.headers['Location'].endswith('/admin/cuenta'))
        self.assertEqual(self.client.get('/admin/cuenta').status_code, 200)
        self.assertEqual(self.client.get('/admin/').status_code, 403)

    def test_login_redirige_al_primer_modulo_permitido(self):
        make_user('contenido', permissions={'blog': 'manage'})
        resp = self.login('contenido')
        self.assertTrue(resp.headers['Location'].endswith('/admin/blog'))

    def test_herramientas_de_mantenimiento_solo_administradores(self):
        make_user('gestor', permissions={'configuracion': 'manage'})
        self.login('gestor')
        self.assertEqual(self.client.post('/admin/seed-db').status_code, 403)

    def test_toda_ruta_del_panel_exige_sesion(self):
        """Ninguna ruta /admin (salvo login) puede quedar abierta a un visitante."""
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith('/admin') or rule.rule == '/admin/login':
                continue
            path = rule.rule
            for arg in rule.arguments:
                path = path.replace(f'<int:{arg}>', '1')
            for method in sorted(rule.methods & {'GET', 'POST'}):
                resp = self.client.open(path, method=method)
                self.assertEqual(resp.status_code, 302, f'{method} {path}')
                self.assertIn('/admin/login', resp.headers['Location'], f'{method} {path}')

    # ---------- cuentas inactivas ----------

    def test_cuenta_inactiva_no_puede_entrar(self):
        make_user('baja', is_active=False, permissions={'productos': 'view'})
        resp = self.login('baja')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('desactivada', resp.get_data(as_text=True))
        self.assertEqual(self.client.get('/admin/productos').status_code, 302)

    def test_desactivar_cierra_la_sesion_abierta(self):
        make_user('activo', permissions={'productos': 'view'})
        self.login('activo')
        self.assertEqual(self.client.get('/admin/productos').status_code, 200)
        update_user('activo', is_active=False)
        resp = self.client.get('/admin/productos')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/login', resp.headers['Location'])

    def test_contrasena_incorrecta(self):
        make_user('x_user')
        resp = self.login('x_user', 'otra-clave')
        self.assertIn('Credenciales', resp.get_data(as_text=True))

    # ---------- gestion de usuarios ----------

    def test_no_administrador_no_gestiona_usuarios(self):
        make_user('gestor', permissions={'configuracion': 'manage'})
        self.login('gestor')
        self.assertEqual(self.client.get('/admin/usuarios').status_code, 403)
        resp = self.client.post('/admin/usuarios/nuevo', data={
            'username': 'intruso', 'password': PASSWORD, 'password_confirm': PASSWORD, 'is_admin': '1'})
        self.assertEqual(resp.status_code, 403)
        self.assertIsNone(state('intruso'))

    def test_crear_usuario_con_permisos(self):
        self.login_admin()
        resp = self.client.post('/admin/usuarios/nuevo', data={
            'full_name': 'Ana Ruiz', 'username': 'ana', 'email': 'ana@example.com',
            'password': PASSWORD, 'password_confirm': PASSWORD, 'is_active': '1',
            'perm_productos': 'manage', 'perm_solicitudes': 'view', 'perm_dashboard': 'manage',
            'perm_blog': '', 'perm_inexistente': 'manage'})
        self.assertEqual(resp.status_code, 302)
        ana = state('ana')
        self.assertFalse(ana['is_admin'])
        self.assertEqual(ana['permissions'], {'productos': 'manage', 'solicitudes': 'view', 'dashboard': 'view'})
        self.assertTrue(ana['password_ok'](PASSWORD))
        # puede iniciar sesion y solo ve lo suyo
        other = app.test_client()
        self.assertEqual(self.login('ana', client=other).status_code, 302)
        self.assertEqual(other.get('/admin/solicitudes').status_code, 200)
        self.assertEqual(other.get('/admin/banners').status_code, 403)

    def test_validaciones_al_crear(self):
        make_user('Existente')
        self.login_admin()
        base = {'username': 'nuevo', 'password': PASSWORD, 'password_confirm': PASSWORD, 'is_active': '1'}
        cases = {
            'clave corta': {**base, 'password': 'corta', 'password_confirm': 'corta'},
            'claves distintas': {**base, 'password_confirm': 'Distinta-123'},
            'usuario invalido': {**base, 'username': 'a b'},
            'duplicado sin importar mayusculas': {**base, 'username': 'existente'},
            'correo invalido': {**base, 'email': 'no-es-correo'},
        }
        for name, data in cases.items():
            resp = self.client.post('/admin/usuarios/nuevo', data=data)
            self.assertEqual(resp.status_code, 200, name)
        for username in ('nuevo', 'a b', 'existente'):
            self.assertIsNone(state(username), username)

    def test_formulario_conserva_lo_escrito_cuando_hay_error(self):
        self.login_admin()
        resp = self.client.post('/admin/usuarios/nuevo', data={
            'full_name': 'Nombre Largo', 'username': 'ok_user', 'password': 'corta', 'password_confirm': 'corta',
            'perm_blog': 'manage'})
        html = resp.get_data(as_text=True)
        self.assertIn('value="Nombre Largo"', html)
        self.assertIn('value="ok_user"', html)
        self.assertRegex(html, r'name="perm_blog" value="manage" checked')

    def test_editar_conserva_o_cambia_la_clave(self):
        user_id = make_user('editable', permissions={'productos': 'view'})
        self.login_admin()
        data = {'username': 'editable', 'full_name': 'Nombre', 'is_active': '1', 'perm_marcas': 'manage'}
        self.assertEqual(self.client.post(f'/admin/usuarios/{user_id}/editar', data=data).status_code, 302)
        editable = state('editable')
        self.assertTrue(editable['password_ok'](PASSWORD))
        self.assertEqual(editable['permissions'], {'marcas': 'manage'})
        data.update(password='Nueva-clave-9', password_confirm='Nueva-clave-9')
        self.client.post(f'/admin/usuarios/{user_id}/editar', data=data)
        self.assertTrue(state('editable')['password_ok']('Nueva-clave-9'))

    def test_hacer_administrador_limpia_permisos(self):
        user_id = make_user('subir', permissions={'productos': 'view'})
        self.login_admin()
        self.client.post(f'/admin/usuarios/{user_id}/editar', data={
            'username': 'subir', 'is_active': '1', 'is_admin': '1', 'perm_productos': 'view'})
        subir = state('subir')
        self.assertTrue(subir['is_admin'])
        self.assertEqual(subir['permissions'], {})
        self.assertEqual(subir['level']('blog'), 'manage')
        self.assertEqual(subir['level']('dashboard'), 'view')
        self.assertFalse(subir['can']('modulo_inexistente'))

    def test_un_administrador_no_puede_quitarse_el_rol_ni_desactivarse_ni_borrarse(self):
        self.login_admin()
        admin_id = state('admin')['id']
        self.client.post(f'/admin/usuarios/{admin_id}/editar', data={'username': 'admin', 'perm_blog': 'view'})
        self.client.post(f'/admin/usuarios/{admin_id}/estado')
        self.client.post(f'/admin/usuarios/{admin_id}/eliminar')
        admin = state('admin')
        self.assertIsNotNone(admin)
        self.assertTrue(admin['is_admin'] and admin['is_active'])

    def test_activar_desactivar_y_eliminar_otro_usuario(self):
        user_id = make_user('temporal')
        self.login_admin()
        self.client.post(f'/admin/usuarios/{user_id}/estado')
        self.assertFalse(state('temporal')['is_active'])
        self.client.post(f'/admin/usuarios/{user_id}/estado')
        self.assertTrue(state('temporal')['is_active'])
        self.client.post(f'/admin/usuarios/{user_id}/eliminar')
        self.assertIsNone(state('temporal'))

    def test_listado_y_formularios_se_renderizan(self):
        make_user('listado', permissions={'productos': 'view', 'blog': 'manage'}, full_name='Persona Listada')
        inactive_id = make_user('listado2', is_active=False)
        self.login_admin()
        html = self.client.get('/admin/usuarios').get_data(as_text=True)
        self.assertIn('Persona Listada', html)
        self.assertIn('Personalizado', html)
        self.assertEqual(self.client.get('/admin/usuarios/nuevo').status_code, 200)
        self.assertEqual(self.client.get(f'/admin/usuarios/{inactive_id}/editar').status_code, 200)
        self.assertEqual(self.client.get('/admin/usuarios/99999/editar').status_code, 404)

    # ---------- mi cuenta ----------

    def test_cambiar_contrasena_propia(self):
        make_user('propia')
        self.login('propia')
        bad = self.client.post('/admin/cuenta', data={
            'action': 'password', 'current_password': 'mal', 'password': 'Otra-clave-1', 'password_confirm': 'Otra-clave-1'},
            follow_redirects=True)
        self.assertIn('no es correcta', bad.get_data(as_text=True))
        self.assertTrue(state('propia')['password_ok'](PASSWORD))
        self.client.post('/admin/cuenta', data={
            'action': 'password', 'current_password': PASSWORD,
            'password': 'Otra-clave-1', 'password_confirm': 'Otra-clave-1'})
        self.assertTrue(state('propia')['password_ok']('Otra-clave-1'))

    def test_actualizar_datos_propios_no_toca_permisos(self):
        make_user('perfil', permissions={'blog': 'view'})
        self.login('perfil')
        self.client.post('/admin/cuenta', data={
            'action': 'profile', 'full_name': 'Perfil Nuevo', 'email': 'p@example.com', 'is_admin': '1'})
        perfil = state('perfil')
        self.assertEqual(perfil['full_name'], 'Perfil Nuevo')
        self.assertFalse(perfil['is_admin'])
        self.assertEqual(perfil['permissions'], {'blog': 'view'})


if __name__ == '__main__':
    unittest.main()
