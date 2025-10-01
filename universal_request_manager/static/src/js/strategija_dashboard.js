/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class StrategijaDashboard extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({ strategijaName: "" });

        const activeId = this.props.action.context.active_id;
        console.log("Strategija Dashboard opened for ID:", activeId);

        if (activeId) {
            this.loadStrategijaName(activeId);
        }
    }

    async loadStrategijaName(activeId) {
        try {
            const result = await this.orm.read(
                "biz.strategija",
                [activeId],
                ["name"]
            );
            if (result.length) {
                this.state.strategijaName = result[0].name;
            }
        } catch (err) {
            console.error("Greška prilikom čitanja strategije:", err);
        }
    }

    async openModel(ev) {
        const model = ev.currentTarget.dataset.model;
        const activeId = this.props.action.context.active_id;

        if (model && activeId) {
            try {
                // provjeri postoji li već zapis za ovu strategiju
                const existing = await this.orm.searchRead(
                    model,
                    [["strategija_id", "=", activeId]],
                    ["id"]
                );

                if (existing.length) {
                    // postoji -> otvori ga
                    this.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: model,
                        res_id: existing[0].id,
                        views: [[false, "form"]],
                        target: "current",
                        context: {
                            default_strategija_id: activeId,
                            from_dashboard: true,   // isti context kao u else
                        },
                    });
                } else {
                    // ne postoji -> otvori novu formu, popuni strategiju
                    this.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: model,
                        views: [[false, "form"]],
                        target: "current",
                        context: {
                            default_strategija_id: activeId,
                            from_dashboard: true,
                        },
                    });
                }
            } catch (err) {
                console.error("Greška prilikom otvaranja modela:", err);
            }
        }
    }
}

StrategijaDashboard.template = "universal_request_manager.strategija_dashboard_template";
registry.category("actions").add("strategija_dashboard", StrategijaDashboard);
