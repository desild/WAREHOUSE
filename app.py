import streamlit as st
import pandas as pd
import requests
import io

# SKUMapper class from Part 1
class SKUMapper:
    def __init__(self, mapping_df):
        self.mapping_df = mapping_df
        self.mapping_df.columns = [col.strip().upper() for col in mapping_df.columns]

    def map_skus(self, sales_df):
        sales_df.columns = [col.strip().upper() for col in sales_df.columns]
        if 'SKU' not in sales_df.columns:
            raise ValueError("Sales data must contain a 'SKU' column.")
        merged_df = sales_df.merge(self.mapping_df, on='SKU', how='left')
        return merged_df

# Baserow push function
def push_to_baserow(df, baserow_url, token, table_id):
    headers = {"Authorization": f"Token {token}"}
    for _, row in df.iterrows():
        payload = {
            "SKU": row.get("SKU", ""),
            "MSKU": row.get("MSKU", ""),
            "Quantity": row.get("QUANTITY", 0),
            "Amount": row.get("AMOUNT", 0),
        }
        requests.post(f"{baserow_url}/api/database/rows/table/{table_id}/", headers=headers, json=payload)

# Streamlit UI
st.set_page_config(page_title="WMS - SKU Mapper", layout="centered")
st.title("📦 WMS - SKU to MSKU Mapper")

# Upload mapping
mapping_file = st.file_uploader("Upload SKU-MSKU Mapping Sheet (.xlsx)", type=["xlsx"])
sales_file = st.file_uploader("Upload Sales Data (.xlsx or .csv)", type=["xlsx", "csv"])

if mapping_file and sales_file:
    try:
        mapping_df = pd.read_excel(mapping_file)
        if sales_file.name.endswith('.csv'):
            sales_df = pd.read_csv(sales_file)
        else:
            sales_df = pd.read_excel(sales_file)

        mapper = SKUMapper(mapping_df)
        result_df = mapper.map_skus(sales_df)

        st.success("Mapping completed ✅")
        st.dataframe(result_df.head())

        csv_buffer = io.BytesIO()
        result_df.to_excel(csv_buffer, index=False)
        st.download_button("Download Mapped Output", data=csv_buffer.getvalue(), file_name="mapped_output.xlsx")

        with st.expander("🔌 Push to Baserow"):
            baserow_url = st.text_input("Baserow API Base URL", placeholder="https://api.baserow.io")
            token = st.text_input("Baserow Token", type="password")
            table_id = st.text_input("Table ID (Sales)", placeholder="12345")
            if st.button("Push Data"):
                push_to_baserow(result_df, baserow_url, token, table_id)
                st.success("Data pushed to Baserow 🎉")

    except Exception as e:
        st.error(f"❌ Error: {e}")
