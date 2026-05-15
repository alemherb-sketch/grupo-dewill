import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'dewill.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add color column to quote_items
    try:
        cursor.execute("ALTER TABLE quote_items ADD COLUMN color VARCHAR(100)")
        print("Column 'color' added to 'quote_items'.")
    except Exception as e:
        print(f"Column might already exist or error: {e}")

    # 2. Create PaintColor table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paint_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                hex_code VARCHAR(10) NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        print("Table 'paint_colors' ensured to exist.")
    except Exception as e:
        print(f"Error creating table: {e}")

    # 3. Seed default colors
    colors = [
        ("Blanco", "#FFFFFF"), ("Crema", "#FFFDD0"), ("Marfil", "#FFFFF0"),
        ("Amarillo", "#FFD700"), ("Naranja", "#FFA500"), ("Rojo", "#FF0000"),
        ("Azul", "#0000FF"), ("Celeste", "#87CEEB"), ("Verde", "#008000"),
        ("Gris", "#808080"), ("Marrón", "#8B4513"), ("Negro", "#000000")
    ]
    
    for name, hex_code in colors:
        cursor.execute("SELECT id FROM paint_colors WHERE name=?", (name,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO paint_colors (name, hex_code, is_active) VALUES (?, ?, 1)", (name, hex_code))
    
    conn.commit()
    conn.close()
    print("Colors seeded successfully.")

if __name__ == '__main__':
    migrate()
