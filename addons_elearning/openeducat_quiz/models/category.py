# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpQuizCategory(models.Model):
    _name = "op.quiz.category"
    _description = "Quiz Category"

    name = fields.Char('Name')
    code = fields.Char('Code', readonly=True)
    description = fields.Text('Description')

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('QUIZ_CATEGORY_SEQUENCE')
        return super(OpQuizCategory, self).create(vals)
