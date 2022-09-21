from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    res_country_state = fields.Many2one('res.country.state', string='Country state',
                                        domain="[('country_id', '=', 'VN')]")
    role_user = fields.Selection([('admin_operate', 'Admin Operate'),
                                  ('admin_province', 'Admin province'),
                                  ('user_operate', 'User Operate'),
                                  ('user', 'User')], string="Role user", default='user')


    otp = fields.Integer('Otp')