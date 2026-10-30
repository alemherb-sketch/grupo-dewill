import json
import re
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from permissions import MODULES, VIEW, clean_permissions, level_allows

db = SQLAlchemy()


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)   # acceso total + gestion de usuarios
    is_active = db.Column(db.Boolean, default=True)   # desactivado: no puede iniciar sesion
    permissions = db.Column(db.Text)                  # JSON {modulo: 'view'|'manage'}, ver permissions.py
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        return self.full_name or self.username

    def get_permissions(self):
        try:
            return clean_permissions(json.loads(self.permissions or '{}'))
        except (ValueError, AttributeError):
            return {}

    def set_permissions(self, permissions):
        self.permissions = json.dumps(clean_permissions(permissions))

    def level(self, module):
        """Nivel efectivo sobre un modulo: '', 'view' o 'manage'."""
        if not self.is_active or module not in MODULES:
            return ''
        if self.is_admin:
            return clean_permissions({module: 'manage'})[module]
        return self.get_permissions().get(module, '')

    def can(self, module, needed=VIEW):
        return level_allows(self.level(module), needed)

    def can_any(self, *modules):
        return any(self.can(m) for m in modules)

    def accessible_modules(self):
        return [m for key, m in MODULES.items() if self.can(key)]


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), default='fas fa-tag')
    order = db.Column(db.Integer, default=0)
    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('SubCategory', backref='category', lazy=True, cascade='all, delete-orphan')


class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    products = db.relationship('Product', backref='subcategory', lazy=True)


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(300))
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='brand', lazy=True)


product_presentations = db.Table('product_presentations',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    db.Column('presentation_id', db.Integer, db.ForeignKey('presentations.id', ondelete='CASCADE'), primary_key=True)
)


# En el Excel el codigo de fabrica del color va al final del nombre: 'AMARILLO LIMON #41'
COLOR_CODE_RE = re.compile(r'^(?P<name>\S.*?)\s*#\s*(?P<code>[\w./-]+)\s*$')


def split_color_code(text):
    """'AMARILLO LIMON #41' -> ('AMARILLO LIMON', '41'). Sin codigo devuelve (texto, None).
    El codigo es texto: '08' conserva el cero."""
    text = (text or '').strip()
    m = COLOR_CODE_RE.match(text)
    return (m.group('name'), m.group('code')) if m else (text, None)


def color_label(name, code=None):
    """El color tal como se muestra y se envia en la cotizacion: 'AMARILLO LIMON #41'."""
    return f'{name} #{code}' if code else name


class ProductPresentationColor(db.Model):
    """Links specific colors to a presentation of a product (from Excel import)."""
    __tablename__ = 'product_presentation_colors'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id', ondelete='CASCADE'), nullable=False)
    color_name = db.Column(db.String(200), nullable=False)
    hex_code = db.Column(db.String(10), default='#cccccc')
    color_code = db.Column(db.String(50))   # codigo de fabrica del color (el '41' de 'AMARILLO LIMON #41'); opcional
    __table_args__ = (db.UniqueConstraint('product_id', 'presentation_id', 'color_name'),)

    @property
    def label(self):
        return color_label(self.color_name, self.color_code)


class ProductVariantCode(db.Model):
    """Codigo (columna Codigo del Excel) de una variante de un producto: la presentacion y el color que elige el cliente.
    presentation_id NULL = fila sin presentacion; color_name '' = fila sin color."""
    __tablename__ = 'product_variant_codes'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id', ondelete='CASCADE'))
    color_name = db.Column(db.String(200), nullable=False, default='')
    code = db.Column(db.String(50), nullable=False)
    __table_args__ = (db.UniqueConstraint('product_id', 'presentation_id', 'color_name'),)


class ProductYield(db.Model):
    """Rendimiento de un producto: metros cuadrados que cubre UNA unidad de la presentacion y a cuantas manos
    ('un galon rinde 21 m2 a 2 manos'). presentation_id NULL = producto sin presentaciones (vale para su unidad)."""
    __tablename__ = 'product_yields'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentations.id', ondelete='CASCADE'))
    area_m2 = db.Column(db.Float, nullable=False)
    coats = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('product_id', 'presentation_id'),)


def find_yield(yields, presentation_id):
    """Rendimiento (ProductYield) de la presentacion elegida; presentation_id None = el de un producto sin presentaciones."""
    return next((y for y in yields if y.presentation_id == presentation_id), None)


def format_m2(value):
    """Metros cuadrados sin ceros de mas: 21.0 -> '21', 10.5 -> '10.5', 31.25 -> '31.25'."""
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def yield_label(area_m2, coats):
    """El rendimiento como se muestra y se envia en el pedido: '63 m² a 2 manos'."""
    return f"{format_m2(area_m2)} m² a {coats} {'mano' if coats == 1 else 'manos'}"


def find_variant_code(codes, presentation_id, color_name=''):
    """Codigo de la variante elegida entre los ProductVariantCode de un producto.
    Prueba la combinacion exacta y, si no existe, la mas general: (presentacion, color), (presentacion), (color), (producto)."""
    color = (color_name or '').strip().upper()
    index = {(c.presentation_id, (c.color_name or '').strip().upper()): c.code for c in codes}
    for key in ((presentation_id, color), (presentation_id, ''), (None, color), (None, '')):
        if key in index:
            return index[key]
    return None


