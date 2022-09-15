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

    # @validate_token
    @http.route("/api/get/all_courses", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_all_courses(self, **payload):
        values = []
        base_url = AllCoursesController.get_url_base(self)
        all_courses = request.env['slide.channel'].search([('is_published', '=', True)])      # .sudo()
        for rec in all_courses:
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
                slide_info = {
                    'name': slide.name,
                    'slide_type': slide.slide_type,
                    'completion_time': slide.completion_time,
                }
                slides.append(slide_info)
            dates['slides'] = slides
            # print(dates)
            values.append(dates)
        return valid_response(values)
