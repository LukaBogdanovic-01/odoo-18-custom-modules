/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/* --------------------
   Postojeći dashboard
-------------------- */
export class OstDashboard extends Component {
    setup() {
        console.log("OST Dashboard component loaded");
    }
}
OstDashboard.template = "universal_request_manager.ost_dashboard_template";
registry.category("actions").add("ost_dashboard_client", OstDashboard);


/* --------------------
   Novi workflow board
-------------------- */
export class OstWorkflowBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");   // dodato da možemo otvarati form view

        this.state = useState({
            goal: null,
            opportunities: [],
            solutions: [],
            experiments: [],
        });

        const activeId = this.props.action.context.active_id;
        console.log("Workflow Board opened for Outcome ID:", activeId);

        // Učitaj podatke prije renderovanja
        onWillStart(async () => {
            // 1) Cilj
            const [goal] = await this.orm.call(
                "ost.outcome",
                "read",
                [[activeId], ["id", "name", "description"]]
            );
            this.state.goal = goal;

            // 2) Prilike
            this.state.opportunities = await this.orm.searchRead(
                "ost.opportunity",
                [["outcome_id", "=", activeId]],
                ["id", "name", "description", "color"]
            );

            // 3) Rješenja
            this.state.solutions = await this.orm.searchRead(
                "ost.solution",
                [["opportunity_id.outcome_id", "=", activeId]],
                ["id", "name", "description", "opportunity_id", "color"]
            );

            // 4) Eksperimenti
            this.state.experiments = await this.orm.searchRead(
                "ost.experiment",
                [["solution_id.opportunity_id.outcome_id", "=", activeId]],
                ["id", "name", "method", "status", "solution_id", "color"]
            );
        });
    }

    // Klik na karticu otvara njen form view
    onCardClick(ev) {
        const id = ev.currentTarget.dataset.id;
        const model = ev.currentTarget.dataset.model;
        if (id && model) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: model,
                res_id: parseInt(id),
                views: [[false, "form"]],
                target: "current",
            });
        }
    }
}
OstWorkflowBoard.template = "universal_request_manager.ost_workflow_board_template";
registry.category("actions").add("ost_workflow_board", OstWorkflowBoard);
