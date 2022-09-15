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
        return "web/content2/?model=ir.attachment&id=" + str(attachment_id) + "&filename_field=name&field=datas&download=true"

    @validate_token
    @http.route("/api/lesson_by_id", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_lesson_by_id(self, **payload):
        values = []
        base_url = LessonByIdController.get_url_base(self)
        list_lessons = request.env['slide.slide'].search(
            [('is_published', '=', True), ('id', '=', payload.get('lesson_id'))])

        for rec in list_lessons:

            dates = {'id': rec.id,
                     'name': rec.name,
                        'slide_type': rec.slide_type,   # loai
                     'channel_id': rec.channel_id,      # khoa hoc
                     'mime_type': rec.mime_type,
                     'completion_time': rec.completion_time,    # thoi luong
                     'date_published': rec.date_published,        # ngay dang
                     'create_uid': rec.create_uid,              # nguoi dang
                     'description': rec.description,            #mo ta
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
            list_attachment_files = request.env['ir.attachment'].sudo().search([('res_model', '=', 'slide.slide'), ('res_id', '=', rec.id)]).ids
            # print('list attachment: ', list_attachment_files)
            list_attachment = [urls.url_join(base_url, self.get_url_attachment(att_id)) for att_id in
                               list_attachment_files]
            dates['files'] = list_attachment

            # đố vui
            dates['quiz'] = {
                'quiz_1': rec.quiz_first_attempt_reward,
                'quiz_2': rec.quiz_second_attempt_reward,
                'quiz_3': rec.quiz_third_attempt_reward,
                'quiz_4': rec.quiz_fourth_attempt_reward
            }

            values.append(dates)
        return valid_response(values)

