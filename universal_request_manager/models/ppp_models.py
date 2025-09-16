from odoo import models, fields, api

class PPPAnalysis(models.Model):
    _name = "ppp.analysis"
    _description = "PPP Analysis"

    description = fields.Char(string="Opis", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")
    tag_ids = fields.Many2many("project.tags", string="Tagovi")
    user_id = fields.Many2one("res.users", string="Created By", default=lambda self: self.env.user)

    stage = fields.Selection(
        [
            ("progres", "Progres"),
            ("problem", "Problem"),
            ("plan", "Plan"),
        ],
        string="Status",
        default="progres",
        required=True,
        group_expand="_group_expand_stage",
    )

    @api.model
    def _group_expand_stage(self, values, domain, order=None):
        """Prikaži uvijek sve stage-ove u definisanom redoslijedu"""
        return ["progres", "problem", "plan"]


    def action_archive_all(self):
        """Prebaci sve PPP kartice u arhivu"""
        Archive = self.env["ppp.archive"]
        records = self.search([])  # sve kartice
        
        for rec in records:
            Archive.create({
                "name": rec.description,
                "project_id": rec.project_id.id,
                "date": rec.create_date,
                "tag_ids": [(6, 0, rec.tag_ids.ids)],
                "user_id": rec.user_id.id,
                "stage": rec.stage,
            })
        records.unlink()  # briše iz ppp.analysis




class PPPArchive(models.Model):
    _name = "ppp.archive"
    _description = "PPP Archive"

    name = fields.Char(string="Opis", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")
    date = fields.Date(string="Datum", required=True)
    tag_ids = fields.Many2many("project.tags", string="Tagovi")
    user_id = fields.Many2one("res.users", string="Created By")

    stage = fields.Selection(
        [
            ("progres", "Progres"),
            ("problem", "Problem"),
            ("plan", "Plan"),
        ],
        string="Status",
        required=True,
    )