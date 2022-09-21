from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    rating_avg = fields.Float('Rating AVG', compute='_compute_rating_avg', store=True)
    not_studied = fields.Integer('Not studied', store=True)
    studied = fields.Integer('studying', store=True)
    exam = fields.Integer('Exam', store=True)
    done_course = fields.Integer('Done course', store=True)

    def average(self, lst):
        return sum(lst) / len(lst)

    def _compute_rating_avg(self):
        for rec in self:
            list_star = self.env['rating.rating'].search([('res_id','=',rec.id)])
            avg_rating_list = [r.star for r in list_star]
            rec.rating_avg = self.average(avg_rating_list) if avg_rating_list else False


    course_level_id = fields.Many2one('course.level', string='course level')
    final_quiz_ids = fields.One2many('slide.quiz.line','slide_channel_id', readonly=True)
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
    user_support = fields.Many2many('res.users', string='User support')

    @api.depends('student_ids')
    def calculate_count_student(self):
        for record in self:
            if record.student_ids:
                student = self.env['student.student'].search([('source_ids', 'in', [record.id])])
                record.count_student = len(student)

    @api.model
    def create(self, vals):
        res = super(SlideChannel, self).create(vals)
        res.user_support += res.create_uid
        res.channel_partner_ids = None
        return res

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    def action_set_completed(self):
        if self._context.get('partner'):
            return self._action_set_completed(self._context.get('partner'))
        if any(not slide.channel_id.is_member for slide in self):
            raise UserError(_('You cannot mark a slide as completed if you are not among its members.'))
        return self._action_set_completed(self.env.user.partner_id)

    quiz_id = fields.Many2one('op.quiz', string='Quiz')