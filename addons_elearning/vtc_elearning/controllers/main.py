# -*- coding: utf-8 -*-

import logging

import boto3
import werkzeug
from werkzeug import utils
from werkzeug.exceptions import BadRequest, Forbidden

from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.http import request
import unidecode

_logger = logging.getLogger(__name__)

ACCESS_KEY_ID = 'AKIAWSHGFYLDQJNV2J4R'
ACCESS_SECRET_KEY = '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'


class S3MediaUpload(http.Controller):

    @http.route(['/get_list_url'], type='json', auth="public", methods=['POST'],
                website=True)
    def get_list_url(self, model, id, **kwargs):
        if model and id:
            record = self.env[model].browse(id)
            return record.s3_urls

    @http.route(['/upload_to_s3'], type='http', auth="user",
                website=True, csrf=False)
    def upload_file_S3(self, **kwargs):
        self._check_security()

        def get_value(direct):
            search_value = {
                'video': 'videos',
                'document': 'documents',
            }
            value_search = search_value.get(direct, None)
            return value_search

        directory = get_value(kwargs['directory'])
        folder = get_value(kwargs['folder'])

        media_list = request.httprequest.files.getlist('upload_files')
        s3_bucket = request.env['ir.config_parameter'].sudo().get_param('s3_bucket', False)
        s3_media_obj = request.env["s3.media"].sudo()
        current_ids = s3_media_obj.search([]).mapped('file_name')
        s3 = boto3.resource('s3')
        for upload_file in media_list:
            if upload_file.filename in current_ids:
                raise ValidationError(_('%s exists on S3 Storage' % (upload_file.filename)))
            content_type = upload_file.content_type
            key = f"{directory}/{upload_file.filename}"
            media = s3_media_obj.search([('bucket_name', '=', s3_bucket), ('key', '=', key)])
            s3.Bucket(s3_bucket).put_object(Key=key, Body=upload_file, Metadata={'ContentType': content_type})
            result = s3.Object(s3_bucket, f"{directory}/{upload_file.filename}")
            if media:
                media.write({
                    'file_name': upload_file.filename,
                    'content_length': result.content_length / 1024,
                    'content_type': content_type,
                    'directory': directory,
                    'folder_id': folder,
                })
                media.generate_presigned_url()
            else:
                media = s3_media_obj.create({
                    'file_name': upload_file.filename,
                    'bucket_name': result.bucket_name,
                    'key': result.key,
                    'content_length': result.content_length / 1024,
                    'content_type': content_type,
                    'directory': directory,
                    'folder_id': folder,
                })
                active_model = request.env[kwargs['active_model']].sudo().browse(int(kwargs['active_id']))
                active_model.s3_media_ids = [(4, media.id)]

    @http.route('/upload/slide/<int:id>', type='http', auth='user', website=True)
    def open_upload_form(self, id):
        # Check security
        self._check_security()
        print(id)
        print('vnkven')
        request._cr = None
        values = {
            "slide_id": id,
        }
        print(values)
        return request.render("vtc_elearning.s3_media_upload_render", values)

    @http.route('/hoya/media_upload_form/success', type='http', auth='user', website=True)
    def open_upload_success_form(self, title='', message=''):
        # Check security
        self._check_security()
        request._cr = None
        return request.render("vti_aws_media.s3_media_upload_finish", {'message': message,
                                                                       'title': title})

    @http.route('/hoya/media/<int:id>/', type='http', auth='user', website=True)
    def s3_download_file(self, id):
        try:
            media_id = request.env["s3.media"].browse(id)
            media_id.sudo().generate_presigned_url()
            aws_url = media_id.url
            if aws_url:
                return werkzeug.utils.redirect(aws_url)
            else:
                return False
        except:
            return False

    @http.route('/hoya/media_upload/<int:id>', auth="user", methods=['POST'], csrf=False)
    def s3_upload_file(self, id=None, directory=None, folder=None, upload_files=None, name='', **kwargs):
        self._check_security()
        slide = request.env['slide.slide'].sudo().search([('id', '=', id)])
        unaccented_string = unidecode.unidecode(slide.channel_id.name)
        bucket = (unaccented_string.replace(' ', '-')).lower()
        s3 = boto3.resource('s3', endpoint_url='https://ss-hn.fptvds.vn',
                            aws_access_key_id='vtcnetviet@A2022!',
                            aws_secret_access_key='a6I6aPf8BRp0kGW2F3h8sC9fDodMUmgQiqRBydAi')
        s3.create_bucket(Bucket=bucket)
        media_list = request.httprequest.files.getlist('upload_files')
        support_types = []
        if directory == 'images':
            support_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/gif', ]
            # ACCEPT_EXT = ['.jpeg', '.jpg', '.png', '.bmp', '.gif']
        elif directory == 'videos':
            support_types = ['video/mp4', 'video/quicktime', 'video/x-ms-wmv', 'video/webm', 'video/mpeg',
                             'video/x-matroska', 'video/x-msvideo', 'audio/mpeg', 'audio/x-wav', 'audio/mp4a-latm']
        elif directory == 'documents':
            support_types = ['application/pdf',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        for upload_file in media_list:
            content_type = upload_file.content_type
            print(support_types)
            print(content_type)
            if content_type not in support_types:
                print('vnweoivneov')
                message = _('Media format type is not suitable.')
                title = _('Upload Error!')
                request._cr = None
                return request.redirect('/hoya/media_upload_form/success?title=%s&message=%s' % (title, message))

            key = f"{directory}/{upload_file.filename}"
            if self._check_media_exits(bucket, key):
                message = _('The media file has been uploaded before.')
                title = _('Upload Error!')
                return request.redirect('/hoya/media_upload_form/success?title=%s&message=%s' % (title, message))

            s3 = boto3.resource('s3', endpoint_url='https://ss-hn.fptvds.vn',
                                aws_access_key_id='vtcnetviet@A2022!',
                                aws_secret_access_key='a6I6aPf8BRp0kGW2F3h8sC9fDodMUmgQiqRBydAi')

            s3.Bucket(bucket).put_object(Key=key, Body=upload_file, Metadata={'ContentType': content_type})
            print(';vnkjcvno')
            print(content_type)
            result = s3.Object(bucket, f"{directory}/{upload_file.filename}")
            print(directory)
            domain = {
                'file_name': upload_file.filename,
                'bucket_name': result.bucket_name,
                'key': result.key,
                'content_length': result.content_length / 1024,
                'content_type': content_type,
                'directory': directory,
            }
            if directory == 'videos':
                domain['slide_type'] = 'video'
            else:
                domain['slide_type'] = 'document'
            slide.update(domain)
        # return request.redirect('/hoya/media_upload_form/success?title=%s&message=%s' % (title, message))



    def open_media_view(self, ids=False):
        form_view = request.env.ref('vti_aws_media.s3_vti_aws_media_form').id
        tree_view = request.env.ref('vti_aws_media.s3_vti_aws_media_list').id
        return {
            'domain': str([('id', 'in', ids)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 's3.media',
            'view_id': False,
            'views': [(tree_view, 'tree'), (form_view, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'new'
        }

    def _check_media_exits(self, bucket, key):
        try:
            client = boto3.client('s3')
            content = client.head_object(Bucket=bucket, Key=key)
            if content.get('ResponseMetadata', None) is not None:
                return True
        except Exception:
            pass
        return False

    # @http.route('/hoya/media/<int:id>/', type='http', auth="user", website=True)
    # def get_media_form_view(self, id):
    #     menu_id = request.env.ref('vti_aws_media.s3_media_menu').id
    #     action_id = request.env.ref('vti_aws_media.s3_media_action').id
    #     link_format = "/web#id={}&view_type=form&model=s3.media&menu_id={}&action={}"
    #     link = link_format.format(id, menu_id, action_id)
    #     return request.redirect(link)

    @http.route('/hoya/media/list/', type='http', auth="user", website=True)
    def get_media_form_view(self):
        menu_id = request.env.ref('vti_aws_media.s3_media_menu').id
        action_id = request.env.ref('vti_aws_media.s3_media_action').id
        link = f"/web#action={action_id}&model=s3.media&view_type=list&menu_id={menu_id}"
        return request.redirect(link)

    @http.route('/media/get_s3_video_suggestion', type='json', auth='user', methods=['POST'])
    def get_s3_video_suggestion(self, name=None, folder=None, **kwargs):
        domain = [('directory', '=', 'videos')]
        if name:
            domain.extend(['|', ('name', 'ilike', name), ('file_name', 'ilike', name)])
        try:
            folder_id = int(folder) if folder else False
        except Exception as e:
            return BadRequest(e)
        if folder_id:
            domain.extend([('folder_id', '=', folder_id)])

        video_suggestion = request.env['s3.media']. \
            search_read(domain, ['id', 'name', 'url', 'download_link'], order="id DESC")

        return video_suggestion

    @http.route('/media/get_documents', type='json', auth='user', methods=['POST'])
    def get_get_documents(self, name=None, folder=None, **kwargs):
        domain = [('directory', '=', 'documents')]
        if name:
            domain.extend(['|', ('name', 'ilike', name), ('file_name', 'ilike', name)])
        try:
            folder_id = int(folder) if folder else False
        except Exception as e:
            return BadRequest(e)
        if folder_id:
            domain.extend([('folder_id', '=', folder_id)])

        media_ids = request.env['s3.media'].search(domain, order="name")

        return [{
            'id': docs.id, 'name': docs.name, 'mimetype': docs.content_type,
            'download_link': docs.download_link, 'url': docs.download_link
        } for docs in media_ids]

    def _check_security(self):
        if request.session.uid and \
                not request.env['res.users'].browse(request.session.uid).user_has_groups(
                    'base.group_user'):
            raise Forbidden(_("Permission denied!"))
