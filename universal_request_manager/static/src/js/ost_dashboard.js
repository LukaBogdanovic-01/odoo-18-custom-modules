/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class OstDashboard extends Component {
    setup() {
        console.log("OST Dashboard component loaded");
    }
}
OstDashboard.template = "universal_request_manager.ost_dashboard_template";

// Registriramo akciju u registry, istim tagom kao i XML
registry.category("actions").add("ost_dashboard_client", OstDashboard);
