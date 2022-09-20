from odoo import fields, models, api, _

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    course_level_id = fields.Many2one('course.level', string='course level')
    final_quiz_ids = fields.One2many('slide.quiz.line','slide_channel_id')
    student_ids = fields.Many2many('student.student', string='Student')
    lecturers_ids = fields.Many2many('lecturers', string='Lecturers')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    type_course = fields.Selection([('free', 'Free'),
                                    ('price', 'Price')], string='Type course', default='free')
    comment_ids = fields.One2many('comment.course', 'course_id', string='Comment')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('expired', 'Expired')], string='State')
    enroll = fields.Selection([
        ('public', 'Public'), ('invite', 'On Invitation'), ('sign', 'Đăng ký (Coming soon)')],
        default='public', string='Enroll Policy', required=True,
        help='Condition to enroll: everyone, on invite, on payment (sale bridge).')
    count_student = fields.Integer('Student count', compute='calculate_count_student', store=True)


    @api.depends('student_ids')
    def calculate_count_student(self):
        for record in self:
            if record.student_ids:
                student = self.env['student.student'].search([('source_ids', 'in', [record.id])])
                record.count_student = len(student)

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    quiz_id = fields.Many2one('op.quiz', string='Quiz')