class Presentation(db.Model):
    __tablename__ = 'presentations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    technical_description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    main_image = db.Column(db.String(300))
    pdf_url = db.Column(db.String(300))
    safety_sheet_url = db.Column(db.String(300))
    catalog_url = db.Column(db.String(300))
    video_url = db.Column(db.String(300))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    presentations = db.relationship('Presentation', secondary=product_presentations, lazy='subquery',
                                   backref=db.backref('products', lazy=True))
    images = db.relationship('ProductImage', backref='product', lazy=True,
                             cascade='all, delete-orphan', order_by='ProductImage.order')
    specs = db.relationship('ProductSpec', backref='product', lazy=True,
                            cascade='all, delete-orphan')
    quote_items = db.relationship('QuoteItem', backref='product', lazy=True, cascade='all, delete-orphan')
    presentation_colors = db.relationship('ProductPresentationColor', backref='product_rel', lazy=True, cascade='all, delete-orphan')
    variant_codes = db.relationship('ProductVariantCode', backref='product_rel', lazy=True, cascade='all, delete-orphan')
    yields = db.relationship('ProductYield', backref='product_rel', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'category': self.category.name if self.category else '',
            'category_slug': self.category.slug if self.category else '',
            'subcategory': self.subcategory.name if self.subcategory else '',
            'subcategory_slug': self.subcategory.slug if self.subcategory else '',
            'brand': self.brand.name if self.brand else '',
            'main_image': self.main_image or '',
            'is_featured': self.is_featured,
            'presentations': [p.name for p in self.presentations]
        }


class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)


class ProductSpec(db.Model):
    __tablename__ = 'product_specs'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(300), nullable=False)


class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200))
    client_document = db.Column(db.String(20))   # DNI (8 digitos) o RUC (11 digitos)
    client_company = db.Column(db.String(200))
    client_email = db.Column(db.String(200))     # opcional
    client_phone = db.Column(db.String(50))      # celular
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pendiente')  # pendiente, en_proceso, respondida
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('QuoteItem', backref='quote', lazy=True,
                            cascade='all, delete-orphan')


class QuoteItem(db.Model):
    __tablename__ = 'quote_items'
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote_requests.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    color = db.Column(db.String(100))
    presentation = db.Column(db.String(100))
    code = db.Column(db.String(50))   # Codigo (Excel) de la presentacion y el color elegidos; NULL si el producto no los tiene cargados
    # Rendimiento total de lo pedido (m2 de la presentacion x cantidad) y a cuantas manos; NULL si no tiene rendimiento
    yield_m2 = db.Column(db.Float)
    yield_coats = db.Column(db.Integer)

    @property
    def yield_text(self):
        return yield_label(self.yield_m2, self.yield_coats) if self.yield_m2 and self.yield_coats else ''


class PaintColor(db.Model):
    __tablename__ = 'paint_colors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hex_code = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.Text)
    image_url = db.Column(db.String(300), nullable=False)
    cta_text = db.Column(db.String(100))
    cta_link = db.Column(db.String(300))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class Offer(db.Model):
    """Banner de la seccion OFERTAS de la portada, debajo de Marcas: uno debajo de otro (se administra en Admin > Ofertas)."""
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))                 # texto alternativo de la imagen y nombre en el panel
    image_url = db.Column(db.String(300), nullable=False)
    link_url = db.Column(db.String(300))              # opcional: a donde lleva el banner al hacer clic
    order = db.Column(db.Integer, default=0)          # menor numero primero
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PageBanner(db.Model):
    """Banner de cabecera de una pagina interna (ver site_pages.py).
    Una fila guarda solo lo que se personalizo: un valor NULL usa el de fabrica; sin fila, todo es de fabrica."""
    __tablename__ = 'page_banners'
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(30), unique=True, nullable=False)
    image_url = db.Column(db.String(300))
    image2_url = db.Column(db.String(300))   # segunda imagen (solo la pagina Ambientes usa dos)
    badge = db.Column(db.String(100))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.Text)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)


class GalleryCategory(db.Model):
    __tablename__ = 'gallery_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    images = db.relationship('GalleryImage', backref='gallery_category', lazy=True,
                             cascade='all, delete-orphan', order_by='GalleryImage.order')


class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('gallery_categories.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    color_code = db.Column(db.String(7))
    order = db.Column(db.Integer, default=0)



class AmbientCategory(db.Model):
    __tablename__ = 'ambient_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), default='room')  # 'color' or 'room'
    cover_image = db.Column(db.String(300))
    description = db.Column(db.Text)
    colors = db.Column(db.String(200)) # comma-separated list of colors e.g. '#f2ebdd,#d7cbb6'
    area = db.Column(db.String(50), default='interior') # 'interior' or 'exterior'
    order = db.Column(db.Integer, default=0)
    images = db.relationship('AmbientImage', backref='category', lazy=True,
                             cascade='all, delete-orphan', order_by='AmbientImage.order')


class AmbientImage(db.Model):
    __tablename__ = 'ambient_images'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('ambient_categories.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)


class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fas fa-tag')
    posts = db.relationship('BlogPost', backref='blog_category', lazy=True)


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)
    cover_image = db.Column(db.String(300))
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    read_time = db.Column(db.Integer, default=5)  # minutes
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SiteConfig(db.Model):
    __tablename__ = 'site_config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

    @staticmethod
    def get(key, default=''):
        config = SiteConfig.query.filter_by(key=key).first()
        return config.value if config else default

    @staticmethod
    def set(key, value):
        config = SiteConfig.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = SiteConfig(key=key, value=value)
            db.session.add(config)
        db.session.commit()
