import logging

from odoo.addons.restful.common import (
    valid_response,
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

    @http.route("/api/get/infor-student", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_infor_student_by_id(self, **payload):
        values = []
        print(payload)
        base_url = StudentInfor.get_url_base(self)
        student = request.env['student.student'].sudo().search([('id', '=', payload.get('student_id'))])
        # cấp độ học
        datas = {'id': student.id,
                 'name': student.name,
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
