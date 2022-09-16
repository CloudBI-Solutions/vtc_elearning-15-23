from odoo import fields, models, api

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
    avatar = fields.Image('Avatar')
    work_unit = fields.Char('Work unit')
    res_country_state = fields.Many2one('res.country.state', string='Country state',
                                        domain="[('country_id', '=', 'VN')]")
    res_country_ward = fields.Many2one('res.country.ward', string='Country ward')
    res_country_district = fields.Many2one('res.country.district', string='Country district')
    user_id = fields.Many2one('res.users', string='User')
    progress_ids = fields.One2many('progress.slide', 'student_id', string='Progress')
    comment_slide_ids = fields.One2many('comment.slide', 'student_id', string='Comment slide')
    comment_source_ids = fields.One2many('comment.course', 'student_id', string='Comment source')


class ProgressSlide(models.Model):
    _name = 'progress.slide'
    _description = 'progress slide student'

    progress = fields.Integer('Progress')
    slide_id = fields.Many2one('slide.slide', string='Slide')
    student_id = fields.Many2one('student.student', string='Student')


