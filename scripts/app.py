import streamlit as st
import pandas as pd

st.set_page_config(page_title="Aura & Alpine", page_icon="🏔️")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/items.csv')

df = load_data()

st.title("🏔️ Aura & Alpine")

# Sidebar
st.sidebar.header("Filters")
brand_list = ["All"] + sorted(df['metadata:brand'].unique().tolist())
selected_brand = st.sidebar.selectbox("Brand", brand_list)

# Main Search
query = st.text_input("Search catalog...", placeholder="e.g. Waterproof, Men, Tee")

# Filter logic
filtered_df = df.copy()
if selected_brand != "All":
    filtered_df = filtered_df[filtered_df['metadata:brand'] == selected_brand]

if query:
    mask = (filtered_df['item_name'].str.contains(query, case=False, na=False) | 
            filtered_df['description'].str.contains(query, case=False, na=False))
    results = filtered_df[mask]
    
    st.write(f"Found {len(results)} matches")
    
    # Display Grid
    cols = st.columns(3)
    for i, row in results.reset_index().iterrows():
        with cols[i % 3]:
            # Prefer the item's own image URL from the CSV. If missing, fall back to
            # a brand-based tag for loremflickr, then to a cleaned item-name tag.
            img_src = row.get('image_url') if isinstance(row.get('image_url'), str) and row.get('image_url').strip() else None

            if not img_src:
                brand = row.get('metadata:brand', '')
                if isinstance(brand, str) and brand.strip():
                    tag = brand.split()[0]
                else:
                    stop = {'a', 'and', '&', 'seasonal', 'product', 'the'}
                    words = [w for w in str(row['item_name']).split() if w.lower().strip(',&') not in stop]
                    tag = words[0] if words else 'apparel'
                img_src = f"https://loremflickr.com/320/240/apparel,outdoor,{tag}"

            # Use a numeric width so Streamlit renders predictably
            st.image(img_src, width=320)
            st.subheader(row['item_name'])
            st.write(f"Price: ${row['metadata:price']}")
            st.divider()
else:
    st.info("Enter a keyword to see our 5,000 products.")