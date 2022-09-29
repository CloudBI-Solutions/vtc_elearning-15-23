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


class MainPayment(http.Controller):

	# @validate_token
	@http.route("/api/momo/payment/atm", type='http', auth="public", methods=["POST"],
	            csrf=False, cors="*")
	def momo_api_paymentqr(self, **kwargs):
		field_requied = [
			'sale_id',
			'uid'
		]
		order = request.env['account.move'].sudo().search([('id', '=', int(4))])
		response = self.redirect_to_momo(order=order)
		return werkzeug.utils.redirect(response.json()['payUrl'])

	def redirect_to_momo(self, order):
		endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
		accessKey = request.env['ir.config_parameter'].sudo().get_param('momo_accessKey')
		secretKey = request.env['ir.config_parameter'].sudo().get_param('momo_secretKey')
		orderInfo = str(order.name)
		partnerCode = request.env['ir.config_parameter'].sudo().get_param('momo_partnerCode')
		redirectUrl = "http://localhost:8073/api/payment/succsess/{}".format(order.name)
		ipnUrl = "http://localhost:8073/api/payment/succsess/{}".format(order.name)
		amount_order = str(order.amount_total)
		amount = amount_order[:-2]
		amount = str(amount)
		orderId = str(uuid.uuid4())
		requestId = str(uuid.uuid4())
		extraData = ""  # pass empty value or Encode base64 JsonString
		partnerName = "MoMo Payment"
		requestType = "payWithMethod"
		storeId = "Test Store"
		orderGroupId = ""
		autoCapture = True
		lang = "vi"
		orderGroupId = ""

		# before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
		# &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
		# &requestType=$requestType
		rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId \
		               + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl \
		               + "&requestId=" + requestId + "&requestType=" + requestType

		# puts raw signature
		print("--------------------RAW SIGNATURE----------------")
		print(rawSignature)
		# signature
		h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
		signature = h.hexdigest()
		print("--------------------SIGNATURE----------------")
		print(signature)

		# json object send to MoMo endpoint

		data = {
			'partnerCode': partnerCode,
			'orderId': orderId,
			'partnerName': partnerName,
			'storeId': storeId,
			'ipnUrl': ipnUrl,
			'amount': amount,
			'lang': lang,
			'requestType': requestType,
			'redirectUrl': redirectUrl,
			'autoCapture': autoCapture,
			'orderInfo': orderInfo,
			'requestId': requestId,
			'extraData': extraData,
			'signature': signature,
			'orderGroupId': orderGroupId
		}

		print("--------------------JSON REQUEST----------------\n")
		data = json.dumps(data)
		print(data)

		clen = len(data)
		response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

		# f.close()
		print("--------------------JSON response----------------\n")
		print(response.json())
		return response
