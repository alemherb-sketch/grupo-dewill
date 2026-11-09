"""Conector con el panel de ERPGEST (el proveedor): usuarios, actividad, suspension, limite y acceso.

El panel de ERPGEST (Panel > Subdominios) da ordenes firmadas con Ed25519 a /erpgest-conector/v1/<operacion>. Este
modulo las comprueba con conector_erpgest.py (copiado tal cual de ERPGEST) y las cumple con las reglas de Grupo
Dewill: los usuarios son los del panel /admin (AdminUser) y su actividad es su ultimo acceso (last_login). Sin
ERPGEST_CONECTOR_SISTEMA y ERPGEST_CONECTOR_LLAVE en el entorno el conector no existe (404) y la suspension no se
consulta.

Lo que ordena el panel se guarda en la tabla panel_erpgest_estado (una fila; la crea db.create_all al arrancar), no
en memoria: gunicorn corre varios workers. Con el sistema suspendido el sitio entero (paginas publicas, API y panel)
responde 503 con el aviso; siguen el conector y los archivos estaticos. Cerrar las sesiones no cambia la SECRET_KEY:
cada sesion guarda cuando se inicio y load_user rechaza las anteriores a la marca del panel.
"""
import json
import time
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, g, jsonify, render_template, request, session
from flask_login import user_logged_in
from sqlalchemy import func

import conector_erpgest as conector
from models import AdminUser, PanelEstado, Product, QuoteRequest, db

MAXIMO_USUARIOS = 500
LIMA = timezone(timedelta(hours=-5))  # el Peru no tiene horario de verano
MENSAJE_LIMITE = ('Su plan permite hasta {n} usuarios activos. Para ampliarlo, '
                  'comuníquese con su proveedor (ERPGEST).')
MENSAJE_SUSPENSION = 'El servicio está suspendido temporalmente.'
CLAVE_INGRESO = 'erpgest_ingreso_ms'  # en la sesion: cuando se inicio (ms UTC)
PREFIJO = conector.PREFIJO  # /erpgest-conector/v1/: tampoco lo cierra el modo mantenimiento
ABIERTOS = (PREFIJO, '/static/')  # lo unico que atiende un sitio suspendido

bp = Blueprint('panel_erpgest', __name__, url_prefix=PREFIJO.rstrip('/'))


# --- Reglas -------------------------------------------------------------------

def leer_estado():
    """El estado vigente, leido una vez por peticion; sin fila, uno nuevo sin guardar (sitio normal y sin limite)."""
    if 'panel_erpgest_estado' not in g:
        g.panel_erpgest_estado = (db.session.get(PanelEstado, 1)
                                  or PanelEstado(id=1, suspendido=False, mensaje='', limite_usuarios=0))
    return g.panel_erpgest_estado


def _activos(excluir=None):
    consulta = AdminUser.query.filter(AdminUser.is_active.is_(True))
    if excluir is not None:
        consulta = consulta.filter(AdminUser.id != excluir)
    return consulta


def error_de_limite(usuario_id, activo):
    """Texto del aviso si dejar activo a este usuario pasaria del limite contratado; '' si se puede.

    Quien ya estaba activo no suma: el limite solo frena altas y reactivaciones. Llamar ANTES de cambiar al usuario
    (con el autoflush, un cambio pendiente ya contaria en la consulta)."""
    if not activo:
        return ''
    limite = leer_estado().limite_usuarios or 0
    if not limite:
        return ''
    if usuario_id is not None and _activos().filter(AdminUser.id == usuario_id).first() is not None:
        return ''
    return MENSAJE_LIMITE.format(n=limite) if _activos(excluir=usuario_id).count() >= limite else ''


def _ms(fecha_utc):
    return int(fecha_utc.replace(tzinfo=timezone.utc).timestamp() * 1000)


def sesion_vigente():
    """False si el panel cerro todas las sesiones despues de que se inicio esta (restablecer el acceso).

    Las sesiones sin marca de inicio (anteriores al conector) caen con el primer cierre."""
    try:
        desde = leer_estado().sesiones_desde
    except Exception:
        db.session.rollback()
        return True
    return desde is None or session.get(CLAVE_INGRESO, 0) >= _ms(desde)


