from odoo import api, fields, models


class SlideQuizLine(models.Model):
    _name = 'slide.quiz.line'

    op_quiz_id = fields.Many2one('op.quiz', 'Quiz')
    slide_channel_id = fields.Many2one('slide.channel')
    cost = fields.Integer('Total Marks', related='op_quiz_id.total_marks')
    start_date = fields.Datetime('Start date', related='op_quiz_id.start_date')
    end_date = fields.Datetime('End date', related='op_quiz_id.end_date')
    count_question = fields.Integer('Count Test', compute='_compute_count')
    count_student = fields.Integer('Count Student', compute='_compute_count')

    @api.depends('op_quiz_id.student_ids', 'op_quiz_id.line_ids', 'op_quiz_id.config_ids')
    def _compute_count(self):
        count = []
        for rec in self:
            rec.count_student = len(rec.op_quiz_id.student_ids)
            if rec.op_quiz_id.line_ids:
                rec.count_question = len(rec.op_quiz_id.line_ids)
            else:
                rec.count_question = 0
            if rec.op_quiz_id.config_ids:
                for r in rec.op_quiz_id.config_ids:
                    count.append(len(r.bank_id.line_ids))
                rec.count_question = sum(count)
            else:
                rec.count_question = 0



