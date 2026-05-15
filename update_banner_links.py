from app import app
from models import Product, Banner, db

with app.app_context():
    products = Product.query.limit(3).all()
    banners = Banner.query.all()
    
    for i, banner in enumerate(banners):
        if i < len(products):
            banner.cta_link = f"/producto/{products[i].id}"
            print(f"Updated Banner {banner.id} to link to Product {products[i].id}")
    
    db.session.commit()
