import pandas as pd
import numpy as np


def load_stock_moves(csv_path=None, df=None):
    if df is None:
        df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    return df


def build_daily_demand(df, product_id):
    product_df = df[df['product_id'] == product_id].copy()
    daily = product_df.groupby(product_df['date'].dt.date)['quantity'].sum().reset_index()
    daily.columns = ['ds', 'y']
    daily['ds'] = pd.to_datetime(daily['ds'])
    full_range = pd.date_range(daily['ds'].min(), daily['ds'].max(), freq='D')
    daily = daily.set_index('ds').reindex(full_range, fill_value=0).rename_axis('ds').reset_index()
    return daily


def add_features(daily_df):
    df = daily_df.copy()
    df['dayofweek'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month
    df['lag_1'] = df['y'].shift(1)
    df['lag_7'] = df['y'].shift(7)
    df['rolling_mean_7'] = df['y'].rolling(7).mean()
    df['rolling_std_7'] = df['y'].rolling(7).std()
    df = df.dropna().reset_index(drop=True)
    return df