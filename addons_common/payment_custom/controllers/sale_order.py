import logging

from odoo.addons.restful.common import (
	valid_response,
	invalid_response
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
	@http.route("/api/order/cource", type='http', auth="public", methods=["POST"],
	            csrf=False, cors="*")
	def payment_cource(self, **kwargs):
		field_require = [
			'course_ids',
			'uid'
		]
		for field in field_require:
			if field not in kwargs.keys():
				return invalid_response(
					"Missing",
					"The parameter %s is missing!!!" % field)
		courses = request.env['slide.channel'].sudo().search([('id', '=', int(kwargs.get('course_ids')))])
		user_login = request.env['res.users'].sudo().search([('id', '=', kwargs.get('uid'))])
		product = request.env['product.product'].sudo().search([('default_code', '=', courses.cource_referen)])
		order_line = {
			'product_id': product.id,
			'product_uom_qty': 1,
			'price_unit': product.lst_price
		}
		# create sale order
		res = request.env['sale.order'].sudo().create({
			'partner_id': user_login.partner_id.id,
			'order_line': [(0, 0, order_line)],
		})
		if res.amount_total < 1000 or res.amount_total > 50000000:
			return invalid_response("Yêu cầu bị từ chối vì số tiền đơn hàng nhỏ hơn số tiền tối thiểu cho phép là 1000 VND hoặc lớn hơn số tiền tối đa cho phép là 50000000 VND.")
		res.sudo().action_confirm()
		inv = res.sudo()._create_invoices(final=True)
		inv.sudo().action_post()
		return valid_response({
			'orderInfo': inv.name,
			'orderId': inv.id,
			'message': 'Đơn hàng của bạn đã tạo thành công!'
		})

	@http.route("/api/payment/succsess/<string:orderCode>", type='http', auth="public", methods=["GET"],
	            csrf=False, cors="*")
	def payment_confirm_succsess(self, orderCode):
		print(orderCode)
		return valid_response('ok')
