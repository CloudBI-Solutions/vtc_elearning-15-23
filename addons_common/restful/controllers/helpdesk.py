"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

from odoo.addons.restful.common import (
    invalid_response,
)
from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class HelpdeskController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/helpdesk/create_helpdesk", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False, cors='*')
    def post_helpdesk(self, **payload):
        print(request.uid)
        # user = request.env['res.users'].sudo().search([('id', '=', payload.get('uid'))])
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'type_maintenance_request',
            'title',
            'area_type_maintenance_request',
        ]
        cate = request.env['sci.maintenance.equipment.category'].sudo().search([('id', '=', '1')])
        print(cate)
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        helpdesk = request.env['sci.maintenance.request'].with_user(SUPERUSER_ID).create({
            'name': payload.get('title'),
            'user_request': request.uid,
            'type': 'onetouch',
            'type_maintenance_request': int(payload.get('type_maintenance_request')),
            'area_type_maintenance_request': int(payload.get('area_type_maintenance_request')),
            'category_id': int(payload.get('cate')),
        })
        return invalid_response("ok")

    @validate_token
    @http.route("/api/v1/type_maintenance_request", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_type_maintenance_request(self, **payload):
        values = []
        data = request.env['type.maintenance.request'].sudo().search([('type', '=', 'onetouch')])
        for rec in data:
            dates = {'id': rec.id,
                     'type': rec.type,
                     'name': rec.name,
                     }
            area = []
            for are in rec.area:
                area.append({
                    'id': are.id,
                    'name': are.name,
                    'the_average_time': are.the_average_time or '',
                })
            dates['area'] = area
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/category-helpdesk", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_category_helpdesk(self, **payload):
        values = []
        data = request.env['sci.maintenance.equipment.category'].sudo().search([])
        for rec in data:
            dates = {'id': rec.id,
                     'department': rec.department_id.name,
                     'name': rec.name,
                     'email': rec.email,
                     'manager': rec.technician_user_id.name,
                     }
            main_team = []
            for team in rec.team_ids:
                team_ids = {
                    'name': team.name,
                    'manager': rec.technician_user_id.name,
                }
                main_team.append(team_ids)
                member_ids = []
                for mem in team.member_ids:
                    member = {
                        'id': mem.id,
                        'name': mem.name,
                    }
                    member_ids.append(member)
                team_ids['member'] = member_ids
            dates['team'] = main_team
            values.append(dates)
        return valid_response(values)

    @http.route('/api/v1/helpdesk/update-helpdesk', type='http', auth='public', method=['PUT'], csrf=False)
    def func_update_helpdesk(self, **payload):
        values = {}

        get_helpdesk = request.env['sci.maintenance.request'].sudo().search([('id', '=', int(payload.get('id')))])
        if not get_helpdesk:
            return valid_response({
                "invalid object model \nThe model is not available in the registry."
            })

        if payload.get('state'):
            values['state'] = payload.get('state')
        if payload.get('type'):
            values['type'] = payload.get('type')
        # người gửi yêu cầu
        if payload.get('person_name'):
            get_person = request.env['hr.employee'].sudo().search([('id', '=', int(payload.get('person_name')))])
            values['person_name'] = payload.get('person_name')
            values['department'] = get_person.department_id.name
            values['email'] = get_person.work_email
            values['phone'] = get_person.work_phone
        # danh sách nhân sự hỗ trợ
        if payload.get('supervisor_ids'):
            values['supervisor_ids'] = [int(i) for i in eval(payload.get('supervisor_ids'))]
        # hiện trạng/nguyên nhân
        if payload.get('tools_description'):
            values['tools_description'] = payload.get('tools_description')
        # giải pháp khắc phục
        if payload.get('operations_description'):
            values['operations_description'] = payload.get('operations_description')

        get_helpdesk.update(values)
