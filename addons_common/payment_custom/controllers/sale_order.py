import logging

from odoo.addons.restful.common import (
	valid_response,
)
from odoo.addons.restful.controllers.main import (
	validate_token
)
import werkzeug
from werkzeug import exceptions, utils

from werkzeug import urls
from odoo import http
from odoo.http import request
import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib

_logger = logging.getLogger(__name__)


class SaleController(http.Controller):

	@validate_token
	@http.route("/api/payment/cource", type='http', auth="public", methods=["POST"],
	            csrf=False, cors="*")
	def payment_cource(self, **kwargs):
		field_require = [
			'course_ids',
			'uid'
		]
		print(kwargs.get('course_ids'))
		print(type(kwargs.get('course_ids')))
		raise
		for field in field_require:
			if field not in kwargs.keys():
				return invalid_response(
					"Missing",
					"The parameter %s is missing!!!" % field)
		courses = request.env['slide.channel'].sudo().search([('id', 'in', kwargs.get('course_ids'))])
		print(courses)
		return valid_response('ok')
