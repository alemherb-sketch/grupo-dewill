from app import app, db
from sqlalchemy import text
from models import PaintColor

def migrate():
    with app.app_context():
        # 1. Crear todas las tablas nuevas si no existen (subcategories, presentations, product_presentations)
        db.create_all()
        print("Tablas de la base de datos creadas/verificadas.")

        # 2. Intentar agregar la columna a la base de datos de producción (quote_items)
        try:
            db.session.execute(text("ALTER TABLE quote_items ADD COLUMN color VARCHAR(100)"))
            db.session.commit()
            print("Columna 'color' agregada a quote_items exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Nota: La columna 'color' probablemente ya existe o hubo un error: {e}")
        
        # 3. Intentar agregar la columna subcategory_id a products
        try:
            db.session.execute(text("ALTER TABLE products ADD COLUMN subcategory_id INTEGER REFERENCES subcategories(id)"))
            db.session.commit()
            print("Columna 'subcategory_id' agregada a products exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Nota: La columna 'subcategory_id' probablemente ya existe o hubo un error: {e}")
            
        # 4. Agregar columna image_url a categories
        try:
            db.session.execute(text("ALTER TABLE categories ADD COLUMN image_url VARCHAR(255)"))
            db.session.commit()
            print("Columna 'image_url' agregada a categories exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Nota: La columna 'image_url' probablemente ya existe o hubo un error: {e}")
        
        # Insertar los colores por defecto
        colors = [
            ("Blanco", "#FFFFFF"), ("Crema", "#FFFDD0"), ("Marfil", "#FFFFF0"),
            ("Amarillo", "#FFD700"), ("Naranja", "#FFA500"), ("Rojo", "#FF0000"),
            ("Azul", "#0000FF"), ("Celeste", "#87CEEB"), ("Verde", "#008000"),
            ("Gris", "#808080"), ("Marrón", "#8B4513"), ("Negro", "#000000")
        ]
        
        for name, hex_code in colors:
            if not PaintColor.query.filter_by(name=name).first():
                db.session.add(PaintColor(name=name, hex_code=hex_code))
                
        db.session.commit()
        print("Migración completada. Base de datos lista.")

if __name__ == '__main__':
    migrate()
