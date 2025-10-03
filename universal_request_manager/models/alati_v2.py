from odoo import models, fields, api

class SwotAnalysis2(models.Model):
    _name = 'swot.analysis2'
    _description = 'SWOT Analiza'


    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one('project.project', string="Projekat")

    # polja za 4 reda × 4 kolone (jer prva kolona je opis)
    cell_1_1 = fields.Html("R1C1")
    cell_1_2 = fields.Html("R1C2")
    cell_1_3 = fields.Html("R1C3")
    cell_1_4 = fields.Html("R1C4")

    cell_2_1 = fields.Html("R2C1")
    cell_2_2 = fields.Html("R2C2")
    cell_2_3 = fields.Html("R2C3")
    cell_2_4 = fields.Html("R2C4")

    cell_3_1 = fields.Html("R3C1")
    cell_3_2 = fields.Html("R3C2")
    cell_3_3 = fields.Html("R3C3")
    cell_3_4 = fields.Html("R3C4")

    cell_4_1 = fields.Html("R4C1")
    cell_4_2 = fields.Html("R4C2")
    cell_4_3 = fields.Html("R4C3")
    cell_4_4 = fields.Html("R4C4")

    

    strategija_id = fields.Many2one(
        "biz.strategija",
        string="Strategija",
        index=True
        # bez required=True
    )
    from_dashboard = fields.Boolean(
        compute="_compute_from_dashboard",
        store=False
    )

    @api.depends_context("from_dashboard")
    def _compute_from_dashboard(self):
        for rec in self:
            rec.from_dashboard = bool(self.env.context.get("from_dashboard"))



class GapAnalysis2(models.Model):
    _name = "gap.analysis2"
    _description = "GAP Analiza"

    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")


    # nazivi redova (umjesto statičnih Red 1, Red 2...)
    row_label_1 = fields.Char(string="Red 1 Label", default="Proces 1")
    row_label_2 = fields.Char(string="Red 2 Label", default="Proces 2")
    row_label_3 = fields.Char(string="Red 3 Label", default="Proces 3")
    row_label_4 = fields.Char(string="Red 4 Label", default="Proces 4")
    row_label_5 = fields.Char(string="Red 5 Label", default="Proces 5")

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



class BmcAnalysis2(models.Model):
    _name = "bmc.analysis2"
    _description = "BMC Analiza 2"

    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")

    # polja za 10 redova × 3 kolone
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

    cell_7_1 = fields.Html("R7C1")
    cell_7_2 = fields.Html("R7C2")
    cell_7_3 = fields.Html("R7C3")

    cell_8_1 = fields.Html("R8C1")
    cell_8_2 = fields.Html("R8C2")
    cell_8_3 = fields.Html("R8C3")

    cell_9_1 = fields.Html("R9C1")
    cell_9_2 = fields.Html("R9C2")
    cell_9_3 = fields.Html("R9C3")

    cell_10_1 = fields.Html("R10C1")
    cell_10_2 = fields.Html("R10C2")
    cell_10_3 = fields.Html("R10C3")


class LcAnalysis2(models.Model):
    _name = "lc.analysis2"
    _description = "LC Analiza 2"

    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one("project.project", string="Projekat")

    # polja za 10 redova × 3 kolone
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

    cell_7_1 = fields.Html("R7C1")
    cell_7_2 = fields.Html("R7C2")
    cell_7_3 = fields.Html("R7C3")

    cell_8_1 = fields.Html("R8C1")
    cell_8_2 = fields.Html("R8C2")
    cell_8_3 = fields.Html("R8C3")

    cell_9_1 = fields.Html("R9C1")
    cell_9_2 = fields.Html("R9C2")
    cell_9_3 = fields.Html("R9C3")



