"""Pruebas del registro de atencion de las solicitudes (pedidos): que usuario del panel cambio su estado y cuando.

Cada cambio de estado queda registrado con el usuario que lo hizo; la lista muestra quien atendio cada solicitud
(con filtro por usuario) y el detalle trae el historial completo. Las horas se muestran en hora de Peru.

Se ejecutan contra una base SQLite temporal, nunca contra la base real:

    python -m unittest test_atencion_pedidos -v
"""
import os
import re
import tempfile
import unittest
import uuid
from datetime import datetime
from functools import cached_property

_tmpdir = tempfile.mkdtemp(prefix='dewill_test_')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(_tmpdir, 'test_atencion.db').replace(os.sep, '/')

from werkzeug.security import generate_password_hash  # noqa: E402

from app import app, db  # noqa: E402  (la URL de la base debe fijarse antes de importar la app)
from models import AdminUser, QuoteRequest, QuoteStatusLog  # noqa: E402

app.config['TESTING'] = True

PASSWORD = 'Clave-segura-1'
PASSWORD_HASH = generate_password_hash(PASSWORD)   # una sola vez: el hash de la clave es lento


def make_user(username, full_name=None, permissions=None):
    with app.app_context():
        user = AdminUser(username=username, full_name=full_name, is_active=True, is_admin=False, password_hash=PASSWORD_HASH)
        user.set_permissions(permissions or {})
        db.session.add(user)
        db.session.commit()
        return user.id


def login(username, password=PASSWORD):
    client = app.test_client()
    assert client.post('/admin/login', data={'username': username, 'password': password}).status_code == 302
    return client


