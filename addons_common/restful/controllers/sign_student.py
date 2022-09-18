import logging

from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from werkzeug import urls

from odoo.addons.restful.common import invalid_response
from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class SignStudent(http.Controller):

    @http.route("/api/v1/sign/student", type='http', auth="public", methods=["POST", "OPTIONS"], website=True,
                csrf=False, cors="*")
    def sign_student(self, **payload):
        field_require = [
            'login',
            'password',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        domain = {
            'name': payload.get('login'),
            'login': payload.get('login'),
            'password': '1'
        }
        request.env['res.users'].with_user(SUPERUSER_ID).create(domain)
        return invalid_response("Bạn đã ứng tuyển thành công vào vị trí %s." % payload.get('job_name'))

    @http.route("/api/update-infor-student", type='http', auth="public", methods=["POST", "OPTIONS"], website=True,
                csrf=False, cors="*")
    def update_infor_student(self, **payload):
        field_require = [
            'login',
            'password',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        domain = {
            'name': payload.get('login'),
            'login': payload.get('login'),
            'password': '1'
        }
        user = request.env['res.users'].with_user(SUPERUSER_ID).create(domain)
        print(user)
        return invalid_response("Bạn đã ứng tuyển thành công vào vị trí %s." % payload.get('job_name'))
