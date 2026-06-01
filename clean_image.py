from PIL import Image
import sys

try:
    img_path = 'static/assets/hero-painter.png'
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # The blob is on the left side, roughly upper half. 
    # Erase the top-left quadrant safely.
    for x in range(int(width * 0.45)):
        for y in range(int(height * 0.55)):
            pixels[x, y] = (0, 0, 0, 0)

    img.save(img_path)
    print("Imagen limpiada correctamente.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
