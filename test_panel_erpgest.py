"""Pruebas del conector con el panel de ERPGEST (panel_erpgest.py): firmas, estado, usuarios, suspension, limite de
usuarios y restablecer el acceso.

Se ejecutan contra una base SQLite temporal, nunca contra la base real:

    python -m unittest test_panel_erpgest -v
"""
import base64
import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest import mock

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test.db').replace(os.sep, '/')

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

import conector_erpgest as conector  # noqa: E402
import panel_erpgest  # noqa: E402
from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import AdminUser, PanelEstado, QuoteRequest, SiteConfig  # noqa: E402

app.config['TESTING'] = True

SISTEMA = 'grupodewill'
PASSWORD = 'Clave-segura-1'


def nueva_llave():
    privada = Ed25519PrivateKey.generate()
    crudo = privada.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return privada, base64.b64encode(crudo).decode()


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
    with app.app_context():
        user = AdminUser.query.filter_by(username=username).first()
        return None if user is None else {'id': user.id, 'is_active': user.is_active,
                                          'password_ok': user.check_password}


def admin_id():
    return state('admin')['id']


def sesiones_desde():
    with app.app_context():
        estado = db.session.get(PanelEstado, 1)
        return estado and estado.sesiones_desde


class ConectorTest(unittest.TestCase):
    def setUp(self):
        self._limpiar()
        with app.app_context():
            admin = AdminUser.query.filter_by(username='admin').one()
            admin.is_admin, admin.is_active, admin.last_login = True, True, None
            admin.set_password('admin123')
            db.session.commit()
        self.privada, publica = nueva_llave()
        entorno = mock.patch.dict(os.environ, {'ERPGEST_CONECTOR_SISTEMA': SISTEMA, 'ERPGEST_CONECTOR_LLAVE': publica})
        entorno.start()
        self.addCleanup(entorno.stop)
        self.addCleanup(self._limpiar)  # un limite o un cierre de sesiones no debe alcanzar a las demas pruebas
        self.client = app.test_client()

    @staticmethod
    def _limpiar():
        with app.app_context():
            PanelEstado.query.delete()
            AdminUser.query.filter(AdminUser.username != 'admin').delete()
            SiteConfig.query.filter_by(key='maintenance_mode').delete()
            db.session.commit()

    def orden(self, operacion, datos=None, sistema=SISTEMA, fecha=None, metodo=None, firmada=None, enviada=None):
        """Orden firmada como la manda el panel. `firmada` firma otra operacion y `enviada` cambia el cuerpo."""
        metodo = metodo or conector.OPERACIONES[operacion]
        cuerpo = json.dumps(datos).encode() if datos is not None else b''
        fecha = int(time.time()) if fecha is None else fecha
        mensaje = conector.mensaje(fecha, metodo, sistema, firmada or operacion, cuerpo)
        cabeceras = {conector.CABECERA_FECHA: str(fecha),
                     conector.CABECERA_FIRMA: base64.b64encode(self.privada.sign(mensaje)).decode()}
        url = conector.PREFIJO + operacion
        if metodo == 'POST':
            return self.client.post(url, data=enviada if enviada is not None else cuerpo, headers=cabeceras,
                                    content_type='application/json')
        return self.client.get(url, headers=cabeceras)

    def login(self, username, password=PASSWORD, client=None):
        return (client or app.test_client()).post('/admin/login', data={'username': username, 'password': password})

    def cliente_con_sesion(self, username, password=PASSWORD):
        cliente = app.test_client()
        self.assertEqual(self.login(username, password, cliente).status_code, 302)
        return cliente

    # ---------- firmas ----------

    def test_sin_configuracion_el_conector_no_existe_y_nada_se_suspende(self):
        with mock.patch.dict(os.environ, {'ERPGEST_CONECTOR_LLAVE': ''}):
            self.assertEqual(self.orden('estado').status_code, 404)
            with app.app_context():
                db.session.add(PanelEstado(id=1, suspendido=True, mensaje='No debe verse', limite_usuarios=0))
                db.session.commit()
            self.assertEqual(self.client.get('/').status_code, 200)

    def test_solo_valen_las_ordenes_firmadas_para_este_sistema_y_esta_operacion(self):
        sin_firma = self.client.get(conector.PREFIJO + 'estado')
        self.assertEqual((sin_firma.status_code, sin_firma.get_json()), (401, {'error': 'firma'}))
        hace_6_min = int(time.time()) - 360
        casos = {
            'otra operacion': self.orden('estado', firmada='usuarios'),
            'otro sistema': self.orden('estado', sistema='metsalud'),
            'vencida': self.orden('estado', fecha=hace_6_min),
            'cuerpo cambiado': self.orden('limite-usuarios', {'limite': 5}, enviada=b'{"limite": 500}'),
        }
        for caso, respuesta in casos.items():
            self.assertEqual(respuesta.status_code, 401, caso)
        self.privada, _ = nueva_llave()  # bien armada, pero firmada con otra llave
        self.assertEqual(self.orden('estado').status_code, 401)
        with app.app_context():
            self.assertIsNone(db.session.get(PanelEstado, 1))  # nada se aplico

    def test_metodo_distinto_al_de_la_operacion(self):
        respuesta = self.orden('suspension', metodo='GET')
        self.assertEqual(respuesta.status_code, 405)
        self.assertEqual(self.orden('no-existe', metodo='GET').status_code, 404)

    # ---------- consultas ----------

    def test_estado_con_usuarios_actividad_y_cifras(self):
        ahora = datetime.utcnow()
        make_user('ana', last_login=ahora, permissions={'productos': 'view'})
        make_user('beto', is_active=False, last_login=ahora - timedelta(days=10))
        with app.app_context():
            db.session.add(QuoteRequest(client_name='Cliente de prueba del conector', status='pendiente'))
            db.session.commit()
        self.addCleanup(self._quitar_solicitud)
        respuesta = self.orden('estado')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.headers['Cache-Control'], 'no-store')
        datos = respuesta.get_json()
        self.assertEqual((datos['protocolo'], datos['sistema'], datos['suspendido'], datos['limite_usuarios']),
                         (1, SISTEMA, False, 0))
        self.assertEqual(datos['usuarios'], {'total': 3, 'activos': 2, 'administradores': 1})
        actividad = datos['actividad']
        self.assertEqual((actividad['activos_hoy'], actividad['activos_7d'], actividad['activos_30d']), (1, 1, 2))
        self.assertTrue(actividad['ultimo_ingreso'].endswith('+00:00'))
        cifras = {d['nombre']: d['valor'] for d in datos['datos']}
        self.assertEqual(list(cifras), ['Productos activos', 'Solicitudes del mes', 'Solicitudes pendientes'])
        self.assertGreaterEqual(cifras['Solicitudes del mes'], 1)
        self.assertGreaterEqual(cifras['Solicitudes pendientes'], 1)

    @staticmethod
    def _quitar_solicitud():
        with app.app_context():
            QuoteRequest.query.filter_by(client_name='Cliente de prueba del conector').delete()
            db.session.commit()

    def test_lista_de_usuarios(self):
        make_user('ana', full_name='Ana Ruiz', email='ana@example.com', permissions={'productos': 'view'})
        make_user('beto', is_active=False)
        datos = self.orden('usuarios').get_json()
        self.assertEqual(datos['total'], 3)
        usuarios = {u['usuario']: u for u in datos['usuarios']}
        self.assertEqual(list(usuarios), ['admin', 'ana', 'beto'])
        self.assertEqual(usuarios['admin']['rol'], 'Administrador')
        self.assertTrue(usuarios['admin']['administrador'])
        ana = usuarios['ana']
        self.assertEqual((ana['id'], ana['nombre'], ana['email'], ana['rol'], ana['activo']),
                         (str(state('ana')['id']), 'Ana Ruiz', 'ana@example.com', 'Personalizado', True))
        self.assertIsNone(ana['ultimo_ingreso'])
        self.assertEqual((usuarios['beto']['rol'], usuarios['beto']['activo']), ('Sin permisos', False))

    # ---------- suspension ----------

    def test_la_suspension_cierra_el_sitio_entero_salvo_el_conector_y_los_estaticos(self):
        admin = self.cliente_con_sesion('admin', 'admin123')
        aviso = 'Servicio suspendido. Comuníquese con su proveedor.'
        respuesta = self.orden('suspension', {'suspendido': True, 'mensaje': aviso})
        self.assertEqual(respuesta.get_json(), {'suspendido': True, 'mensaje_suspension': aviso})

        for ruta in ('/', '/productos', '/admin/login'):
            pagina = self.client.get(ruta)
            self.assertEqual(pagina.status_code, 503, ruta)
            self.assertIn(aviso, pagina.get_data(as_text=True))
        self.assertIn('Sitio no disponible', self.client.get('/').get_data(as_text=True))
        api = self.client.get('/api/productos/search?q=latex')
        self.assertEqual((api.status_code, api.get_json()['error']), (503, aviso))
        self.assertEqual(admin.get('/admin/').status_code, 503)  # con sesion tampoco
        self.assertEqual(self.client.get('/static/assets/logo.png').status_code, 200)
        self.assertTrue(self.orden('estado').get_json()['suspendido'])

        reactivar = self.orden('suspension', {'suspendido': False, 'mensaje': 'se ignora'})
        self.assertEqual(reactivar.get_json(), {'suspendido': False, 'mensaje_suspension': ''})
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(admin.get('/admin/').status_code, 200)  # la suspension no cerro la sesion

    def test_el_modo_mantenimiento_no_cierra_el_conector(self):
        with app.app_context():
            SiteConfig.set('maintenance_mode', '1')
        self.assertEqual(self.client.get('/').status_code, 503)
        self.assertEqual(self.orden('estado').status_code, 200)

    # ---------- limite de usuarios ----------

    def test_el_limite_no_deja_crear_ni_activar_usuarios_de_mas(self):
        for invalido in ('dos', -1, True, None):
            self.assertEqual(self.orden('limite-usuarios', {'limite': invalido}).status_code, 400, invalido)
        respuesta = self.orden('limite-usuarios', {'limite': 2})
        self.assertEqual(respuesta.get_json(), {'limite_usuarios': 2, 'activos': 1})
        admin = self.cliente_con_sesion('admin', 'admin123')
        nuevo = {'password': PASSWORD, 'password_confirm': PASSWORD, 'is_active': '1'}

        self.assertEqual(admin.post('/admin/usuarios/nuevo', data={**nuevo, 'username': 'ana'}).status_code, 302)
        bloqueado = admin.post('/admin/usuarios/nuevo', data={**nuevo, 'username': 'carla'})
        self.assertIn('Su plan permite hasta 2 usuarios activos', bloqueado.get_data(as_text=True))
        self.assertIsNone(state('carla'))
        # inactivo si se puede crear, pero no activarlo
        inactivo = {**nuevo, 'username': 'dora', 'is_active': ''}
        self.assertEqual(admin.post('/admin/usuarios/nuevo', data=inactivo).status_code, 302)
        dora = state('dora')['id']
        admin.post(f'/admin/usuarios/{dora}/estado')
        self.assertFalse(state('dora')['is_active'])
        editar = admin.post(f'/admin/usuarios/{dora}/editar', data={'username': 'dora', 'is_active': '1'})
        self.assertIn('Su plan permite hasta 2 usuarios activos', editar.get_data(as_text=True))
        self.assertFalse(state('dora')['is_active'])
        conectado = self.orden('usuario-activo', {'usuario': str(dora), 'activo': True})
        self.assertEqual(conectado.status_code, 409)
        self.assertIn('Su plan permite hasta 2', conectado.get_json()['error'])
        # quien ya estaba activo se sigue editando
        ana = state('ana')['id']
        self.assertEqual(admin.post(f'/admin/usuarios/{ana}/editar',
                                    data={'username': 'ana', 'full_name': 'Ana', 'is_active': '1'}).status_code, 302)
        # sin limite, se activa
        self.orden('limite-usuarios', {'limite': 0})
        admin.post(f'/admin/usuarios/{dora}/estado')
        self.assertTrue(state('dora')['is_active'])

    # ---------- usuarios ----------

    def test_activar_y_desactivar_un_usuario(self):
        ana = make_user('ana')
        self.assertEqual(self.orden('usuario-activo', {'usuario': str(ana), 'activo': False}).get_json(),
                         {'usuario': 'ana', 'activo': False})
        self.assertFalse(state('ana')['is_active'])
        self.assertEqual(self.orden('usuario-activo', {'usuario': str(ana), 'activo': True}).status_code, 200)
        self.assertTrue(state('ana')['is_active'])
        ultimo_admin = self.orden('usuario-activo', {'usuario': str(admin_id()), 'activo': False})
        self.assertEqual(ultimo_admin.status_code, 409)
        self.assertTrue(state('admin')['is_active'])
        for desconocido in ('99999', 'abc', None):
            self.assertEqual(self.orden('usuario-activo', {'usuario': desconocido, 'activo': True}).status_code, 404)

    def test_restablecer_el_acceso_cambia_la_clave_activa_al_usuario_y_cierra_todas_las_sesiones(self):
        make_user('ana', permissions={'productos': 'view'})
        beto = make_user('beto', is_active=False)
        admin = self.cliente_con_sesion('admin', 'admin123')
        ana = self.cliente_con_sesion('ana')
        self.assertEqual(ana.get('/admin/productos').status_code, 200)
        self.orden('limite-usuarios', {'limite': 1})  # devolver el acceso no cuenta contra el limite

        self.assertEqual(self.orden('restablecer-acceso', {'usuario': str(beto), 'clave': 'corta'}).status_code, 400)
        self.assertEqual(self.orden('restablecer-acceso', {'usuario': '99999', 'clave': 'Nueva-clave-9'}).status_code,
                         404)
        respuesta = self.orden('restablecer-acceso',
                               {'usuario': str(beto), 'clave': 'Nueva-clave-9', 'cerrar_sesiones': True})
        self.assertEqual(respuesta.get_json(), {'usuario': 'beto', 'sesiones_cerradas': True})
        beto_ahora = state('beto')
        self.assertTrue(beto_ahora['is_active'] and beto_ahora['password_ok']('Nueva-clave-9'))

        for cliente, ruta in ((admin, '/admin/'), (ana, '/admin/productos')):
            cerrada = cliente.get(ruta)
            self.assertEqual(cerrada.status_code, 302, ruta)
            self.assertIn('/admin/login', cerrada.headers['Location'])
        # quien vuelve a iniciar sesion entra normal
        de_nuevo = self.cliente_con_sesion('admin', 'admin123')
        self.assertEqual(de_nuevo.get('/admin/').status_code, 200)
        self.assertEqual(self.cliente_con_sesion('beto', 'Nueva-clave-9').get('/admin/cuenta').status_code, 200)

    def test_restablecer_sin_cerrar_sesiones_las_deja_abiertas(self):
        ana = make_user('ana')
        admin = self.cliente_con_sesion('admin', 'admin123')
        respuesta = self.orden('restablecer-acceso', {'usuario': str(ana), 'clave': 'Nueva-clave-9'})
        self.assertEqual(respuesta.get_json(), {'usuario': 'ana', 'sesiones_cerradas': False})
        self.assertIsNone(sesiones_desde())
        self.assertEqual(admin.get('/admin/').status_code, 200)

    def test_las_sesiones_de_antes_del_conector_siguen_hasta_el_primer_cierre(self):
        cliente = app.test_client()
        with cliente.session_transaction() as sesion:  # como las que ya estaban abiertas al desplegar
            sesion['_user_id'] = str(admin_id())
            sesion['_fresh'] = True
        self.assertEqual(cliente.get('/admin/').status_code, 200)
        ana = make_user('ana')
        self.orden('restablecer-acceso', {'usuario': str(ana), 'clave': 'Nueva-clave-9', 'cerrar_sesiones': True})
        self.assertEqual(cliente.get('/admin/').status_code, 302)

    def test_el_registro_no_guarda_la_contrasena(self):
        ana = make_user('ana')
        with self.assertLogs(app.logger, level='WARNING') as registro:
            self.orden('restablecer-acceso', {'usuario': str(ana), 'clave': 'Secreta-que-no-se-ve', 'cerrar_sesiones': True})
        self.assertIn('restablecio el acceso de ana', '\n'.join(registro.output))
        self.assertNotIn('Secreta-que-no-se-ve', '\n'.join(registro.output))


class ErrorDeLimiteTest(unittest.TestCase):
    def setUp(self):
        ConectorTest._limpiar()
        self.addCleanup(ConectorTest._limpiar)

    def test_sin_limite_o_desactivando_no_hay_aviso(self):
        with app.app_context():
            self.assertEqual(panel_erpgest.error_de_limite(None, True), '')
            db.session.add(PanelEstado(id=1, suspendido=False, mensaje='', limite_usuarios=1))
            db.session.commit()
        with app.app_context():
            self.assertEqual(panel_erpgest.error_de_limite(None, False), '')
            self.assertEqual(panel_erpgest.error_de_limite(admin_id(), True), '')  # ya activo: no suma
            self.assertIn('hasta 1 usuarios activos', panel_erpgest.error_de_limite(None, True))


if __name__ == '__main__':
    unittest.main()
