from odoo import fields, models, api, _
from odoo.exceptions import UserError
from random import randint
class Tag(models.Model):
    _name = 'tag.slide'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10, index=True, required=True)
    color = fields.Integer(
        string='Color Index', default=lambda self: randint(1, 11), )
class SlideChannel(models.Model):
    _inherit = 'slide.channel'


    is_outstanding_channel = fields.Boolean('Khóa học đặc biệt')
    rating_avg = fields.Float('Rating AVG', compute='_compute_rating_avg')
    is_special = fields.Boolean('Course Special')
    not_studied = fields.Integer('Not studied', store=True)
    studied = fields.Integer('studying', store=True)
    exam = fields.Integer('Exam', store=True)
    done_course = fields.Integer('Done course', store=True)
    price_course = fields.Float('Price')
    level = fields.Selection([
        ('basic', 'Basic'),
        ('common', 'Common'),
        ('advanced', 'Advanced'),
        ('high_class', 'High class'),
        ('depth', 'Depth')], string='Level')

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
    total_time_video = fields.Float(compute='calculate_total_time_video', string='Total time video')
    tag_id = fields.Many2one('tag.slide', string='Chuyên mục khóa học')


    def open_website_url(self):
        return {
            'type': 'ir.actions.act_url',
            'url': "http://daotao.vtcnetviet.com/courses/%s/%s" %(self.name, self.id),
            'target': 'new',
        }

    @api.depends('slide_ids')
    def calculate_total_time_video(self):
        for record in self:
            record.total_time_video = 0
            for rec in record.slide_ids:
                if rec.slide_type == 'video':
                    record.total_time_video += rec.completion_time

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
        res.is_published = True
        return res

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    def _my_new_selection(self):
        lst = [('infographic', 'Đồ hoạ thông tin'), ('webpage', 'Trang web'), ('presentation', 'Bài thuyết trình'),
               ('document', 'Tài liệu'), ('video', 'Video'), ('quiz', 'Bài kiểm tra')]
        try:
            lst.remove(
                [item for item in lst if item[0] == 'infographic'][
                    0])
            lst.remove(
                [item for item in lst if item[0] == 'webpage'][
                    0])
            lst.remove(
                [item for item in lst if item[0] == 'presentation'][
                    0])
        except IndexError as e:
            pass
        return lst

    file_upload = fields.Binary('Video upload', attachment=True)
    type_video = fields.Selection([
        ('url', 'Get video Url'),
        ('vimeo', 'Get video from Vimeo'),
        ('upload', 'Get video by upload from device')], string='Type video')

    post_to_website = fields.Boolean(string='Post to website?')
    slide_type = fields.Selection(_my_new_selection,)

    def action_set_completed(self):
        if self._context.get('partner'):
            return self._action_set_completed(self._context.get('partner'))
        if any(not slide.channel_id.is_member for slide in self):
            raise UserError(_('You cannot mark a slide as completed if you are not among its members.'))
        return self._action_set_completed(self.env.user.partner_id)

    quiz_id = fields.Many2one('op.quiz', string='Quiz')

    @api.model
    def create(self, vals):
        res = super(SlideSlide, self).create(vals)
        res.is_published = True
        return res