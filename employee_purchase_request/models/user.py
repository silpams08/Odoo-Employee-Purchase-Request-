# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    user_type = fields.Selection([('Internal', 'Internal'), ('Manager', 'Manager'), ('Employee', 'Employee')], default='Internal', string="User Type")

    def is_rejected_month(self):
        if self.employee_ids:
            return self.employee_ids[0].rejected_month
        return True

    @api.model
    def create(self, vals):
        groups = []
        if vals['user_type'] == 'Employee' or vals['user_type'] == 'Manager':
            groups.append((2, self.env.ref('base.group_user').id))
            groups.append((4, self.env.ref('base.group_portal').id))
            if vals['user_type'] == 'Manager':
                groups.append((4, self.env.ref('employee_purchase_request.group_manager_portal').id))
            vals['groups_id'] = groups
            vals['sel_groups_1_9_10'] = 9
        res = super(Users, self).create(vals)
        res.create_emp_from_user()
        res.partner_id.signup_prepare()
        return res

    @api.multi
    def create_emp_from_user(self):
        """ Create an hr.employee from the res.users """
        if self.partner_id:
            address_id = self.partner_id.address_get(['contact'])['contact']
            contact_name = self.partner_id.name_get()[0][1]
            employee = self.env['hr.employee'].create({
                'name': self.name or contact_name,
                'address_home_id': address_id,
                'address_id': self.company_id and self.company_id.partner_id
                              and self.company_id.partner_id.id or False,
                'work_email': self.login or False,
                'employee_type': self.user_type,
                'user_id': self.id,
            })




