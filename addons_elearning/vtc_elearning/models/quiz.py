from odoo import models, fields, api

class OpQuiz(models.Model):
    _inherit = 'op.quiz'

    student_ids = fields.Many2many('student.student', string='Student')
    lecturers_id = fields.Many2one('lecturers', string='Lecturers')

class OpQuizResult(models.Model):
    _inherit = 'op.quiz.result'

    student_id = fields.Many2one('student.student', string='Student')
