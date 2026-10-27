"""Modulos del panel de administracion y niveles de permiso.

Cada usuario recibe un nivel por modulo:
  - ''       sin acceso (el modulo no aparece en el menu)
  - 'view'   solo consulta: puede abrir las pantallas pero no guardar cambios
  - 'manage' consulta, crea, edita y elimina

Los administradores (AdminUser.is_admin) tienen acceso total y son los unicos que gestionan usuarios.
Para proteger una ruta nueva del panel basta agregar su modulo aqui y decorarla con @module_required.
"""

NO_ACCESS = ''
VIEW = 'view'
MANAGE = 'manage'

LEVEL_RANK = {NO_ACCESS: 0, VIEW: 1, MANAGE: 2}
LEVEL_LABELS = {NO_ACCESS: 'Sin acceso', VIEW: 'Solo ver', MANAGE: 'Gestionar'}

# (clave, nombre, icono, endpoint de entrada, solo_lectura)
# solo_lectura: el modulo no tiene acciones de escritura, asi que no admite 'manage'.
MODULE_GROUPS = [
    ('General', [
        ('dashboard', 'Dashboard', 'fas fa-chart-pie', 'admin_dashboard', True),
    ]),
    ('Catálogo', [
        ('productos', 'Productos', 'fas fa-box', 'admin_products', False),
        ('categorias', 'Categorías', 'fas fa-tags', 'admin_categories', False),
        ('subcategorias', 'Sub Categorías', 'fas fa-sitemap', 'admin_subcategories', False),
        ('marcas', 'Marcas', 'fas fa-building', 'admin_brands', False),
        ('colores', 'Colores', 'fas fa-palette', 'admin_colors', False),
        ('presentaciones', 'Presentaciones', 'fas fa-box-open', 'admin_presentations', False),
    ]),
    ('Ventas', [
        ('solicitudes', 'Solicitudes', 'fas fa-file-invoice', 'admin_quotes', False),
    ]),
    ('Contenido', [
        ('banners', 'Banners', 'fas fa-image', 'admin_banners', False),
        ('ofertas', 'Ofertas', 'fas fa-percent', 'admin_offers', False),
        ('galeria', 'Galería', 'fas fa-images', 'admin_gallery', False),
        ('ambientes', 'Ambientes', 'fas fa-paint-roller', 'admin_ambientes', False),
        ('blog', 'Blog', 'fas fa-blog', 'admin_blog', False),
    ]),
    ('Sistema', [
        ('configuracion', 'Configuración', 'fas fa-cog', 'admin_settings', False),
    ]),
]

MODULES = {
    key: {'key': key, 'label': label, 'icon': icon, 'endpoint': endpoint, 'view_only': view_only, 'group': group}
    for group, items in MODULE_GROUPS
    for key, label, icon, endpoint, view_only in items
}

# Plantillas de permisos para rellenar el formulario con un clic
_CATALOG = ['productos', 'categorias', 'subcategorias', 'marcas', 'colores', 'presentaciones']
_CONTENT = ['banners', 'ofertas', 'galeria', 'ambientes', 'blog']

PRESETS = [
    {'key': 'catalogo', 'label': 'Gestor de catálogo',
     'permissions': {'dashboard': VIEW, **{m: MANAGE for m in _CATALOG}, 'solicitudes': VIEW}},
    {'key': 'ventas', 'label': 'Ventas',
     'permissions': {'dashboard': VIEW, 'solicitudes': MANAGE, **{m: VIEW for m in _CATALOG}}},
    {'key': 'contenido', 'label': 'Contenido y marketing',
     'permissions': {'dashboard': VIEW, **{m: MANAGE for m in _CONTENT}}},
    {'key': 'lectura', 'label': 'Solo lectura',
     'permissions': {key: VIEW for key in MODULES if key != 'configuracion'}},
]


def clean_permissions(raw):
    """Deja solo modulos conocidos con un nivel valido; un modulo de solo lectura nunca pasa de 'view'."""
    cleaned = {}
    for key, level in (raw or {}).items():
        module = MODULES.get(key)
        if not module or level not in (VIEW, MANAGE):
            continue
        if module['view_only']:
            level = VIEW
        cleaned[key] = level
    return cleaned


def level_allows(granted, needed):
    return LEVEL_RANK.get(granted or NO_ACCESS, 0) >= LEVEL_RANK[needed]
