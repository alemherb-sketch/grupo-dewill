import os
import re
import unicodedata
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from config import Config
from models import db, AdminUser, Category, Brand, Product, ProductImage, ProductSpec
from models import QuoteRequest, QuoteItem, Banner, GalleryCategory, GalleryImage, AmbientCategory, AmbientImage, SiteConfig, PaintColor
import time
import threading
import resend
from seed_data import seed as seed_database

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()
    # Asegurar que existe al menos un admin
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

if app.config.get('RESEND_API_KEY'):
    resend.api_key = app.config['RESEND_API_KEY']

def send_async_email(app, msg_data):
    with app.app_context():
        try:
            # Try Resend first if configured
            if app.config.get('RESEND_API_KEY'):
                resend.Emails.send({
                    "from": f"Grupo Dewill <onboarding@resend.dev>", # Update this once domain is verified
                    "to": msg_data['recipients'],
                    "subject": msg_data['subject'],
                    "text": msg_data['body']
                })
                print("Email sent via Resend API")
            else:
                # Fallback to Flask-Mail
                msg = Message(
                    msg_data['subject'],
                    recipients=msg_data['recipients'],
                    body=msg_data['body']
                )
                mail.send(msg)
                print("Email sent via SMTP")
        except Exception as e:
            print(f"Async email failed: {e}")

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_upload(file, subfolder=''):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"
        folder = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        return f"uploads/{subfolder}/{filename}" if subfolder else f"uploads/{filename}"
    return None

def get_site_config():
    configs = SiteConfig.query.all()
    return {c.key: c.value for c in configs}

@app.context_processor
def inject_site_config():
    return {'site': get_site_config()}

def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

# ==================== PUBLIC ====================

@app.route('/')
def index():
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.order).all()
    featured = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = Category.query.order_by(Category.order).all()
    brands = Brand.query.all()
    return render_template('index.html', banners=banners, featured_products=featured,
                           categories=categories, brands=brands)

@app.route('/productos')
def productos():
    categories = Category.query.order_by(Category.order).all()
    brands = Brand.query.order_by(Brand.name).all()
    cat_slug = request.args.get('cat', '')
    brand_slug = request.args.get('marca', '')
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    query = Product.query.filter_by(is_active=True)
    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if brand_slug:
        brand = Brand.query.filter_by(slug=brand_slug).first()
        if brand:
            query = query.filter_by(brand_id=brand.id)
    if q:
        search_term = ''.join(['_' if c.lower() in 'aeiouáéíóú' else c for c in q])
        query = query.filter(db.or_(Product.name.ilike(f'%{search_term}%'), Product.description.ilike(f'%{search_term}%')))
    prods = query.order_by(Product.name).paginate(page=page, per_page=12, error_out=False)
    return render_template('productos.html', products=prods, categories=categories, brands=brands,
                           current_cat=cat_slug, current_brand=brand_slug, search_query=q)

@app.route('/api/productos/search')
def api_search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    search_term = ''.join(['_' if c.lower() in 'aeiouáéíóú' else c for c in q])
    results = Product.query.filter(Product.is_active == True,
        db.or_(Product.name.ilike(f'%{search_term}%'), Product.description.ilike(f'%{search_term}%'))).limit(8).all()
    return jsonify([p.to_dict() for p in results])

