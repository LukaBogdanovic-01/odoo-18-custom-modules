from jsonschema import ValidationError
from odoo import models, fields, api, SUPERUSER_ID


class UniversalRequest(models.Model):
    _name = 'universal.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Univerzalni poslovni zahtjev'
    _order = "status_sequence, status, write_date desc, sequence"



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
    _order = 'type, sequence, id'


    name = fields.Char(string='Naziv', required=True)
    description = fields.Html(string='Opis')
    
    type = fields.Selection([
        ('strength', 'Snaga'),
        ('weakness', 'Slabost'),
        ('opportunity', 'Prilika'),
        ('threat', 'Prijetnja')
    ], string='Tip', required=True, group_expand='_group_expand_type')



    project_id = fields.Many2one('project.project', string='Projekat')
    swot_analysis_id = fields.Many2one('swot.analysis', string="SWOT analizaaaaa", required=True, ondelete='cascade')
    sequence = fields.Integer(string='Redoslijed', default=10)



    def action_create_task(self):
        self.ensure_one()
        project = self.project_id or self.swot_analysis_id.project_id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Novi Zadak',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                
                'default_project_id': project.id if project else False,
                'default_description': self.description,
            }
        }

    

    @api.model
    def _group_expand_type(self, values, domain, order=None):
        return ['strength', 'weakness', 'opportunity', 'threat']


class GapAnalysisTemplate(models.Model):
    _name = 'gap.analysis.template'
    _description = 'GAP Analiza Šablon'

    name = fields.Char(string="Naziv šablona", required=True)
    project_id = fields.Many2one('project.project', string="Projekat", required=True)
    x_gap_domain = fields.Selection([
        ('procesi', 'Procesi'),
        ('tehnologija', 'Tehnologija'),
        ('organizacija', 'Organizacija'),
        ('produkti', 'Produkti'),
        ('drugo', 'Drugo'),
    ], string="Oblast")


    x_gap_current_html = fields.Html(string="Trenutno stanje")
    x_gap_target_html = fields.Html(string="Ciljano stanje")
    x_gap_gap_html = fields.Html(string="GAP")
    x_gap_solutions_html = fields.Html(string="Rješenja")
    x_gap_benefits = fields.Html(string="Benefiti")
    x_gap_budget = fields.Html(string="Budzet")
    x_gap_related_tasks = fields.Many2many('project.task',string="Povezani zadaci")








# OVO JE ZA GAP ANALIZU U CILJEVIMA

class GapAnalysis(models.Model):
    _name = 'gap.analysis'
    _description = 'GAP Analiza'

    name = fields.Char(string="Naziv GAP Analize", required=True)
    project_id = fields.Many2one('project.project', string="Projekat", required=True)



    item_ids = fields.One2many('gap.analysis.item', 'gap_analysis_id', string="Oblasti GAP Analize")


