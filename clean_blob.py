from PIL import Image
import sys

try:
    img_path = 'static/assets/hero-painter.png'
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # Erase the blob safely
    # We erase the top-left area. x < width * 0.25 and y < height * 0.6
    # This is safe and won't cut the painter in half.
    for x in range(int(width * 0.3)):
        for y in range(int(height * 0.65)):
            pixels[x, y] = (0, 0, 0, 0)

    img.save(img_path)
    print("Mancha limpiada.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
