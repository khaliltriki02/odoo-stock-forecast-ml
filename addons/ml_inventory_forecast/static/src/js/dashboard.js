/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onPatched, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MlForecastDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            data: null,
            productData: null,
        });
        this.pieCanvas = useRef("pieCanvas");
        this.lineCanvas = useRef("lineCanvas");
        this.pieChart = null;
        this.lineChart = null;

        onWillStart(async () => {
            await this.loadDashboard();
        });

        onMounted(() => this.updateCharts());
        onPatched(() => this.updateCharts());
    }

    async loadDashboard() {
        const data = await this.orm.call("stock.forecast", "get_dashboard_data", []);
        this.state.data = data;
        this.state.loading = false;
        if (data.products.length > 0) {
            await this.selectProduct(data.products[0].product_id);
        }
    }

    async selectProduct(productId) {
        const productData = await this.orm.call("stock.forecast", "get_product_timeseries", [productId]);
        this.state.productData = productData;
    }

    async onSelectProduct(ev) {
        await this.selectProduct(parseInt(ev.target.value));
    }

    updateCharts() {
        this.renderPieChart();
        this.renderLineChart();
    }

    renderPieChart() {
        if (!this.pieCanvas.el || !this.state.data) return;
        const counts = this.state.data.risk_counts;
        if (this.pieChart) this.pieChart.destroy();
        this.pieChart = new Chart(this.pieCanvas.el, {
            type: "doughnut",
            data: {
                labels: ["Risque élevé", "Risque moyen", "Risque faible"],
                datasets: [{
                    data: [counts.high, counts.medium, counts.low],
                    backgroundColor: ["#dc3545", "#ffc107", "#28a745"],
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } },
            },
        });
    }

    renderLineChart() {
        if (!this.lineCanvas.el || !this.state.productData) return;
        const hist = this.state.productData.history;
        const labels = hist.map((h) => h.date);
        const values = hist.map((h) => h.quantity);

        if (this.lineChart) this.lineChart.destroy();
        this.lineChart = new Chart(this.lineCanvas.el, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Demande réelle (historique)",
                    data: values,
                    borderColor: "#5b47e0",
                    backgroundColor: "rgba(91,71,224,0.15)",
                    tension: 0.3,
                    fill: true,
                    pointRadius: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } },
                scales: { y: { beginAtZero: true } },
            },
        });
    }
}

MlForecastDashboard.template = "ml_inventory_forecast.Dashboard";

registry.category("actions").add("ml_forecast_dashboard", MlForecastDashboard);