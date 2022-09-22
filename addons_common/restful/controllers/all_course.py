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


class AllCoursesController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/get_course_by_user", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
    def get_course_by_user(self, **kwargs):
        base_url = AllCoursesController.get_url_base(self)
        user_login = request.env['res.users'].sudo().search([('id', '=', int(kwargs.get('uid')))])
        partner_channel = request.env['slide.channel.partner'].sudo().search(
            [('partner_id', '=', user_login.partner_id.id)])
        all_courses = [r.channel_id for r in partner_channel]
        data = {}
        vals = []
        for rec in all_courses:
            # cấp độ học
            # tag_id = rec.tag_ids[0].id
            course_level = rec.course_level_id

            data = {'id': rec.id,
                    'name': rec.name,
                    'description': rec.description,
                    'image': urls.url_join(base_url,
                                           '/web/image?model=slide.channel&id={0}&field=image_1920'.format(
                                               rec.id)),
                    'course_level': course_level,  # cấp độ học
                    'rating_avg_stars': rec.rating_avg,  # đánh giá trung bình, tự chia cho 5, vd 3/5
                    'total_time': rec.total_time,
                    }
            vals.append(data)
        for i in range(len(partner_channel)):
            vals[i]['process'] = partner_channel[i].completion
        return valid_response(vals)

    @http.route("/api/all_courses", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
    def get_all_courses(self, **payload):
        values = []
        base_url = AllCoursesController.get_url_base(self)
        all_courses = request.env['slide.channel'].search([('is_published', '=', True)])  # .sudo()
        for rec in all_courses:
            # cấp độ học
            # tag_id = rec.tag_ids[0].id
            course_level = rec.course_level_id
            level = rec.level if rec.level else 'none'

            dates = {'id': rec.id,
                     'name': rec.name,
                     'description': rec.description,
                     'image': urls.url_join(base_url,
                                            '/web/image?model=slide.channel&id={0}&field=image_1920'.format(
                                                rec.id)),
                     'level': level,
                     'is_special': rec.is_special,
                     'course_level': course_level,  # cấp độ học
                     'rating_avg_stars': rec.rating_avg if rec.rating_avg != 0 else 'Chưa có đánh giá nào',  # đánh giá trung bình, tự chia cho 5, vd 3/5
                     'total_time': rec.total_time,  # tổng thời lượng khoá học
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
            category = []
            # print(rec.slide_ids)
            total_slide = 0
            count_time_slide = 0
            for slide in rec.slide_ids:
                # print(slide.completion_time)
                if slide.is_category != True:
                    total_slide += 1
                    count_time_slide += slide.completion_time
            dates['total_slide'] = total_slide
            dates['count_time_slide'] = count_time_slide
            #
            #     slide_info = {
            #         'name': slide.name,
            #         'slide_type': slide.slide_type,
            #         'completion_time': slide.completion_time,
            #     }
            #     slides.append(slide_info)
            # dates['slides'] = slides
            # print(dates)
            values.append(dates)
        return valid_response(values)
