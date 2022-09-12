from odoo import fields, models, api, _

class Lecturers(models.Model):
    _name = 'lecturers'
    _description = 'Lecturers'

    name = fields.Char('Name')
    phone = fields.Char('Phone')
    source_ids = fields.Many2many('slide.channel', string='Source')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')], string='Gender')
    comment_ids = fields.One2many('rat.lecturers', 'lecturers_id', string='Evaluate')
    email = fields.Char('Email')
    birth = fields.Date('Birthday')
    address = fields.Char('Address')
    identity_card = fields.Char('Identity card')
    quiz_ids = fields.One2many('op.quiz', 'lecturers_id', string='Lecturers')
    evaluate_count = fields.Integer(string='Evaluate count', compute='comment_count', store=True)
    total_course = fields.Integer('Total course', compute='calculate_count_course_student', store=True)
    total_student = fields.Integer('Total student', compute='calculate_count_course_student', store=True)
    rating = fields.Float('Rating', compute='calculate_rating', store=True)
    rating_text = fields.Char('Rating')

    @api.depends('comment_ids')
    def calculate_rating(self):
        for record in self:
            if record.comment_ids:
                rating = 0
                total_rating = len(record.comment_ids)
                for rec in record.comment_ids:
                    rating += int(rec.rating)
                record.rating = (rating/(total_rating * 5) * 5)
                record.rating_text = str(round(record.rating, 1)) + '/5'

    @api.depends('source_ids')
    def calculate_count_course_student(self):
        for record in self:
            record.total_student = 0
            course = self.env['slide.channel'].search([('lecturers_ids', 'in', [record.id])])
            record.total_course = len(course)
            for rec in course:
                record.total_student += rec.count_student
    @api.depends('comment_ids')
    def comment_count(self):
        print('______')
        for record in self:
            comment_ids = self.env['rat.lecturers'].sudo().search([('lecturers_id', '=', record.id)])
            record.evaluate_count = len(comment_ids)
