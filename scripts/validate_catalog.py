import pandas as pd
import os

def validate_catalog():
    items_path = 'data/items.csv'
    vars_path = 'data/variations.csv'
    
    if not os.path.exists(items_path) or not os.path.exists(vars_path):
        print("❌ Error: CSV files not found in /data folder. Run the generator first!")
        return

    # Load data into DataFrames
    items_df = pd.read_csv(items_path)
    vars_df = pd.read_csv(vars_path)
    errors = 0

    print(f"--- 🔍 Validating {len(items_df)} Parents and {len(vars_df)} Variations ---")

    # 1. Check for Duplicate Parent IDs
    dupes = items_df['id'].duplicated().sum()
    if dupes > 0:
        print(f"❌ Error: {dupes} Duplicate Parent IDs found.")
        errors += 1

    # 2. Referential Integrity (Child -> Parent)
    # This ensures every variation actually has a parent product to live under
    orphan_vars = vars_df[~vars_df['item_id'].isin(items_df['id'])]
    if not orphan_vars.empty:
        print(f"❌ Error: {len(orphan_vars)} variations found with no matching Parent ID.")
        errors += 1

    # 3. Check for Variation ID (SKU) uniqueness
    v_dupes = vars_df['variation_id'].duplicated().sum()
    if v_dupes > 0:
        print(f"❌ Error: {v_dupes} Duplicate Variation IDs detected.")
        errors += 1

    if errors == 0:
        print("✅ Validation Passed! Your catalog is clean and ready for Constructor.com.")
    else:
        print(f"⚠️ Validation Failed with {errors} major error(s).")

if __name__ == "__main__":
    validate_catalog()