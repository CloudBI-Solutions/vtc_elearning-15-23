# -*- coding: utf-8 -*-

import datetime
import random
import string
from datetime import timedelta
from random import randint

import pytz

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import UserError


class MaintenanceEquipmentCategory(models.Model):
    _name = 'sci.maintenance.equipment.category'
    _description = 'Maintenance Equipment Category'

    department_id = fields.Many2one('hr.department', 'Phòng ban quản lý')
    name = fields.Char('Category Name', required=True, translate=True)
    email = fields.Char('Email')
    technician_user_id = fields.Many2one('hr.employee', 'Chịu trách nhiệm',
                                         domain="[('department_id', 'child_of', department_id)]")
    color = fields.Integer('Color Index')
    note = fields.Text('Comments', translate=True)
    maintenance_ids = fields.One2many('sci.maintenance.request', 'category_id', copy=False)
    maintenance_count = fields.Integer(string="Maintenance Count", compute='_compute_maintenance_count')
    user_ids = fields.Many2many('res.users', string='User support')

    @api.onchange('department_id')
    def _onchange_department(self):
        self.name = self.department_id.name

    def _compute_maintenance_count(self):
        maintenance_data = self.env['sci.maintenance.request'].read_group([('category_id', 'in', self.ids)],
                                                                          ['category_id'], ['category_id'])
        mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in maintenance_data])
        for category in self:
            category.maintenance_count = mapped_data.get(category.id, 0)


