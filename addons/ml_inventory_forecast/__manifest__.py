{
    'name': 'ML Inventory Forecast',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Prédiction intelligente des stocks avec Prophet / Scikit-learn',
    'description': """
        Module de forecasting ML pour la gestion des inventaires.
        - Anticipation des ruptures de stock
        - Optimisation des seuils de réapprovisionnement
        - Dashboards analytiques
    """,
    'author': 'Khalil Triki',
    'depends': ['stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_forecast_views.xml',
        'views/dashboard_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
            'ml_inventory_forecast/static/src/js/dashboard.js',
            'ml_inventory_forecast/static/src/xml/dashboard.xml',
            'ml_inventory_forecast/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}