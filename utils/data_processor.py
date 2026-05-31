import pandas as pd
import numpy as np


class DataProcessor:
    """
    Handles data loading, cleaning, and mean imputation.
    Implements data wrangling concepts from the project proposal.
    """

    def load_sample_data(self) -> pd.DataFrame:
        """
        Returns a realistic sample dataset for a small Pakistani retail shop.
        10-day sales history + current stock levels.
        """
        data = {
            'product': [
                'Tapal Tea (200g)',
                'Lipton Yellow Label',
                'Dalda Cooking Oil (1L)',
                'Surf Excel (500g)',
                'Lays Chips (Classic)',
                'Pepsi (1.5L)',
                'Sunsilk Shampoo',
                'Colgate Toothpaste',
                'Walls Ice Cream',
                'Gol Biscuits',
                'Shan Masala Mix',
                'Nestle Mineral Water'
            ],
            'day_1':  [5, 3, 4, 2, 8, 10, 1, 2, 6, 12, 3, 15],
            'day_2':  [4, 4, 3, 3, 9, 8,  2, 1, 5, 10, 2, 18],
            'day_3':  [6, 2, 5, np.nan, 7, 12, 1, 3, 7, 11, 4, 14],
            'day_4':  [5, 3, 4, 2, 10, 9, np.nan, 2, 4, 13, 3, 20],
            'day_5':  [7, 4, 6, 3, 8, 11, 2, 1, 6, 9,  3, 16],
            'day_6':  [4, np.nan, 3, 2, 9, 10, 1, 2, 8, 14, 2, 17],
            'day_7':  [6, 3, 5, 4, 11, 13, 2, 3, 5, 12, 4, 19],
            'day_8':  [5, 4, 4, 2, 7, 8,  1, 2, 6, 10, 3, 15],
            'day_9':  [7, 3, 6, np.nan, 9, 10, 2, 1, 7, 13, 3, 22],
            'day_10': [6, 4, 5, 3, 10, 12, 2, 2, 5, 11, 4, 18],
            'current_stock': [12, 8, 20, 6, 85, 24, 5, 15, 14, 30, 18, 45]
        }
        
        df = pd.DataFrame(data)
        df = self._clean_data(df)
        return df

  def process_uploaded_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
    """Process user-uploaded CSV after basic validation."""
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    if 'product_id' in df_raw.columns and 'product' not in df_raw.columns:
        # This file has Date, Product_ID, Units_Sold, Stock_Left format
        # Convert to our required format: product, day_1..day_10, current_stock
        df_raw['date'] = pd.to_datetime(df_raw['date'])
        df_raw = df_raw.sort_values('date', ascending=False)
        
        latest_date = df_raw['date'].max()
        current_stock_map = df_raw[df_raw['date'] == latest_date].set_index('product_id')['stock_left'].to_dict()
        
        last_10_dates = sorted(df_raw['date'].unique())[-10:]
        df_10 = df_raw[df_raw['date'].isin(last_10_dates)]
        
        records = []
        for pid in df_raw['product_id'].unique():
            p_data = df_10[df_10['product_id'] == pid].sort_values('date', ascending=False)
            sales = p_data['units_sold'].values[:10]
            import numpy as np
            while len(sales) < 10:
                sales = np.append(sales, int(np.mean(sales)))
            row = {'product': pid}
            for i, s in enumerate(sales[:10]):
                row[f'day_{i+1}'] = int(s)
            row['current_stock'] = current_stock_map.get(pid, 0)
            records.append(row)
        
        df_raw = pd.DataFrame(records)
    
    df_raw = self._clean_data(df_raw)
    return df_raw

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Data wrangling:
        - Identifies sales day columns
        - Applies mean imputation on missing values (NaN)
        - Ensures correct dtypes
        """
        day_cols = [c for c in df.columns if c.startswith('day_')]
        
        for col in day_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        row_means = df[day_cols].mean(axis=1)
        for col in day_cols:
            df[col] = df[col].fillna(row_means)
        
        df['current_stock'] = pd.to_numeric(df['current_stock'], errors='coerce').fillna(0)
        
        return df
