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


class ResCountry(http.Controller):

    @http.route("/api/get/country", type='http', auth="public", methods=["GET"],
                csrf=False, cors="*")
    def get_country(self, **payload):
        values = []
        data = request.env['res.country.state'].sudo().search([('country_id', '=', 'VN')])
        for rec in data:
            dates = {'name': rec.name,
                     'id': rec.id,
                     }
            country_district = []
            for district in rec.district_ids:
                data_district = {
                    'id': district.id or '',
                    'name': district.name or '',
                }
                country_district.append(data_district)
                country_ward = []
                for ward in district.ward_ids:
                    data_ward = {
                        'id': ward.id,
                        'name': ward.name,
                    }
                    country_ward.append(data_ward)
                    data_district['ward'] = country_ward
                dates['district'] = country_district
            values.append(dates)
        return valid_response(values)
