import base64
import logging

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
    valid_response_once,
)

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class StudentInfor(http.Controller):

    @http.route("/api/v1/rating-system", type='http', auth="public", methods=["POST", "OPTIONS"], website=True,
                csrf=False, cors="*")
    def rating_system(self, **payload):
        field_require = [
            'uid',
            'system_onetouch',
            'rating_lecturers',
            'content_slide',
            'teaching_methods',
            'inspire',
            'document_quality',
            'helpful',
            'service_quality',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        domain = {
            'user_id': payload.get('uid'),
            'system_onetouch': payload.get('system_onetouch'),
            'rating_lecturers': payload.get('rating_lecturers'),
            'content_slide': payload.get('content_slide'),
            'teaching_methods': payload.get('teaching_methods'),
            'inspire': payload.get('inspire'),
            'document_quality': payload.get('document_quality'),
            'helpful': payload.get('helpful'),
            'service_quality': payload.get('service_quality'),
        }
        request.env['rating.system'].sudo().create(domain)
        return invalid_response("Bạn đã ứng tuyển thành công vào vị trí %s." % payload.get('job_name'))
