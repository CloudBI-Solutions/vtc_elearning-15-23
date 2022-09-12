from odoo import fields, models, api, _

class Lecturers(models.Model):
    _name = 'lecturers'
    _description = 'Lecturers'

    name = fields.Char('Name')
    phone = fields.Char('Phone')
    source_ids = fields.Many2many('slide.channel', string='Source')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')], string='Gender')
    comment_ids = fields.One2many('rat.lecturers', 'lecturers_id', string='Evaluate')
    email = fields.Char('Email')
    birth = fields.Date('Birthday')
    address = fields.Char('Address')
    identity_card = fields.Char('Identity card')
    quiz_ids = fields.One2many('op.quiz', 'lecturers_id', string='Lecturers')
    evaluate_count = fields.Integer(string='Evaluate count', compute='comment_count', store=True)

    @api.depends('comment_ids')
    def comment_count(self):
        print('______')
        for record in self:
            comment_ids = self.env['rat.lecturers'].sudo().search([('lecturers_id', '=', record.id)])
            record.evaluate_count = len(comment_ids)
