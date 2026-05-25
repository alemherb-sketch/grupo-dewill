import os
import time
import requests
from app import app
from models import db, Product
from duckduckgo_search import DDGS
from werkzeug.utils import secure_filename

def download_image(url, filename):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"    Intentando descargar: {url[:60]}...")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"    Ignorado: no es una imagen ({content_type})")
                return False
                
            folder = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"    Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"    Error en descarga: {type(e).__name__} - {str(e)[:50]}")
    return False

def fetch_images_for_products():
    with app.app_context():
        # Buscar productos activos que no tengan imagen principal
        products = Product.query.filter(Product.is_active == True).filter(
            (Product.main_image == None) | (Product.main_image == '')
        ).all()
        
        if not products:
            print("Todos los productos activos ya tienen imagen.")
            return

        print(f"Se encontraron {len(products)} productos sin imagen. Iniciando búsqueda...")
        ddgs = DDGS()

        for idx, product in enumerate(products, 1):
            brand_name = product.brand.name if product.brand else ""
            cat_name = product.category.name if product.category else ""
            
            # Construir una consulta relevante
            query = f"{brand_name} {product.name} {cat_name}".strip()
            print(f"[{idx}/{len(products)}] Buscando: '{query}'")
            
            try:
                # Buscar hasta 3 imágenes
                results = list(ddgs.images(query, max_results=3))
                if results:
                    success = False
                    for res in results:
                        img_url = res.get('image')
                        if not img_url: 
                            continue
                            
                        # Intentar determinar extensión
                        ext = img_url.split('.')[-1].split('?')[0].lower()
                        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                            ext = 'jpg'
                            
                        # Limpiar nombre de archivo
                        safe_sku = secure_filename(product.sku or str(product.id))
                        filename = f"{safe_sku}_{int(time.time())}.{ext}"
                        
                        if download_image(img_url, filename):
                            product.main_image = f"uploads/products/{filename}"
                            db.session.commit()
                            print(f"  -> ÉXITO: Imagen asignada a '{product.name}'")
                            success = True
                            break # Salir del loop de resultados, pasar al siguiente producto
                            
                    if not success:
                        print("  -> FALLO: No se pudo descargar ninguna de las imágenes encontradas.")
                else:
                    print(f"  -> No se encontraron resultados en la web.")
            except Exception as e:
                print(f"  -> Error en la búsqueda DuckDuckGo: {e}")
            
            # Pausa para no saturar DuckDuckGo
            time.sleep(2)
            
        print("\nProceso finalizado.")

if __name__ == '__main__':
    fetch_images_for_products()
