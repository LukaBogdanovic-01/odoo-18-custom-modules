from odoo import models, fields, api
import re
from odoo.exceptions import AccessError, UserError


class PPPAnalysis(models.Model):
    _name = "ppp.analysis"
    _description = "PPP Analysis"
    _rec_name = "name"   # koristi name kao glavno polje

    # Tehničko ime (čisti tekst iz opisa)
    name = fields.Char(string="Naslov", compute="_compute_name", store=True)

    description = fields.Html(string="Opis")
    project_id = fields.Many2one("project.project", string="Projekat")
    tag_ids = fields.Many2many("project.tags", string="Tagovi")
    user_id = fields.Many2one("res.users", string="Created By", default=lambda self: self.env.user)
    active = fields.Boolean(default=True)

    assigned_user_ids = fields.Many2many(
        "res.users",
        "ppp_analysis_user_rel", 
        "ppp_id", "user_id",
        string="Tim"
    )
    activity_ids = fields.Many2many(
        "universal.request",
        string="Aktivnosti "
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

    @api.depends("description", "name")
    def _compute_name(self):
        """Ako korisnik unese ime direktno (npr. quick create), prepiši ga u description.
           Inače generiši name iz description."""
        for rec in self:
            if rec.name and not rec.description:
                # Kad quick create upiše name, prebacujemo ga u description
                rec.description = rec.name

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
        records.unlink() 

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

        # uzmi definisanu akciju za ppp.analysis
        action = self.env.ref("universal_request_manager.action_ppp_analysis").sudo().read()[0]

        # veži je na meni PPP Analiza (ili šta god da je tvoj meni)
        menu = self.env.ref("universal_request_manager.menu_ppp_analysis", raise_if_not_found=False)
        if menu:
            action["menu_id"] = menu.id

        # ključno: otvaraj u main contentu (reset breadcrumbs)
        action["target"] = "main"

        # očisti res_id ako postoji
        action.pop("res_id", None)

        return action












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
    active = fields.Boolean(default=True)


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


    def action_restore(self):
        self.ensure_one()

        if not self.env.user.has_group("base.group_system") and self.user_id != self.env.user:
            raise AccessError("Nije vam dozvoljeno da vratite ovu arhivu.")

        # prebaci u analysis
        self.env["ppp.analysis"].create({
            "description": self.name,
            "project_id": self.project_id.id,
            "tag_ids": [(6, 0, self.tag_ids.ids)],
            "user_id": self.user_id.id,
            "stage": self.stage,
        })

        # soft delete (da izbjegnemo crvenu poruku)
        self.write({"active": False})

        # akcija za PPP Archive
        action = self.env.ref("universal_request_manager.action_ppp_archive").sudo().read()[0]

        # vežemo je na meni PPP Archive
        menu = self.env.ref("universal_request_manager.menu_ppp_archive", raise_if_not_found=False)
        if menu:
            action["menu_id"] = menu.id

        # ključno: otvaramo u "main" contentu
        action["target"] = "main"

        # očisti res_id ako postoji
        action.pop("res_id", None)

        return action











