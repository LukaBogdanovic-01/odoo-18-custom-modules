/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { orm } from "@web/core/orm_service";

// helper funkcija za čišćenje HTML-a
function stripHtml(html) {
    let div = document.createElement("div");
    div.innerHTML = html || "";
    return div.textContent || div.innerText || "";
}

export class GapAnalysisReportClient extends Component {
    setup() {
        this.state = useState({ analysis: null });
        const ormService = this.env.services.orm;

        onWillStart(async () => {
            // Uzmi prvu analizu iz baze (za test)
            const analyses = await ormService.searchRead(
                "gap.analysis",
                [],
                ["id", "name", "project_id", "item_ids"], // dodaj item_ids ako postoje
                { limit: 1 }
            );
            console.log("🔍 Analyses loaded:", analyses);

            if (analyses.length) {
                const analysis = analyses[0];

                // ako postoji model gap.analysis.item
                if (analysis.item_ids && analysis.item_ids.length) {
                    let items = await ormService.read(
                        "gap.analysis.item",
                        analysis.item_ids,
                        ["id", "name", "description", "gap_analysis_id", "type"]
                    );

                    // očisti HTML u description
                    items = items.map(i => ({
                        ...i,
                        description: stripHtml(i.description),
                    }));

                    analysis.item_ids = items;
                }

                this.state.analysis = analysis;
            }
        });
    }
}

GapAnalysisReportClient.template = "universal_request_manager.gap_analysis_report_template";

registry.category("actions").add("gap_analysis_report_client", GapAnalysisReportClient);

console.log("✅ gap_report.js loaded");
