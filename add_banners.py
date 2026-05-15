from app import app
from models import db, Banner

def add_banners():
    with app.app_context():
        if Banner.query.count() < 3:
            b2 = Banner(title='Calidad en Herramientas Toretto',
                        subtitle='Potencia y precisión para sus proyectos',
                        image_url='assets/product_herramientas.png',
                        cta_text='Cotizar Ahora', cta_link='/productos?marca=toretto',
                        order=2, is_active=True)
            b3 = Banner(title='Pinturas Soprin',
                        subtitle='Acabados perfectos y duraderos',
                        image_url='assets/product_paint.png',
                        cta_text='Ver Pinturas', cta_link='/productos?cat=pinturas-y-acabados',
                        order=3, is_active=True)
            db.session.add(b2)
            db.session.add(b3)
            db.session.commit()
            print("Banners added successfully.")
        else:
            print("Banners already exist.")

if __name__ == '__main__':
    add_banners()
