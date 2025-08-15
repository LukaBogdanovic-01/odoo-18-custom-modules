from odoo import http
from odoo.http import request

class MyCustomPortal(http.Controller):

    @http.route('/my/requests', type='http', auth="user", website=True)
    def portal_request_list(self, **kwargs):
        user = request.env.user
        requests = request.env['universal.request'].sudo().search([
            ('assigned_user_id', 'in', [user.id])
        ])
        return request.render("universal_request_manager.portal_universal_request_list", {
            'requests': requests,
            'page_name': 'universal_requests',
        })


    @http.route('/my/request/<int:request_id>', type='http', auth="user", website=True)
    def portal_request_detail(self, request_id, **kwargs):
        req = request.env['universal.request'].sudo().browse(request_id)
        # Dodaj sigurnosnu proveru da korisnik zaista vidi samo svoje requeste
        if request.env.user.id not in req.assigned_user_id.ids:
            return request.redirect('/my')

        return request.render("universal_request_manager.portal_universal_request_detail", {
            'req': req,
        })

