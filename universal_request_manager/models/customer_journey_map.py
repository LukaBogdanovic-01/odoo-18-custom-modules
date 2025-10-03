from odoo import models, fields

class CjmAnalysis(models.Model):
    _name = "cjm.analysis"
    _description = "Customer Journey Map"

    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")

    # polja za 5 redova × 6 kolona
    cell_1_1 = fields.Html("R1C1")
    cell_1_2 = fields.Html("R1C2")
    cell_1_3 = fields.Html("R1C3")
    cell_1_4 = fields.Html("R1C4")
    cell_1_5 = fields.Html("R1C5")
    cell_1_6 = fields.Html("R1C6")

    cell_2_1 = fields.Html("R2C1")
    cell_2_2 = fields.Html("R2C2")
    cell_2_3 = fields.Html("R2C3")
    cell_2_4 = fields.Html("R2C4")
    cell_2_5 = fields.Html("R2C5")
    cell_2_6 = fields.Html("R2C6")

    cell_3_1 = fields.Html("R3C1")
    cell_3_2 = fields.Html("R3C2")
    cell_3_3 = fields.Html("R3C3")
    cell_3_4 = fields.Html("R3C4")
    cell_3_5 = fields.Html("R3C5")
    cell_3_6 = fields.Html("R3C6")

    cell_4_1 = fields.Html("R4C1")
    cell_4_2 = fields.Html("R4C2")
    cell_4_3 = fields.Html("R4C3")
    cell_4_4 = fields.Html("R4C4")
    cell_4_5 = fields.Html("R4C5")
    cell_4_6 = fields.Html("R4C6")

    cell_5_1 = fields.Html("R5C1")
    cell_5_2 = fields.Html("R5C2")
    cell_5_3 = fields.Html("R5C3")
    cell_5_4 = fields.Html("R5C4")
    cell_5_5 = fields.Html("R5C5")
    cell_5_6 = fields.Html("R5C6")

    cell_6_1 = fields.Html("R5C1")
    cell_6_2 = fields.Html("R5C2")
    cell_6_3 = fields.Html("R5C3")
    cell_6_4 = fields.Html("R5C4")
    cell_6_5 = fields.Html("R5C5")
    cell_6_6 = fields.Html("R5C6")
