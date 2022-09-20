"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import logging
from odoo.addons.website_slides.controllers.main import WebsiteSlides

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
from distutils.command.config import config

_logger = logging.getLogger(__name__)


class ElearningController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @http.route("/api/v1/slide_channel", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_source(self, **payload):
        """ API 1.13 Danh sách khóa học"""
        values = []
        headers = request.httprequest.headers
        base_url = ElearningController.get_url_base(self)
        data = request.env['slide.channel'].sudo().search([('website_published', '=', True),
                                                           ('enroll', '=', 'public'),
                                                           ('visibility', '=', 'public')
                                                           ])
        if headers.get("access_token"):
            user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user:
                employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
                channels_my = request.env['slide.channel'].sudo().search([('website_published', '=', True),
                                                                          ('employee_id', 'in', employee.id),
                                                                          ])
                for channel in channels_my:
                    if channel not in data:
                        data += channel
        for rec in data:
            dates = {'name': rec.name,
                     'id': rec.id,
                     'description': rec.description,
                     'total_time': rec.total_time,
                     "avatar": urls.url_join(base_url,
                                             '/web/image?model=slide.channel&id={0}&field=image_1024'.format(
                                                 rec.id)),
                     'members_count': rec.members_count,
                     'avatar_lecturers': urls.url_join(base_url,
                                                       '/web/image?model=slide.channel&id={0}&field=lecturers.avatar'.format(
                                                           rec.id)),
                     'rating_lecturers': rec.lecturers.rating,
                     'department': rec.department_id if rec.department_id else rec.general_course_type}
            tag_ids = []
            for tag in rec.tag_ids:
                tag_ids.append({
                    'id': tag.id or '',
                    'name': tag.name or '',
                })
            dates['tag_ids'] = tag_ids
            # ____________________________________________________
            ratings = []
            for rat in rec.rating_ids:
                ratings.append({
                    'name': rat.rated_partner_name,
                    'partner': rat.partner_id.name,
                    'name_rating': rat.rated_partner_id.name,
                    'rating_text': rat.rating_text,
                    'rating': rat.rating,
                    'res_model': rat.res_model,
                    'res_model_id': rat.res_model_id,
                    'res_name': rat.res_name,
                    'res_id': rat.res_id,
                })
            dates['rating'] = ratings
            # ____________________________________________________
            comment = []
            for mes in rec.website_message_ids:
                comment.append({
                    'model': mes.model,
                    'body': mes.body,
                    'create_date': mes.create_date,
                    'description': mes.description,
                    'res_id': mes.res_id,
                    'author_id': mes.author_id.name,
                    'partner_ids': mes.partner_ids,
                    'reply_to': mes.reply_to,
                })
            dates['comment'] = comment
            # ____________________________________________________
            quiz_ids = []
            for quiz in rec.quiz_ids:
                quiz_ids.append({
                    'id': quiz.id or '',
                    'name': quiz.name or '',
                })
            dates['quiz_ids'] = quiz_ids
            # ____________________________________________________
            lecturers = []
            for lec in rec.lecturers:
                lecturers.append({
                    'id': lec.id or '',
                    'name': lec.name or '',
                    'seniority': lec.experience or '',
                    'position': lec.position or '',
                })
            dates['lecturers'] = lecturers
            lesson = []
            for cate in rec.slide_category_ids:
                category = {
                    'id': cate.id,
                    'title': cate.name,
                }
                lesson.append(category)
                slides = []
                for sl in cate.slide_ids:
                    slide = {
                        'id': sl.id,
                        'name': sl.name,
                        'type': sl.slide_type,
                        'url': sl.url,
                        'completion_time': sl.completion_time,
                        'description': sl.description,
                        'preview': sl.is_preview,
                    }
                    slides.append(slide)
                    questions = []
                    for ques in sl.question_ids:
                        question = {
                            'question': ques.question,
                        }
                        questions.append(question)
                        answers = []
                        for aw in ques.answer_ids:
                            answer = {
                                'value': aw.text_value,
                                'is_correct': aw.is_correct,
                                'comment': aw.comment,
                            }
                            answers.append(answer)
                        question['answers'] = answers
                    slide['questions'] = questions
                category['slides'] = slides
            dates['lesson'] = lesson
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/slide_channel/join_course", type="http", auth="public", methods=["POST", "OPTIONS"],
                csrf=False, cors='*')
    def join_course(self, **payload):
        field_require = [
            'course_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['course_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', int(payload.get('uid')))])
        if user.self not in slide_channel.channel_partner_ids.partner_id:
            channel_partner = request.env['slide.channel.partner'].with_user(SUPERUSER_ID).create({
                'channel_id': slide_channel.id,
                'partner_id': user.partner_id.id,
            })
        return valid_response("ok")

    @validate_token
    @http.route("/api/v1/slide_channel/rating", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False,
                cors='*')
    def update_rating_slide_channel(self, **payload):
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['course_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', payload.get('uid'))])
        student = request.env['student.student'].sudo().search([('user_id', '=', user.id)])
        rating = request.env['rating.rating'].sudo().create({
            'res_id': slide_channel.id,
            'rating': int(payload['star']),
            'feedback': payload.get('rating'),
            'star': int(payload['star']),
            'partner_id': user.partner_id.id,
            'student_id': student.id,
            'res_model_id': request.env['ir.model']._get_id('slide.channel'),
        })
        print(rating)
        return valid_response("Bạn đã đánh giá vào khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/comment", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False,
                cors='*')
    def update_comment_slide_channel(self, **payload):
        field_require = [
            'res_id',
            'body',
            'description',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['res_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        comment = request.env['mail.message'].sudo().create({
            'subject': payload['body'],
            'email_from': user.self.email,
            'model': 'slide.channel',
            # _________________________
            'res_id': slide_channel.id,
            'body': payload['body'],
            'author_id': user.self.id,
        })
        return invalid_response("Bạn đã bình luận vào khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/apply_member", type="http", auth="public", methods=["POST", "OPTIONS"],
                csrf=False, cors='*')
    def apply_member_slide_channel(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        channel_partner_ids = request.env['slide.channel.partner'].sudo().create({
            'channel_id': int(payload['channel_id']),
            'partner_id': user.self.id,
        })

    @validate_token
    @http.route("/api/v1/slide_channel/completion", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_completion_slide_channel_partner(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['channel_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if user.self in slide_channel.channel_partner_ids.partner_id:
            channel_partner = request.env['slide.channel.partner'].sudo().search(
                [('channel_id', '=', payload['channel_id']), ('partner_id', '=', user.self.id)])
            if channel_partner.completion:
                return valid_response(channel_partner.completion)
            else:
                return invalid_response("Bạn đã chưa bắt đầu tham gia khóa học %s." % slide_channel.name)
        else:
            return invalid_response("Bạn chưa tham gia khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/completed", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_completed_slide_channel_partner(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['channel_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        channel_partner = request.env['slide.channel.partner'].sudo().search(
            [('channel_id', '=', payload['channel_id']), ('partner_id', '=', user.self.id)])
        if channel_partner.completed:
            return valid_response("Bạn đã hoàn thành khóa học %s." % slide_channel.name)
        else:
            return invalid_response("Bạn chưa hoàn thành khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/allcomment", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_comment_slide_channel(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['channel_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if user.self in slide_channel.channel_partner_ids.partner_id:
            mail_message = request.env['mail.message'].sudo().search(
                [('res_id', '=', payload['channel_id']), ('model', '=', 'slide.channel')])
            values = []
            for msg in mail_message:
                values.append({
                    'id': msg.id,
                    'subject': msg.subject,
                    'body': msg.body,
                    'author_id': msg.author_id,
                    'parent_id': msg.parent_id
                })
            return valid_response(values)
        else:
            return invalid_response("Bạn chưa tham gia khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/content", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_content_slide_channel(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['channel_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if user.self in slide_channel.channel_partner_ids.partner_id:
            slide_slide = request.env['slide.slide'].sudo().search([('channel_id', '=', slide_channel.id)])
            values = []
            for slide in slide_slide:
                values.append({
                    'id': slide.id,
                    'name': slide.name,
                    'slide_type': slide.slide_type,
                    'total_views': slide.total_views,
                    'is_preview': slide.is_preview,
                    'is_published': slide.is_published,
                    'likes': slide.like,
                    'dislikes': slide.dislikes
                })
            return valid_response(values)
        else:
            return invalid_response("Bạn chưa tham gia khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/completion_time", type="http", auth="public", methods=["GET", "OPTIONS"],
                csrf=False, cors='*')
    def get_completion_time_slide_channel(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['channel_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if user.self in slide_channel.channel_partner_ids.partner_id:
            slide_slide = request.env['slide.slide'].sudo().search([('channel_id', '=', slide_channel.id)])
            values = []
            for slide in slide_slide:
                values.append({
                    'id': slide.id,
                    'name': slide.name,
                    'completion_time': slide.completion_time,
                })
            return valid_response(values)
        else:
            return invalid_response("Bạn chưa tham gia khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_slide/completed", type="http", auth="public", methods=["POST", "OPTIONS"], csrf=False,
                cors='*')
    def get_completed_slide_slide_partner(self, **payload):
        print(payload)
        userlogin = request.env['res.users'].sudo().search([('id', '=', payload.get('uid'))])
        slide = request.env['slide.slide'].sudo().search([('id', '=', int(payload.get('slide_id')))])
        slide.sudo().with_context(partner=userlogin.partner_id).action_set_completed()
        slide_partner = request.env['slide.channel.partner'].sudo().search(
            [('partner_id', '=', userlogin.partner_id.id), ('channel_id', '=', int(payload.get('course_id')))])
        print(slide_partner)
        return valid_response({
            'progress': slide_partner.completion
        })

    @http.route("/api/v1/op_quiz", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False, cors='*')
    def get_op_quiz(self, **payload):
        field_require = [
            'slide_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        values = []
        op_quiz = request.env['op.quiz'].sudo().search([('slide_channel_id', '=', payload['slide_id'])])
        for rec in op_quiz:
            quiz = {
                'name': rec.name,
                'id': rec.id,
                'quiz_config': rec.quiz_config,
                'type': rec.type,
                'categ_id': rec.categ_id,
                'total_marks': rec.total_marks,
                'single_que': rec.single_que,
                'prev_allow': rec.prev_allow,
                'prev_readonly': rec.prev_readonly,
                'show_result': rec.show_result,
                'no_of_attempt': rec.no_of_attempt,
                'que_required': rec.que_required,
                'auth_required': rec.auth_required,
                'time_config': rec.time_config,
            }
            line_ids = []
            for line in rec.line_ids:
                line_ids.append({
                    'id': line.id,
                    'name': line.name,
                    'que_type': line.name,
                    'mark': line.name,
                })
            quiz['line_ids'] = line_ids
            # ____________________________________________________
            quiz_message_ids = []
            for msg in rec.quiz_message_ids:
                quiz_message_ids.append({
                    'result_from': msg.result_from,
                    'result_to': msg.result_to,
                })
            quiz['quiz_message_ids'] = quiz_message_ids
            # ____________________________________________________
            employees = []
            for emp in rec.list_candidates:
                employees.append({
                    'name': emp.model,
                    'work_phone': emp.work_phone,
                    'work_email': emp.work_email,
                    'company_id': emp.company_id,
                    'department_id': emp.department_id,
                    'job_id': emp.job_id,
                    'partner_id': emp.partner_id,
                })
            quiz['employees'] = employees
            values.append(quiz)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/question_bank_line", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_question_bank_line(self, **payload):
        question_bank_line = request.env['op.question.bank.line'].sudo().search([])
        values = []
        for line in question_bank_line:
            values.append({
                'id': line.id,
                'name': line.name,
                'que_type': line.que_type,
                'bank_id': line.bank_id
            })
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/question_bank_answer", type="http", auth="public", methods=["GET", "OPTIONS"], csrf=False,
                cors='*')
    def get_question_bank_answer(self, **payload):
        question_bank_answer = request.env['op.question.bank.answer'].sudo().search([])
        values = []
        for answer in question_bank_answer:
            values.append({
                'id': answer.id,
                'name': answer.name,
                'grade_id': answer.grade_id,
                'question_id': answer.question_id
            })
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/slide_slide_partner/completed", type="http", auth="public", methods=["POST", "OPTIONS"],
                csrf=False, cors='*')
    def update_completed_slide_slide_partner(self, **payload):
        field_require = [
            'slide_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_slide = request.env['slide.slide'].sudo().search([('id', '=', payload['slide_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        slide_partner = request.env['slide.slide.partner'].sudo().search(
            [('slide_id', '=', payload['slide_id']), ('partner_id', '=', user.self.id)])
        if slide_partner.completed:
            return invalid_response("Bạn đã hoàn thành bài học %s." % slide_slide.name)
        else:
            slide_partner.completed = True
            return invalid_response("Bạn đã hoàn thành bài học %s." % slide_slide.name)
