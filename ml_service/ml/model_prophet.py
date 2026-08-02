from prophet import Prophet
import pandas as pd


def train_prophet_model(daily_df, weekly_seasonality=True, yearly_seasonality=False):
    model = Prophet(
        weekly_seasonality=weekly_seasonality,
        yearly_seasonality=yearly_seasonality,
        daily_seasonality=False,
        interval_width=0.9,
    )
    model.fit(daily_df)
    return model


def forecast_demand(model, periods=30, freq='D'):
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)


def compute_reorder_point(forecast_df, current_stock, lead_time_days=7, safety_factor=1.2):
    lead_time_demand = forecast_df.head(lead_time_days)['yhat'].sum()
    reorder_point = lead_time_demand * safety_factor
    stockout_date = None

    cumulative = 0
    for _, row in forecast_df.iterrows():
        cumulative += row['yhat']
        if current_stock - cumulative <= 0:
            stockout_date = row['ds']
            break

    return {
        'reorder_point': reorder_point,
        'estimated_stockout_date': stockout_date,
    }