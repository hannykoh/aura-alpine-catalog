import csv
import random
import os

# Configuration
TOTAL_PRODUCTS = 5000
DATA_DIR = 'data'
GENDERS = ["Men", "Women", "Unisex"]
COLORS = ["Midnight Black", "Arctic White", "Slate Grey", "Forest Green", "Sandstone", "Ocean Blue"]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
BRANDS = ["Aura & Alpine", "Alpine Tech", "Urban Peak", "Summit Style"]

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_catalog():
    items_file = os.path.join(DATA_DIR, 'items.csv')
    vars_file = os.path.join(DATA_DIR, 'variations.csv')

    # 1. Create Items (Parent Products)
    with open(items_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'item_name', 'image_url', 'url', 'description', 'group_ids', 'metadata:price', 'metadata:brand', 'metadata:gender'])
        
        # 2. Create Variations (Child SKUs)
        with open(vars_file, 'w', newline='') as v_f:
            v_writer = csv.writer(v_f)
            v_writer.writerow(['variation_id', 'item_id', 'item_name', 'image_url', 'metadata:color', 'metadata:size', 'metadata:inventory'])
            
            for i in range(1, TOTAL_PRODUCTS + 1):
                item_id = f"AA-{10000 + i}"
                brand = random.choice(BRANDS)
                gender = random.choice(GENDERS)
                price = round(random.uniform(15.0, 250.0), 2)
                
                # Assign groups based on gender logic
                group = "mens" if gender == "Men" else "womens" if gender == "Women" else "accessories"
                
                # Write Parent Row
                writer.writerow([
                    item_id, 
                    f"{brand} Seasonal Product {i}", 
                    f"https://images.aura-alpine.com/{item_id}.jpg",
                    f"https://aura-alpine.com/products/{item_id}",
                    f"A high-quality {brand} product designed for {gender}.",
                    group,
                    price,
                    brand,
                    gender
                ])
                
                # Generate 3-6 variations (Size/Color combos) per parent
                num_vars = random.randint(3, 6)
                selected_colors = random.sample(COLORS, 2) # Pick 2 colors
                selected_sizes = random.sample(SIZES, 3)  # Pick 3 sizes
                
                for color in selected_colors:
                    for size in selected_sizes:
                        var_id = f"{item_id}-{color[:3].upper()}-{size}"
                        v_writer.writerow([
                            var_id,
                            item_id,
                            f"{brand} Product {i} ({color} / {size})",
                            f"https://images.aura-alpine.com/{item_id}-{color[:3].lower()}.jpg",
                            color,
                            size,
                            random.randint(0, 100) # Random stock level
                        ])

    print(f"✅ Successfully generated {TOTAL_PRODUCTS} items and their variations in the /data folder.")

if __name__ == "__main__":
    generate_catalog()