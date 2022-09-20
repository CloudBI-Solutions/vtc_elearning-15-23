from odoo import api, fields, models


class Rating(models.Model):
    _inherit = 'rating.rating'

    star = fields.Float('Star')
    course_id = fields.Many2one('slide.channel')
