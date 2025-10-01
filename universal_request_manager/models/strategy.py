from odoo import models, fields

class Strategija(models.Model):
    _name = "biz.strategija"
    _description = "Biznis Strategija"

    name = fields.Char(string="Naziv strategije", required=True)
    description = fields.Text(string="Opis")
