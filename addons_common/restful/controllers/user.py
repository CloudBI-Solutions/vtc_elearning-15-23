"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging
from random import randint

from odoo.addons.restful.common import (
	valid_response,
	invalid_response
)
from odoo.addons.restful.controllers.main import (
	validate_token
)
import re

# Make a regular expression
# for validating an Email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Define a function for
# for validating an Email

import passlib.context
import operator
from odoo.exceptions import AccessError, UserError, AccessDenied
from werkzeug import urls
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

DEFAULT_CRYPT_CONTEXT = passlib.context.CryptContext(
	# kdf which can be verified by the context. The default encryption kdf is
	# the first of the list
	['pbkdf2_sha512', 'plaintext'],
	# deprecated algorithms are still verified as usual, but ``needs_update``
	# will indicate that the stored hash should be replaced by a more recent
	# algorithm. Passlib 1.6 supports an `auto` value which deprecates any
	# algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
	deprecated=['plaintext'],
)


class ResUsersController(http.Controller):

	def check(self,email):

		# pass the regular expression
		# and the string into the fullmatch() method
		if re.fullmatch(regex, email):
			print("Valid Email")

		else:
			print("Invalid Email")

	def _crypt_context(self):
		""" Passlib CryptContext instance used to encrypt and verify
		passwords. Can be overridden if technical, legal or political matters
		require different kdfs than the provided default.

		Requires a CryptContext as deprecation and upgrade notices are used
		internally
		"""
		return DEFAULT_CRYPT_CONTEXT

	def get_url_base(self):
		config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
		if config:
			return config
		return 'https://test.diligo.vn:15000'

	@http.route("/api/otp/check", type="http", auth="public", methods=["POST"], csrf=False, cors="*")
	def check_with_otp(self, **kwargs):
		otp = int(kwargs.get('otp'))
		user = request.env['res.users'].sudo().search([('otp', '=', otp)])
		if not user:
			return invalid_response('otp không chính xác')
		return valid_response({
			'user_id': user.id
		})

	@http.route("/api/change_new_pass_otp", type='http', auth='public', methods=["POST"], csrf=False, cors="*")
	def change_new_pass_otp(self, **kwargs):
		if kwargs.get('user_id_otp'):
			user = request.env['res.users'].sudo().search([('id','=', kwargs.get('user_id_otp'))])
			res = request.env.cr.execute(
				'UPDATE res_users SET password=%s WHERE id=%s',
				(kwargs.get('newpass'), int(user.id))
			)
			return valid_response('Success changed!')


	@http.route("/api/resetpassword/send_token_by_email", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors="*")
	def send_token_by_email(self, **kwargs):
		student = request.env['student.student'].sudo().search([('email', '=', kwargs.get('email_reset'))])
		mail_server = request.env['ir.mail_server'].sudo().search([('active', '=', True)], limit=1,
																  order='sequence DESC')
		user = student.user_id
		otp_num = []
		for i in range(6):
			num = randint(0, 9)
			otp_num.append(str(num))
		otp_num = ''.join(otp_num)
		main_content = {
			'subject': _("Thư thay đổi mật khẩu"),
			'email_from': mail_server.smtp_user,
			'body_html': '<p> Chào {},</p> Chúng tôi vừa nhận được yêu cầu cấp lại mật khẩu cho tài khoản của bạn trên '
						 'Website One Touch. Hệ thống đã cấp lại mật khẩu mới cho bạn: {}. '
						 '<p>+ Vui lòng bỏ qua thư này nếu bạn không gửi yêu cầu đến chúng tôi</p>'
						 '<p>+ Email cập nhật mật khẩu chỉ có giá trị trong 3 ngày</p>'.format(student.name, otp_num),
			'email_to': kwargs.get('email_reset'),
		}
		request.env['mail.mail'].sudo().create(main_content).send()
		user.otp = otp_num
		# if self.check(kwargs.get('email_reset')):
		return valid_response('ok')

	@validate_token
	@http.route("/api/v1/reset_password", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
	def reset_password_user(self, **kwargs):
		fields = [{'name': 'old_pwd', 'value': 'admin'}, {'name': 'new_password', 'value': '12'}, {'name': 'confirm_pwd', 'value': '12'}]
		fields[0]['value'] = kwargs.get('password')
		fields[1]['value'] = kwargs.get('newpass')
		fields[2]['value'] = kwargs.get('pass_confirm')
		old_password, new_password, confirm_password = operator.itemgetter('old_pwd', 'new_password', 'confirm_pwd')(
			{f['name']: f['value'] for f in fields})
		if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
			return invalid_response('You cannot leave any password empty.')
		if new_password != confirm_password:
			return invalid_response('The new password and its confirmation must be identical.')

		request.env.cr.execute(
			"SELECT COALESCE(password, '') FROM res_users WHERE id={}".format(int(kwargs.get('uid'))))
		[hashed] = request.env.cr.fetchone()
		valid, replacement = self._crypt_context().verify_and_update(kwargs.get('password'), hashed)

		if not valid:
			return invalid_response('Old password is not true, pls try again!')

		if valid:
			res = request.env.cr.execute(
				'UPDATE res_users SET password=%s WHERE id=%s',
				(kwargs.get('newpass'), int(kwargs.get('uid')))
			)

		return valid_response('Success changed!')

	@http.route("/api/v1/res_users", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
	def get_res_users(self, **payload):
		values = []
		base_url = ResUsersController.get_url_base(self)
		data = request.env['res.users'].sudo().search([])
		for rec in data:
			dates = {'id': rec.id,
			         'name': rec.name,
			         'avatar': urls.url_join(base_url,
			                                 '/web/image?model=res.users&id={0}&field=image_1920'.format(
				                                 rec.id)),
			         }
			values.append(dates)
		return valid_response(values)
