/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";

class AutoSaveFormController extends FormController {
    async commitChanges(record, ...args) {
        const res = await super.commitChanges(record, ...args);

        const autosaveModels = ["gap.analysis2", "swot.analysis2", "bmc.analysis2"];
        if (record && record.isDirty && autosaveModels.includes(this.props.resModel)) {
            try {
                // 👉 umjesto saveRecord, koristi model.save()
                await this.model.save({ stayInEdition: true });
                console.log("✅ Auto-saved (with UI refresh)", this.props.resModel);
            } catch (e) {
                console.error("❌ AutoSave error:", e);
            }
        }
        return res;
    }
}

const formView = registry.category("views").get("form");
registry.category("views").remove("form");
registry.category("views").add("form", {
    ...formView,
    Controller: AutoSaveFormController,
});
