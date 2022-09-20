

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Student(models.Model):
    _name = 'student.student'
    _description = 'Student'

    name = fields.Char('Name')
    phone = fields.Char('Phone')
    source_ids = fields.Many2many('slide.channel', string='Source')
    quiz_ids = fields.Many2many('op.quiz', string='Quiz')
    quiz_result_ids = fields.Many2many('op.quiz.result', string='Quiz result')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')], string='Gender')
    email = fields.Char('Email')
    birth = fields.Date('Birthday')
    address = fields.Char('Address')
    identity_card = fields.Char('Identity card')
    certificate_ids = fields.One2many('certificate', 'student_id', string='Certificate')
    position = fields.Many2one('position', string='Position')
    avatar = fields.Image('Avatar', max_width=128, max_height=128)
    work_unit = fields.Char('Work unit')
    res_country_state = fields.Many2one('res.country.state', string='Country state',
                                        domain="[('country_id', '=', 'VN')]")
    res_country_ward = fields.Many2one('res.country.ward', string='Country ward')
    res_country_district = fields.Many2one('res.country.district', string='Country district')
    user_id = fields.Many2one('res.users', string='User')
    progress_ids = fields.One2many('progress.slide', 'student_id', string='Progress')
    comment_slide_ids = fields.One2many('comment.slide', 'student_id', string='Comment slide')
    comment_source_ids = fields.One2many('comment.course', 'student_id', string='Comment source')
    partner_id = fields.Many2one('res.partner', string='Partner')
    state = fields.Selection([('confirm', 'Confirm'), ('pending', 'Pending'), ('cancel', 'Cancel'), ('recall', 'Recall')], string='State', default='pending')
    favorite_course_ids = fields.One2many('favorite.course', 'student_id', string='Favorite course')
    def active_user(self):
        self.user_id.active = True
        self.state = 'confirm'

    def cancel_user(self):
        self.state = 'cancel'

    def recall_user(self):
        self.state = 'recall'
        self.user_id.active = False

    @api.model
    def create(self, vals):
        res = super(Student, self).create(vals)
        return res


    def check_email_login_user(self):
        if self.email:
            user = self.env['res.users'].search([('login', '=', self.email)])
            if user:
                raise ValueError('Email đã được đăng ký tài khoản, vui lòng nhập email mới để được tạo tài khoản học trực tuyến.')
            self.user_id = self.env['res.users'].sudo().create({
                'name': self.name,
                'login': self.email,
                'password': '1',
                'active': False,
            })
        else:
            raise UserError(_('Vui lòng nhập email để được tạo tài khoản học trực tuyến.'))


class ProgressSlide(models.Model):
    _name = 'progress.slide'
    _description = 'progress slide student'

    progress = fields.Integer('Progress')
    slide_id = fields.Many2one('slide.slide', string='Slide')
    student_id = fields.Many2one('student.student', string='Student')

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    student_id = fields.Many2one('student.student', string="Student")


    # @api.onchange('email')
class FavoriteCourse(models.Model):
    _name = 'favorite.course'
    _description = 'Favorite course'

    slide_channel_id = fields.Many2one('slide.channel', string='Slide channel')
    student_id = fields.Many2one('student.student', string='Student')

