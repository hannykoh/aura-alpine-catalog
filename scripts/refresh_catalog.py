#!/usr/bin/env python3
"""
Refresh the catalog data:
- Tweak naming style (brand-centric, adjective, casual, premium)
- Update descriptions and regenerate SEO-friendly URL slugs
- Regenerate local placeholder images under data/generated_images/ using the new slugs
- Update items.csv and variations.csv to reference the new images and names

Usage: python3 scripts/refresh_catalog.py [--style brand|adjective|casual|premium]

This tool is deterministic (seeded from numeric id) so re-running with the same
style will produce the same outputs.
"""
import argparse
import os
import re
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(__file__))
ITEMS_CSV = os.path.join(BASE, 'data', 'items.csv')
VARS_CSV = os.path.join(BASE, 'data', 'variations.csv')
OUT_DIR = os.path.join(BASE, 'data', 'generated_images')
os.makedirs(OUT_DIR, exist_ok=True)

ADJECTIVES = [
    'Summit','Harbor','Cascade','Ridge','Trail','Echo','Aurora','North','Coast','Prairie',
    'Ember','Willow','Stone','River','Cinder','Pioneer','Atlas','Horizon','Canyon','Meadow'
]

NOUNS = [
    'Shirt','Tee','Polo','Tank','Jacket','Hoodie','Sweater','Chino','Cargo Pants','Pants',
    'Shorts','Cap','Beanie','Skort','Dress','Leggings','Joggers','Blouse','Cardigan','Vest'
]

CASUAL_ADJ = ['Cozy','Easy','Daily','Street','Fresh','Urban','Comfy','Breezy']
PREMIUM_ADJ = ['Heritage','Lux','Reserve','Signature','Elite','Foundry','Classic','Merino']

COLOR_PALETTE = [
    '#0e6ea8','#bdb07a','#d6c6a6','#6b0f0f','#111111','#f6f7f8','#7b8a93','#e29aa6','#26466d'
]

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", '-', s)
    s = s.strip('-')
    return s or 'item'

def numeric_seed_from_id(item_id: str) -> int:
    m = re.search(r"(\d+)", str(item_id))
    return int(m.group(1)) if m else abs(hash(item_id)) % 100000

def generate_name(item_id: str, brand: str, style: str) -> str:
    seed = numeric_seed_from_id(item_id)
    rnd = random.Random(seed)

    if style == 'brand':
        # Brand-centric: <Brand> <Noun> or <Brand> <Adjective> <Noun>
        brand_word = (brand.split()[0] if isinstance(brand, str) and brand.strip() else 'Aura')
        if rnd.random() < 0.2:
            adj = rnd.choice(ADJECTIVES)
            noun = rnd.choice(NOUNS)
            return f"{brand_word} {adj} {noun}"
        else:
            noun = rnd.choice(NOUNS)
            return f"{brand_word} {noun}"

    if style == 'adjective':
        # Adjective heavy: <Adjective> <Noun>
        adj = rnd.choice(ADJECTIVES)
        noun = rnd.choice(NOUNS)
        return f"{adj} {noun}"

    if style == 'casual':
        adj = rnd.choice(CASUAL_ADJ)
        noun = rnd.choice(NOUNS)
        return f"{adj} {noun}"

    # premium
    adj = rnd.choice(PREMIUM_ADJ)
    noun = rnd.choice(NOUNS)
    return f"{adj} {noun}"

def render_image(path: str, color: str, text: str):
    size = (800, 800)
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 36)
    except Exception:
        font = ImageFont.load_default()
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
    except Exception:
        try:
            w, h = font.getsize(text)
        except Exception:
            w, h = (len(text)*10, 20)
    fill = 'white' if color.lower() not in ('#f6f7f8','#ffffff') else 'black'
    draw.text(((size[0]-w)/2,(size[1]-h)/2), text, fill=fill, font=font)
    img.save(path, format='JPEG', quality=85)

def main(style: str):
    print('Loading items...')
    items = pd.read_csv(ITEMS_CSV)
    vars_df = pd.read_csv(VARS_CSV)

    id_to_slug = {}
    print(f'Generating names using style: {style}')
    for idx, row in items.iterrows():
        item_id = row['id']
        brand = row.get('metadata:brand', '')
        name = generate_name(item_id, brand, style)
        items.at[idx, 'item_name'] = name

        # regenerate description
        items.at[idx, 'description'] = f"The {name} from {brand} — premium apparel built for everyday adventure."

        # slug and URL
        slug = slugify(name)
        id_to_slug[item_id] = slug
        items.at[idx, 'url'] = f"https://aura-alpine.com/products/{slug}"

        # image path
        img_fname = f"{slug}.jpg"
        img_rel = os.path.join('data', 'generated_images', img_fname)
        img_full = os.path.join(BASE, img_rel)
        # deterministic color pick
        seed = numeric_seed_from_id(item_id)
        rnd = random.Random(seed)
        color = rnd.choice(COLOR_PALETTE)
        label = f"{name}"
        if not os.path.exists(img_full):
            render_image(img_full, color, label)
        items.at[idx, 'image_url'] = img_rel

    # backups
    items_backup = ITEMS_CSV + '.bak'
    if not os.path.exists(items_backup):
        items.to_csv(items_backup, index=False)
        print(f'Backup written to {items_backup}')
    items.to_csv(ITEMS_CSV, index=False)
    print(f'Wrote updated items to {ITEMS_CSV}')

    # Update variations: item_name and image_url to match parent
    print('Updating variations...')
    for idx, row in vars_df.iterrows():
        item_id = row['item_id']
        base = items[items['id'] == item_id]
        if base.empty:
            continue
        base_name = base.iloc[0]['item_name']
        color = row.get('metadata:color', '')
        size = row.get('metadata:size', '')
        color_str = '' if pd.isna(color) else str(color)
        size_str = '' if pd.isna(size) else str(size)
        if color_str and size_str:
            new_var_name = f"{base_name} ({color_str} / {size_str})"
        elif color_str:
            new_var_name = f"{base_name} ({color_str})"
        elif size_str:
            new_var_name = f"{base_name} ({size_str})"
        else:
            new_var_name = base_name
        vars_df.at[idx, 'item_name'] = new_var_name

        # point variation images to the parent slug image
        slug = id_to_slug.get(item_id)
        if slug:
            img_rel = os.path.join('data', 'generated_images', f"{slug}.jpg")
            vars_df.at[idx, 'image_url'] = img_rel

    vars_backup = VARS_CSV + '.bak'
    if not os.path.exists(vars_backup):
        vars_df.to_csv(vars_backup, index=False)
        print(f'Backup written to {vars_backup}')
    vars_df.to_csv(VARS_CSV, index=False)
    print(f'Wrote updated variations to {VARS_CSV}')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--style', choices=['brand','adjective','casual','premium'], default='brand')
    args = p.parse_args()
    main(args.style)