class SCIMaintenanceRequest(models.Model):
    _name = 'sci.maintenance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Maintenance Request'
    _order = "id desc"

    state = fields.Selection([('new', '	Yêu cầu mới'),
                              ('doing', 'Đang thực hiện'),
                              ('done', '	Hoàn thành'),
                              ('cancel', 'Hủy'),
                              ('closed', 'Đóng')],
                             default='new', string='Trạng thái')
    name = fields.Char('Subjects', required=True, states={'new': [('readonly', False)]}, readonly=True)
    code = fields.Char('Code', readonly=True)
    channel = fields.Selection([('website', 'Website'), ('email', 'Email'), ('phone', 'Phone'), ('other', 'Khác')],
                               default='website',
                               string='Nguồn', states={'new': [('readonly', False)]}, readonly=True)
    person_name = fields.Many2one('hr.employee', string='Người yêu cầu', states={'new': [('readonly', False)]},
                                  readonly=True)
    email = fields.Char(string="Email", states={'new': [('readonly', False)]}, readonly=True)
    phone = fields.Char(string="Điện thoại", states={'new': [('readonly', False)]}, readonly=True)
    # department = fields.Char(string="Phòng ban", states={'new': [('readonly', False)]}, readonly=True)
    description = fields.Html('Mô tả', states={'new': [('readonly', False)]}, readonly=True)
    type = fields.Selection([('pc', 'PC'),
                             ('erp', 'ERP'),
                             ('onetouch', 'One Touch'),
                             ('informatics_equipment', 'Informatics equipment'),
                             ('external_access', 'External access'),
                             ('website', 'Website'),
                             ('security', 'Security'), ], default='onetouch',
                            string='Type maintenance')
    request_date = fields.Datetime('Ngày yêu cầu', default=lambda self: fields.Datetime.now(), tracking=True,
                                   help="Date requested for the maintenance to happen")
    category_id = fields.Many2one('sci.maintenance.equipment.category', 'Bộ phận tiếp nhận', required=True,
                                  tracking=True, states={'new': [('readonly', False)]}, readonly=True)
    emp_id = fields.Many2one('hr.employee', string='Người phụ trách')
    priority = fields.Selection(related='area_type_maintenance_request.priority')
    support_rating = fields.Selection(
        [('1', 'Rất tệ'), ('2', 'Tệ'), ('3', 'Bình thường'), ('4', 'Tốt'), ('5', 'Rất tốt')], string='Đánh giá')
    color = fields.Integer('Color Index')
    close_date = fields.Datetime('Ngày đóng', help="Ngày bảo trì hoàn thành. ", compute='calculation_close_date',
                                 store=True)
    kanban_state = fields.Selection(
        [('normal', 'In Progress'), ('doing', 'Doing'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
        string='Kanban State', required=True, default='normal', tracking=True)
    supervisor_ids = fields.Many2many('hr.employee', string='Danh sách nhân sự bảo trì',
                                      tracking=True, domain="[('active','=','usage')]")
    archive = fields.Boolean(default=False,
                             help="Set archive to true to hide the maintenance request without deleting it.")
    maintenance_type = fields.Selection([('corrective', 'Khắc phục sự cố'), ('preventive', 'Bảo dưỡng định kỳ')],
                                        string='Loại bảo trì', default="corrective", readonly=True)
    schedule_date = fields.Datetime('Lịch hẹn', help="Ngày nhóm bảo trì lên kế hoạch bảo trì ")
    tools_description = fields.Html('Hiện trạng', translate=True)
    operations_description = fields.Html('Kết quả', translate=True)
    status = fields.Text('Tình trạng', compute="_compute_status")
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    portal_access_key = fields.Char(string="Portal Access Key")
    support_comment = fields.Text(string="Support Comment")
    close_comment = fields.Html(string="Close Comment")
    closed_by_id = fields.Many2one('res.users', string="Closed By")
    time_to_close = fields.Integer(string="Time to close (seconds)")
    type_maintenance_request = fields.Many2one('type.maintenance.request', string='Type maintenance request',
                                               states={'new': [('readonly', False)]}, readonly=True)
    area_type_maintenance_request = fields.Many2one('area.type.maintenance.request',
                                                    states={'new': [('readonly', False)]}, readonly=True,
                                                    string='area type maintenance request')
    the_average_time = fields.Integer(related='area_type_maintenance_request.the_average_time')
    completion_time = fields.Char('Thời gian hoàn thành')
    wizard_result_id = fields.Many2many('maintenance.request.get.result')
    result_id = fields.Many2many('maintenance.request.reason')
    survey_url = fields.Char('Survey URL')
    base_url = fields.Char('Base URL')

    default_cc = fields.Text('Cc (Emails)', help='Carbon copy message recipients (Emails)',
                             states={'new': [('readonly', False)]}, readonly=True)
    default_bcc = fields.Char('Bcc (Emails)', help='Blind carbon copy message recipients (Emails)',
                              states={'new': [('readonly', False)]}, readonly=True)

    template_id = fields.Many2one('mail.template', string='Email Template',
                                  compute='_compute_send_mail', store=True, readonly=False,
                                  domain="[('model', '=', 'sci.maintenance.request')]")
    mail_tz = fields.Selection(_tz_get, compute='_compute_mail_tz',
                               help='Timezone used for displaying time in the mail template')
    reason_change = fields.Char('Lí do thay đổi người phụ trách')
    completed_process = fields.Integer('Completed process')
    deadline = fields.Datetime('Deadline')
    student_id = fields.Many2one('student.student', string='Học viên yêu cầu', states={'new': [('readonly', False)]},
                                 readonly=True)
    work_unit = fields.Char('Đơn vị công tác')
    position = fields.Many2one('position', string='Vị trí', related='student_id.position')
    res_country_state = fields.Many2one('res.country.state', string='Country state',
                                        related='student_id.res_country_state',
                                        domain="[('country_id', '=', 'VN')]")
    res_country_ward = fields.Many2one('res.country.ward', string='Country ward',
                                       related='student_id.res_country_ward',
                                       domain="[('district_id', '=', res_country_district)]")
    res_country_district = fields.Many2one('res.country.district', string='Country district',
                                           related='student_id.res_country_district',
                                           domain="[('state_id', '=', res_country_state)]")
    user_support = fields.Many2one('res.users', string='User support')

    @api.constrains('the_average_time', 'request_date')
    def get_deadline(self):
        for record in self:
            if record.the_average_time and record.request_date:
                record.deadline = record.request_date + timedelta(minutes=record.the_average_time)

    def _compute_mail_tz(self):
        for attendee in self:

            if attendee.message_partner_ids:
                attendee.mail_tz = attendee.message_partner_ids[0].tz
            else:
                attendee.mail_tz = attendee.student_id.user_id.tz

    @api.depends('result_id')
    def _compute_send_mail(self):
        for record in self:
            template = record.result_id.template_id
            record.template_id = template

    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.email = rec.student_id.email
                rec.phone = rec.student_id.phone

    @api.depends('schedule_date')
    def _compute_status(self):
        for record in self:
            if record.state in ['new', 'doing']:
                msg = ''
                time = datetime.datetime.now()
                tz_current = pytz.timezone(self._context.get('tz') or 'UTC')  # get timezone user
                tz_database = pytz.timezone('UTC')
                time = tz_database.localize(time)
                time = time.astimezone(tz_current)
                time = time.date()
                if record.schedule_date:
                    expected_date = record.schedule_date.date()
                    days = (expected_date - time).days
                    if days < 0:
                        msg += ('- Quá hạn hoàn thành %s ngày') % abs(days)
                    elif days == 0:
                        msg += ('- Hôm nay là hạn chót')
                    elif days < 7:
                        msg += ('- Còn %s ngày đến hạn hoàn thành') % abs(days)
            elif record.state == 'done':
                msg = '- Đã hoàn thành'
            elif record.state == 'cancel':
                msg = '- Đã hủy'
            else:
                msg = '- Yêu cầu đã được đóng'
            record.status = msg

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id.department_id:
            return {
                'domain': {'user_support': [('id', 'child_of', self.category_id.user_ids.ids)]}
            }

    @api.onchange('maintenance_team_id')
    def _onchange_maintenance_team_id(self):
        self.emp_id = self.maintenance_team_id.technician_user_id

    def archive_equipment_request(self):
        self.write({'archive': True})

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        if vals.get('user_support'):
            vals['state'] = 'doing'
        vals['code'] = self.env['ir.sequence'].next_by_code('maintenance.code.action')
        # print(vals)
        request = super(SCIMaintenanceRequest, self).create(vals)
        if request.student_id:
            request.email = request.student_id.email
            request.phone = request.student_id.phone
            request.position = request.student_id.position
            request.work_unit = request.student_id.work_unit
            request.res_country_state = request.student_id.res_country_state
            request.res_country_district = request.student_id.res_country_district
            request.res_country_ward = request.student_id.res_country_ward
        request.portal_access_key = randint(1000000000, 2000000000)
        # survey_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        request.survey_url = 'http://daotao.vtcnetviet.com/support/%s' %request.code
        if request.the_average_time:
            request.completed_process = request.the_average_time

        return request

    def rpc_render_completed_process(self, progress):
        self.completed_process = 0

    def write(self, vals):
        if vals.get('user_support'):
            vals['state'] = 'doing'
        super(SCIMaintenanceRequest, self).write(vals)

    @api.constrains('state')
    def send_mail_confirm(self):
        if self.state == 'doing':
            survey_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.base_url = survey_url + '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)

            template = self.env.ref('diligo_maintenance.email_template_data_maintenance_receive')
            for record in self:
                self.env['mail.thread'].message_post_with_template(
                    template.id,
                    res_id=record.id,
                    model=record._name,
                    composition_mode='comment',
                )

    def open_close_ticket_wizard(self):
        if not self.email:
            raise UserError(_("The requestor's email is not available. Please provide the requester's email."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Kết quả yêu cầu'),
            'res_model': 'maintenance.request.get.result',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_maintenance_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    @api.onchange('type', 'type_maintenance_request')
    def clear_type_maintenance_request(self):
        if self.type != self.type_maintenance_request.type:
            self.type_maintenance_request = False
            self.area_type_maintenance_request = False
        elif self.type_maintenance_request != self.area_type_maintenance_request.type_maintenance_request:
            self.area_type_maintenance_request = False


class TypeMaintenanceRequest(models.Model):
    _name = 'type.maintenance.request'

    name = fields.Char('name', required=True)
    area = fields.One2many('area.type.maintenance.request', 'type_maintenance_request', string='area')
    type = fields.Selection([('pc', 'PC'),
                             ('erp', 'ERP'),
                             ('onetouch', 'One Touch'),
                             ('informatics_equipment', 'Informatics equipment'),
                             ('external_access', 'External access'),
                             ('website', 'Website'),
                             ('security', 'Security'), ], default='onetouch',
                            string='Type maintenance')


class AreaTypeMaintenanceRequest(models.Model):
    _name = 'area.type.maintenance.request'

    def get_code(self):
        size = 8
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    code = fields.Char('Code', default=get_code, readonly=True)
    type_maintenance_request = fields.Many2one('type.maintenance.request', string='Type maintenance request')
    name = fields.Char('Name', required=True)
    the_average_time = fields.Integer('Average time')
    priority = fields.Selection(
        [('0', 'Rất thấp'), ('1', 'Thấp'), ('2', 'Bình thường'), ('3', 'Cao'), ('4', 'Rất cao'), ('5', 'Thương lượng')],
        string='Độ ưu tiên', required=True)


class ApplicantRefuseReason(models.Model):
    _name = "maintenance.request.reason"
    _description = 'Refuse Reason of Maintenance Request'

    name = fields.Char('Description', required=True, translate=True)
    template_id = fields.Many2one('mail.template', string='Email Template',
                                  domain="[('model', '=', 'sci.maintenance.request')]")
    active = fields.Boolean('Active', default=True)


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        self.email_bcc = self.email_cc = self.reply_to = ''

        if template_id and composition_mode == 'mass_mail':
            template = self.env['mail.template'].browse(template_id)
            fields = ['subject', 'body_html', 'email_from', 'reply_to', 'mail_server_id']
            values = dict((field, getattr(template, field)) for field in fields if getattr(template, field))
            if template.attachment_ids:
                values['attachment_ids'] = [att.id for att in template.attachment_ids]
            if template.mail_server_id:
                values['mail_server_id'] = template.mail_server_id.id
        elif template_id:
            if template_id == self.env.ref("diligo_maintenance.email_template_data_maintenance_new").id:
                ls = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                      'attachment_ids', 'mail_server_id']
            elif template_id == self.env.ref("diligo_maintenance.email_template_data_maintenance_refuse").id:
                ls = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc',
                      'reply_to',
                      'attachment_ids', 'mail_server_id']
            elif template_id == self.env.ref("diligo_maintenance.email_template_data_maintenance_receive").id:
                ls = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                      'attachment_ids', 'mail_server_id']
            elif template_id == self.env.ref("diligo_maintenance.email_template_data_maintenance_complete").id:
                ls = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc',
                      'reply_to',
                      'attachment_ids', 'mail_server_id']
            else:
                ls = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc',
                      'reply_to', 'attachment_ids', 'mail_server_id']
            values = self.generate_email_for_composer(
                template_id, [res_id], ls)[res_id]
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send
            attachment_ids = []
            Attachment = self.env['ir.attachment']
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            if values.get('attachment_ids', []) or attachment_ids:
                values['attachment_ids'] = [self.Command.set(values.get('attachment_ids', []) + attachment_ids)]
        else:
            default_values = self.with_context(default_composition_mode=composition_mode, default_model=model,
                                               default_res_id=res_id).default_get(
                ['composition_mode', 'model', 'res_id', 'parent_id', 'partner_ids', 'subject', 'body', 'email_from',
                 'reply_to', 'attachment_ids', 'mail_server_id'])
            values = dict((key, default_values[key]) for key in
                          ['subject', 'body', 'partner_ids', 'email_from', 'reply_to', 'attachment_ids',
                           'mail_server_id'] if key in default_values)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')

        # This onchange should return command instead of ids for x2many field.
        values = self._convert_to_write(values)

        return {'value': values}
