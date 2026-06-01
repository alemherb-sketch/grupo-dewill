from rembg import remove
from PIL import Image
import sys

input_path = "static/uploads/modelo_pintor.PNG"
output_path = "static/uploads/modelo_pintor_recortado.png"

try:
    print("Abriendo imagen...")
    input_image = Image.open(input_path)
    print("Eliminando fondo (esto puede tardar unos segundos)...")
    output_image = remove(input_image)
    print("Guardando imagen recortada...")
    output_image.save(output_path)
    print(f"Exito! Imagen guardada en {output_path}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
