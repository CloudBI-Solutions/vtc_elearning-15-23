import logging

from odoo.addons.restful.common import (
    valid_response,
)
from werkzeug import urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PositionStudent(http.Controller):


    @http.route("/api/get/position-student", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_position_student(self, **payload):
        values = []
        position = request.env['position'].sudo().search([])
        # cấp độ học
        for record in position:
            datas = {'id': record.id,
                     'name': record.name,
                     }
            values.append(datas)
        return valid_response(values)
