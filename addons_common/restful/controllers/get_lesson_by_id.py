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


class LessonByIdController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    def get_url_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        return "web/content2/?model=ir.attachment&id=" + str(
            attachment_id) + "&filename_field=name&field=datas&download=true"

    @validate_token
    @http.route("/api/lesson_by_id", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
    def get_lesson_by_id(self, **payload):
        values = []
        base_url = LessonByIdController.get_url_base(self)
        list_lessons = request.env['slide.slide'].sudo().search(
            [('is_published', '=', True), ('id', '=', payload.get('lesson_id'))])

        for rec in list_lessons:
            # list_quiz = []
            # for r in rec.question_ids:
            #     print(r)
            list_attachment_files = request.env['ir.attachment'].sudo().search(
                [('res_model', '=', 'slide.slide'), ('res_id', '=', rec.id)])
            dates = {'id': rec.id, 'name': rec.name, 'slide_type': rec.slide_type, 'channel_id': rec.channel_id,
                     'mime_type': rec.mime_type, 'completion_time': rec.completion_time,
                     'date_published': rec.date_published, 'create_uid': rec.create_uid, 'description': rec.description,
                     'url': rec.url or rec.document_url or False
                     }

            # thông tin tab nội dung
            # slides = []
            # for slide in rec.slide_ids:
            #     slide_detail = {
            #         'id': slide.id,
            #         'name': slide.name,
            #         'slide_type': slide.slide_type,
            #         'completion_time': slide.completion_time,
            #     }
            #     slides.append(slide_detail)
            # dates['slide_ids'] = slides

            # tài liệu
            # print('list attachment: ', list_attachment_files)
            # đố vui
            values.append(dates)
        return valid_response(values)
