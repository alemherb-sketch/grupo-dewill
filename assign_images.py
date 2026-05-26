import sqlite3
import shutil
import os
import glob

# Paths of generated images
src_dir = r"C:\Users\ALEM\.gemini\antigravity\brain\bb94aa33-dde3-432f-aa65-9d567629437b"
dest_dir = r"static\assets\products"

def find_img(prefix):
    files = glob.glob(os.path.join(src_dir, f"{prefix}_*.png"))
    return files[0] if files else None

img_map = {
    'cpp': find_img('cpp_sellador'),
    'vencedor': find_img('vencedor_supermate'),
    'anypsa': find_img('anypsa_latex'),
    'tools': find_img('tools')
}

print("Found images:", img_map)

# Copy to static folder
for key, path in img_map.items():
    if path:
        dest_path = os.path.join(dest_dir, f"{key}.png")
        shutil.copy(path, dest_path)
        img_map[key] = f"assets/products/{key}.png"

conn = sqlite3.connect('instance/dewill.db')
c = conn.cursor()

# Update products based on name
c.execute("UPDATE products SET main_image = ? WHERE name LIKE '%CPP%' OR name LIKE '%Pato%'", (img_map['cpp'],))
c.execute("UPDATE products SET main_image = ? WHERE name LIKE '%Vencedor%'", (img_map['vencedor'],))
c.execute("UPDATE products SET main_image = ? WHERE name LIKE '%Anypsa%'", (img_map['anypsa'],))
c.execute("UPDATE products SET main_image = ? WHERE name LIKE '%Brocha%' OR name LIKE '%Rodillo%' OR name LIKE '%Espátula%' OR name LIKE '%Taladro%' OR name LIKE '%Esptula%'", (img_map['tools'],))

# For any other paint we can set a default
c.execute("UPDATE products SET main_image = ? WHERE main_image IS NULL", (img_map['cpp'],))

conn.commit()
print("Database updated!")
conn.close()
