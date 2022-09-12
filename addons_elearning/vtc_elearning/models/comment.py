from odoo import fields, models, api

class CommentCourse(models.Model):
    _name = 'comment.course'
    _description = 'Comment course'

    name = fields.Char('Comment')
    comment_id = fields.Many2one('comment')
    course_id = fields.Many2one('slide.channel', string='Course')
    user_id = fields.Many2one('res.users', string='User')

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

