import logging

from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from werkzeug import urls

from odoo.addons.restful.common import invalid_response
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CourseByIdController(http.Controller):

    def Average(self, lst):
        return sum(lst) / len(lst)

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    def get_url_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        return "web/content2/?model=ir.attachment&id=" + str(
            attachment_id) + "&filename_field=name&field=datas&download=true"

    # @validate_token
    @http.route("/api/get/course_by_id", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_course_by_id(self, **payload):
        values = []
        user_login = request.env['res.users'].sudo().search([('id','=',int(payload.get('uid')))])
        base_url = CourseByIdController.get_url_base(self)
        list_courses = request.env['slide.channel'].sudo().search([('id', '=', payload.get('course_id'))])
        ratings = request.env['rating.rating'].sudo().search([('res_id', '=', payload.get('course_id'))])
        avg_rating = [r.star for r in ratings]
        list_users, list_students, rating_response = [], [], []
        for rec in ratings:
            list_users.append(request.env['res.users'].sudo().search([('partner_id', '=', rec.partner_id.id)]))
        for rec in list_users:
            list_students.append(request.env['student.student'].sudo().search([('user_id', '=', rec.id)]))
        rating_response = []
        process = request.env['slide.channel.partner'].sudo().search([('partner_id','=',user_login.partner_id.id),('channel_id','=', int(payload.get('course_id')))])
        for r in ratings:
            rating_response.append({
                'customer_name': r.partner_id.name,
                'avatar': urls.url_join(base_url,
                                        '/web/image?model=student.student&id={}&field=avatar'.format(
                                            r.student_id.id)),
                'star': r.star,
                'time': r.create_date,
                'comment': r.feedback,
            })
        # cấp độ học
        datas = {'id': list_courses.id,
                 'name': list_courses.name,
                 'description': list_courses.description,
                 'total_student': list_courses.count_student,
                 'total_time': list_courses.total_time,
                 'total_time_video': list_courses.total_time_video,
                 'total_slides': list_courses.total_slides,
                 'level': list_courses.course_level_id,
                 'final': list_courses.final_quiz_ids[0].op_quiz_id.id if list_courses.final_quiz_ids else '',
                 'rating_course': rating_response,
                 'avt_star': list_courses.rating_avg if list_courses.rating_avg != 0 else 'Chưa có đánh giá nào',
                 'process': process.completion
                 }
        # list giảng viên
        list_lecturers = []
        for lecturer in list_courses.lecturers_ids:
            lecturer_info = {
                'id': lecturer.id,
                'name': lecturer.name,
            }
            list_lecturers.append(lecturer_info)
        datas['lecturers'] = list_lecturers

        # thông tin tab nội dung

        cate = request.env['slide.slide'].sudo().search(
            [('is_category', '=', True), ('channel_id', '=', list_courses.id)])
        slide = request.env['slide.slide'].sudo().search(
            [('channel_id', '=', list_courses.id), ('is_category', '=', False)])
        if slide:
            list_slide = []
            for s in slide:
                slide_infor = {
                    'id': s.id,
                    'name': s.name,
                    'slide_type': s.slide_type,
                    'completion_time': s.completion_time,
                }
                list_slide.append(slide_infor)
            datas['slide'] = list_slide
        list_cate = []
        for c in cate:
            infor_cate = {
                'id': c.id,
                'name': c.name,
            }
            list_slide_in_cate = []
            for s in c.slide_ids:
                if s.slide_type in ['document', 'video', 'quiz']:
                    slide_cate = {
                        'id': s.id,
                        'name': s.name,
                        'slide_type': s.slide_type,
                        'completion_time': s.completion_time,
                    }
                    list_slide_in_cate.append(slide_cate)
            infor_cate['slide'] = list_slide_in_cate
            list_cate.append(infor_cate)
            # print(c.slide_ids)
        datas['category'] = list_cate
        # tổng học viên

        # tài liệu
        list_attachment_files = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'slide.channel'), ('res_id', '=', list_courses.id)])

        attachment = []
        for rec in list_attachment_files:
            url = urls.url_join(base_url, self.get_url_attachment(rec.id))
            name = rec.name
            attachment.append({'name': name, 'url': url})

        datas['files'] = attachment

        values.append(datas)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/cource/process", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False, cors='*')
    def get_process_percent_of_course(self, **kwargs):
        user = request.env['res.users'].sudo().search([('id', '=', kwargs.get('uid'))])
        slide_partner = request.env['slide.slide.partner'].sudo().search(
            [('channel_id', '=', kwargs['cource_id']), ('partner_id', '=', user.self.id)])

    @http.route("/api/get/lesson_by_id", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_lesson_by_id(self, **payload):
        values = []
        # base_url = CourseByIdController.get_url_base(self)
        lesson = request.env['slide.slide'].sudo().search([('id', '=', payload.get('lesson_id'))])
        progress = request.env['progress.slide'].sudo().search(
            [('student_id.user_id', '=', request.uid), ('slide_id', '=', lesson.id)])
        # list_comment = request.env['comment.slide'].sudo().search([('student.user_id', '=', request.uid), ('slide_id', '=', lesson.id)])
        data = {
            'id': lesson.id,
            'name': lesson.name,
            'type': lesson.slide_type,
            'progress': progress.progress,
            'is_done': 'False',
        }
        if lesson.slide_type == 'video':
            data['url'] = lesson.url
            data['duration'] = lesson.completion_time
        elif lesson.slide_type == 'document':
            data['url'] = lesson.url
        elif lesson.slide_type == 'quiz':
            data['time'] = lesson.quiz_id.time_config
        else:
            return invalid_response("Coming soon")
        # comment = []
        # for record in list_comment:
        #     cmt = {
        #         'id': record.id,
        #         'comment': record.comment,
        #
        #     }
        if progress.progress == 100:
            data['is_done'] = 'True'
        values.append(data)
        return valid_response(values)
