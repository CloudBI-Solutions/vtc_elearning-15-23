from odoo import api, fields, models


class SlideChannel(models.Model):
	_inherit = 'slide.channel'

	cource_referen = fields.Char('Course code')