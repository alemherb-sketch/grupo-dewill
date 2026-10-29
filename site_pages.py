"""Paginas publicas del sitio: cuales se pueden deshabilitar y como se configura el banner de cada una.

Para que una pagina aparezca en Admin > Configuracion (habilitar / deshabilitar) y en Admin > Banners basta
agregarla a PAGES. Las claves (key) se guardan en la base de datos (SiteConfig 'disabled_pages' y
PageBanner.page): no cambiarlas una vez publicadas.

Banner de cada pagina: PageBanner guarda solo lo que el administrador personalizo; un valor NULL significa
"usar el de fabrica" (el que se declara aqui), asi el sitio se ve igual hasta que alguien lo cambie.
En los textos, *asteriscos* resaltan una palabra con el color de la marca y Enter hace un salto de linea.
"""
import re
from types import SimpleNamespace

# 'endpoints': rutas publicas que pertenecen a la pagina; si la pagina se deshabilita, todas dejan de estar disponibles.
# 'banner': imagenes y textos editables de su cabecera (ver BANNER_TEXT_FIELDS); 'hideable': False impide ocultarla.
PAGES = [
    {'key': 'nosotros', 'label': 'Nosotros', 'icon': 'fas fa-users', 'endpoint': 'nosotros',
     'endpoints': ('nosotros',),
     'banner': {
         'hideable': False,   # la cabecera de Nosotros es parte del contenido de la pagina
         'images': [
             {'key': 'image', 'label': 'Foto del local', 'default': 'assets/local_foto.jpeg',
              'hint': 'Foto vertical, por ejemplo 1160 × 1356 px.'},
         ],
         'texts': {
             'badge': 'CONÓCENOS',
             'title': 'Sobre\n*Nosotros*',
             'subtitle': 'Más de 20 años construyendo *confianza* en el Perú',
             'description': 'Somos aliados estratégicos en pinturas, herramientas, adhesivos y soluciones '
                            'para la construcción, industria y hogar.',
         },
         'text_labels': {'subtitle': 'Frase destacada'},
     }},
    {'key': 'productos', 'label': 'Productos', 'icon': 'fas fa-box', 'endpoint': 'productos',
     # El catalogo incluye el detalle de producto, el buscador, los colores y el envio de cotizaciones
     'endpoints': ('productos', 'producto_detalle', 'api_search', 'api_product_colors', 'api_product_options',
                   'api_cotizacion'),
     'banner': {
         'images': [
             {'key': 'image', 'label': 'Imagen de fondo', 'default': 'assets/banner_productos_new.png',
              'hint': 'Imagen horizontal de 2170 × 725 px (proporción 3:1).'},
         ],
         'texts': {
             'title': 'Nuestros *Productos*',
             'subtitle': 'Pinturas de alta calidad para cada necesidad.',
         },
     }},
    {'key': 'galeria', 'label': 'Galería', 'icon': 'fas fa-images', 'endpoint': 'galeria',
     'endpoints': ('galeria',),
     'banner': {
         'images': [
             {'key': 'image', 'label': 'Imagen del banner', 'default': 'assets/banner_comunidad.png',
              'hint': 'Imagen horizontal de 2170 × 725 px (proporción 3:1). El texto del banner va dentro de la imagen.'},
         ],
         'texts': {},
     }},
    {'key': 'ambientes', 'label': 'Ambientes', 'icon': 'fas fa-paint-roller', 'endpoint': 'galeria_ambientes',
     'endpoints': ('galeria_ambientes', 'api_ambiente'),
     'banner': {
         'images': [
             {'key': 'image', 'label': 'Imagen izquierda', 'default': 'assets/ambiente_sala.png',
              'hint': 'Imagen cuadrada, por ejemplo 1024 × 1024 px.'},
             {'key': 'image2', 'label': 'Imagen derecha', 'default': 'assets/ambiente_dormitorio.png',
              'hint': 'Imagen cuadrada, por ejemplo 1024 × 1024 px.'},
         ],
         'texts': {
             'badge': 'INSPIRACIÓN REAL',
             'title': 'Galería de\n*Ambientes*',
             'subtitle': 'Visualiza la armonía de colores en espacios reales\ny elige el estilo que mejor se adapte a ti.',
         },
     }},
    {'key': 'blog', 'label': 'Blog', 'icon': 'fas fa-blog', 'endpoint': 'blog',
     'endpoints': ('blog', 'blog_post'),
     'banner': {
         'images': [
             {'key': 'image', 'label': 'Imagen de fondo', 'default': 'assets/blog_bg.png',
              'hint': 'Imagen horizontal de 2170 × 725 px (proporción 3:1).'},
         ],
         'texts': {
             'badge': 'BLOG',
             'title': 'Consejos, ideas y *soluciones*',
             'subtitle': 'Encuentra recomendaciones prácticas, inspiración y todo lo que necesitas saber '
                         'para lograr los mejores acabados.',
         },
     }},
    {'key': 'contacto', 'label': 'Contacto', 'icon': 'fas fa-envelope', 'endpoint': 'contacto',
     'endpoints': ('contacto',),
     'banner': {
         'images': [
             {'key': 'image', 'label': 'Imagen del banner', 'default': 'assets/banner_contacto.png',
              'hint': 'Imagen horizontal de 1922 × 818 px. El texto del banner va dentro de la imagen.'},
         ],
         'texts': {},
     }},
]

