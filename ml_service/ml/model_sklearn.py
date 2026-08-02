from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd
import joblib


FEATURES = ['dayofweek', 'month', 'lag_1', 'lag_7', 'rolling_mean_7', 'rolling_std_7']


def train_sklearn_model(featured_df, n_estimators=200, max_depth=8):
    X = featured_df[FEATURES]
    y = featured_df['y']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
    }
    return model, metrics


def predict_next_n_days(model, featured_df, n_days=30):
    history = featured_df.copy()
    predictions = []

    for i in range(n_days):
        last_row = history.iloc[-1]
        next_features = {
            'dayofweek': (last_row['dayofweek'] + 1) % 7,
            'month': last_row['month'],
            'lag_1': last_row['y'],
            'lag_7': history.iloc[-7]['y'] if len(history) >= 7 else last_row['y'],
            'rolling_mean_7': history['y'].tail(7).mean(),
            'rolling_std_7': history['y'].tail(7).std(),
        }
        X_next = np.array([[next_features[f] for f in FEATURES]])
        pred = model.predict(X_next)[0]
        predictions.append(pred)

        new_row = last_row.copy()
        new_row['y'] = pred
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    return predictions


def save_model(model, path='models/sklearn_model.pkl'):
    joblib.dump(model, path)


def load_model(path='models/sklearn_model.pkl'):
    return joblib.load(path)