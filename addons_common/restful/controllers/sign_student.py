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

    @http.route("/api/v1/sign/student", type='http', auth="public", methods=["POST", "OPTIONS"],
                csrf=False, cors="*")
    def sign_student(self, **payload):
        group_public = self.env.ref('base.group_public')
        domain = {
            'name': payload.get('login'),
            'login': payload.get('login'),
            'password': payload.get('password'),
            'active': 'False',
            'groups_id': [0, 0, group_public.id],
            'share': False
        }
        user = request.env['res.users'].sudo().create(domain)
        vals = {
            'name': payload.get('ho') + payload.get('ten'),
            'email': payload.get('login'),
            'user_id': user.id,
            'birth': payload.get('birth'),
            'phone': payload.get('phone'),
            'gender': payload.get('gender'),
            'position': payload.get('position'),
            'work_unit': payload.get('work_unit'),
            'res_country_state': payload.get('res_country_state'),
            'res_country_ward': payload.get('res_country_ward'),
            'res_country_district': payload.get('res_country_district'),
        }
        request.env['student.student'].sudo().create(vals)
        return valid_response("Bạn đã đăng kí thành công !")

    @http.route("/api/update-infor-student", type='http', auth="public", methods=["POST", "OPTIONS"],
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
        return valid_response("Cập nhập thành công!")
