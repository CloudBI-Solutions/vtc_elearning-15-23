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
        return "web/content2/?model=ir.attachment&id=" + str(attachment_id) + "&filename_field=name&field=datas&download=true"

    # @validate_token
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
                     'total_student': rec.count_student,
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
            cate = request.env['slide.slide'].search([('is_category', '=', True), ('channel_id', '=', rec.id)])
            print(cate)
            list_cate = []
            for c in cate:
                infor_cate = {
                    'id': c.id,
                    'name': c.name,
                }
                list_slide_in_cate = []
                for s in c.slide_ids:
                    slide_cate = {
                        'id': s.id,
                        'name': s.name,
                        'slide_type': s.slide_type,
                        'completion_time': s.completion_time,
                    }
                    list_slide_in_cate.append(slide_cate)
                infor_cate['slide'] = list_slide_in_cate
                list_cate.append(infor_cate)
                print(c.slide_ids)
            dates['category'] = list_cate
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
            list_attachment_files = request.env['ir.attachment'].sudo().search([('res_model', '=', 'slide.channel'), ('res_id', '=', rec.id)]).ids
            # print('list attachment: ', list_attachment_files)
            list_attachment = [urls.url_join(base_url, self.get_url_attachment(att_id)) for att_id in
                               list_attachment_files]
            dates['files'] = list_attachment

            values.append(dates)
        return valid_response(values)

