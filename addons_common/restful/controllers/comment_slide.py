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


class CommentSlide(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/comment/slide", type='http', auth="public", methods=["GET", "OPTIONS"], website=False,
                cors="*")
    def get_comment_slide_by_id(self, **payload):
        values = []
        base_url = CommentSlide.get_url_base(self)
        # comment1 = request.env['comment.slide'].sudo().search([('slide_id', '=', int(payload.get('lesson_id')))])
        list_comment = request.env['comment.slide'].sudo().search([('slide_id', '=', int(payload.get('lesson_id')))])
        print(list_comment)
        for record in list_comment:
            data = {
                'id': record.id,
                'content': record.name,
                'user_id': {'id': record.user_id.id, 'name': record.user_id.name, 'avatar': urls.url_join(base_url,
                                                                                                          '/web/image?model=res.users&id={}&field=image_1920'.format(
                                                                                                              record.user_id.id))} or '',
                # 'content': record.name,
            }
            comments_below = []
            for rec in record.comment_ids:
                comment_ids = {
                    'id': rec.id,
                    'content': rec.name,
                    'user_id': {'id': rec.user_id.id, 'name': rec.user_id.name, 'avatar': urls.url_join(base_url,
                                                                                                        '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                                                                            record.user_id.id))} or '',
                }
                comments_below.append(comment_ids)
                data['comments_below'] = comments_below

            values.append(data)
        return valid_response(values)

    @http.route("/api/v1/add-comment-slide", type='http', auth="public", methods=["POST", "OPTIONS"], website=True,
                csrf=False, cors="*")
    def add_comment_slide_by_id(self, **payload):
        field_require = [
            'name',
            'slide_id',
            'comment_id',
            'uid',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        domain = {
            'name': payload.get('name'),
            'slide_id': int(payload.get('slide_id')),
            'comment_id': payload.get('comment_id'),
            'user_id': payload.get('uid'),
        }
        ress = request.env['comment.slide'].sudo().create(domain)
        return valid_response({
            'ok': 'ok'
        })
