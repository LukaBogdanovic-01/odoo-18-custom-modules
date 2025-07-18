from odoo import _, api, fields, models


class AttachmentInherit(models.Model):
    _inherit = "ir.attachment"

    document_number = fields.Char(readonly=True)
    document_type_id = fields.Many2one("document.type")
    date_from = fields.Date()
    date_to = fields.Date()
    classification_plan_id = fields.Many2one("document.classification.plan")
    contact_id = fields.Many2one("res.partner")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("closed", "Closed"),
        ]
    )

    def generate_document_number(self, directory):
        # Provera da li direktorijum već ima dodeljen broj
        if not directory.directory_number:
            # Ako nema, generiši broj direktorijuma
            directory.directory_number = self.env["ir.sequence"].next_by_code(
                "document.directory.number"
            ) or _("New")

        # Prebroj postojeće dokumente u direktorijumu
        existing_docs_count = (
            self.env["ir.attachment"].search_count([("directory_id", "=", directory.id)]) + 1
        )  # Dodajemo 1 za trenutni dokument koji se kreira

        # Formiraj novi broj dokumenta
        document_number = "{}/{}".format(
            directory.directory_number, str(existing_docs_count).zfill(4)
        )
        return document_number

    @api.model_create_multi
    def create(self, vals_list):
        if "directory_id" in vals_list:
            directory_id = vals_list.get("directory_id")
            directory = self.env["document.directory"].browse(directory_id)
            vals_list["document_number"] = self.generate_document_number(directory)

        return super(AttachmentInherit, self).create(vals_list)
