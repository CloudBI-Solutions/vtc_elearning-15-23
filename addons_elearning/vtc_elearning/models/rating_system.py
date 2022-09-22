from odoo import fields, models, api

class RatingSystem(models.Model):
    _name = 'rating.system'

    user_id = fields.Many2one('res.users', string='User')
    name = fields.Char(related='user_id.name')
    student_id = fields.Many2one('student.student', string='Student')
    slide_id = fields.Many2one('slide.channel', string='Slide channel')
    system_onetouch = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='System OneTouch')
    rating_lecturers = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Lecturers')
    content_slide = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Content slide')
    teaching_methods = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Teaching methods')
    inspire = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Inspire')
    document_quality = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Document quality')
    helpful = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Helpful')
    service_quality = fields.Selection([('0', 'No rating'),
                                        ('1', 'Bad'),
                                        ('2', 'Unsatisfied'),
                                        ('3', 'Normal'),
                                        ('4', 'satisfied'),
                                        ('5', 'Wonderful')], string='Service quality')