@app.route('/producto/<int:product_id>')
def producto_detalle(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(Product.category_id == product.category_id,
        Product.id != product.id, Product.is_active == True).limit(4).all()
    paint_colors = []
    if product.category and 'pintura' in product.category.name.lower():
        paint_colors = PaintColor.query.filter_by(is_active=True).all()
    return render_template('producto_detalle.html', product=product, related=related, paint_colors=paint_colors)

@app.route('/api/cotizacion', methods=['POST'])
def api_cotizacion():
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({'error': 'No hay productos'}), 400
    quote = QuoteRequest(client_name=data.get('name',''), client_company=data.get('company',''),
        client_email=data.get('email',''), client_phone=data.get('phone',''), message=data.get('message',''))
    db.session.add(quote)
    db.session.flush()
    for item in data['items']:
        db.session.add(QuoteItem(quote_id=quote.id, product_id=item['product_id'], quantity=item.get('quantity',1), color=item.get('color')))
    db.session.commit()
    try:
        # Obtener configuración de correo
        notify = SiteConfig.get('notify_email', app.config.get('MAIL_NOTIFY_TO'))
        if notify and app.config.get('MAIL_USERNAME'):
            # Construir cuerpo detallado
            items_text = ""
            for item in data['items']:
                prod = Product.query.get(item['product_id'])
                if prod:
                    color_info = f" - Color: {item.get('color')}" if item.get('color') else ""
                    items_text += f"- {prod.name} (SKU: {prod.sku or 'N/A'}){color_info} x {item.get('quantity', 1)}\n"
            
            body = (
                f"Nueva Solicitud de Cotización #{quote.id}\n"
                f"----------------------------------------\n"
                f"CLIENTE:\n"
                f"Nombre: {quote.client_name}\n"
                f"Empresa: {quote.client_company or 'No especificada'}\n"
                f"Email: {quote.client_email}\n"
                f"Teléfono: {quote.client_phone}\n\n"
                f"MENSAJE:\n{quote.message or 'Sin mensaje'}\n\n"
                f"PRODUCTOS:\n{items_text}\n"
                f"----------------------------------------\n"
                f"Ver en el panel: {url_for('admin_quote_detail', qid=quote.id, _external=True)}"
            )
            
            msg_data = {
                'subject': f'Nueva Solicitud de Cotización #{quote.id}',
                'recipients': [notify],
                'body': body
            }
            # Send in background to avoid hanging the UI
            threading.Thread(target=send_async_email, args=(app._get_current_object(), msg_data)).start()
    except Exception as e:
        print(f"Email failed: {e}")
    return jsonify({'success': True, 'quote_id': quote.id})

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/galeria')
def galeria():
    gallery_cats = GalleryCategory.query.all()
    current_cat = request.args.get('cat', '')
    if current_cat:
        gc = GalleryCategory.query.filter_by(slug=current_cat).first()
        images = gc.images if gc else []
    else:
        images = GalleryImage.query.order_by(GalleryImage.order).all()
    return render_template('galeria.html', gallery_categories=gallery_cats, images=images, current_cat=current_cat)

@app.route('/galeria/ambientes')
def galeria_ambientes():
    colors = AmbientCategory.query.filter_by(type='color').order_by(AmbientCategory.order).all()
    rooms = AmbientCategory.query.filter_by(type='room').order_by(AmbientCategory.order).all()
    return render_template('galeria_ambientes.html', colors=colors, rooms=rooms)

@app.route('/api/ambientes/<int:id>')
def api_ambiente(id):
    a = AmbientCategory.query.get_or_404(id)
    return jsonify({
        'id': a.id,
        'name': a.name,
        'images': [{'image_url': img.image_url} for img in a.images]
    })


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        user = AdminUser.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Credenciales inválidas', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/')
@login_required
def admin_dashboard():
    stats = {'total_products': Product.query.count(), 'active_products': Product.query.filter_by(is_active=True).count(),
        'total_quotes': QuoteRequest.query.count(), 'pending_quotes': QuoteRequest.query.filter_by(status='pendiente').count(),
        'categories': Category.query.count(), 'brands': Brand.query.count()}
    recent = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_quotes=recent)

@app.route('/admin/productos')
@login_required
def admin_products():
    q = request.args.get('q', '')
    cat_id = request.args.get('cat', '')
    page = request.args.get('page', 1, type=int)
    query = Product.query
    if q: query = query.filter(Product.name.ilike(f'%{q}%'))
    if cat_id: query = query.filter_by(category_id=int(cat_id))
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    categories = Category.query.order_by(Category.order).all()
    return render_template('admin/products.html', products=products, categories=categories, q=q, cat_id=cat_id)

