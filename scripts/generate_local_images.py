#!/usr/bin/env python3
"""
Read data/variations.csv, generate simple placeholder JPEGs for any rows that
currently point to Unsplash, and rewrite those rows to point to
data/generated_images/<item>-<color>.jpg.

This uses Pillow to render a solid color background (best-effort from the
metadata color name) with the product id printed on the image.
"""
import csv
import os
import re
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE, 'data', 'variations.csv')
OUT_DIR = os.path.join(BASE, 'data', 'generated_images')

os.makedirs(OUT_DIR, exist_ok=True)

# very small color name -> hex map for friendly placeholders
COLOR_MAP = {
    'black': '#111111',
    'navy': '#0b3d91',
    'midnight black': '#0b0b0b',
    'midnight': '#0b0b0b',
    'grey': '#9ea7ad',
    'light grey': '#d6d8da',
    'slate grey': '#7b8a93',
    'charcoal': '#333333',
    'olive': '#6b8f4c',
    'khaki': '#bdb07a',
    'tan': '#d2b48c',
    'sandstone': '#d6c6a6',
    'arctic white': '#f6f7f8',
    'white': '#ffffff',
    'ocean blue': '#0e6ea8',
    'ocean': '#0e6ea8',
    'indigo': '#26466d',
    'rose': '#e29aa6',
    'maroon': '#6b0f0f',
    'platinum': '#e5e7eb',
    'pink': '#f3b0c3',
    'pastel': '#d8e8e8',
    'natural': '#f0e6d6',
    'olive': '#708238',
}

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", '-', s)
    s = s.strip('-')
    return s or 'x'

def pick_color_hex(color_name: str) -> str:
    if not color_name:
        return '#888888'
    key = color_name.strip().lower()
    return COLOR_MAP.get(key, '#888888')

def render_image(path: str, bg_hex: str, text: str):
    size = (800, 800)
    img = Image.new('RGB', size, bg_hex)
    draw = ImageDraw.Draw(img)
    try:
        # Try to use a default truetype font for nicer output
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 36)
    except Exception:
        font = ImageFont.load_default()

    # Draw text in center. textsize() was removed in some Pillow releases; try textbbox then fallback
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        try:
            w, h = font.getsize(text)
        except Exception:
            w, h = (len(text) * 10, 20)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill='white' if bg_hex != '#f6f7f8' else 'black', font=font)
    img.save(path, format='JPEG', quality=85)

def main():
    rows = []
    changed = 0
    with open(CSV_PATH, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            url = r.get('image_url', '')
            if 'images.unsplash.com' in (url or ''):
                item_id = r.get('item_id') or 'unknown'
                color = r.get('metadata:color') or r.get('metadata:color', '')
                # create filename based on item & color to reuse across sizes
                fname = f"{slugify(item_id)}-{slugify(color)}.jpg"
                out_path = os.path.join('data', 'generated_images', fname)
                full_out = os.path.join(BASE, out_path)
                if not os.path.exists(full_out):
                    bg = pick_color_hex(color)
                    label = f"{item_id} {color}" if color else item_id
                    render_image(full_out, bg, label)
                r['image_url'] = out_path
                changed += 1
            rows.append(r)

    if changed:
        # write back CSV preserving fieldnames and order
        tmp = CSV_PATH + '.tmp'
        with open(tmp, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        os.replace(tmp, CSV_PATH)
        print(f"Updated {changed} rows and generated images in {OUT_DIR}")
    else:
        print("No Unsplash image URLs found; nothing to do.")

if __name__ == '__main__':
    main()
