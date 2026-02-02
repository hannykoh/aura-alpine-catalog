#!/usr/bin/env python3
"""
Improve product names in data/items.csv and data/variations.csv.

This script deterministically generates apparel-focused names like
"Summit Ridge Shirt" or "Harbor Trail Pants" for each parent product
and updates each variation's `item_name` to include the color and size,
e.g. "Summit Ridge Shirt (Ocean Blue / XL)".

Deterministic mapping uses the numeric part of the item id as a seed
so repeated runs produce the same results.
"""
import pandas as pd
import re
import random
import os

BASE = os.path.dirname(os.path.dirname(__file__))
ITEMS_CSV = os.path.join(BASE, 'data', 'items.csv')
VARS_CSV = os.path.join(BASE, 'data', 'variations.csv')

NAME_WORDS = [
    'Summit','Harbor','Cascade','Ridge','Trail','Echo','Aurora','North','Coast','Prairie',
    'Ember','Willow','Stone','River','Cinder','Pioneer','Atlas','Horizon','Canyon','Meadow',
    'Boulder','Glacier','Solace','Fjord','Peak','Timber','Drift','Cove','Sage','Mariner'
]

NAME_TYPES = [
    'Shirt','Tee','Polo','Tank','Jacket','Hoodie','Sweater','Chino','Cargo Pants','Pants',
    'Shorts','Cap','Beanie','Skort','Dress','Leggings','Joggers','Blouse','Cardigan','Vest'
]

def numeric_seed_from_id(item_id: str) -> int:
    m = re.search(r"(\d+)", str(item_id))
    return int(m.group(1)) if m else abs(hash(item_id)) % 100000

def make_item_name(item_id: str) -> str:
    seed = numeric_seed_from_id(item_id)
    rnd = random.Random(seed)
    word = rnd.choice(NAME_WORDS)
    typ = rnd.choice(NAME_TYPES)
    # Slight variety: sometimes insert a connector like 'Ridge Tee' vs 'Ridge Trail Tee'
    if rnd.random() < 0.15:
        extra = rnd.choice(NAME_WORDS)
        name = f"{word} {extra} {typ}"
    else:
        name = f"{word} {typ}"
    return name

def main():
    print('Reading items...')
    items = pd.read_csv(ITEMS_CSV)

    # Generate new names
    print('Generating new item names...')
    id_to_name = {}
    for idx, row in items.iterrows():
        item_id = row['id']
        new_name = make_item_name(item_id)
        id_to_name[item_id] = new_name
        items.at[idx, 'item_name'] = new_name

    # Backup original file
    items_backup = ITEMS_CSV + '.bak'
    if not os.path.exists(items_backup):
        items.to_csv(items_backup, index=False)
        print(f'Backup written to {items_backup}')

    items.to_csv(ITEMS_CSV, index=False)
    print(f'Wrote updated items to {ITEMS_CSV}')

    # Update variations
    print('Reading variations...')
    vars_df = pd.read_csv(VARS_CSV)
    print('Updating variation names to match new parent names...')
    for idx, row in vars_df.iterrows():
        item_id = row['item_id']
        base_name = id_to_name.get(item_id)
        if base_name:
            color = row.get('metadata:color', '')
            size = row.get('metadata:size', '')
            # Normalize color/size to string
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

    vars_backup = VARS_CSV + '.bak'
    if not os.path.exists(vars_backup):
        vars_df.to_csv(vars_backup, index=False)
        print(f'Backup written to {vars_backup}')

    vars_df.to_csv(VARS_CSV, index=False)
    print(f'Wrote updated variations to {VARS_CSV}')

if __name__ == '__main__':
    main()
