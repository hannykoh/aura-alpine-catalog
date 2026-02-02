import pandas as pd

def search_catalog():
    try:
        # Load the items you generated
        df = pd.read_csv('data/items.csv')
        
        print("\n--- 🏔️ Welcome to the Aura & Alpine Catalog Search ---")
        query = input("What are you looking for today? (e.g. 'Cotton', 'Cargo', 'Women'): ")
        
        # Search the item_name and description columns
        results = df[df['item_name'].str.contains(query, case=False) | 
                     df['description'].str.contains(query, case=False)]
        
        if not results.empty:
            print(f"\n✅ Found {len(results)} matches for '{query}':")
            # Show the top 10 results
            print(results[['item_name', 'metadata:price', 'metadata:brand']].head(10).to_string(index=False))
        else:
            print(f"\n❌ No products found for '{query}'.")
            
    except FileNotFoundError:
        print("❌ Error: data/items.csv not found. Make sure you ran the generator script!")

if __name__ == "__main__":
    search_catalog()
