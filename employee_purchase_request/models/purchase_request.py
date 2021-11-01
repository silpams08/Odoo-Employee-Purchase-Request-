# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _order = 'id desc'

    ORDER_STATUS = [
        ('Draft', 'Draft'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Purchase in progress', 'Purchase in progress'),
        ('Ready to pick - up', 'Ready to pick - up'),
        ('Done', 'Done')
    ]

    def get_employee_domain(self):
        """Remove the login employee if the user is manager/internal user."""
        domain = []
        login_employee = self.env.user.employee_ids.ids
        domain.append(('id', 'not in', login_employee))
        return domain

    def _default_currency_id(self):
        company_id = self.env.context.get('force_company') or self.env.context.get(
            'company_id') or self.env.user.company_id.id
        return self.env['res.company'].browse(company_id).currency_id

    @api.depends('product_id', 'quantity', 'price', 'taxes_id')
    def _compute_amount(self):
        for record in self:
            taxes = record.taxes_id.compute_all(
                record.price,
                record.currency_id,
                record.quantity,
                record.product_id,
                record.employee_id.address_home_id)
            record.update({
                'amount_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'amount_total': taxes['total_included'],
                'amount_untaxed': taxes['total_excluded'],
            })

    @api.depends('product_id')
    def _compute_attributes(self):
        for record in self:
            if record.product_id and record.product_id.sudo()._check_attribute_value_ids():
                for attr in record.product_id.attribute_value_ids.sudo().filtered(
                        lambda a: a.attribute_id.id == record.env.ref('employee_purchase_request.product_attribute_color').id):
                    record.color = attr.name
                for attr in record.product_id.attribute_value_ids.sudo().filtered(
                        lambda a: a.attribute_id.id == record.env.ref('employee_purchase_request.product_attribute_size').id):
                    record.size = attr.name
            if record.product_id.image:
                record.image = record.product_id.image


    name = fields.Char(string="Order Reference", default='New')
    order_date = fields.Date(string='Order Date', default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', string="Employee")
    partner_id = fields.Many2one('res.partner', string="Partner")
    email = fields.Char(string="Email", related="employee_id.work_email")
    mobile = fields.Char(string="Mobile", related="employee_id.mobile_phone")
    employee_company = fields.Char(string="Company Name", related="company_id.name")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one('res.users', string="User")
    state = fields.Selection(ORDER_STATUS, default='Draft', string="Order Status")

    attachment_ids = fields.Many2many('ir.attachment', 'purchase_request_ir_attachments_rel',
                                      'purchase_request_id', 'attachment_id', string='Attachments')

    vendor_id = fields.Many2one('res.partner', domain=[('supplier', '=', True)], string="Supplier")
    product_template_id = fields.Many2one('product.template', string="Products")
    product_id = fields.Many2one('product.product', string="Products")
    category_id = fields.Many2one('product.category', string="Category", related='product_id.categ_id')
    image = fields.Binary(string="Picture")
    color = fields.Char(String='Color', compute=_compute_attributes, store=True)
    size = fields.Char(String='Size', compute=_compute_attributes, store=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    price = fields.Float(string="Unit Price", default=0.0)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True, default=_default_currency_id)

    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])

    amount_untaxed = fields.Monetary(string='Net Price', store=True, readonly=True, compute='_compute_amount',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Gross Price', store=True, readonly=True, compute='_compute_amount')

    po_id = fields.Many2one('purchase.order', string="Purchase Order")
    picking_date = fields.Date('Picking Date')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.lst_price
            if not self.employee_id:
                self.employee_id = self.env['hr.employee'].search([('address_home_id', '=', self.partner_id.id)])
            if self.employee_id and self.employee_id.custom_tax_id:
                self.taxes_id = [(6, 0, self.employee_id.custom_tax_id.ids)]
            elif self.product_id.supplier_taxes_id:
                self.taxes_id = [(6, 0, self.product_id.supplier_taxes_id.ids)]

    @api.onchange('vendor_id')
    def onchange_vendor_id(self):
        if self.vendor_id:
            vendor = self.env['product.supplierinfo'].sudo().search(
                [('product_id', '=', self.product_id.id), ('name', '=', self.vendor_id.id)])
            self.price = vendor.price

    def write(self, vals):
        for record in self:
            res = super(PurchaseRequest, record).write(vals)
            if 'attachment_ids' in vals:
                for attachment in self.attachment_ids.filtered(lambda a: not a.public):
                    attachment.public = True
            if record.state == 'Approved':
                template = record.env.ref('employee_purchase_request.order_approve_email_template')
                template.with_context(lang=record.partner_id.lang).send_mail(record.id, force_send=True)
            elif record.state == 'Rejected':
                template = record.env.ref('employee_purchase_request.order_reject_email_template')
                template.with_context(lang=record.partner_id.lang).send_mail(record.id, force_send=True)
            elif record.state == 'Ready to pick - up':
                template = record.env.ref('employee_purchase_request.ready_to_pick_email_template')
                template.with_context(lang=record.partner_id.lang).send_mail(record.id, force_send=True)
            return res

    @api.model
    def get_email_to(self, group):
        user_group = self.env.ref(group)
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def get_managers(self):
        user_group = self.env.ref("employee_purchase_request.group_manager_portal")
        name_list = [
            usr.partner_id.name for usr in user_group.users if usr.partner_id]
        return ",".join(name_list)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or '/'
        res = super(PurchaseRequest, self).create(vals)
        if res.state == 'Draft':
            template = self.env.ref('employee_purchase_request.order_creation_email_template')
            template.with_context(lang=res.partner_id.lang).send_mail(res.id, force_send=True)
        return res

    def action_approve(self):
        self.state = 'Approved'

    def action_reject(self):
        self.state = 'Rejected'

    def action_done(self):
        self.state = 'Done'

    def create_purchase(self):
        order_line = [(0, 0, {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_qty': self.quantity,
            'price_unit': self.price,
            'taxes_id': [(6, 0, self.taxes_id.ids)],
            'date_planned': self.order_date,
            'product_uom':self.product_id.uom_id.id,
        })]
        po_id = self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
            'partner_ref': self.name,
            'order_line': order_line,
        })
        return po_id

    def action_buy_product(self):
        po_id = self.create_purchase()
        self.po_id = po_id.id
        self.state = 'Purchase in progress'
