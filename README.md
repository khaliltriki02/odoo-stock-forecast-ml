# ML Inventory Forecast for Odoo

An Odoo 17 application for forecasting product demand and identifying stockout risk. The project combines a custom Odoo inventory module with a FastAPI machine-learning service that supports Prophet and Scikit-learn forecasts.

## What it includes

- `addons/ml_inventory_forecast` — Odoo module that stores forecasts, calculates risk levels, and provides the dashboard.
- `ml_service` — FastAPI service that trains a model from completed stock moves and returns demand and reorder-point predictions.
- PostgreSQL 15 — database used by Odoo.
- `docker-compose.yml` — local development stack for all services.

## Requirements

- Docker Desktop with Docker Compose v2
- At least 10 completed stock moves for a product before running a forecast

## Quick start

Start the complete stack from the project root:

```bash
docker compose up --build
```

Open Odoo at [http://localhost:8069](http://localhost:8069), create or select a database, then:

1. Enable developer mode if necessary.
2. Go to **Apps** and update the Apps List.
3. Search for **ML Inventory Forecast** and install it.
4. Create a forecast record for a product with sufficient completed stock history, choose a model, and run the forecast.

The ML service health check is available at [http://localhost:8000/health](http://localhost:8000/health).

Stop the services with:

```bash
docker compose down
```

To also remove the persisted PostgreSQL volume (this deletes local Odoo databases), run:

```bash
docker compose down -v
```

## Services and ports

| Service | Container | Address | Purpose |
| --- | --- | --- | --- |
| Odoo | `odoo-app` | `http://localhost:8069` | Odoo web application and custom module |
| PostgreSQL | `odoo-db` | `localhost:5432` | Odoo database |
| ML service | `ml-forecast-service` | `http://localhost:8000` | Forecasting API |

For the bundled local setup, PostgreSQL uses database `postgres`, username `odoo`, and password `odoo`. Change these credentials before using the stack outside local development.

## Forecasting workflow

When a forecast is run, the Odoo module reads completed `stock.move.line` records for the selected product and sends their dates and quantities to `POST /predict`. The service returns:

- total predicted demand over the requested period;
- predicted remaining stock;
- suggested reorder point;
- estimated stockout date (Prophet only);
- model used.

The module classifies stockout risk as high when predicted stock is zero or below, medium when it is below 20% of the current quantity, and low otherwise.

## ML service API

### `GET /health`

Returns a simple readiness response:

```json
{"status":"ok"}
```

### `POST /predict`

Example request:

```json
{
  "product_id": 42,
  "history": [
    {"date": "2026-01-01", "quantity": 12},
    {"date": "2026-01-02", "quantity": 9}
  ],
  "current_stock": 150,
  "lead_time_days": 7,
  "periods": 30,
  "model": "prophet"
}
```

`history` must contain at least 10 data points. Use `model: "prophet"` for Prophet forecasting or `model: "sklearn"` for the Scikit-learn model.

Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) while the service is running.

## Development

Source changes are mounted into both the Odoo and ML-service containers. Restart the relevant service after Python changes:

```bash
docker compose restart ml_service
docker compose restart odoo
```

After changing Odoo module Python, XML, security, or frontend assets, upgrade the **ML Inventory Forecast** module from Odoo's Apps page (or via the Odoo command line) to apply the changes.

## Project layout

```text
.
├── addons/
│   └── ml_inventory_forecast/   # Odoo module
├── ml_service/
│   ├── ml/                      # Preprocessing and ML implementations
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```

## License

The Odoo module is licensed under LGPL-3. See the module manifest for details. Navitrends 
