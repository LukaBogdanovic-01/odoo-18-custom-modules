{
    "name": "Montex - SH document counter field",
    "version": "18.0.2.0.0",
    "summary": "",
    "author": "Bojan Mijuskovic,Montex-Elektronika",
    "website": "https://www.montexel.com",
    "license": "AGPL-3",
    "category": "productivity",
    "depends": ["hr", "sh_document_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/sh_document_sequence.xml",
        "views/sh_directory_views.xml",
        "views/ir_attachment_views.xml",
        "views/document_type_views.xml",
    ],
    "auto_install": False,
    "application": False,
    "assets": {
        "web.assets_backend": [
            "me_sh_document_counter/static/src/scss/me_sh_document_counter.scss",
        ],
        "web.report_assets_common": [],
    },
}
