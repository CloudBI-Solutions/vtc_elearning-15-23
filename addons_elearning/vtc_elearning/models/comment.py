from odoo import fields, models, api

class CommentCourse(models.Model):
    _name = 'comment.course'
    _description = 'Comment course'

    name = fields.Char('Comment')
    comment_id = fields.Many2one('comment.course')
    course_id = fields.Many2one('slide.channel', string='Course')
    student_id = fields.Many2one('student.student', string='Student')
    user_id = fields.Many2one(related='student_id.user_id')


class CommentSlide(models.Model):
    _name = 'comment.slide'
    _description = "Student comment slide"

    name = fields.Char('Comment')
    comment_id = fields.Many2one('comment.slide', string='Comment')
    comment_ids = fields.One2many('comment.slide', 'comment_id', string='Comment')
    slide_id = fields.Many2one('slide.slide', string='Course')
    student_id = fields.Many2one('student.student', string='Student')
    user_id = fields.Many2one(related='student_id.user_id')


class RatLecturers(models.Model):
    _name = 'rat.lecturers'
    _description = 'Rating lecturers'

    name = fields.Char('Evaluate')
    rating = fields.Selection([('1', '1'),
                               ('2', '2'),
                               ('3', '3'),
                               ('4', '4'),
                               ('5', '5')], string='Rating')
    lecturers_id = fields.Many2one('lecturers', string='Lecturers')
    comment_id = fields.Many2one('comment')
    user_id = fields.Many2one('res.users', string='User')

