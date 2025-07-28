from jsonschema import ValidationError
from odoo import models, fields, api

class UniversalRequest(models.Model):
    _name = 'universal.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Univerzalni poslovni zahtjev'
    _order = "status_sequence, status, sequence, id"


    name = fields.Char(string="Naziv zadatka", required=True, tracking=True)
    description = fields.Html(string="Opis")
    description_text = fields.Text(compute='_compute_description_text', store=True)
    proces = fields.Many2one('code.book.proces', string="Proces")
    tag_ids = fields.Many2many('project.tag', string="Tagovi")
    status_sequence = fields.Integer(compute="_compute_status_sequence", store=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Prioritet", default='medium')
    deadline = fields.Date(string="Rok")
    assigned_user_id = fields.Many2many('res.users', string="Zaduženje")
    created_by_id = fields.Many2one('res.users', string="Kreator", default=lambda self: self.env.user)
    request_type_id = fields.Many2one('request.type', string="Šablon zahtjeva")

    template_description = fields.Text(compute='_compute_template_values', string="Opis (šablon)")
    template_priority = fields.Char(compute='_compute_template_values', string="Prioritet (šablon)")
    template_assigned_user = fields.Char(compute='_compute_template_values', string="Izvršilac (šablon)")

    project_id = fields.Many2one('project.project', string="Projekat")
    goals_id = fields.Many2one('code.book', string="Ciljevi")
    attachment_file = fields.Binary(string="Uploaduj dokument")
    attachment_filename = fields.Char(string="Naziv fajla")
    attachment_preview_url = fields.Html(
        string="Pregled dokumenta",
        compute='_compute_attachment_preview_url',
        sanitize=False
    )
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    show_approve_button = fields.Boolean(compute="_compute_show_approve_button")
    show_request_fields = fields.Boolean(compute="_compute_show_custom_fields")

    state = fields.Selection([
        ('draft', 'Nacrt'),
        ('cancel', 'Odbijeno'),
        ('done', 'Završeno'),
    ], string="State", default='draft')

    sequence = fields.Integer(string="Redoslijed", default=10)
    document_directory_id = fields.Many2one(
        'document.directory',
        string="Dokumenti"
    )


    




    @api.depends('request_type_id')
    def _compute_show_custom_fields(self):
        for rec in self:
            rec.show_custom_fields = bool(rec.request_type_id)

    @api.depends('status')
    def _compute_show_approve_button(self):
        for rec in self:
            rec.show_approve_button = rec.status == 'approval'



    @api.depends('description')
    def _compute_description_text(self):
        for rec in self:
            rec.description_text = rec.description and rec.description.replace('<br>', '\n').replace('<p>', '').replace('</p>', '') or ''

    @api.depends('request_type_id')
    def _compute_template_values(self):
        for rec in self:
            rec.template_description = rec.request_type_id.default_description or ''
            rec.template_priority = dict(rec.request_type_id._fields['default_priority'].selection).get(rec.request_type_id.default_priority, '') if rec.request_type_id.default_priority else ''
            rec.template_assigned_user = rec.request_type_id.default_assigned_user_id.name if rec.request_type_id.default_assigned_user_id else ''

        
    def _check_any_group(self, group_xml_ids):
        if not any(self.env.user.has_group(g) for g in group_xml_ids):
            raise ValidationError("Nemate pravo da izvršite ovu radnju.")




    @api.constrains('request_type_id')
    def _check_request_type_access(self):
        for rec in self:
            allowed_groups = rec.request_type_id.allowed_group_ids.ids
            user_groups = self.env.user.groups_id.ids
            if allowed_groups and not any(group_id in user_groups for group_id in allowed_groups):
                raise ValidationError("Nemate pravo da koristite ovu vrstu zahtjeva.")
            

    @api.depends('status')
    def _compute_status_sequence(self):
        order_map = {
            'inbox': 0,
            'submitted': 1,
            'approval': 2,
            'approved': 3,
            'archived': 4,
        }
        for rec in self:
            rec.status_sequence = order_map.get(rec.status, 99)


    @api.model
    def _read_group_status(self, domain, order):
        return [
            ('inbox', 'Inbox', False),
            ('submitted', 'Zadaci', False),
            ('approval', 'Delegiranje', False),
            ('approved', 'Planovi', False),
            ('archived', 'Arhiva', True),  # <- ovdje je fold
        ]


    @api.model
    def _get_all_statuses(self):
        return [
            ('inbox', 'Inbox'),
            ('submitted', 'Zadaci'),
            ('approval', 'Delegiranje'),
            ('approved', 'Planovi'),
            ('archived', 'Arhiva'),
        ]


    status = fields.Selection(
        selection=_get_all_statuses,
        string="Status",
        default='inbox',
        tracking=True,
        readonly=False,
        index=True,
        group_expand='_expand_status'  # koristi i dalje ovo
    )




    @api.model
    def _expand_status(self, values, domain, order=None):
        return [key for key, _ in self._get_all_statuses()]



    def action_convert_to_task(self):
        self._check_any_group([
            'universal_request_manager.group_manager',
            'universal_request_manager.group_director',
            'base.group_system'
        ])
        self.status = 'submitted'


    def get_attachment_url(self):
            for rec in self:
                if rec.attachment_file:
                    return f"/web/content?model=universal.request&id={rec.id}&field=attachment_file&filename_field=attachment_filename&download=true"
                return ''

    @api.depends('attachment_file', 'attachment_filename')
    def _compute_attachment_preview_url(self):
        for rec in self:
            if rec.attachment_file:
                rec.attachment_preview_url = (
                    f'<a href="/web/content?model=universal.request&id={rec.id}&field=attachment_file&filename_field=attachment_filename" '
                    f'target="_blank" style="color:#875A7B;text-decoration:underline;">📄 Otvori dokument</a>'
                )
            else:
                rec.attachment_preview_url = ''

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.assigned_user_id:
                record.message_subscribe(
                    partner_ids=[record.assigned_user_id.partner_id.id],
                    subtype_ids=[]
                )
                record.message_post(
                    body="Dodijeljen ti je novi zadatak: <b>%s</b>" % record.name,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )
        return records









class RequestType(models.Model):
    _name = 'request.type'
    _description = 'Tip zahtjeva'

    name = fields.Char(string="Naziv šablona", required=True)
    allowed_group_ids = fields.Many2many('res.groups', string="Dozvoljene grupe")

    default_description = fields.Text(string="Podrazumijevani opis")
    default_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Podrazumijevani prioritet")
    default_assigned_user_id = fields.Many2one('res.users', string="Podrazumijevani izvršilac")
    required_documents = fields.Text(string="Tražena dokumentacija")
    requires_signature = fields.Boolean(string="Potreban fizički potpis")
    approval_responsible_group_id = fields.Many2one('res.groups', string="Grupa odgovorna za odobrenje")
    estimated_duration_days = fields.Integer(string="Procijenjeno trajanje (u danima)")
    user_note = fields.Text(string="Napomena za korisnika")

    show_deadline = fields.Boolean(string="Prikaži Rok", default=True)
    show_description = fields.Boolean(string="Prikaži Opis", default=True)
    show_priority = fields.Boolean(string="Prikaži Prioritet", default=True)
    show_assigned_user = fields.Boolean(string="Prikaži Dodijeljenog korisnika", default=True)
    description = fields.Html(string="Opis")



    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        user_groups = self.env.user.groups_id.ids
        args += ['|', ('allowed_group_ids', '=', False), ('allowed_group_ids', 'in', user_groups)]

        return super().name_search(name=name, args=args, operator=operator, limit=limit)


class CodeBook(models.Model):
    _name = 'code.book'
    _description = 'Šifarnik za Ciljeve'

    name = fields.Char(string="Naziv šifre", required=True)


class CodeBook(models.Model):
    _name = 'code.book.proces'
    _description = 'Šifarnik za Proces'

    name = fields.Char(string="Naziv šifre", required=True)

class Tags(models.Model):
    _name = 'project.tag'
    _description = 'Tagovi'

    name = fields.Char(string="Naziv taga", required=True)

class SwotAnalysis(models.Model):
    _name = 'swot.analysis'
    _description = 'SWOT Analiza'

    name = fields.Char(string="Naziv", required=True)
    project_id = fields.Many2one('project.project', string="Projekat", required=True)
    item_ids = fields.One2many('swot.item', 'swot_analysis_id', string="Stavke SWOT-a")


class SwotItem(models.Model):
    _name = 'swot.item'
    _description = 'SWOT Stavka'

    name = fields.Char(string='Naziv', required=True)
    description = fields.Text(string='Opis')
    
    type = fields.Selection([
        ('strength', 'Snaga'),
        ('weakness', 'Slabost'),
        ('opportunity', 'Prilika'),
        ('threat', 'Prijetnja')
    ], string='Tip', required=True, group_expand='_group_expand_type')

    priority = fields.Selection([
        ('0', 'Niska'),
        ('1', 'Srednja'),
        ('2', 'Visoka')
    ], string='Prioritet', default='1')

    project_id = fields.Many2one('project.project', string='Projekat')
    swot_analysis_id = fields.Many2one('swot.analysis', string="SWOT analizaaaaa", required=True, ondelete='cascade')



    

    @api.model
    def _group_expand_type(self, values, domain, order=None):
        return ['strength', 'weakness', 'opportunity', 'threat']


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # GAP analiza polja
    x_gap_area_description = fields.Text(string="Opis oblasti")
    x_gap_team = fields.Selection([
        ('hr', 'Ljudski resursi'),
        ('it', 'IT'),
        ('finance', 'Finansije'),
        ('marketing', 'Marketing'),
        ('other', 'Ostalo'),
    ], string="Tim", tracking=True)

    x_gap_domain = fields.Selection([
        ('procesi', 'Procesi'),
        ('tehnologija', 'Tehnologija'),
        ('organizacija', 'Organizacija'),
        ('produkti', 'Produkti'),
        ('drugo', 'Drugo'),
    ], string="Oblast", tracking=True)

    x_gap_quarter = fields.Selection([
        ('q1', 'Q1'),
        ('q2', 'Q2'),
        ('q3', 'Q3'),
        ('q4', 'Q4'),
    ], string="Kvartal", tracking=True)
    x_gap_target_state = fields.Text(string="Cilj koji želimo postići")
    x_gap_current_state = fields.Text(string="Procjena trenutnog stanja")
    x_gap_score = fields.Selection(
        selection=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string="Identifikovani GAP (0–5)"
    )
    x_gap_causes = fields.Text(string="Uzroci")
    x_gap_solutions = fields.Text(string="Moguće mjere i rješenja")
    x_gap_priority = fields.Selection(
        selection=[('low', 'Niski'), ('medium', 'Srednji'), ('high', 'Visoki')],
        string="Prioritet GAP-a"
    )
    x_gap_related_tasks = fields.Many2many(
        'project.task', 'gap_task_rel', 'gap_id', 'task_id', string="Vezani zadaci"
    )
    x_gap_comments = fields.Text(string="Komentari / Napomene")


    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)

        # Pronađi ili kreiraj tag "GAP analiza"
        gap_tag = self.env['project.tags'].search([('name', '=', 'GAP analiza')], limit=1)
        if not gap_tag:
            gap_tag = self.env['project.tags'].create({'name': 'GAP analiza'})

        # Svakom task-u dodaj taj tag
        for task, vals in zip(tasks, vals_list):
            task.tag_ids = [(4, gap_tag.id)]

        return tasks

    @api.onchange('x_gap_priority')
    def _onchange_gap_priority_color(self):
        priority_color_map = {
            'high': 1,     # crvena
            'medium': 3,   # narandžasta
            'low': 10      # zelena
        }
        self.color = priority_color_map.get(self.x_gap_priority, 0)

