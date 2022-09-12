from odoo import models, fields, api

class Position(models.Model):
    _name = 'position'
    _description = 'Position Student'

    name = fields.Char('Position')