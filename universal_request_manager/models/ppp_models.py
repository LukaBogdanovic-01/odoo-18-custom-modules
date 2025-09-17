from odoo import models, fields, api
import re

class PPPAnalysis(models.Model):
    _name = "ppp.analysis"
    _description = "PPP Analysis"
    _rec_name = "name"   # koristi name kao glavno polje

    # Tehničko ime (čisti tekst iz opisa)
    name = fields.Char(string="Naslov", compute="_compute_name", store=True)

    description = fields.Html(string="Opis", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")
    tag_ids = fields.Many2many("project.tags", string="Tagovi")
    user_id = fields.Many2one("res.users", string="Created By", default=lambda self: self.env.user)
    active = fields.Boolean(default=True)

    assigned_user_ids = fields.Many2many(
        "res.users",
        "ppp_analysis_user_rel",  # through table
        "ppp_id", "user_id",
        string="Tim"
    )

    stage = fields.Selection(
        [
            ("progres", "Progres"),
            ("problem", "Problem"),
            ("plan", "Plan"),
            ("future", "U budućnosti"),
        ],
        string="Status",
        default="progres",
        required=True,
        group_expand="_group_expand_stage",
    )

    @api.depends("description")
    def _compute_name(self):
        """Generiše čisti tekstualni naslov iz HTML opisa"""
        for rec in self:
            clean_text = re.sub('<[^<]+?>', '', rec.description or '')
            rec.name = (clean_text[:50] + '...') if len(clean_text) > 50 else clean_text or "PPP Analysis"

    @api.model
    def _group_expand_stage(self, values, domain, order=None):
        """Prikaži uvijek sve stage-ove u definisanom redoslijedu"""
        return ["progres", "problem", "plan", "future"]

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

    def action_archive_selected(self):
        """Soft arhivira PPP kartice + upis u ppp.archive"""
        Archive = self.env["ppp.archive"]
        for rec in self:
            Archive.create({
                "name": rec.description,
                "project_id": rec.project_id.id,
                "date": rec.create_date,
                "tag_ids": [(6, 0, rec.tag_ids.ids)],
                "user_id": rec.user_id.id,
                "stage": rec.stage,
            })
        # umjesto unlink → soft archive
        self.write({"active": False})










class PPPArchive(models.Model):
    _name = "ppp.archive"
    _description = "PPP Archive"
    _rec_name = "clean_name"   # koristi čisto polje kao naziv

    name = fields.Html(string="Opis", required=True)
    clean_name = fields.Char(string="Naslov", compute="_compute_clean_name", store=True)

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

    @api.depends("name")
    def _compute_clean_name(self):
        for rec in self:
            clean_text = re.sub('<[^<]+?>', '', rec.name or '')
            rec.clean_name = (clean_text[:50] + '...') if len(clean_text) > 50 else clean_text or "PPP Archive"
