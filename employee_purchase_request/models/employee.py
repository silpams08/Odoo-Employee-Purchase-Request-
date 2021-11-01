# -*- coding: utf-8 -*-
import calendar
import datetime

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _compute_rejected_month(self):
        today = datetime.datetime.today()
        date_range = calendar.monthrange(today.year, today.month)
        start = today.replace(day=1)
        end = today.replace(day=date_range[1])
        for employee in self:
            rejected_orders = self.env['purchase.request'].search([('employee_id', '=', employee.id), ('order_date', '<=', end), ('order_date', '>=', start), ('state', '=', 'Rejected')])
            if len(rejected_orders) > 0:
                employee.rejected_month = True

    employee_type = fields.Selection([('Internal', 'Internal'), ('Manager', 'Manager'), ('Employee', 'Employee')], default='Employee')
    allowed_category_ids = fields.Many2many('product.category', String="Allowed Categories")
    allowed_product_qty = fields.Selection([
        (1, 1),
        (2, 2),
        (3, 3)
    ], string="Allowed products", help="Allowed product quantity in each purchase", default=1)
    custom_tax_id = fields.Many2one('account.tax', domain=[('type_tax_use', '=', 'purchase')], string="Custom Tax", help="Custom tax for employee")

    rejected_month = fields.Boolean(default=False, compute=_compute_rejected_month)