@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@login_required
def admin_product_new():
    categories = Category.query.order_by(Category.order).all()
    brands = Brand.query.order_by(Brand.name).all()
    if request.method == 'POST':
        p = Product(name=request.form['name'], sku=request.form.get('sku',''),
            description=request.form.get('description',''), technical_description=request.form.get('technical_description',''),
            category_id=request.form.get('category_id',type=int), brand_id=request.form.get('brand_id',type=int) or None,
            video_url=request.form.get('video_url',''), is_featured='is_featured' in request.form,
            is_active='is_active' in request.form)
        if 'main_image' in request.files and request.files['main_image'].filename:
            p.main_image = save_upload(request.files['main_image'], 'products')
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            p.pdf_url = save_upload(request.files['pdf_file'], 'docs')
        db.session.add(p)
        db.session.flush()
        for f in request.files.getlist('extra_images'):
            if f.filename:
                url = save_upload(f, 'products')
                if url: db.session.add(ProductImage(product_id=p.id, image_url=url))
        for k, v in zip(request.form.getlist('spec_key[]'), request.form.getlist('spec_value[]')):
            if k.strip() and v.strip():
                db.session.add(ProductSpec(product_id=p.id, key=k.strip(), value=v.strip()))
        db.session.commit()
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None, categories=categories, brands=brands)

@app.route('/admin/productos/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def admin_product_edit(pid):
    p = Product.query.get_or_404(pid)
    categories = Category.query.order_by(Category.order).all()
    brands = Brand.query.order_by(Brand.name).all()
    if request.method == 'POST':
        p.name = request.form['name']; p.sku = request.form.get('sku','')
        p.description = request.form.get('description',''); p.technical_description = request.form.get('technical_description','')
        p.category_id = request.form.get('category_id',type=int); p.brand_id = request.form.get('brand_id',type=int) or None
        p.video_url = request.form.get('video_url',''); p.is_featured = 'is_featured' in request.form
        p.is_active = 'is_active' in request.form
        if 'main_image' in request.files and request.files['main_image'].filename:
            p.main_image = save_upload(request.files['main_image'], 'products')
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            p.pdf_url = save_upload(request.files['pdf_file'], 'docs')
        for f in request.files.getlist('extra_images'):
            if f.filename:
                url = save_upload(f, 'products')
                if url: db.session.add(ProductImage(product_id=p.id, image_url=url))
        ProductSpec.query.filter_by(product_id=p.id).delete()
        for k, v in zip(request.form.getlist('spec_key[]'), request.form.getlist('spec_value[]')):
            if k.strip() and v.strip():
                db.session.add(ProductSpec(product_id=p.id, key=k.strip(), value=v.strip()))
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=p, categories=categories, brands=brands)

