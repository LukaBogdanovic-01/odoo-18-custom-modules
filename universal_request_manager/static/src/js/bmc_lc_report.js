/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { orm } from "@web/core/orm_service";   // ✅ koristimo orm servis

// helper funkcija za čišćenje HTML-a
function stripHtml(html) {
    let div = document.createElement("div");
    div.innerHTML = html || "";
    return div.textContent || div.innerText || "";
}

export class BMCReportClient extends Component {
    setup() {
        this.state = useState({ canvas: null });
        const ormService = this.env.services.orm;

        onWillStart(async () => {
            // Uzmi prvi canvas iz baze (za test)
            const canvases = await ormService.searchRead(
                "bmc.canvas",
                [], // domain
                ["id", "name", "date", "planner_id", "item_ids"], // fields
                { limit: 1 }
            );

            if (canvases.length) {
                const canvas = canvases[0];

                // učitaj iteme povezane sa canvasom
                let items = await ormService.read(
                    "bmc.item",
                    canvas.item_ids,
                    ["id", "name", "goal", "result", "block"]
                );

                // očisti HTML u goal i result
                items = items.map(i => ({
                    ...i,
                    goal: stripHtml(i.goal),
                    result: stripHtml(i.result),
                }));

                canvas.item_ids = items;
                this.state.canvas = canvas;
            }
        });
    }
}
BMCReportClient.template = "universal_request_manager.bmc_report_template";

registry.category("actions").add("bmc_report", BMCReportClient);



export class LCReportClient extends Component {
    setup() {
        this.state = useState({ canvas: null });
        const ormService = this.env.services.orm;

        onWillStart(async () => {
            // Uzmi prvi canvas iz baze (za test)
            const canvases = await ormService.searchRead(
                "lc.canvas",
                [], // domain
                ["id", "name", "date", "planner_id", "item_ids"], // fields
                { limit: 1 }
            );

            if (canvases.length) {
                const canvas = canvases[0];

                // učitaj iteme povezane sa canvasom
                let items = await ormService.read(
                    "lc.item",
                    canvas.item_ids,
                    ["id", "name", "goal", "result", "block"]
                );

                // očisti HTML u goal i result
                items = items.map(i => ({
                    ...i,
                    goal: stripHtml(i.goal),
                    result: stripHtml(i.result),
                }));

                canvas.item_ids = items;
                this.state.canvas = canvas;
            }
        });
    }
}
LCReportClient.template = "universal_request_manager.lc_report_template";

registry.category("actions").add("lc_report", LCReportClient);

console.log("✅ bmc_lc_report.js loaded");