class GapAnalysisItem(models.Model):
    _name = 'gap.analysis.item'
    _description = 'GAP Oblast'
    _order = 'sequence, id'


    name = fields.Char(string='Naziv', required=True)
    description = fields.Html(string='Opis')

    type = fields.Selection([
        ('current', 'Trenutno stanje'),
        ('target', 'Ciljano stanje'),
        ('gap', 'Ograničenje (Problem)'),
        ('solution', 'Rješenje'),
        ('benefit', 'Benefit'),
        ('budget', 'Budžet')
    ], string='Tip', default="current", required=True, group_expand='_group_expand_type')

    gap_analysis_id = fields.Many2one('gap.analysis', string="GAP analiza", required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Projekat')

    x_gap_related_tasks = fields.Many2many('project.task', string="Povezani zadaci")
    sequence = fields.Integer(string='Redoslijed', default=10)

    

    @api.onchange('gap_analysis_id')
    def _onchange_gap_analysis_id(self):
        if self.gap_analysis_id:
            self.project_id = self.gap_analysis_id.project_id

    @api.model
    def _group_expand_type(self, values, domain, order=None):
        return ['current', 'target', 'gap', 'solution', 'benefit', 'budget']

    @api.model_create_multi
    def create(self, vals_list):
        records = super(GapAnalysisItem, self).create(vals_list)

        for record in records:
            # Ako project_id nije postavljen, uzmi iz gap_analysis_id
            if not record.project_id and record.gap_analysis_id.project_id:
                record.project_id = record.gap_analysis_id.project_id

            # Kreiraj duplikate u ostalim kolonama
            if record.gap_analysis_id and record.type:
                all_types = self._group_expand_type([], [], [])
                other_types = [t for t in all_types if t != record.type]

                for t in other_types:
                    exists = self.search_count([
                        ('gap_analysis_id', '=', record.gap_analysis_id.id),
                        ('name', '=', record.name),
                        ('type', '=', t)
                    ])
                    if exists:
                        continue

                    self.create({
                        'name': record.name,
                        'type': t,
                        'gap_analysis_id': record.gap_analysis_id.id,
                        'project_id': record.project_id.id,
                    })

        return records

    






class TemplatePlan(models.Model):
    _name = 'template.plan'
    _description = 'Template Plan'

    name = fields.Char(string='Plan Name', required=True)
    line_ids = fields.One2many('template.plan.line', 'plan_id', string='Plan Lines')
    recapitulation = fields.Html(string="Rekapitulacija",related='line_ids.recapitulation',readonly=False)
    task_ids = fields.Many2many('project.task',string="Povezani zadaci")



class TemplatePlanLine(models.Model):
    _name = 'template.plan.line'
    _description = 'Template Plan Line'

    plan_id = fields.Many2one('template.plan', string='Plan', ondelete='cascade')
    position = fields.Text(string='Pozicija')
    goals = fields.Text(string='Ciljevi')
    realisation = fields.Text(string='Realizacija')
    deviations = fields.Text(string='Odstupanja')
    notes = fields.Text(string='Napomene')
    recapitulation = fields.Html(string='Rekapitulacija')






class DigimenLinkbox(models.Model):
    _name = 'digimen.linkbox'
    _description = 'Centralni registar linkova'
    _order = 'category_id, write_date desc, name'

    name = fields.Char(string="Naziv linka", required=True)
    url = fields.Char(string="URL", required=True)
    description = fields.Text(string="Opis")
    link_type = fields.Selection([
        ('document', 'Dokument'),
        ('video', 'Video'),
        ('tool', 'Interni alat'),
        ('wiki', 'Wiki'),
        ('product', 'Proizvod'),
        ('url', 'URL'),
    ], string="Tip linka")
    project_id = fields.Many2one('project.project', string="Projekat")
    related_model_id = fields.Selection([
        ('task', 'Zadatak'),
        ('partner', 'Partner'),
    ], string="Poveži sa")
    related_task_id = fields.Many2one('project.task', string="Zadatak", domain="[('project_id', '=', project_id)]")
    related_partner_id = fields.Many2one('res.partner', string="Partner")
    category_id = fields.Many2one('digimen.linkbox.category', string="Kategorija", group_expand='_expand_category')
    tag_ids = fields.Many2many('project.tags', string="Tagovi")
    is_favorite = fields.Boolean(string="Omiljeni")
    
    available_partner_ids = fields.Many2many(
        'res.partner',
        compute='_compute_available_partners',
        string='Dostupni partneri'
    )

    @api.model
    def _expand_category(self, categories, domain, order=None):
        return self.env['digimen.linkbox.category'].search([], order=order)

    @api.depends('project_id')
    def _compute_available_partners(self):
        for rec in self:
            partner = rec.project_id.partner_id
            rec.available_partner_ids = partner if partner else False


    def action_open_link(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'new'
        }


    def action_create_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Novi zadatak',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_description': self.description,
                'default_related_model_id': '%s,%s' % (self._name, self.id)
            }
        }


class DigimenLinkboxCategory(models.Model):
    _name = 'digimen.linkbox.category'
    _description = 'Kategorije linkova'
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Naziv kategorije mora biti jedinstven.')
    ]

    name = fields.Char(string="Naziv kategorije", required=True)
    description = fields.Text(string="Opis")



class ProjectTask(models.Model):
    _inherit = 'project.task'

    linkbox_ids = fields.One2many(
        comodel_name='digimen.linkbox',
        inverse_name='id',
        compute='_compute_linkbox_ids',
        string="Povezani linkovi"
    )

    def _compute_linkbox_ids(self):
        for record in self:
            if not record.id:
                record.linkbox_ids = []
            else:
                record.linkbox_ids = self.env['digimen.linkbox'].search([
                    ('related_model_id', '=', 'task'),
                    ('related_task_id', '=', record.id)
                ])



class ProjectProject(models.Model):
    _inherit = 'project.project'

    linkbox_ids = fields.One2many(
        comodel_name='digimen.linkbox',
        inverse_name='id',
        compute='_compute_linkbox_ids',
        string="Povezani linkovi"
    )

    def _compute_linkbox_ids(self):
        for project in self:
            project.linkbox_ids = self.env['digimen.linkbox'].search([
                ('project_id', '=', project.id)
            ])



class ResPartner(models.Model):
    _inherit = 'res.partner'

    linkbox_ids = fields.One2many(
        comodel_name='digimen.linkbox',
        inverse_name='id',
        compute='_compute_linkbox_ids',
        string="Povezani linkovi"
    )

    def _compute_linkbox_ids(self):
        for partner in self:
            if not partner.id:
                partner.linkbox_ids = []
            else:
                partner.linkbox_ids = self.env['digimen.linkbox'].search([
                    ('related_model_id', '=', 'partner'),
                    ('related_partner_id', '=', partner.id)
                ])

