import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app
from models import db, AmbientCategory, AmbientImage

# Beautiful environments matching the screenshot exactly
AMBIENTES_DATA = [
    {
        'name': 'SALA MODERNA',
        'slug': 'sala',
        'type': 'room',
        'area': 'interior',
        'cover_image': 'assets/ambiente_sala.png',
        'description': 'Colores neutros cálidos',
        'colors': '#f2ebdd,#d7cbb6,#c5ab8d',
        'images': ['assets/ambiente_sala.png']
    },
    {
        'name': 'DORMITORIO RELAJANTE',
        'slug': 'dormitorio',
        'type': 'room',
        'area': 'interior',
        'cover_image': 'assets/ambiente_dormitorio.png',
        'description': 'Colores fríos suaves',
        'colors': '#9ab8db,#4b7db5,#bbd0ea',
        'images': ['assets/ambiente_dormitorio.png']
    },
    {
        'name': 'COCINA FRESCA',
        'slug': 'cocina',
        'type': 'room',
        'area': 'interior',
        'cover_image': 'assets/ambiente_cocina.png',
        'description': 'Colores naturales',
        'colors': '#6f8f53,#88a26d,#ccd7b1',
        'images': ['assets/ambiente_cocina.png']
    },
    {
        'name': 'FACHADA MODERNA',
        'slug': 'fachada-moderna',
        'type': 'room',
        'area': 'exterior',
        'cover_image': 'assets/ambiente_fachada_moderna.png',
        'description': 'Colores grises',
        'colors': '#eaeaea,#b5b5b5,#5a5a5a',
        'images': ['assets/ambiente_fachada_moderna.png']
    },
    {
        'name': 'OFICINA PROFESIONAL',
        'slug': 'oficina',
        'type': 'room',
        'area': 'interior',
        'cover_image': 'assets/ambiente_oficina.png',
        'description': 'Colores corporativos',
        'colors': '#0f2e5c,#1f4f8f,#cbd5e1',
        'images': ['assets/ambiente_oficina.png']
    },
    {
        'name': 'FACHADA CÁLIDA',
        'slug': 'fachada-calida',
        'type': 'room',
        'area': 'exterior',
        'cover_image': 'assets/ambiente_fachada_calida.png',
        'description': 'Colores tierra',
        'colors': '#e5cca8,#cd8b5b,#c24b17,#563b2f',
        'images': ['assets/ambiente_fachada_calida.png']
    }
]

def seed_ambientes():
    with app.app_context():
        print("Cleaning old ambient categories and images...")
        AmbientImage.query.delete()
        AmbientCategory.query.delete()
        db.session.commit()

        for data in AMBIENTES_DATA:
            cat = AmbientCategory(
                name=data['name'],
                slug=data['slug'],
                type=data['type'],
                area=data['area'],
                cover_image=data['cover_image'],
                description=data['description'],
                colors=data['colors']
            )
            db.session.add(cat)
            db.session.flush()
            
            for img_path in data['images']:
                db.session.add(AmbientImage(category_id=cat.id, image_url=img_path))
            
        db.session.commit()
        print("Seeded new beautiful environments successfully.")

if __name__ == '__main__':
    seed_ambientes()
