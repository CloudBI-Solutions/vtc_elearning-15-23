from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class Slide(models.Model):
    _inherit = 'slide.slide'


    document_url = fields.Char('Document URL')

    def write(self, values):
        if 'datas' in values and values['datas']:
            old_atth = self.env['ir.attachment'].search([('res_model', '=', self._name), ('res_id', '=', self.id)])
            if old_atth:
                for rec in old_atth:
                    rec.unlink()
            data = self.env['ir.attachment'].create({
                'name': 'slide(%s)' % self.id,
                'datas': values['datas'],
                'res_model': self._name,
                'res_id': self.id
            })
        return super(Slide, self).write(values)

    @api.model
    def create(self, values):
        res = super(Slide, self).create(values)
        if 'datas' in values and values['datas']:
            old_atth = self.env['ir.attachment'].search([('res_model', '=', self._name), ('res_id', '=', self.id)])
            if old_atth:
                for rec in old_atth:
                    rec.unlink()
            data = self.env['ir.attachment'].create({
                'datas': res.datas,
                'res_model': res._name,
                'res_id': res.id
            })
        return res
