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
    @http.route("/api/update/lession/process", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False, cors="*")
    def update_lession_process(self, **kwargs):
        print('2')
        return valid_response('ok')

    @validate_token
    @http.route("/api/lesson_by_id", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
    def get_lesson_by_id(self, **payload):
        values = []
        base_url = LessonByIdController.get_url_base(self)
        lesson = request.env['slide.slide'].sudo().search(
            [('is_published', '=', True), ('id', '=', payload.get('lesson_id'))])
        dates = {
            'id': lesson.id, 'name': lesson.name, 'slide_type': lesson.slide_type, 'channel_id': lesson.channel_id,
            'mime_type': lesson.mime_type, 'completion_time': lesson.completion_time,
            'date_published': lesson.date_published, 'create_uid': lesson.create_uid, 'description': lesson.description,
            'url': lesson.url or lesson.document_url or False,
            'duration': lesson.completion_time,
            'base64_file': lesson.datas or lesson.file_upload or False
        }
        quiz = [{'question_id': r.id, "question_name": r.question,
                 "answer": [{'answer_name': rec.text_value, 'is_correct': rec.is_correct, 'comment': rec.comment} for
                            rec in r.answer_ids]} for r in lesson.question_ids]
        # list_attachment_files = request.env['ir.attachment'].sudo().search(
        # [('res_model', '=', 'slide.slide'), ('res_id', '=', lesson.id)])
        dates['quiz'] = quiz
        values.append(dates)
        return valid_response(values)