PAGES_BY_KEY = {page['key']: page for page in PAGES}
PAGE_BY_ENDPOINT = {endpoint: page['key'] for page in PAGES for endpoint in page['endpoints']}

# Campos de texto de un banner: clave en PageBanner -> (etiqueta, filas del campo, longitud maxima)
BANNER_TEXT_FIELDS = {
    'badge': ('Etiqueta superior', 1, 100),
    'title': ('Título', 2, 200),
    'subtitle': ('Subtítulo', 3, 600),
    'description': ('Descripción', 3, 600),
}

DISABLED_PAGES_KEY = 'disabled_pages'


def disabled_pages(config):
    """Claves de las paginas deshabilitadas, segun la configuracion del sitio (dict de SiteConfig)."""
    raw = (config or {}).get(DISABLED_PAGES_KEY) or ''
    return {key for key in (part.strip() for part in raw.split(',')) if key in PAGES_BY_KEY}


def serialize_disabled_pages(keys):
    """Valor a guardar en SiteConfig, en el orden del menu y sin claves desconocidas."""
    return ','.join(page['key'] for page in PAGES if page['key'] in set(keys))


def banner_text_fields(page_key):
    """Campos de texto editables del banner de una pagina, en orden: [{key, label, rows, maxlength, default}]."""
    banner = PAGES_BY_KEY[page_key]['banner']
    labels = banner.get('text_labels', {})
    return [{'key': key, 'label': labels.get(key, BANNER_TEXT_FIELDS[key][0]), 'rows': BANNER_TEXT_FIELDS[key][1],
             'maxlength': BANNER_TEXT_FIELDS[key][2], 'default': default}
            for key, default in banner['texts'].items()]


def resolve_banner(page_key, row=None):
    """Banner efectivo de una pagina: lo personalizado en `row` (PageBanner) o, si falta, el de fabrica."""
    banner = PAGES_BY_KEY[page_key]['banner']
    values = {'active': not banner.get('hideable', True) or row is None or row.is_active is not False}
    for image in banner['images']:
        custom = getattr(row, image['key'] + '_url', None) if row is not None else None
        values[image['key']] = custom or image['default']
    for field in BANNER_TEXT_FIELDS:
        custom = getattr(row, field, None) if row is not None else None
        values[field] = custom if custom is not None else banner['texts'].get(field, '')
    values.setdefault('image2', '')
    values['title_plain'] = plain_text(values['title'])
    return SimpleNamespace(**values)


EMPHASIS_RE = re.compile(r'\*([^*\n]+)\*')


def plain_text(value):
    """Texto de un banner sin marcas (para atributos alt y titulos)."""
    return EMPHASIS_RE.sub(r'\1', value or '').replace('\n', ' ').strip()
