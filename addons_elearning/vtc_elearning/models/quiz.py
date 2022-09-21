from odoo import models, fields, api


class OpQuiz(models.Model):
    _inherit = 'op.quiz'

    @api.model
    def create(self, vals_list):
        res = super(OpQuiz, self).create(vals_list)
        if 'slide_channel_id' in vals_list and vals_list['slide_channel_id']:
            slide_channel = self.env['slide.channel'].search([('id', '=', vals_list['slide_channel_id'])])
            self.env['slide.quiz.line'].create({
                'op_quiz_id':res.id,
                'slide_channel_id':slide_channel.id
            })
        return res

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
    time_spent = fields.Float('Time Spent')
