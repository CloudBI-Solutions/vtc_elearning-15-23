from odoo import fields, models, api

class Certificate(models.Model):
    _name = 'certificate'
    _description = 'Certificate'

    student_id = fields.Many2one('student.student')
    attachment_id = fields.Binary(string='File certificate')
