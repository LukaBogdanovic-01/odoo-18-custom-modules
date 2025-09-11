from odoo import models, api

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        action = self.env.ref("universal_request_manager.action_universal_request")
        group = self.env.ref("base.group_user")  
        for user in users:
            if group in user.groups_id:
                user.action_id = action.id
        return users
