import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import logging

# Setup logging
logging.basicConfig(filename='sku_mapper.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# SKU Mapper Class
class SKUMapper:
    def __init__(self, mapping_file):
        self.mapping_file = mapping_file
        self.mapping_df = self.load_mapping()

    def load_mapping(self):
        try:
            df = pd.read_excel(self.mapping_file)
            df.columns = [col.strip().upper() for col in df.columns]
            if 'SKU' not in df.columns or 'MSKU' not in df.columns:
                raise ValueError("Mapping sheet must contain 'SKU' and 'MSKU' columns.")
            return df[['SKU', 'MSKU']]
        except Exception as e:
            logging.error(f"Failed to load mapping: {e}")
            raise

    def map_skus(self, sales_df):
        sales_df.columns = [col.strip().upper() for col in sales_df.columns]
        if 'SKU' not in sales_df.columns:
            raise ValueError("Sales data must contain a 'SKU' column.")
        merged_df = sales_df.merge(self.mapping_df, on='SKU', how='left')
        missing = merged_df[merged_df['MSKU'].isna()]
        if not missing.empty:
            logging.warning(f"Missing mappings for SKUs: {missing['SKU'].tolist()}")
        return merged_df

# GUI Class
class SKUMapperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SKU to MSKU Mapper")
        self.root.geometry("400x200")
        self.mapper = None
        self.sales_file = None

        tk.Button(root, text="Load Mapping Sheet", command=self.load_mapping).pack(pady=10)
        tk.Button(root, text="Load Sales Data", command=self.load_sales).pack(pady=10)
        tk.Button(root, text="Map SKUs", command=self.map_data).pack(pady=10)

    def load_mapping(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            try:
                self.mapper = SKUMapper(file_path)
                messagebox.showinfo("Success", "Mapping sheet loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mapping sheet:\n{e}")

    def load_sales(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")])
        if file_path:
            self.sales_file = file_path
            messagebox.showinfo("Success", "Sales data loaded.")

    def map_data(self):
        if not self.mapper or not self.sales_file:
            messagebox.showerror("Error", "Please load both mapping sheet and sales data.")
            return
        try:
            if self.sales_file.endswith('.csv'):
                sales_df = pd.read_csv(self.sales_file)
            else:
                sales_df = pd.read_excel(self.sales_file)
            result_df = self.mapper.map_skus(sales_df)
            output_path = os.path.join(os.path.dirname(self.sales_file), "mapped_sales_output.xlsx")
            result_df.to_excel(output_path, index=False)
            messagebox.showinfo("Success", f"Mapping complete.\nOutput saved to:\n{output_path}")
        except Exception as e:
            logging.error(f"Error during mapping: {e}")
            messagebox.showerror("Error", f"Mapping failed:\n{e}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SKUMapperGUI(root)
    root.mainloop()
