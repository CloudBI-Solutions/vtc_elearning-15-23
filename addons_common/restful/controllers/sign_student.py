import logging

from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from werkzeug import urls

from odoo.addons.restful.common import invalid_response
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
import base64
import json

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

    @validate_token
    @http.route("/api/update-avt-student", type='http', auth="public", methods=["POST", "OPTIONS"],
                csrf=False, cors="*")
    def update_infor_student(self, **kwargs):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        data_model = request.env['student.student'].search([('user_id', '=', user.id)])
        FileStorage = kwargs.get('file')
        FileExtension = FileStorage.filename.split('.')[-1].lower()
        ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png', 'gif']
        if FileExtension not in ALLOWED_IMAGE_EXTENSIONS:
            return json.dumps({'status': 400, 'message': _("Only allowed image file with extension: %s" % (",".join(ALLOWED_IMAGE_EXTENSIONS)))})
        try:
            FileData = FileStorage.read()
            file_base64 = base64.b64encode(FileData)
            data_model.avatar = file_base64
            return json.dumps({'status': 200, 'message': _("Success")})
        except Exception as e:
            print(e)
            return invalid_response01(e)