def _al_iniciar_sesion(sender, user, **extra):
    session[CLAVE_INGRESO] = int(time.time() * 1000)


def _bloquear_si_suspendido():
    if conector.configuracion() is None or request.path.startswith(ABIERTOS):
        return None
    try:
        estado = leer_estado()
        if not estado.suspendido:
            return None
        mensaje = estado.mensaje or MENSAJE_SUSPENSION
    except Exception:
        # Si la base falla, mejor dejar pasar la peticion que bloquear todo el sitio (como el modo mantenimiento)
        db.session.rollback()
        return None
    cabeceras = {'Retry-After': '3600', 'Cache-Control': 'no-store'}
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': mensaje}), 503, cabeceras
    return render_template('mantenimiento.html', maintenance_message=mensaje, maintenance_title='Sitio no disponible',
                           maintenance_icon='fa-circle-pause'), 503, cabeceras


def instalar(app):
    """Rutas del conector, bloqueo por suspension (antes que las demas comprobaciones) y marca de inicio de sesion."""
    app.register_blueprint(bp)
    app.before_request_funcs.setdefault(None, []).insert(0, _bloquear_si_suspendido)
    user_logged_in.connect(_al_iniciar_sesion, app)


def _auditar(texto):
    """El sitio no tiene bitacora propia: queda en el registro del servicio (journalctl -u grupo-dewill)."""
    current_app.logger.warning('ERPGEST (proveedor): %s', texto)


# --- Operaciones --------------------------------------------------------------

def _iso(valor):
    return valor.replace(tzinfo=timezone.utc).isoformat() if valor else None


def _json(datos, status=200):
    respuesta = jsonify(datos)
    respuesta.status_code = status
    respuesta.headers['Cache-Control'] = 'no-store'
    return respuesta


def _rol(usuario):
    if usuario.is_admin:
        return 'Administrador'
    return 'Personalizado' if usuario.get_permissions() else 'Sin permisos'


def _estado(datos, sistema):
    ahora = datetime.utcnow()
    inicio_hoy = (datetime.now(LIMA).replace(hour=0, minute=0, second=0, microsecond=0)
                  .astimezone(timezone.utc).replace(tzinfo=None))
    inicio_mes = inicio_hoy.replace(day=1)
    estado = leer_estado()

    def ingresaron(desde):
        return AdminUser.query.filter(AdminUser.last_login >= desde).count()

    return _json({
        'protocolo': 1, 'sistema': sistema, 'version': None, 'hora': _iso(ahora),
        'suspendido': bool(estado.suspendido), 'mensaje_suspension': estado.mensaje or '',
        'limite_usuarios': estado.limite_usuarios or 0,
        'usuarios': {'total': AdminUser.query.count(), 'activos': _activos().count(),
                     'administradores': _activos().filter(AdminUser.is_admin.is_(True)).count()},
        'actividad': {'ultimo_ingreso': _iso(db.session.query(func.max(AdminUser.last_login)).scalar()),
                      'activos_hoy': ingresaron(inicio_hoy), 'activos_7d': ingresaron(ahora - timedelta(days=7)),
                      'activos_30d': ingresaron(ahora - timedelta(days=30))},
        'datos': [
            {'nombre': 'Productos activos', 'valor': Product.query.filter(Product.is_active.is_(True)).count()},
            {'nombre': 'Solicitudes del mes',
             'valor': QuoteRequest.query.filter(QuoteRequest.created_at >= inicio_mes).count()},
            {'nombre': 'Solicitudes pendientes',
             'valor': QuoteRequest.query.filter(QuoteRequest.status == 'pendiente').count()},
        ],
    })


def _usuarios(datos, sistema):
    usuarios = AdminUser.query.order_by(func.lower(AdminUser.username))
    lista = [{
        'id': str(u.id), 'usuario': u.username, 'nombre': u.display_name, 'email': u.email or None, 'rol': _rol(u),
        'administrador': bool(u.is_admin), 'activo': bool(u.is_active), 'ultimo_ingreso': _iso(u.last_login),
        'creado': _iso(u.created_at),
    } for u in usuarios.limit(MAXIMO_USUARIOS)]
    return _json({'total': usuarios.count(), 'usuarios': lista})


