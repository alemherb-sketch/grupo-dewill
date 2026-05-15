import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import app
from models import db, AmbientCategory, AmbientImage

# Simulated data extracted from anypsa.com.pe/galeria-ambientes
AMBIENTES_DATA = [
    {
        'name': 'Rojo', 'type': 'color', 'slug': 'rojo', 
        'cover': 'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Psicologia-del-color-Rojo-Pinturas-ANYPSA.jpg',
        'images': [
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Psicologia-del-color-Rojo-Pinturas-ANYPSA-1.jpg',
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Psicologia-del-color-Rojo-Pinturas-ANYPSA-2.jpg'
        ]
    },
    {
        'name': 'Azul', 'type': 'color', 'slug': 'azul',
        'cover': 'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Psicologia-del-color-Azul-Pinturas-ANYPSA.jpg',
        'images': [
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Psicologia-del-color-Azul-Pinturas-ANYPSA-1.jpg'
        ]
    },
    {
        'name': 'Salas', 'type': 'room', 'slug': 'salas',
        'cover': 'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Galeria-de-ambientes-Salas-Pinturas-ANYPSA.jpg',
        'images': [
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Galeria-de-ambientes-Salas-Pinturas-ANYPSA-1.jpg',
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Galeria-de-ambientes-Salas-Pinturas-ANYPSA-2.jpg'
        ]
    },
    {
        'name': 'Dormitorios', 'type': 'room', 'slug': 'dormitorios',
        'cover': 'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Galeria-de-ambientes-Dormitorios-Pinturas-ANYPSA.jpg',
        'images': [
            'https://www.anypsa.com.pe/wp-content/uploads/2021/04/Galeria-de-ambientes-Dormitorios-Pinturas-ANYPSA-1.jpg'
        ]
    }
]

def seed_ambientes():
    with app.app_context():
        # Check if already seeded
        if AmbientCategory.query.count() > 0:
            print("Ambient categories already exist. Skipping seed.")
            return

        for data in AMBIENTES_DATA:
            cat = AmbientCategory(
                name=data['name'], 
                slug=data['slug'], 
                type=data['type'], 
                cover_image=data['cover'] # Using remote URLs for demo
            )
            db.session.add(cat)
            db.session.flush()
            
            for img_url in data['images']:
                db.session.add(AmbientImage(category_id=cat.id, image_url=img_url))
            
        db.session.commit()
        print("Seeded Ambientes successfully.")

if __name__ == '__main__':
    seed_ambientes()
