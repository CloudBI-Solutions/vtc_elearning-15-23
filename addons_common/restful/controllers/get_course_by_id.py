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
        print(payload)
        base_url = CourseByIdController.get_url_base(self)
        list_courses = request.env['slide.channel'].sudo().search([('id', '=', payload.get('course_id'))])
        print(list_courses)
        # cấp độ học
        datas = {'id': list_courses.id,
                 'name': list_courses.name,
                 'description': list_courses.description,
                 'total_student': list_courses.count_student,
                 'level': list_courses.course_level_id,
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
        print(cate)
        slide = request.env['slide.slide'].search([('channel_id', '=', list_courses.id),
                                                   ('is_category', '=', False),
                                                   ('slide_type', 'in', ['document', 'video', 'quiz'])])
        print(slide, 'Slide')
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
        # total_students = len(list_courses.student_ids)
        # dates['total_students'] = total_students

        # đánh giá
        ratings = []
        for rate in list_courses.sudo().rating_ids:
            rating_detail = {
                'id': rate.id,
                'feedback': rate.feedback,
            }
            ratings.append(rating_detail)
        datas['rating_ids'] = ratings

        # tài liệu
        list_attachment_files = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'slide.channel'), ('res_id', '=', list_courses.id)]).ids
        # print('list attachment: ', list_attachment_files)
        list_attachment = [urls.url_join(base_url, self.get_url_attachment(att_id)) for att_id in
                           list_attachment_files]
        datas['files'] = list_attachment

        values.append(datas)
        return valid_response(values)

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
        print(lesson.slide_type)
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
