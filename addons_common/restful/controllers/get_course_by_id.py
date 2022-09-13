import logging

from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from werkzeug import urls
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
        return "web/content2/?model=ir.attachment&id=" + str(attachment_id) + "&filename_field=name&field=datas&download=true&name=" + attachment.name

    @validate_token
    @http.route("/api/get/course_by_id", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_course_by_id(self, **payload):
        values = []
        base_url = CourseByIdController.get_url_base(self)
        list_courses = request.env['slide.channel'].search(
            [('is_published', '=', True), ('id', '=', payload.get('course_id'))])

        for rec in list_courses:
            # cấp độ học
            tag_id = rec.tag_ids[0].id
            dates = {'id': rec.id,
                     'name': rec.name,
                     'description': rec.description,
                     'tag_id': tag_id,
                     }

            # list giảng viên
            list_lecturers = []
            for lecturer in rec.lecturers_ids:
                lecturer_info = {
                    'id': lecturer.id,
                    'name': lecturer.name,
                }
                list_lecturers.append(lecturer_info)
            dates['lecturers'] = list_lecturers

            # thông tin tab nội dung
            slides = []
            for slide in rec.slide_ids:
                slide_detail = {
                    'id': slide.id,
                    'name': slide.name,
                    'slide_type': slide.slide_type,
                    'completion_time': slide.completion_time,
                }
                slides.append(slide_detail)
            dates['slide_ids'] = slides

            # tổng học viên
            total_students = len(rec.student_ids)
            dates['total_students'] = total_students

            # đánh giá
            ratings = []
            for rate in rec.rating_ids:
                rating_detail = {
                    'id': rate.id,
                    'feedback': rate.feedback,
                }
                ratings.append(rating_detail)
            dates['rating_ids'] = ratings

            # tài liệu
            list_attachment = [urls.url_join(base_url, self.get_url_attachment(att_id)) for att_id in
                               rec.message_main_attachment_id]
            # dates['files'] = list_attachment
            print(list_attachment)

            values.append(dates)
        return valid_response(values)

    # @validate_token
    # @http.route("/api/course_by_id/<id>", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    # def get_course_by_id(self, **payload):
    #     values = []
    #     base_url = CourseByIdController.get_url_base(self)
    #     list_courses = request.env['slide.channel'].search(
    #         [('id', '=', int(id))], limit=1)
    #
    #     for rec in list_courses:
    #         dates = {'id': rec.id,
    #                  'name': rec.name,
    #                  }
    #         slides = []
    #         for slide in rec.slide_ids:
    #             slide_detail = {
    #                 'name': slide.name,
    #                 'slide_type': slide.slide_type,
    #                 'completion_time': slide.completion_time
    #
    #             }
    #             slides.append(slide_detail)
    #         dates['slide_ids'] = slides
    #         values.append(dates)
    #     return valid_response(values)