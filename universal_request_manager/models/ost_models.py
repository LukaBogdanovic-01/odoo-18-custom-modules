from odoo import api, fields, models


AVAILABLE_COLORS = [
    "#FF0000",  # crvena
    "#008000",  # zelena
    "#0000FF",  # plava
    "#FFA500",  # narandžasta
    "#800080",  # ljubičasta
    "#00CED1",  # tirkizna
    "#FFD700",  # žuta
    "#A52A2A",  # braon
]



class OstOutcome(models.Model):
    _name = "ost.outcome"
    _description = "OST Outcome (Cilj)"
    _order = "priority desc, deadline asc, id desc"

    name = fields.Char(required=True)
    description = fields.Text()

    # KPI/OKR polja
    kpi_name = fields.Char(string="KPI/OKR")
    target_value = fields.Char(string="Target")

    deadline = fields.Date()
    priority = fields.Selection([
        ("0", "Nisko"),
        ("1", "Srednje"),
        ("2", "Visoko"),
    ], default="1")

    # Relacije
    opportunity_ids = fields.One2many("ost.opportunity", "outcome_id", string="Prilike")
    opportunity_count = fields.Integer(compute="_compute_counts")

    strategija_id = fields.Many2one(
        "biz.strategija",
        string="Strategija",
        index=True
        # bez required=True
    )

    @api.depends("opportunity_ids")
    def _compute_counts(self):
        for rec in self:
            rec.opportunity_count = len(rec.opportunity_ids)

class OstOpportunity(models.Model):
    _name = "ost.opportunity"
    _description = "OST Opportunity (Prilika)"
    _order = "create_date desc"

    name = fields.Char(required=True)
    description = fields.Text()
    source = fields.Selection([
        ("customer", "Feedback klijenata"),
        ("market", "Tržište"),
        ("internal", "Interno"),
        ("other", "Ostalo"),
    ], default="customer")

    outcome_id = fields.Many2one("ost.outcome", required=True, ondelete="cascade")

    solution_ids = fields.One2many("ost.solution", "opportunity_id", string="Rješenja")
    solution_count = fields.Integer(compute="_compute_counts")

    color = fields.Char(string="Color", readonly=True)

    @api.depends("solution_ids")
    def _compute_counts(self):
        for rec in self:
            rec.solution_count = len(rec.solution_ids)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("color"):
                count = self.search_count([])
                vals["color"] = AVAILABLE_COLORS[count % len(AVAILABLE_COLORS)]
        return super().create(vals_list)



class OstSolution(models.Model):
    _name = "ost.solution"
    _description = "OST Solution (Rješenje)"
    _order = "status desc, create_date desc"

    name = fields.Char(required=True)
    description = fields.Text()

    type = fields.Selection([
        ("process", "Procesno"),
        ("product", "Proizvodno/Tehničko"),
        ("org", "Organizaciono"),
        ("other", "Ostalo"),
    ], default="product")

    status = fields.Selection([
        ("idea", "Ideja"),
        ("testing", "U testiranju"),
        ("implemented", "Implementirano"),
        ("validated", "Validirano"),
        ("rejected", "Odbijeno"),
    ], default="idea")

    opportunity_id = fields.Many2one("ost.opportunity", required=True, ondelete="cascade")

    experiment_ids = fields.One2many("ost.experiment", "solution_id", string="Eksperimenti")
    experiment_count = fields.Integer(compute="_compute_counts")

    color = fields.Char(string="Color", compute="_compute_color", store=True)


    @api.depends("opportunity_id.color")
    def _compute_color(self):
        for rec in self:
            rec.color = rec.opportunity_id.color or "#CCCCCC"

    @api.depends("experiment_ids")
    def _compute_counts(self):
        for rec in self:
            rec.experiment_count = len(rec.experiment_ids)

    # Auto-validacija: ako su svi eksperimenti završeni i uspješni → validated
    @api.depends("experiment_ids.status", "experiment_ids.success")
    def _compute_auto_status(self):
        for rec in self:
            exps = rec.experiment_ids
            if exps and all(e.status == "done" and e.success for e in exps):
                rec.status = "validated"


class OstExperiment(models.Model):
    _name = "ost.experiment"
    _description = "OST Experiment (Eksperiment)"
    _order = "status asc, id desc"

    name = fields.Char(required=True)
    method = fields.Char(string="Metoda")
    result_notes = fields.Text(string="Rezultat/Zapažanja")

    status = fields.Selection([
        ("planned", "Planirano"),
        ("running", "U toku"),
        ("done", "Završeno"),
    ], default="planned")

    success = fields.Boolean(string="Uspješno?")

    solution_id = fields.Many2one("ost.solution", required=True, ondelete="cascade")

    color = fields.Char(string="Color", compute="_compute_color", store=True)

    @api.depends("solution_id.color")
    def _compute_color(self):
        for rec in self:
            rec.color = rec.solution_id.color or "#CCCCCC"


# class OstDashboard(models.Model):
#     _name = "ost.dashboard"
#     _description = "Static OST Dashboard"