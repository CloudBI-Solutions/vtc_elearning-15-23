from odoo import api, fields, models

class CourseLevel(models.Model):

    _name = "course.level"
    _description = "Course level"
    _rec_name = 'course_level'

    course_level = fields.Char(string='course level')
