from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fas fa-tag')
    order = db.Column(db.Integer, default=0)
    products = db.relationship('Product', backref='category', lazy=True)


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(300))
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='brand', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    technical_description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    main_image = db.Column(db.String(300))
    pdf_url = db.Column(db.String(300))
    video_url = db.Column(db.String(300))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('ProductImage', backref='product', lazy=True,
                             cascade='all, delete-orphan', order_by='ProductImage.order')
    specs = db.relationship('ProductSpec', backref='product', lazy=True,
                            cascade='all, delete-orphan')
    quote_items = db.relationship('QuoteItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'category': self.category.name if self.category else '',
            'category_slug': self.category.slug if self.category else '',
            'brand': self.brand.name if self.brand else '',
            'main_image': self.main_image or '',
            'is_featured': self.is_featured,
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
    client_company = db.Column(db.String(200))
    client_email = db.Column(db.String(200))
    client_phone = db.Column(db.String(50))
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
    order = db.Column(db.Integer, default=0)
    images = db.relationship('AmbientImage', backref='category', lazy=True,
                             cascade='all, delete-orphan', order_by='AmbientImage.order')


class AmbientImage(db.Model):
    __tablename__ = 'ambient_images'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('ambient_categories.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)


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
