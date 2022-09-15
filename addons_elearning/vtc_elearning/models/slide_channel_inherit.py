from odoo import api, fields, models

class SlideChannelInherit(models.Model):

    _inherit = "slide.channel"

    course_level_id = fields.Many2one('course.level', string='course level')
