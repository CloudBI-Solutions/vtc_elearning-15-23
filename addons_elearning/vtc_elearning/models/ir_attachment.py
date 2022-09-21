from odoo import models, fields, api

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        slide = self.env['slide.slide'].search([('id', '=', vals['res_id'])])
        vals['name'] = slide.name
        res = super(IrAttachment, self).create(vals)
        return res