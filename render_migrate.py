from app import app, db
from sqlalchemy import text
from models import PaintColor

def migrate():
    with app.app_context():
        # Intentar agregar la columna a la base de datos de producción
        try:
            db.session.execute(text("ALTER TABLE quote_items ADD COLUMN color VARCHAR(100)"))
            db.session.commit()
            print("Columna 'color' agregada a quote_items exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Nota: La columna 'color' probablemente ya existe o hubo un error: {e}")
        
        # Crear la tabla paint_colors si no existe
        db.create_all()
        
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
