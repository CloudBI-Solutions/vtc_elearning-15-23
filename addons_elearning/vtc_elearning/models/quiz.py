from odoo import models, fields, api

class OpQuiz(models.Model):
    _inherit = 'op.quiz'

    student_ids = fields.Many2many('student.student', string='Student')
    lecturers_id = fields.Many2one('lecturers', string='Lecturers')

    @api.constrains('type', 'department_id', 'slide_channel_id')
    def render_employee_participating(self):
        if self.type == 'integration_exam':
            self.list_candidates = self.department_id.member_ids
        elif self.type == 'channel_slide':
            self.student_ids = self.slide_channel_id.student_ids.ids
        else:
            self.list_candidates = self.env['hr.employee'].search([])

class OpQuizResult(models.Model):
    _inherit = 'op.quiz.result'

    student_id = fields.Many2one('student.student', string='Student')
