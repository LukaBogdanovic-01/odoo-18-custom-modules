from odoo import models, fields

class Scenario(models.Model):
    _name = "scenario.scenario"
    _description = "Scenario Table"

    name = fields.Char("Name", required=True)

    # polja za 6 redova × 3 kolone (jer prva kolona je opis)
    cell_1_1 = fields.Html("R1C1")
    cell_1_2 = fields.Html("R1C2")
    cell_1_3 = fields.Html("R1C3")

    cell_2_1 = fields.Html("R2C1")
    cell_2_2 = fields.Html("R2C2")
    cell_2_3 = fields.Html("R2C3")

    cell_3_1 = fields.Html("R3C1")
    cell_3_2 = fields.Html("R3C2")
    cell_3_3 = fields.Html("R3C3")

    cell_4_1 = fields.Html("R4C1")
    cell_4_2 = fields.Html("R4C2")
    cell_4_3 = fields.Html("R4C3")

    cell_5_1 = fields.Html("R5C1")
    cell_5_2 = fields.Html("R5C2")
    cell_5_3 = fields.Html("R5C3")

    cell_6_1 = fields.Html("R6C1")
    cell_6_2 = fields.Html("R6C2")
    cell_6_3 = fields.Html("R6C3")

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        index=True,
        required=True
    )

    strategija_id = fields.Many2one(
        "biz.strategija",
        string="Strategija",
        index=True
        # bez required=True
    )
