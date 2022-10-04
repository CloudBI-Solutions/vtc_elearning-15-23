from odoo import api, fields, models


class ApproveRequest(models.Model):
	_inherit = 'approval.request'


	student_id = fields.Many2one('student.student', string='Student', readonly=True)
	is_change_info_student = fields.Boolean('Is change', compute='_compute_field_value_student')
	old_name = fields.Char('Old name', related='student_id.name')
	old_birth = fields.Date('Old date',related='student_id.birth')
	old_phone = fields.Char('Old Phone',related='student_id.phone')

	new_name = fields.Char('New name',readonly=True)
	new_birth = fields.Date('New date',readonly=True)
	new_phone = fields.Char('New Phone',readonly=True)

	def action_approve(self, approver=None):
		if self.is_change_info_student:
			student = self.env['student.student'].search([('id','=', self.student_id.id)])
			val = {
				'name': self.new_name,
				'birth':self.new_birth,
				'phone':self.new_phone
			}
			student.write(val)
		return super(ApproveRequest, self).action_approve()

	def _compute_field_value_student(self):
		ctg_id = self.env.ref('vtc_elearning.approval_category_data_info_student', raise_if_not_found=False)
		for rec in self:
			if rec.category_id == ctg_id:
				rec.is_change_info_student = True
			else:
				rec.is_change_info_student = False
