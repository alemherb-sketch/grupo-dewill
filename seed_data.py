"""Seed the database with initial data from the original static site."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import current_app
from models import db, AdminUser, Category, Brand, Product, ProductSpec, Banner, SiteConfig

CATEGORIES = [
    {'name': 'Pinturas', 'slug': 'pinturas', 'icon': 'fas fa-fill-drip', 'order': 1},
    {'name': 'Tráfico', 'slug': 'trafico', 'icon': 'fas fa-road', 'order': 2},
    {'name': 'Epóxicos', 'slug': 'epoxicos', 'icon': 'fas fa-shield-halved', 'order': 3},
    {'name': 'Solventes', 'slug': 'solventes', 'icon': 'fas fa-flask', 'order': 4},
    {'name': 'Accesorios', 'slug': 'accesorios', 'icon': 'fas fa-paint-roller', 'order': 5},
]

BRANDS = [
    {'name': 'CPP', 'slug': 'cpp'},
    {'name': 'Anypsa', 'slug': 'anypsa'},
    {'name': 'Vencedor', 'slug': 'vencedor'},
    {'name': 'Maestro', 'slug': 'maestro'},
    {'name': 'Tamsa', 'slug': 'tamsa'},
    {'name': 'Bonn', 'slug': 'bonn'},
    {'name': 'JET', 'slug': 'jet'},
    {'name': 'A3m', 'slug': 'a3m'},
    {'name': 'Expert', 'slug': 'expert'},
    {'name': 'CMC', 'slug': 'cmc'},
    {'name': 'Toretto', 'slug': 'toretto'},
    {'name': 'Soprin', 'slug': 'soprin'},
    {'name': 'Goya', 'slug': 'goya'},
    {'name': 'Atlas', 'slug': 'atlas'},
    {'name': 'Tumi', 'slug': 'tumi'},
    {'name': 'ABRO', 'slug': 'abro'},
    {'name': 'C&A', 'slug': 'cya'},
]

PRODUCTS = [
    {'name':'Sellador CPP','cat':'pinturas','brand':'cpp','desc':'Sellador acrílico para interiores y exteriores. Base ideal para acabados de calidad.','img':'assets/product_paint.png','specs':[('Tipo','Sellador Acrílico'),('Aplicación','Interior/Exterior'),('Rendimiento','40-50 m²/gal')],'featured':True},
    {'name':'Temple Fino Sinolit CPP','cat':'pinturas','brand':'cpp','desc':'Temple fino de alta calidad para acabados interiores lisos y uniformes.','img':'assets/product_paint.png','specs':[('Tipo','Temple Fino'),('Aplicación','Interior'),('Acabado','Mate')]},
    {'name':'Temple Majestad','cat':'pinturas','brand':'cpp','desc':'Temple económico de buena cobertura para proyectos de gran escala.','img':'assets/product_paint.png','specs':[('Tipo','Temple Estándar'),('Aplicación','Interior'),('Presentación','25 kg')]},
    {'name':'Satinado CPP','cat':'pinturas','brand':'cpp','desc':'Pintura látex satinada lavable de excelente resistencia al frote húmedo.','img':'assets/product_paint.png','specs':[('Tipo','Látex Satinado'),('Acabado','Satinado'),('Resistencia','Alta al lavado')],'featured':True},
    {'name':'Duralatex CPP','cat':'pinturas','brand':'cpp','desc':'Látex acrílico de alta durabilidad para interiores y exteriores.','img':'assets/product_paint.png','specs':[('Tipo','Látex Acrílico'),('Aplicación','Interior/Exterior'),('Rendimiento','45-55 m²/gal')]},
    {'name':'Latex Pato CPP','cat':'pinturas','brand':'cpp','desc':'Pintura látex económica de buena calidad.','img':'assets/product_paint.png','specs':[('Tipo','Látex Económico'),('Aplicación','Interior/Exterior'),('Acabado','Mate')]},
    {'name':'Supermate Vencedor','cat':'pinturas','brand':'vencedor','desc':'Pintura mate premium de máxima cobertura y excelente rendimiento.','img':'assets/product_paint.png','specs':[('Tipo','Látex Mate'),('Acabado','Mate Premium'),('Rendimiento','50-60 m²/gal')],'featured':True},
    {'name':'Masterlast Anypsa','cat':'pinturas','brand':'anypsa','desc':'Pintura acrílica de alto rendimiento con tecnología anti-hongos.','img':'assets/product_paint.png','specs':[('Tipo','Acrílico Anti-hongos'),('Aplicación','Interior/Exterior'),('Tecnología','Antibacterial')],'featured':True},
    {'name':'X3 Gloss Anypsa (Esmalte)','cat':'pinturas','brand':'anypsa','desc':'Esmalte sintético de alto brillo para superficies metálicas y madera.','img':'assets/product_paint.png','specs':[('Tipo','Esmalte Sintético'),('Acabado','Alto Brillo'),('Superficies','Metal/Madera')]},
    {'name':'Pintura para Pizarra Anypsa','cat':'pinturas','brand':'anypsa','desc':'Pintura especial que convierte cualquier superficie en pizarra.','img':'assets/product_paint.png','specs':[('Tipo','Pintura Especial'),('Uso','Pizarras'),('Colores','Negro/Verde')]},
    {'name':'Pintura Fluorescente Anypsa','cat':'pinturas','brand':'anypsa','desc':'Pintura de alta visibilidad con pigmentos fluorescentes.','img':'assets/product_paint.png','specs':[('Tipo','Fluorescente'),('Uso','Señalización/Decoración'),('Visibilidad','Alta')]},
    {'name':'Pintura para Tráfico Maestro','cat':'trafico','brand':'maestro','desc':'Pintura acrílica para demarcación vial de alta resistencia.','img':'assets/product_traffic.png','specs':[('Tipo','Acrílica de Tráfico'),('Colores','Amarillo/Blanco'),('Norma','MTC')],'featured':True},
    {'name':'Pintura para Tráfico Tamsa','cat':'trafico','brand':'tamsa','desc':'Pintura de señalización vial de secado rápido.','img':'assets/product_traffic.png','specs':[('Tipo','Tráfico Rápido Secado'),('Aplicación','Vial'),('Durabilidad','Alta')]},
    {'name':'Juego Epóxico Bonn Zincromato','cat':'epoxicos','brand':'bonn','desc':'Sistema epóxico anticorrosivo de dos componentes.','img':'assets/product_epoxy.png','specs':[('Tipo','Epóxico 2 Componentes'),('Uso','Anticorrosivo'),('Base','Zincromato')],'featured':True},
    {'name':'Juego Epóxico JET POX 2000','cat':'epoxicos','brand':'jet','desc':'Recubrimiento epóxico de alto espesor para ambientes industriales.','img':'assets/product_epoxy.png','specs':[('Tipo','Epóxico Alto Espesor'),('Uso','Industrial/Marino'),('Resistencia','Química')]},
    {'name':'Juego Epóxico JET 70 MP','cat':'epoxicos','brand':'jet','desc':'Epóxico multipropósito de alta performance para pisos industriales.','img':'assets/product_epoxy.png','specs':[('Tipo','Epóxico Multipropósito'),('Uso','Pisos/Estructuras'),('Acabado','Semi-brillante')]},
    {'name':'Juego Epóxico Anticorrosivo JET 62 ZP','cat':'epoxicos','brand':'jet','desc':'Primer epóxico rico en zinc para máxima protección anticorrosiva.','img':'assets/product_epoxy.png','specs':[('Tipo','Primer Epóxico'),('Base','Rico en Zinc'),('Protección','Catódica')]},
    {'name':'Juego Epóxico Poliuretano JETHANE 500','cat':'epoxicos','brand':'jet','desc':'Acabado poliuretano de alto brillo y excelente retención de color.','img':'assets/product_epoxy.png','specs':[('Tipo','Poliuretano'),('Acabado','Alto Brillo'),('Resistencia','UV')]},
    {'name':'Juego Epóxico Poliuretano JETHANE 650 HS','cat':'epoxicos','brand':'jet','desc':'Poliuretano de altos sólidos para acabados de máxima durabilidad.','img':'assets/product_epoxy.png','specs':[('Tipo','Poliuretano HS'),('Sólidos','Alto contenido'),('Uso','Industrial pesado')]},
    {'name':'Barniz Epóxico Alta Duración Anypsa','cat':'epoxicos','brand':'anypsa','desc':'Barniz epóxico transparente de dos componentes para pisos.','img':'assets/product_epoxy.png','specs':[('Tipo','Barniz Epóxico'),('Acabado','Transparente'),('Uso','Pisos de concreto')]},
    {'name':'Thinner Automotriz A3m','cat':'solventes','brand':'a3m','desc':'Thinner de alta pureza para dilución de pinturas automotrices.','img':'assets/product_thinner.png','specs':[('Tipo','Automotriz'),('Pureza','Alta'),('Uso','Pinturas automotrices')]},
    {'name':'Thinner Estándar Expert','cat':'solventes','brand':'expert','desc':'Solvente de uso general para dilución de esmaltes.','img':'assets/product_thinner.png','specs':[('Tipo','Estándar'),('Uso','General'),('Compatibilidad','Esmaltes/Sintéticos')]},
    {'name':'Thinner Acrílico Expert','cat':'solventes','brand':'expert','desc':'Diluyente especializado para pinturas acrílicas.','img':'assets/product_thinner.png','specs':[('Tipo','Acrílico'),('Uso','Automotriz/Industrial'),('Evaporación','Media')]},
    {'name':'Thinner Acrílico MS1 CMC','cat':'solventes','brand':'cmc','desc':'Thinner acrílico de secado medio para sistemas base-barniz.','img':'assets/product_thinner.png','specs':[('Tipo','Acrílico MS1'),('Secado','Medio'),('Sistema','Base-Barniz')]},
    {'name':'Thinner Acrílico Premium CPP','cat':'solventes','brand':'cpp','desc':'Solvente acrílico premium de alta calidad.','img':'assets/product_thinner.png','specs':[('Tipo','Acrílico Premium'),('Calidad','Premium'),('Poder Solvente','Alto')]},
    {'name':'Maestrazo Thinner Acrílico','cat':'solventes','brand':'maestro','desc':'Thinner acrílico económico de buen rendimiento.','img':'assets/product_thinner.png','specs':[('Tipo','Acrílico Económico'),('Uso','Alto Volumen'),('Presentación','Galón/Cilindro')]},
    {'name':'Rodillo Peluche Blanco Toretto','cat':'accesorios','brand':'toretto','desc':'Rodillo de peluche blanco profesional para acabados finos.','img':'assets/product_accessories.png','specs':[('Tipo','Peluche Blanco'),('Uso','Interiores'),('Acabado','Fino')]},
    {'name':'Rodillo Antigoteo B y P Soprin','cat':'accesorios','brand':'soprin','desc':'Rodillo con tecnología anti-goteo para trabajo limpio.','img':'assets/product_accessories.png','specs':[('Tipo','Antigoteo'),('Tecnología','Anti-salpicaduras'),('Marca','Soprin')]},
    {'name':'Rodillo Peluche Carnero Toretto','cat':'accesorios','brand':'toretto','desc':'Rodillo de fibra de carnero para superficies rugosas.','img':'assets/product_accessories.png','specs':[('Tipo','Peluche Carnero'),('Uso','Superficies rugosas'),('Durabilidad','Alta')]},
    {'name':'Rodillo Espuma Profesional Goya','cat':'accesorios','brand':'goya','desc':'Rodillo de espuma de alta densidad para acabados ultralisos.','img':'assets/product_accessories.png','specs':[('Tipo','Espuma HD'),('Acabado','Ultra liso'),('Uso','Esmaltes')]},
    {'name':'Espátula Multiusos ATLAS 4"','cat':'accesorios','brand':'atlas','desc':'Espátula profesional de acero inoxidable.','img':'assets/product_accessories.png','specs':[('Tipo','Multiusos'),('Material','Acero Inoxidable'),('Tamaño','4 pulgadas')]},
    {'name':'Espátula Atlas Angular','cat':'accesorios','brand':'atlas','desc':'Espátula angular de precisión para esquinas y bordes.','img':'assets/product_accessories.png','specs':[('Tipo','Angular'),('Uso','Esquinas y bordes'),('Material','Acero')]},
    {'name':'Brocha Tumi Nylon','cat':'accesorios','brand':'tumi','desc':'Brocha profesional de filamentos de nylon.','img':'assets/product_accessories.png','specs':[('Tipo','Brocha Profesional'),('Filamento','Nylon'),('Uso','Universal')]},
    {'name':'Spray ABRO Colores Metálicos Premium','cat':'accesorios','brand':'abro','desc':'Pintura en spray con acabado metálico premium.','img':'assets/product_accessories.png','specs':[('Tipo','Spray Metálico'),('Acabado','Premium'),('Marca','ABRO')]},
    {'name':'Spray ABRO Colores Fluorescentes','cat':'accesorios','brand':'abro','desc':'Spray de alta visibilidad con colores fluorescentes.','img':'assets/product_accessories.png','specs':[('Tipo','Spray Fluorescente'),('Uso','Señalización'),('Marca','ABRO')]},
    {'name':'Spray C&A Colores','cat':'accesorios','brand':'cya','desc':'Spray multicolor de secado rápido.','img':'assets/product_accessories.png','specs':[('Tipo','Spray Multicolor'),('Secado','Rápido'),('Uso','Pintura/Decoración')]},
]

SITE_DEFAULTS = {
    'phone': '+51 977 585 654',
    'whatsapp': '51983461199',
    'whatsapp_2': '51977585654',
    'email': 'ventas@grupodewill.com',
    'address': 'Lima, Perú',
    'facebook': '#',
    'instagram': '#',
    'hero_title': 'Soluciones Industriales de Alto Rendimiento',
    'hero_subtitle': 'Pinturas, recubrimientos, solventes y accesorios de calidad premium para potenciar tus proyectos.',
    'hero_badge': 'Proveedor Industrial Certificado',
    'meta_title': 'Grupo Dewill | Suministros Industriales de Calidad',
    'meta_description': 'Grupo Dewill - Distribuidor líder de pinturas, recubrimientos epóxicos, solventes y accesorios para pintura en Perú.',
}

def seed(app=None):
    if app is None:
        from flask import current_app
        app = current_app
    with app.app_context():
        db.create_all()

        # Admin user
        if not AdminUser.query.first():
            admin = AdminUser(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("[OK] Admin user created (admin / admin123)")
        
        # Categories
        cat_map = {}
        for c in CATEGORIES:
            existing = Category.query.filter_by(slug=c['slug']).first()
            if not existing:
                existing = Category(**c)
                db.session.add(existing)
                db.session.flush()
            cat_map[c['slug']] = existing.id
            
        # Brands
        brand_map = {}
        for b in BRANDS:
            existing = Brand.query.filter_by(slug=b['slug']).first()
            if not existing:
                existing = Brand(**b)
                db.session.add(existing)
                db.session.flush()
            brand_map[b['slug']] = existing.id
            
        # Products
        if Product.query.count() == 0:
            for i, p in enumerate(PRODUCTS):
                product = Product(
                    name=p['name'], sku=f"GD-{i+1:04d}",
                    description=p['desc'], main_image=p['img'],
                    category_id=cat_map.get(p['cat']),
                    brand_id=brand_map.get(p.get('brand')),
                    is_featured=p.get('featured', False), is_active=True
                )
                db.session.add(product)
                db.session.flush()
                for key, val in p.get('specs', []):
                    db.session.add(ProductSpec(product_id=product.id, key=key, value=val))
            print(f"[OK] {len(PRODUCTS)} products seeded")
            
        # Default banner
        if Banner.query.count() == 0:
            db.session.add(Banner(title='Soluciones Industriales de Alto Rendimiento',
                subtitle='Más de 500 productos disponibles', image_url='assets/hero_bg.png',
                cta_text='Ver Catálogo', cta_link='/productos', order=1, is_active=True))
            print("[OK] Default banner created")
            
        # Site config
        for key, val in SITE_DEFAULTS.items():
            if not SiteConfig.query.filter_by(key=key).first():
                db.session.add(SiteConfig(key=key, value=val))
                
        db.session.commit()
        print("[OK] Seed complete!")

if __name__ == '__main__':
    from app import app
    seed(app)
