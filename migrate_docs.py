import sqlite3
import os

db_path = os.path.join('instance', 'dewill.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN safety_sheet_url VARCHAR(300)")
        print("Added safety_sheet_url")
    except sqlite3.OperationalError as e:
        print(f"Error adding safety_sheet_url: {e}")
        
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN catalog_url VARCHAR(300)")
        print("Added catalog_url")
    except sqlite3.OperationalError as e:
        print(f"Error adding catalog_url: {e}")
        
    conn.commit()
    conn.close()
    print("Migration complete.")
else:
    print(f"Database not found at {db_path}")