def _suspension(datos, sistema):
    estado = leer_estado()
    estado.suspendido = bool(datos.get('suspendido'))
    estado.mensaje = str(datos.get('mensaje') or '').strip()[:300] if estado.suspendido else ''
    db.session.add(estado)
    db.session.commit()
    _auditar(('suspendio el sitio: ' + (estado.mensaje or MENSAJE_SUSPENSION)) if estado.suspendido
             else 'reactivo el sitio')
    return _json({'suspendido': estado.suspendido, 'mensaje_suspension': estado.mensaje})


def _limite(datos, sistema):
    limite = datos.get('limite')
    if not isinstance(limite, int) or isinstance(limite, bool) or limite < 0:
        return _json({'error': 'El límite debe ser un número entero de 0 en adelante.'}, 400)
    estado = leer_estado()
    estado.limite_usuarios = limite
    db.session.add(estado)
    db.session.commit()
    _auditar(f'fijo el limite de usuarios activos en {limite}')
    return _json({'limite_usuarios': limite, 'activos': _activos().count()})


def _usuario(datos):
    try:
        return db.session.get(AdminUser, int(str(datos.get('usuario'))))
    except ValueError:
        return None


def _restablecer_acceso(datos, sistema):
    usuario = _usuario(datos)
    if usuario is None:
        return _json({'error': 'No existe ese usuario.'}, 404)
    clave = datos.get('clave')
    if not isinstance(clave, str) or len(clave) < 8:
        return _json({'error': 'La contraseña debe tener al menos 8 caracteres.'}, 400)
    cerrar = bool(datos.get('cerrar_sesiones'))
    usuario.set_password(clave)
    usuario.is_active = True  # devolver el acceso no cuenta contra el limite de usuarios
    if cerrar:
        estado = leer_estado()
        estado.sesiones_desde = datetime.utcnow()  # las sesiones iniciadas antes ya no valen (sesion_vigente)
        db.session.add(estado)
    db.session.commit()
    _auditar(f'restablecio el acceso de {usuario.username}' + (' y cerro todas las sesiones' if cerrar else ''))
    return _json({'usuario': usuario.username, 'sesiones_cerradas': cerrar})


def _usuario_activo(datos, sistema):
    usuario = _usuario(datos)
    if usuario is None:
        return _json({'error': 'No existe ese usuario.'}, 404)
    activo = bool(datos.get('activo'))
    if activo:
        mensaje = error_de_limite(usuario.id, True)
        if mensaje:
            return _json({'error': mensaje}, 409)
    elif usuario.is_admin and usuario.is_active and not _activos(excluir=usuario.id).filter(
            AdminUser.is_admin.is_(True)).count():
        return _json({'error': 'No se puede desactivar al último administrador activo.'}, 409)
    usuario.is_active = activo
    db.session.commit()
    _auditar(f'{"activo" if activo else "desactivo"} al usuario {usuario.username}')
    return _json({'usuario': usuario.username, 'activo': activo})


OPERACIONES = {'estado': _estado, 'usuarios': _usuarios, 'suspension': _suspension, 'limite-usuarios': _limite,
               'restablecer-acceso': _restablecer_acceso, 'usuario-activo': _usuario_activo}


@bp.route('/<operacion>', methods=['GET', 'POST'])
def orden(operacion):
    configuracion = conector.configuracion()
    if configuracion is None or operacion not in OPERACIONES:
        return _json({'error': 'No existe.'}, 404)
    sistema, llave = configuracion
    cuerpo = request.get_data(cache=True)  # los bytes tal como llegaron: la firma cubre su SHA-256
    try:
        conector.verificar(request.method, operacion, cuerpo, request.headers.get(conector.CABECERA_FECHA),
                           request.headers.get(conector.CABECERA_FIRMA), sistema, llave)
    except conector.FirmaInvalida:
        return _json({'error': 'firma'}, 401)
    if request.method != conector.OPERACIONES[operacion]:
        return _json({'error': 'Método no permitido.'}, 405)
    try:
        datos = json.loads(cuerpo) if cuerpo else {}
    except ValueError:
        return _json({'error': 'El cuerpo no es JSON.'}, 400)
    if not isinstance(datos, dict):
        return _json({'error': 'El cuerpo debe ser un objeto JSON.'}, 400)
    return OPERACIONES[operacion](datos, sistema)
