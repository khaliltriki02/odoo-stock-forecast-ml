from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

from ml.model_prophet import train_prophet_model, forecast_demand, compute_reorder_point
from ml.model_sklearn import train_sklearn_model, predict_next_n_days
from ml.preprocessing import add_features

app = FastAPI(title="ML Inventory Forecast Service")


class StockMove(BaseModel):
    date: str
    quantity: float


class PredictRequest(BaseModel):
    product_id: int
    history: List[StockMove]
    current_stock: float
    lead_time_days: int = 7
    periods: int = 30
    model: str = "prophet"


class PredictResponse(BaseModel):
    product_id: int
    predicted_demand_total: float
    predicted_stock_level: float
    reorder_point: float
    estimated_stockout_date: Optional[str]
    model_used: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if len(req.history) < 10:
        raise HTTPException(status_code=400, detail="Historique insuffisant (minimum 10 points)")

    daily_df = pd.DataFrame([{"ds": h.date, "y": h.quantity} for h in req.history])
    daily_df["ds"] = pd.to_datetime(daily_df["ds"])
    daily_df = daily_df.sort_values("ds").reset_index(drop=True)

    if req.model == "prophet":
        model = train_prophet_model(daily_df)
        forecast = forecast_demand(model, periods=req.periods)
        result = compute_reorder_point(forecast, req.current_stock, req.lead_time_days)
        predicted_demand_total = float(forecast["yhat"].sum())
        stockout_date = str(result["estimated_stockout_date"]) if result["estimated_stockout_date"] is not None else None

        return PredictResponse(
            product_id=req.product_id,
            predicted_demand_total=predicted_demand_total,
            predicted_stock_level=req.current_stock - predicted_demand_total,
            reorder_point=result["reorder_point"],
            estimated_stockout_date=stockout_date,
            model_used="prophet",
        )

    elif req.model == "sklearn":
        featured = add_features(daily_df)
        if len(featured) < 10:
            raise HTTPException(status_code=400, detail="Pas assez de données après feature engineering")
        model, metrics = train_sklearn_model(featured)
        preds = predict_next_n_days(model, featured, n_days=req.periods)
        predicted_demand_total = float(sum(preds))
        lead_time_demand = float(sum(preds[:req.lead_time_days]))

        return PredictResponse(
            product_id=req.product_id,
            predicted_demand_total=predicted_demand_total,
            predicted_stock_level=req.current_stock - predicted_demand_total,
            reorder_point=lead_time_demand * 1.2,
            estimated_stockout_date=None,
            model_used="sklearn",
        )

    else:
        raise HTTPException(status_code=400, detail="Modèle inconnu (utiliser 'prophet' ou 'sklearn')")