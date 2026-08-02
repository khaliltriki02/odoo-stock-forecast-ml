import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

ML_SERVICE_URL = "http://ml_service:8000"


class StockForecast(models.Model):
    _name = 'stock.forecast'
    _description = 'Prévision de stock ML'
    _order = 'forecast_date desc'

    product_id = fields.Many2one('product.product', string='Produit', required=True)
    forecast_date = fields.Date(string='Date de prévision', required=True, default=fields.Date.today)
    predicted_demand = fields.Float(string='Demande prédite')
    predicted_stock_level = fields.Float(string='Niveau de stock prédit')
    reorder_point_suggested = fields.Float(string='Seuil de réappro suggéré')
    estimated_stockout_date = fields.Date(string='Date de rupture estimée')
    model_used = fields.Selection([
        ('prophet', 'Prophet'),
        ('sklearn', 'Scikit-learn'),
    ], string='Modèle utilisé', default='prophet')
    stockout_risk = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
    ], string='Risque de rupture', compute='_compute_stockout_risk', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('predicted_stock_level', 'product_id')
    def _compute_stockout_risk(self):
        for rec in self:
            if not rec.product_id:
                rec.stockout_risk = 'low'
                continue
            current_qty = rec.product_id.qty_available
            if rec.predicted_stock_level <= 0:
                rec.stockout_risk = 'high'
            elif current_qty and rec.predicted_stock_level < current_qty * 0.2:
                rec.stockout_risk = 'medium'
            else:
                rec.stockout_risk = 'low'

    def _get_stock_history(self, product):
        moves = self.env['stock.move.line'].search([
            ('product_id', '=', product.id),
            ('state', '=', 'done'),
        ], order='date asc')
        history = []
        for m in moves:
            if m.date:
                history.append({
                    "date": m.date.strftime('%Y-%m-%d'),
                    "quantity": m.quantity,
                })
        return history

    def action_run_forecast(self):
        for rec in self:
            history = rec._get_stock_history(rec.product_id)

            if len(history) < 10:
                raise UserError(
                    "Historique insuffisant pour '%s' (%d mouvements trouvés, minimum 10 requis)."
                    % (rec.product_id.name, len(history))
                )

            payload = {
                "product_id": rec.product_id.id,
                "history": history,
                "current_stock": rec.product_id.qty_available,
                "lead_time_days": 7,
                "periods": 30,
                "model": rec.model_used or "prophet",
            }

            try:
                response = requests.post(ML_SERVICE_URL + "/predict", json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()

                rec.write({
                    'predicted_demand': data['predicted_demand_total'],
                    'predicted_stock_level': data['predicted_stock_level'],
                    'reorder_point_suggested': data['reorder_point'],
                    'estimated_stockout_date': data.get('estimated_stockout_date'),
                })
            except requests.exceptions.RequestException as e:
                _logger.error("Erreur lors de l'appel au service ML: %s", e)
                raise UserError("Impossible de contacter le service de prédiction: %s" % e)

        return True

    @api.model
    def get_products_at_risk(self, risk_level='high'):
        return self.search([
            ('stockout_risk', '=', risk_level),
            ('forecast_date', '>=', fields.Date.today()),
        ])