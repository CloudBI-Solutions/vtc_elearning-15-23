from odoo import api, fields, models


class Rating(models.Model):
    _inherit = 'rating.rating'

    star = fields.Integer('Star')
    course_id = fields.Many2one('slide.channel')
    student_id = fields.Many2one('student.student')