from odoo import fields, models, api

class RatingSystem(models.Model):
    _name = 'rating.system'

    user_id = fields.Many2one('res.users', string='User')
    name = fields.Char(related='user_id.name')
    student_id = fields.Many2one('student.student', string='Student')
    slide_id = fields.Many2one('slide.channel', string='Slide channel')
    system_onetouch = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='System OneTouch')
    rating_lecturers = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Lecturers')
    content_slide = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Content slide')
    teaching_methods = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', 'Wonderful')], string='Teaching methods')
    inspire = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Inspire')
    document_quality = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Document quality')
    helpful = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Helpful')
    service_quality = fields.Selection([('0', 'No rating'),
                                        ('1', '1 star'),
                                        ('2', '2 star'),
                                        ('3', '3 star'),
                                        ('4', '4 star'),
                                        ('5', '5 star')], string='Service quality')
