from rembg import remove
from PIL import Image
import sys

input_path = "static/uploads/modelo_pintor.PNG"
output_path = "static/assets/hero-painter.png"

try:
    print("Abriendo imagen...")
    input_image = Image.open(input_path)
    
    # Crop the image before removing background to avoid the blob!
    # The blob is on the far left. The painter is on the right.
    # The original image is a screenshot. We crop the left 20%.
    width, height = input_image.size
    # Let's do a safe crop: remove the left 30% of the image entirely.
    cropped_image = input_image.crop((int(width * 0.35), 0, width, height))
    
    print("Eliminando fondo de la imagen recortada...")
    output_image = remove(cropped_image)
    
    print("Guardando imagen final...")
    output_image.save(output_path)
    print(f"Exito! Imagen guardada en {output_path}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
