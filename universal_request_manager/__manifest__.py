{
    'name': 'DIGIMEN',
    'version': '18.0.1.0.0',
    'summary': 'Digitalni menadžer',
    'license': 'LGPL-3',
    'depends': ['project', 'base', 'mail', 'hr', 'auth_signup', 'web', 'crm', 'sale', 'survey', 'portal', 'website', 'me_sh_document_counter', 'sh_document_management'],
    'data': [
        'security/security.xml',
        'security/demo_users.xml',
        'security/request_rules.xml',
        'security/ir.model.access.csv',
        'views/universal_request_views.xml',
        'views/request_type_views.xml',
        'views/code_book_data.xml',
        'views/code_book_proces.xml',
        'views/calendar_view.xml',
        'views/swot_item_kanban.xml',
        'views/gap_analysis_template.xml',
        'views/gap_analysis_template_ciljevi.xml',
        'views/template_plan_views.xml',
        'views/linkbox_views.xml',
        'views/universal_request_menus.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'universal_request_manager/static/src/css/universal_request.css',
        ],
        'web.assets_common': [
            'universal_request_manager/static/src/css/universal_request.css',
        ]
    },
    'installable': True,
    'application': True,
}
