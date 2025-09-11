{
    'name': 'App Dashboard',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Custom landing page with all installed apps',
    'depends': ['base'],
    'data': [
        'views/app_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'app_dashboard/static/src/js/app_dashboard.js',
            'app_dashboard/static/src/css/app_dashboard.css',
            'app_dashboard/static/src/xml/app_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
}
