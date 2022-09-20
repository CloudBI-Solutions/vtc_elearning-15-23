from odoo import fields, models, api

class RatingSystem(models.Model):
    _name = 'rating.system'

    user_id = fields.Many2one('res.users', string='User')
    name = fields.Char(related='user_id.name')
    student_id = fields.Many2one('student.student', string='Student')
    slide_id = fields.Many2one('slide.channel', string='Slide channel')
    system_onetouch = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='System OneTouch')
    rating_lecturers = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Lecturers')
    content_slide = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Content slide')
    teaching_methods = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Teaching methods')
    inspire = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Inspire')
    document_quality = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Document quality')
    helpful = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Helpful')
    service_quality = fields.Selection([('0', '0'),
                                        ('1', '1'),
                                        ('2', '2'),
                                        ('3', '3'),
                                        ('4', '4'),
                                        ('5', '5')], string='Service quality')
