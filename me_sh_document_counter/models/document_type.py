from odoo import fields, models


class DocumentType(models.Model):
    _name = "document.type"
    _description = "Type of document"

    name = fields.Char()


class DirectoryType(models.Model):
    _name = "directory.type"
    _description = "Type of irectory"

    name = fields.Char()


class SignaturePlan(models.Model):
    _name = "document.signature.plan"
    _description = "Signature plan of document"

    name = fields.Char()


class ClassificationPlan(models.Model):
    _name = "document.classification.plan"
    _description = "Classification plan of document"

    name = fields.Char()
    date = fields.Date()
