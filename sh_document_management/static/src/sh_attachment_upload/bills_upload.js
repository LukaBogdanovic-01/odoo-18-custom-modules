/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { ListController } from "@web/views/list/list_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanDropdownMenuWrapper } from "@web/views/kanban/kanban_dropdown_menu_wrapper";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { FileUploader } from "@web/views/fields/file_handler";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

const { Component, useState } = owl;

export class DirectoryFileUploader extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.attachmentIdsToProcess = [];
        const rec = this.props.record ? this.props.record.data : false;
        this.extraContext = rec ? {
            default_journal_id: rec.id,
            default_move_type: (rec.type === 'sale' && 'out_invoice') || (rec.type === 'purchase' && 'in_invoice') || 'entry',
        } : this.props.extraContext || {}; //TODO remove this.props.extraContext
    }

    async onFileUploaded(file) {
        const att_data = {
            name: file.name,
            mimetype: file.type,
            datas: file.data,
        };
        const att_id = await this.orm.create("ir.attachment", [att_data], {
            context: { ...this.extraContext, ...this.env.searchModel.context },
        });
        this.attachmentIdsToProcess.push(att_id);
    }

    async onUploadComplete() {
        const action = await this.orm.call("account.journal", "create_document_from_attachment", ["", this.attachmentIdsToProcess], {
            context: { ...this.extraContext, ...this.env.searchModel.context },
        });
        this.attachmentIdsToProcess = [];
        if (action.context && action.context.notifications) {
            for (let [file, msg] of Object.entries(action.context.notifications)) {
                this.notification.add(
                    msg,
                    {
                        title: file,
                        type: "info",
                        sticky: true,
                    });
            }
            delete action.context.notifications;
        }
        this.action.doAction(action);
    }
}
DirectoryFileUploader.components = {
    FileUploader,
};
DirectoryFileUploader.template = "account.DirectoryFileUploader";
DirectoryFileUploader.extractProps = ({ attrs }) => ({
    togglerTemplate: attrs.template || "account.JournalUploadLink",
    btnClass: attrs.btnClass || "",
    linkText: attrs.linkText || _lt("Upload"),
});
DirectoryFileUploader.props = {
    ...standardWidgetProps,
    record: { type: Object, optional: true },
    togglerTemplate: { type: String, optional: true },
    btnClass: { type: String, optional: true },
    linkText: { type: String, optional: true },
    slots: { type: Object, optional: true },
    extraContext: { type: Object, optional: true }, //this prop is only for stable databases with the old journal dashboard view, it should be deleted in master as it is not used
}
//when file uploader is used on account.journal (with a record)
DirectoryFileUploader.fieldDependencies = {
    id: { type: "integer" },
    type: { type: "selection" },
};

registry.category("view_widgets").add("directory_file_uploader", DirectoryFileUploader);

export class DirectoryDropZone extends Component {
    setup() {
        this.notificationService = useService("notification");
    }

    onDrop(ev) {
        const selector = '.directory_file_uploader.o_input_file.o_hidden';
        // look for the closest uploader Input as it may have a context
        let uploadInput = ev.target.closest('.o_drop_area').parentElement.querySelector(selector) || document.querySelector(selector);
        let files = ev.dataTransfer ? ev.dataTransfer.files : false;
        if (uploadInput && !!files) {
            uploadInput.files = ev.dataTransfer.files;
            uploadInput.dispatchEvent(new Event("change"));
        } else {
            this.notificationService.add(
                this.env._t("Could not upload files"),
                {
                    type: "danger",
                });
        }
        this.props.hideZone();
    }
}
DirectoryDropZone.defaultProps = {
    hideZone: () => { },
};
DirectoryDropZone.template = "account.DropZone";

// Account Move List View
export class AccountMoveUploadListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.state.dropzoneVisible = false;
    }
}
AccountMoveUploadListRenderer.template = "account.ListRenderer";
AccountMoveUploadListRenderer.components = {
    ...ListRenderer.components,
    DirectoryDropZone,
};

export class AccountMoveUploadListController extends ListController { }
AccountMoveUploadListController.components = {
    ...ListController.components,
    DirectoryFileUploader,
};

export const AccountMoveUploadListView = {
    ...listView,
    Controller: AccountMoveUploadListController,
    Renderer: AccountMoveUploadListRenderer,
    buttonTemplate: "account.ListView.Buttons",
};

// Account Move Kanban View
export class AccountMoveUploadKanbanRenderer extends KanbanRenderer {
    setup() {
        super.setup();
        this.state.dropzoneVisible = false;
    }
}
AccountMoveUploadKanbanRenderer.template = "account.KanbanRenderer";
AccountMoveUploadKanbanRenderer.components = {
    ...KanbanRenderer.components,
    DirectoryDropZone,
};

export class AccountMoveUploadKanbanController extends KanbanController { }
AccountMoveUploadKanbanController.components = {
    ...KanbanController.components,
    DirectoryFileUploader,
};

export const AccountMoveUploadKanbanView = {
    ...kanbanView,
    Controller: AccountMoveUploadKanbanController,
    Renderer: AccountMoveUploadKanbanRenderer,
    buttonTemplate: "account.KanbanView.Buttons",
};

// Accounting Dashboard
export class DashboardKanbanDropdownMenuWrapper extends KanbanDropdownMenuWrapper {
    onClick(ev) {
        // Keep the dropdown open as we need the fileuploader to remain in the dom
        if (!ev.target.tagName === "INPUT" && !ev.target.closest('.file_upload_kanban_action_a')) {
            super.onClick(ev);
        }
    }
}
export class DashboardKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
        this.state = useState({
            dropzoneVisible: false,
        });
    }
}
DashboardKanbanRecord.components = {
    ...DashboardKanbanRecord.components,
    DirectoryDropZone,
    DirectoryFileUploader,
    KanbanDropdownMenuWrapper: DashboardKanbanDropdownMenuWrapper,
};
DashboardKanbanRecord.template = "account.DashboardKanbanRecord";

export class DashboardKanbanRenderer extends KanbanRenderer { }
DashboardKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: DashboardKanbanRecord,
};

export const DashboardKanbanView = {
    ...kanbanView,
    Renderer: DashboardKanbanRenderer,
};

registry.category("views").add("account_tree", AccountMoveUploadListView);
registry.category("views").add("account_documents_kanban", AccountMoveUploadKanbanView);
registry.category("views").add("account_dashboard_kanban", DashboardKanbanView);
