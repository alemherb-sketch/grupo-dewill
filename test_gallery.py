from app import app, db
from models import GalleryCategory, GalleryImage

with app.app_context():
    try:
        categories = GalleryCategory.query.all()
        images = GalleryImage.query.order_by(GalleryImage.order).all()
        print("Categories:", len(categories))
        print("Images:", len(images))
        for img in images:
            print(img.id, img.title, img.gallery_category.name if img.gallery_category else 'No category')
    except Exception as e:
        print("Error:", e)