def texto(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()


class AtencionDePedidosTest(unittest.TestCase):
    def setUp(self):
        self.limpiar()
        self.addCleanup(self.limpiar)
        s = uuid.uuid4().hex[:6]
        self.ana = make_user(f'ana{s}', 'Ana López', {'solicitudes': 'manage', 'dashboard': 'view'})
        self.luis = make_user(f'luis{s}', 'Luis Pérez', {'solicitudes': 'manage'})
        self.rosa = make_user(f'rosa{s}', None, {'solicitudes': 'manage'})   # sin nombre completo: se muestra el usuario
        self.lector = make_user(f'lector{s}', 'Carla Lector', {'solicitudes': 'view'})
        self.usernames = {'ana': f'ana{s}', 'luis': f'luis{s}', 'rosa': f'rosa{s}', 'lector': f'lector{s}'}

    # las sesiones se abren la primera vez que una prueba las usa
    @cached_property
    def cliente_ana(self):
        return login(self.usernames['ana'])

    @cached_property
    def cliente_luis(self):
        return login(self.usernames['luis'])

    @cached_property
    def admin(self):
        return login('admin', 'admin123')

    def limpiar(self):
        # la base se comparte con otras suites: sin registros ni solicitudes ni usuarios de prueba sobrantes
        with app.app_context():
            QuoteStatusLog.query.delete()
            QuoteRequest.query.delete()
            AdminUser.query.filter(AdminUser.username != 'admin').delete()
            db.session.commit()

    # ---------- utilidades ----------

    def solicitud(self, nombre='Cliente', status='pendiente', created_at=None):
        with app.app_context():
            quote = QuoteRequest(client_name=nombre, client_phone='987654321', status=status)
            if created_at:
                quote.created_at = created_at
            db.session.add(quote)
            db.session.commit()
            return quote.id

    def cambiar(self, client, qid, status):
        resp = client.post(f'/admin/solicitudes/{qid}/estado', data={'status': status}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def registro(self, qid):
        """[(usuario, nombre guardado, estado anterior, estado nuevo)] de la solicitud, en orden."""
        with app.app_context():
            return [(log.user_id, log.user_name, log.from_status, log.to_status)
                    for log in QuoteStatusLog.query.filter_by(quote_id=qid).order_by(QuoteStatusLog.id)]

    def estado(self, qid):
        with app.app_context():
            return db.session.get(QuoteRequest, qid).status

    def agregar_registro(self, qid, user_id, nombre, desde, hasta, cuando=None):
        with app.app_context():
            db.session.add(QuoteStatusLog(quote_id=qid, user_id=user_id, user_name=nombre, from_status=desde, to_status=hasta,
                                          **({'created_at': cuando} if cuando else {})))
            db.session.commit()

    def lista(self, client=None, **params):
        resp = (client or self.admin).get('/admin/solicitudes', query_string=params)
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    def ids_de(self, html):
        return [int(i) for i in re.findall(r'<div class="col-id">#(\d+)</div>', html)]

    def celda_atendido(self, html, qid):
        """Texto de la columna 'Atendido por' de la fila de la solicitud."""
        fila = next(f for f in html.split('<div class="quote-card-row">')[1:] if f'<div class="col-id">#{qid}</div>' in f)
        return texto(fila[fila.index('<div class="col-attended">'):fila.index('<div class="col-date">')])

    def detalle(self, qid, client=None):
        resp = (client or self.admin).get(f'/admin/solicitudes/{qid}')
        self.assertEqual(resp.status_code, 200)
        return resp.get_data(as_text=True)

    # ---------- registro de cada cambio de estado ----------

    def test_cambiar_el_estado_registra_quien_lo_hizo(self):
        qid = self.solicitud()
        self.assertIn('Estado actualizado', self.cambiar(self.cliente_ana, qid, 'en_proceso'))
        self.assertEqual(self.estado(qid), 'en_proceso')
        self.assertEqual(self.registro(qid), [(self.ana, 'Ana López', 'pendiente', 'en_proceso')])
        detalle = texto(self.detalle(qid))
        self.assertIn('Atendido por: Ana López', detalle)
        self.assertIn('Historial de atención Ana López Pendiente En proceso', detalle)

    def test_cada_cambio_queda_en_el_historial_y_la_lista_muestra_a_quienes_intervinieron(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.cambiar(self.cliente_luis, qid, 'respondida')
        self.assertEqual(self.registro(qid), [(self.ana, 'Ana López', 'pendiente', 'en_proceso'),
                                              (self.luis, 'Luis Pérez', 'en_proceso', 'respondida')])
        # quien la tomo y quien la respondio, en el orden en que intervinieron
        self.assertTrue(self.celda_atendido(self.lista(), qid).startswith('Ana López, Luis Pérez'))
        detalle = self.detalle(qid)
        self.assertIn('Atendido por: Ana López, Luis Pérez', texto(detalle))
        self.assertLess(detalle.index('Luis Pérez</span>'), detalle.index('Ana López</span>'), 'el mas reciente va primero')

    def test_un_usuario_que_cambia_el_estado_varias_veces_aparece_una_sola_vez(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.cambiar(self.cliente_ana, qid, 'respondida')
        self.assertEqual(len(self.registro(qid)), 2)
        self.assertRegex(self.celda_atendido(self.lista(), qid), r'^Ana López \d{2}/\d{2}/\d{4} \d{2}:\d{2}$')
        self.assertIn('Atendido por: Ana López ·', texto(self.detalle(qid)))

    def test_sin_nombre_completo_se_registra_el_usuario(self):
        qid = self.solicitud()
        self.cambiar(login(self.usernames['rosa']), qid, 'en_proceso')
        self.assertEqual(self.registro(qid)[0][1], self.usernames['rosa'])
        self.assertIn(self.usernames['rosa'], self.celda_atendido(self.lista(), qid))

    def test_el_mismo_estado_no_se_registra(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.assertIn('ya tenía ese estado', self.cambiar(self.cliente_luis, qid, 'en_proceso'))
        self.assertEqual(len(self.registro(qid)), 1)
        self.assertTrue(self.celda_atendido(self.lista(), qid).startswith('Ana López'))

    def test_un_estado_invalido_no_cambia_nada(self):
        qid = self.solicitud()
        for status in ('cerrada', '', 'EN_PROCESO'):
            self.assertIn('no es válido', self.cambiar(self.cliente_ana, qid, status), status)
        self.assertEqual(self.estado(qid), 'pendiente')
        self.assertEqual(self.registro(qid), [])

    def test_volver_a_pendiente_queda_registrado_pero_la_lista_dice_sin_atender(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.cambiar(self.cliente_luis, qid, 'pendiente')
        self.assertEqual([r[3] for r in self.registro(qid)], ['en_proceso', 'pendiente'])
        self.assertEqual(self.celda_atendido(self.lista(), qid), 'Sin atender')
        detalle = texto(self.detalle(qid))
        self.assertIn('Atendido por: Sin atender', detalle)
        self.assertIn('Luis Pérez En proceso Pendiente', detalle)   # el historial conserva ambos cambios
        self.assertIn('Ana López Pendiente En proceso', detalle)

    def test_solicitudes_sin_registro(self):
        pendiente = self.solicitud('Nueva')
        antigua = self.solicitud('Antigua', status='respondida')   # se atendio antes de que existiera el registro
        html = self.lista()
        self.assertEqual(self.celda_atendido(html, pendiente), 'Sin atender')
        self.assertEqual(self.celda_atendido(html, antigua), 'Sin registro')
        self.assertIn('Nadie ha atendido esta solicitud todavía', self.detalle(pendiente))
        self.assertIn('antes de que existiera el registro de atención', self.detalle(antigua))
        # y una antigua puede seguir su curso: el primer cambio ya queda registrado
        self.cambiar(self.cliente_ana, antigua, 'en_proceso')
        self.assertEqual(self.registro(antigua), [(self.ana, 'Ana López', 'respondida', 'en_proceso')])

    # ---------- permisos ----------

    def test_un_usuario_de_solo_lectura_ve_el_registro_pero_no_puede_cambiar_el_estado(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        lector = login(self.usernames['lector'])
        self.assertIn('Ana López', self.detalle(qid, lector))
        self.assertTrue(self.celda_atendido(self.lista(lector), qid).startswith('Ana López'))
        resp = lector.post(f'/admin/solicitudes/{qid}/estado', data={'status': 'respondida'})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(self.estado(qid), 'en_proceso')
        self.assertEqual(len(self.registro(qid)), 1)

    # ---------- filtro 'Atendido por' ----------

    def preparar_filtro(self):
        q1, q2, q3, q4 = (self.solicitud(f'Cliente {n}') for n in range(1, 5))
        self.cambiar(self.cliente_ana, q1, 'en_proceso')
        self.cambiar(self.cliente_ana, q2, 'en_proceso')
        self.cambiar(self.cliente_ana, q2, 'respondida')
        self.cambiar(self.cliente_luis, q3, 'en_proceso')
        self.cambiar(self.cliente_luis, q2, 'pendiente')   # q2 la trabajaron los dos
        return q1, q2, q3, q4

    def test_el_filtro_muestra_las_solicitudes_que_atendio_cada_usuario(self):
        q1, q2, q3, q4 = self.preparar_filtro()
        self.assertEqual(sorted(self.ids_de(self.lista())), [q1, q2, q3, q4])
        self.assertEqual(sorted(self.ids_de(self.lista(atendido=self.ana))), [q1, q2])
        self.assertEqual(sorted(self.ids_de(self.lista(atendido=self.luis))), [q2, q3])
        self.assertEqual(self.ids_de(self.lista(atendido=self.ana, status='en_proceso')), [q1])
        self.assertEqual(self.ids_de(self.lista(atendido=self.luis, status='respondida')), [])

    def test_el_filtro_ofrece_solo_a_quienes_han_atendido(self):
        self.assertNotIn('attendantFilter', self.lista())   # sin registros no hay nada que filtrar
        self.preparar_filtro()
        html = self.lista(atendido=self.luis)
        opciones = re.findall(r'<option value="(\d*)"( selected)?>([^<]*)</option>', html[html.index('attendantFilter'):])
        self.assertEqual(opciones, [('', '', 'Todos'), (str(self.ana), '', 'Ana López'), (str(self.luis), ' selected', 'Luis Pérez')])
        # el estado elegido se conserva al filtrar, y el filtro al cambiar de estado
        html = self.lista(atendido=self.luis, status='en_proceso')
        self.assertIn('<input type="hidden" name="status" value="en_proceso">', html)
        self.assertIn(f'href="/admin/solicitudes?status=respondida&amp;atendido={self.luis}"', html)

    def test_un_usuario_inexistente_o_un_valor_raro_en_el_filtro_se_ignoran(self):
        q1, q2, q3, q4 = self.preparar_filtro()
        for valor in ('999999', 'abc', str(self.rosa)):   # rosa nunca atendio nada
            self.assertEqual(sorted(self.ids_de(self.lista(atendido=valor))), [q1, q2, q3, q4], valor)

    def test_la_paginacion_conserva_el_filtro(self):
        with app.app_context():
            quotes = [QuoteRequest(client_name=f'Cliente {n}', status='en_proceso') for n in range(22)]
            db.session.add_all(quotes)
            db.session.flush()
            db.session.add_all(QuoteStatusLog(quote_id=q.id, user_id=self.ana, user_name='Ana López', from_status='pendiente',
                                              to_status='en_proceso') for q in quotes)
            db.session.commit()
        otra = self.solicitud('De otro usuario')
        self.cambiar(self.cliente_luis, otra, 'en_proceso')
        html = self.lista(atendido=self.ana, status='en_proceso')
        self.assertEqual(len(self.ids_de(html)), 20)
        self.assertIn(f'href="?page=2&status=en_proceso&atendido={self.ana}"', html)
        pagina2 = self.lista(atendido=self.ana, status='en_proceso', page=2)
        self.assertEqual(len(self.ids_de(pagina2)), 2)
        self.assertNotIn(otra, self.ids_de(pagina2))

    # ---------- usuarios eliminados ----------

    def test_si_se_elimina_al_usuario_se_conserva_su_nombre_en_el_registro(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.assertEqual(self.admin.post(f'/admin/usuarios/{self.ana}/eliminar').status_code, 302)
        with app.app_context():
            self.assertIsNone(db.session.get(AdminUser, self.ana))
        self.assertIn('Ana López', self.celda_atendido(self.lista(), qid))
        detalle = texto(self.detalle(qid))
        self.assertIn('Atendido por: Ana López', detalle)
        self.assertIn('Historial de atención Ana López', detalle)
        self.assertNotIn('Ana López</option>', self.lista())   # ya no se puede filtrar por un usuario que no existe

    def test_si_el_usuario_cambia_de_nombre_se_muestra_el_actual(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        with app.app_context():
            db.session.get(AdminUser, self.ana).full_name = 'Ana López Díaz'
            db.session.commit()
        self.assertIn('Atendido por: Ana López Díaz', texto(self.detalle(qid)))
        self.assertEqual(self.registro(qid)[0][1], 'Ana López')   # lo guardado es el de aquel momento

    # ---------- hora de Peru ----------

    def test_las_horas_se_muestran_en_hora_de_peru(self):
        # se guardan en UTC: 15:00 UTC son las 10:00 en Lima
        qid = self.solicitud(created_at=datetime(2026, 11, 2, 15, 0))
        self.agregar_registro(qid, self.ana, 'Ana López', 'pendiente', 'en_proceso', datetime(2026, 11, 2, 15, 30))
        with app.app_context():
            db.session.get(QuoteRequest, qid).status = 'en_proceso'
            db.session.commit()
        lista = texto(self.lista())
        self.assertIn('Ana López 02/11/2026 10:30', lista)
        self.assertIn('02/11/2026 10:00', lista)
        detalle = texto(self.detalle(qid))
        self.assertIn('Fecha de solicitud: 02/11/2026 10:00', detalle)
        self.assertIn('Atendido por: Ana López · 02/11/2026 10:30', detalle)
        self.assertIn('Pendiente En proceso 02/11/2026 10:30', detalle)
        for utc in ('15:00', '15:30'):
            self.assertNotIn(utc, lista + detalle)
        tablero = texto(self.admin.get('/admin/').get_data(as_text=True))
        self.assertIn('02/11/2026 10:00', tablero)
        self.assertNotIn('15:00', tablero)

    # ---------- eliminar la solicitud ----------

    def test_al_eliminar_la_solicitud_se_elimina_su_historial(self):
        qid = self.solicitud()
        self.cambiar(self.cliente_ana, qid, 'en_proceso')
        self.cambiar(self.cliente_luis, qid, 'respondida')
        with app.app_context():
            db.session.delete(db.session.get(QuoteRequest, qid))
            db.session.commit()
            self.assertEqual(QuoteStatusLog.query.filter_by(quote_id=qid).count(), 0)


if __name__ == '__main__':
    unittest.main()
