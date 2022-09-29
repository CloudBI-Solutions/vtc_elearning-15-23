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


	@http.route("/api/momo/payment/atm", type='http', auth="public", methods=["POST"],
	            csrf=False, cors="*")
	def test_api_paymentqr(self, **kwargs):
		endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
		accessKey = "F8BBA842ECF85"
		secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
		orderInfo = "pay with MoMo"
		partnerCode = "MOMO"
		redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
		ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
		amount = "50000"
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
		return werkzeug.utils.redirect(response.json()['payUrl'])
