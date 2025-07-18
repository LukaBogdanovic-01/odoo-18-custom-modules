from odoo import _, api, fields, models


class DocumentDirectoryInherit(models.Model):
    _inherit = "document.directory"

    directory_number = fields.Char(
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"),
    )
    directory_type_id = fields.Many2one("directory.type")
    classification_plan_id = fields.Many2one("document.classification.plan")
    department_id = fields.Many2one("hr.department")
    signature_plan_id = fields.Many2one("document.signature.plan")
    partner_type = fields.Selection([
        ("individial", "Individual"),
        ("company", "Company")
    ])
    partner_id = fields.Many2one("res.partner")
    note = fields.Text()

    # Ovo su "realna" many2many polja koja se koriste kao filter iz XML
    sh_user_ids_domain = fields.Many2many("res.users", string="Korisnici za filter")
    partner_type_domain = fields.Many2many("res.partner", string="Partneri za filter")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("directory_number", _("New")) == _("New"):
                vals["directory_number"] = self.env["ir.sequence"].next_by_code(
                    "document.directory.number"
                ) or _("New")
        return super(DocumentDirectoryInherit, self).create(vals_list)

    @api.onchange("department_id")
    def _onchange_department_id(self):
        if self.department_id:
            users = self.env["res.users"].search([("department_id", "=", self.department_id.id)])
            self.sh_user_ids_domain = [(6, 0, users.ids)]
        else:
            self.sh_user_ids_domain = [(5,)]

    @api.onchange("partner_type")
    def _onchange_partner_type(self):
        if self.partner_type:
            partners = self.env["res.partner"].search([
                ("is_company", "=", self.partner_type == "company")
            ])
            self.partner_type_domain = [(6, 0, partners.ids)]
        else:
            self.partner_type_domain = [(5,)]
