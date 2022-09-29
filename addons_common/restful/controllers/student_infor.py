import logging

from odoo.addons.restful.common import (
    valid_response,
    invalid_response
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class StudentInfor(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/get/infor_student", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
    def get_infor_student_by_id(self, **payload):
        values = []
        base_url = StudentInfor.get_url_base(self)
        print(request.uid)
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        student = request.env['student.student'].sudo().search([('user_id', '=', user.id)])
        if not student:
            return invalid_response(
                "Kiểm tra xem người đang đăng nhập đã là student chưa, nếu có rồi thì kiểm tra xem trong thằng student này đã có tài khoản chưa")
        # cấp độ học
        datas = {'id': user.id,
                 'name': user.name,
                 'avatar': urls.url_join(base_url,
                                         '/web/image?model=student.student&id={0}&field=avatar'.format(
                                             student.id)),
                 'birth': student.birth,
                 'phone': student.phone,
                 'email': student.email,
                 'position': {'id': student.position.id, 'name': student.position.name} or '',
                 'work_unit': student.work_unit,
                 'res_country_state': {'id': student.res_country_state.id,
                                       'name': student.res_country_state.name} or '',
                 'res_country_ward': {'id': student.res_country_ward.id, 'name': student.res_country_ward.name} or '',
                 'res_country_district': {'id': student.res_country_district.id,
                                          'name': student.res_country_district.name} or '',
                 }
        values.append(datas)
        return valid_response(values)
