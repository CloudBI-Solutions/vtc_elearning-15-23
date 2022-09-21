from odoo import models, fields, api

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = '.'
        res = super(IrAttachment, self).create(vals)
        return res