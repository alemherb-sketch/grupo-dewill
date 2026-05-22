import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'dewill.db')
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create subcategories table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subcategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        print("Table 'subcategories' created or already exists.")
    except Exception as e:
        print(f"Error creating table 'subcategories': {e}")

    # 2. Create presentations table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presentations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL
            )
        """)
        print("Table 'presentations' created or already exists.")
    except Exception as e:
        print(f"Error creating table 'presentations': {e}")

    # 3. Create product_presentations association table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_presentations (
                product_id INTEGER NOT NULL,
                presentation_id INTEGER NOT NULL,
                PRIMARY KEY (product_id, presentation_id),
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
                FOREIGN KEY (presentation_id) REFERENCES presentations (id) ON DELETE CASCADE
            )
        """)
        print("Table 'product_presentations' created or already exists.")
    except Exception as e:
        print(f"Error creating table 'product_presentations': {e}")

    # 4. Add subcategory_id column to products table
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN subcategory_id INTEGER REFERENCES subcategories(id)")
        print("Column 'subcategory_id' added to 'products' table.")
    except Exception as e:
        print(f"Column 'subcategory_id' might already exist or error: {e}")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == '__main__':
    migrate()
