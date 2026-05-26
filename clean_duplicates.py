import sqlite3
import os
from config import Config
from flask import Flask
from models import db, Product, ProductSpec, Presentation, product_presentations

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def clean_duplicates():
    with app.app_context():
        # Get all products grouped by name
        # We need to find products with the same name
        products = Product.query.order_by(Product.id).all()
        
        name_map = {}
        for p in products:
            name_lower = p.name.strip().lower()
            if name_lower not in name_map:
                name_map[name_lower] = []
            name_map[name_lower].append(p)
            
        deleted_count = 0
        merged_colors = 0
        
        for name_lower, prod_list in name_map.items():
            if len(prod_list) > 1:
                base_prod = prod_list[0]
                duplicates = prod_list[1:]
                
                print(f"Merging duplicates for: {base_prod.name}")
                
                # We merge specs and presentations into base_prod
                base_colors = [s.value.lower() for s in base_prod.specs if s.key.lower() == 'color']
                base_presentations = [p.id for p in base_prod.presentations]
                
                for dup in duplicates:
                    # Move colors
                    for spec in dup.specs:
                        if spec.key.lower() == 'color' and spec.value.lower() not in base_colors:
                            new_spec = ProductSpec(product_id=base_prod.id, key='Color', value=spec.value)
                            db.session.add(new_spec)
                            base_colors.append(spec.value.lower())
                            merged_colors += 1
                            
                    # Move presentations
                    for pres in dup.presentations:
                        if pres.id not in base_presentations:
                            base_prod.presentations.append(pres)
                            base_presentations.append(pres.id)
                            
                    # Delete duplicate product
                    db.session.delete(dup)
                    deleted_count += 1
                    
        db.session.commit()
        print(f"Cleanup complete. Deleted {deleted_count} duplicate products. Merged {merged_colors} colors.")

if __name__ == '__main__':
    clean_duplicates()
