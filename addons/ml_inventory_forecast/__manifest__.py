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
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}