@app.route('/admin/productos/<int:pid>/eliminar', methods=['POST'])
@login_required
def admin_product_delete(pid):
    db.session.delete(Product.query.get_or_404(pid)); db.session.commit()
    flash('Producto eliminado', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/productos/imagen/<int:img_id>/eliminar', methods=['POST'])
@login_required
def admin_product_image_delete(img_id):
    img = ProductImage.query.get_or_404(img_id); pid = img.product_id
    db.session.delete(img); db.session.commit()
    return redirect(url_for('admin_product_edit', pid=pid))

@app.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
def admin_categories():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            db.session.add(Category(name=request.form['name'], slug=request.form['slug'],
                icon=request.form.get('icon','fas fa-tag'), order=request.form.get('order',0,type=int)))
            db.session.commit(); flash('Categoría creada', 'success')
        elif action == 'update':
            c = Category.query.get(request.form['id'])
            if c:
                c.name=request.form['name']; c.slug=request.form['slug']
                c.icon=request.form.get('icon','fas fa-tag'); c.order=request.form.get('order',0,type=int)
                db.session.commit(); flash('Categoría actualizada', 'success')
        elif action == 'delete':
            c = Category.query.get(request.form['id'])
            if c and not c.products:
                db.session.delete(c); db.session.commit(); flash('Categoría eliminada', 'success')
            else: flash('No se puede eliminar: tiene productos', 'error')
        return redirect(url_for('admin_categories'))
    return render_template('admin/categories.html', categories=Category.query.order_by(Category.order).all())

@app.route('/admin/marcas', methods=['GET', 'POST'])
@login_required
def admin_brands():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            b = Brand(name=request.form['name'], slug=request.form['slug'], description=request.form.get('description',''))
            if 'logo' in request.files and request.files['logo'].filename:
                b.logo_url = save_upload(request.files['logo'], 'brands')
            db.session.add(b); db.session.commit(); flash('Marca creada', 'success')
        elif action == 'update':
            b = Brand.query.get(request.form['id'])
            if b:
                b.name=request.form['name']; b.slug=request.form['slug']; b.description=request.form.get('description','')
                if 'logo' in request.files and request.files['logo'].filename:
                    b.logo_url = save_upload(request.files['logo'], 'brands')
                db.session.commit(); flash('Marca actualizada', 'success')
        elif action == 'delete':
            b = Brand.query.get(request.form['id'])
            if b and not b.products:
                db.session.delete(b); db.session.commit(); flash('Marca eliminada', 'success')
            else: flash('No se puede eliminar: tiene productos', 'error')
        return redirect(url_for('admin_brands'))
    return render_template('admin/brands.html', brands=Brand.query.order_by(Brand.name).all())

@app.route('/admin/solicitudes')
@login_required
def admin_quotes():
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    query = QuoteRequest.query
    if status: query = query.filter_by(status=status)
    quotes = query.order_by(QuoteRequest.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/quotes.html', quotes=quotes, current_status=status)

@app.route('/admin/solicitudes/<int:qid>')
@login_required
def admin_quote_detail(qid):
    return render_template('admin/quote_detail.html', quote=QuoteRequest.query.get_or_404(qid))

@app.route('/admin/solicitudes/<int:qid>/estado', methods=['POST'])
@login_required
def admin_quote_status(qid):
    q = QuoteRequest.query.get_or_404(qid)
    q.status = request.form.get('status', 'pendiente')
    db.session.commit(); flash('Estado actualizado', 'success')
    return redirect(url_for('admin_quote_detail', qid=qid))

@app.route('/admin/banners', methods=['GET', 'POST'])
@login_required
def admin_banners():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            b = Banner(title=request.form.get('title',''), subtitle=request.form.get('subtitle',''),
                cta_text=request.form.get('cta_text',''), cta_link=request.form.get('cta_link',''),
                order=request.form.get('order',0,type=int), is_active='is_active' in request.form)
            if 'image' in request.files and request.files['image'].filename:
                b.image_url = save_upload(request.files['image'], 'banners')
            db.session.add(b); db.session.commit(); flash('Banner creado', 'success')
        elif action == 'update':
            b = Banner.query.get(request.form['id'])
            if b:
                b.title=request.form.get('title',''); b.subtitle=request.form.get('subtitle','')
                b.cta_text=request.form.get('cta_text',''); b.cta_link=request.form.get('cta_link','')
                b.order=request.form.get('order',0,type=int); b.is_active='is_active' in request.form
                if 'image' in request.files and request.files['image'].filename:
                    b.image_url = save_upload(request.files['image'], 'banners')
                db.session.commit(); flash('Banner actualizado', 'success')
        elif action == 'delete':
            b = Banner.query.get(request.form['id'])
            if b: db.session.delete(b); db.session.commit(); flash('Banner eliminado', 'success')
        return redirect(url_for('admin_banners'))
    return render_template('admin/banners.html', banners=Banner.query.order_by(Banner.order).all())

@app.route('/admin/galeria', methods=['GET', 'POST'])
@login_required
def admin_gallery():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_category':
            db.session.add(GalleryCategory(name=request.form['name'], slug=request.form['slug']))
            db.session.commit(); flash('Categoría creada', 'success')
        elif action == 'delete_category':
            gc = GalleryCategory.query.get(request.form['id'])
            if gc: db.session.delete(gc); db.session.commit(); flash('Categoría eliminada', 'success')
        elif action == 'add_image':
            if 'image' in request.files and request.files['image'].filename:
                url = save_upload(request.files['image'], 'gallery')
                if url:
                    db.session.add(GalleryImage(category_id=request.form.get('category_id',type=int),
                        image_url=url, title=request.form.get('title',''),
                        color_code=request.form.get('color_code',''), order=request.form.get('order',0,type=int)))
                    db.session.commit(); flash('Imagen agregada', 'success')
        elif action == 'delete_image':
            gi = GalleryImage.query.get(request.form['id'])
            if gi: db.session.delete(gi); db.session.commit(); flash('Imagen eliminada', 'success')
        return redirect(url_for('admin_gallery'))
    return render_template('admin/gallery.html', gallery_categories=GalleryCategory.query.all(),
        all_images=GalleryImage.query.order_by(GalleryImage.order).all())

@app.route('/admin/configuracion', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        for key in ['phone','whatsapp','whatsapp_2','email','notify_email','address','facebook','instagram','tiktok',
                     'hero_title','hero_subtitle','hero_badge','meta_title','meta_description','meta_keywords','maps_embed']:
            SiteConfig.set(key, request.form.get(key, ''))
        flash('Configuración guardada', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html')


@app.route('/admin/seed-db', methods=['POST'])
@login_required
def admin_seed_db():
    try:
        seed_database()
        flash('Datos de demostración cargados exitosamente', 'success')
    except Exception as e:
        flash(f'Error al cargar datos: {e}', 'error')
    return redirect(url_for('admin_settings'))


@app.route('/admin/ambientes')
@login_required
def admin_ambientes():
    ambientes = AmbientCategory.query.order_by(AmbientCategory.type, AmbientCategory.order).all()
    return render_template('admin/ambientes.html', ambientes=ambientes)


@app.route('/admin/ambientes/nuevo', methods=['GET', 'POST'])
@login_required
def admin_ambient_new():
    if request.method == 'POST':
        name = request.form['name']
        a = AmbientCategory(
            name=name,
            slug=slugify(name),
            type=request.form['type'],
            description=request.form.get('description', ''),
            order=int(request.form.get('order', 0))
        )
        if 'cover_image' in request.files and request.files['cover_image'].filename:
            a.cover_image = save_upload(request.files['cover_image'], 'ambientes')
        
        db.session.add(a)
        db.session.flush()

        for f in request.files.getlist('extra_images'):
            if f.filename:
                url = save_upload(f, 'ambientes')
                if url: db.session.add(AmbientImage(category_id=a.id, image_url=url))
        
        db.session.commit()
        flash('Ambiente creado exitosamente')
        return redirect(url_for('admin_ambientes'))
    return render_template('admin/ambient_form.html', ambient=None)


@app.route('/admin/ambientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_ambient_edit(id):
    a = AmbientCategory.query.get_or_404(id)
    if request.method == 'POST':
        a.name = request.form['name']
        a.slug = slugify(a.name)
        a.type = request.form['type']
        a.description = request.form.get('description', '')
        a.order = int(request.form.get('order', 0))

        if 'cover_image' in request.files and request.files['cover_image'].filename:
            a.cover_image = save_upload(request.files['cover_image'], 'ambientes')

        for f in request.files.getlist('extra_images'):
            if f.filename:
                url = save_upload(f, 'ambientes')
                if url: db.session.add(AmbientImage(category_id=a.id, image_url=url))

        db.session.commit()
        flash('Ambiente actualizado exitosamente')
        return redirect(url_for('admin_ambientes'))
    return render_template('admin/ambient_form.html', ambient=a)


@app.route('/admin/ambientes/<int:id>/eliminar', methods=['POST'])
@login_required
def admin_ambient_delete(id):
    a = AmbientCategory.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash('Ambiente eliminado')
    return redirect(url_for('admin_ambientes'))


@app.route('/admin/ambientes/imagen/<int:img_id>/eliminar', methods=['POST'])
@login_required
def admin_ambient_image_delete(img_id):
    img = AmbientImage.query.get_or_404(img_id)
    parent_id = img.category_id
    db.session.delete(img)
    db.session.commit()
    flash('Imagen eliminada')
    return redirect(url_for('admin_ambient_edit', id=parent_id))


@app.route('/admin/colores', methods=['GET', 'POST'])
@login_required
def admin_colors():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            db.session.add(PaintColor(name=request.form['name'], hex_code=request.form['hex_code'], is_active='is_active' in request.form))
            db.session.commit(); flash('Color creado', 'success')
        elif action == 'update':
            c = PaintColor.query.get(request.form['id'])
            if c:
                c.name = request.form['name']; c.hex_code = request.form['hex_code']; c.is_active = 'is_active' in request.form
                db.session.commit(); flash('Color actualizado', 'success')
        elif action == 'delete':
            c = PaintColor.query.get(request.form['id'])
            if c: db.session.delete(c); db.session.commit(); flash('Color eliminado', 'success')
        return redirect(url_for('admin_colors'))
    return render_template('admin/colors.html', colors=PaintColor.query.all())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
