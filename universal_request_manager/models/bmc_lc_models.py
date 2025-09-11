from odoo import models, fields, api

class BMCCanvas(models.Model):
    _name = 'bmc.canvas'
    _description = 'BMC Platno'

    name = fields.Char(string='Naziv', required=True)
    date = fields.Date(string='Datum')
    planner_id = fields.Many2one(
        'res.users', string='Planer', default=lambda self: self.env.user
    )
    type = fields.Selection([
            ('company', 'Kompanijski'),
            ('segment', 'Segment')], 
        string='Tip',required=True)
    assigned_user_id = fields.Many2one('res.users', string='Dodijeljeni korisnik')
    item_ids = fields.One2many('bmc.item', 'canvas_id', string='Stavke')

    def action_open_items(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bmc.item',
            'view_mode': 'kanban,list,form',
            'domain': [('canvas_id', '=', self.id)],
            'context': {
                'default_canvas_id': self.id
            },
            'name': f'Stavke - {self.name}'
        }

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref("universal_request_manager.action_report_bmc_canvas").report_action(self)






class BMCItem(models.Model):
    _name = 'bmc.item'
    _description = 'BMC Stavka'

    name = fields.Char(string='Naziv', required=True)
    description = fields.Html(string='Opis')
    task = fields.Many2one('project.task', string='Zadaci')
    goal = fields.Html(string='Cilj')
    result = fields.Html(string='Rezultat')

    canvas_id = fields.Many2one('bmc.canvas', string='Platno', required=True, ondelete='cascade')

    block = fields.Selection(
        [
            ('value', 'Value Propositions'),
            ('segments', 'Customer Segments'),
            ('channels', 'Channels'),
            ('relationships', 'Customer Relationships'),
            ('revenue', 'Revenue Streams'),
            ('resources', 'Key Resources'),
            ('activities', 'Key Activities'),
            ('partnerships', 'Key Partnerships'),
            ('cost', 'Cost Structure'),
            ('internal', 'Interni procesi')
        ],
        string='Stage',required=True, group_expand="_group_expand_block")

    @api.model
    def _group_expand_block(self, values, domain, order=None):
        return ['value','segments','channels','relationships','revenue','resources','activities','partnerships','cost','internal']





class LCCanvas(models.Model):
    _name = 'lc.canvas'
    _description = 'LC Platno'

    name = fields.Char(string='Naziv', required=True)
    date = fields.Date(string='Datum')
    planner_id = fields.Many2one(
        'res.users', string='Planer', default=lambda self: self.env.user
    )
    type = fields.Selection([
        ('company', 'Kompanijski'),
        ('segment', 'Segment')
    ], string='Tip', required=True)
    assigned_user_id = fields.Many2one('res.users', string='Dodijeljeni korisnik')

    item_ids = fields.One2many('lc.item', 'canvas_id', string='Stavke')

    def action_open_items(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lc.item',
            'view_mode': 'kanban,list,form',
            'domain': [('canvas_id', '=', self.id)],
            'context': {'default_canvas_id': self.id},
            'name': f'Stavke - {self.name}'
        }



class LCItem(models.Model):
    _name = 'lc.item'
    _description = 'LC Stavka'

    name = fields.Char(string='Naziv', required=True)
    description = fields.Html(string='Opis')
    task = fields.Many2one('project.task', string='Zadaci')
    goal = fields.Html(string='Cilj')
    result = fields.Html(string='Rezultat')

    canvas_id = fields.Many2one(
        'lc.canvas', string='Platno', required=True, ondelete='cascade'
    )

    block = fields.Selection([
        ('problem', 'Problem'),
        ('segments', 'Customer Segments'),
        ('value', 'Unique Value Proposition'),
        ('solution', 'Solution'),
        ('channels', 'Channels'),
        ('revenue', 'Revenue Streams'),
        ('cost', 'Cost Structure'),
        ('metrics', 'Key Metrics'),
        ('advantage', 'Unfair Advantage')
    ], string='Blok', required=True, group_expand='_group_expand_block')

    @api.model
    def _group_expand_block(self, values, domain, order=None):
        return [
            'problem',
            'segments',
            'value',
            'solution',
            'channels',
            'revenue',
            'cost',
            'metrics',
            'advantage'
        ]