import base64
import logging
import unicodedata

import werkzeug
from werkzeug.exceptions import NotFound

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)


class Home(Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        res = super(Home, self).web_login(redirect, **kw)
        if request.params['login_success']:
            uid = request.session.authenticate(request.session.db, request.params['login'],
                                               request.params['password'])
            user = request.env['res.users'].browse([uid])
            if not user.has_group('base.group_user') and user.has_group('base.group_portal'):
                if user.user_type == 'Employee' or user.user_type == 'Manager':
                    return http.redirect_with_hash('/orders')
            else:
                return res
        else:
            return res


class PurchaseRequestController(CustomerPortal, ProductConfiguratorController):
    _references_per_page = 20

    @http.route(['/orders',
                 '/orders/page/<int:page>'], type='http', auth='user', website=True)
    def orders(self, page=0,sortby=None, filterby=None, search=None, search_in='content', **post):
        Request = request.env['purchase.request']
        domain = []

        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Order #')},
            'order_date': {'input': 'order_date', 'label': _('Search in Order Date')},
            'state': {'input': 'state', 'label': _('Search in States')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('order_date', 'all'):
                search_domain = OR([search_domain, [('order_date', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        if not request.env.user.has_group('employee_purchase_request.group_manager_portal') and request.env.user.has_group('base.group_portal'):
            domain.append(('user_id', '=', request.env.user.id))
        order_count = Request.search_count(domain)
        # pager
        pager = portal_pager(
            url="/orders",
            url_args={},
            total=order_count,
            page=page,
            step=self._items_per_page
        )

        orders = Request.search(domain, limit=self._items_per_page, offset=pager['offset'])

        values = {
            'orders': orders,
            'order_count': order_count,
            'pager': pager,
            'default_url': '/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
        }
        return request.render("employee_purchase_request.orders", values)

    @http.route(['/orders/<int:order_id>'], type='http', auth="user", website=True)
    def order_detail(self, order_id, **post):
        values = {}
        order = request.env['purchase.request'].browse(order_id)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1,
                                                            order="id asc")
        if post:
            values.update(post)
            # values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
            order.write(values)
            return request.redirect('/orders/'+str(order_id))
        if order.exists():
            values.update({
                'order': order,
            })
            return request.render("employee_purchase_request.order_detail", values)

        return self.orders(**post)

    @http.route(['/orders/new'], type='http', auth="user", website=True)
    def new_order(self, **post):
        Request = request.env['purchase.request']
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1, order="id asc")
        products = request.env['product.template'].search([('categ_id', 'in', employee.allowed_category_ids.ids)])


        # attrib_list = [post['attrib']] if 'attrib' in post else []
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = sorted({v[1] for v in attrib_values})
        pricelist = request.env['product.pricelist'].sudo().search([])

        values = {
            'partner_id': request.env.user.partner_id,
            'email': employee.work_email,
            'mobile': employee.mobile_phone,
            'partner_name': request.env.user.partner_id.name,
            'employee_id': employee.id,
            'products': products,
            'amount_to_buy': employee.allowed_product_qty,
            'attributes': [],
            'attrib_set': attrib_set,
            'pricelist': pricelist,
            'quantity': post['quantity'] if 'quantity' in post else 1,
            'currency': request.env.user.company_id.currency_id,
            'price': post['price'] if 'price' in post else 0.0,
            'tax': employee.custom_tax_id if employee.custom_tax_id else request.env.user.company_id.account_purchase_tax_id,
            'amount_untaxed': post['amount_untaxed'] if 'amount_untaxed' in post else 0.0,
            'amount_tax': post['amount_tax'] if 'amount_tax' in post else 0.0,
            'amount_total': post['amount_total'] if 'amount_total' in post else 0.0,
            'user': request.env.user,
            'vendor_id': post['vendor_id'] if'vendor_id' in post else False
        }
        if post:
            if 'product_id' in post and post['product_id'] and 'button_submit' in post and post['button_submit'] == 'Request Product':
                    post['product_id'] = int(post.get('product_id'))
                    post['quantity'] = int(post.get('quantity'))
                    post['price'] = values['price']
                    post['taxes_id'] = [(6, 0, values['tax'].ids)]
                    if 'vendor_id' in post and post['vendor_id']:
                        values['vendor_id'] = int(post.get('vendor_id'))
                    values.update({'user_id': request.env.user.id})
                    attachments = post.get('attachment', '')
                    filename = attachments.filename
                    if request.httprequest.user_agent.browser == 'safari':
                        # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                        # we need to send it the same stuff, otherwise it'll fail
                        filename = unicodedata.normalize('NFD', attachments.filename)
                    if filename != '':
                        attachment_id = request.env['ir.attachment'].create({
                            'name': filename,
                            'datas': base64.encodestring(attachments.read()),
                            'datas_fname': filename,
                            'public': True,
                        })
                        values.update({'attachment_ids': [(4, attachment_id.id)]})
                    values.update(post)
                    order_id = Request.sudo().create(values)
                    return request.redirect('/orders/' + str(order_id.id))
            if 'product_template_id' in post and post['product_template_id']:
                values['product_template_id'] = products.filtered(lambda t: t.id == int(post['product_template_id']))
                values['price'] = values['product_template_id'].list_price
            variants = request.env['product.template.attribute.line'].search([
                        ('product_tmpl_id', '=', values['product_template_id'].id)
                    ])
            values.update({'attributes': variants})
            if len(variants) == len(attrib_set):
                for product in request.env['product.product'].search([('product_tmpl_id', '=', values['product_template_id'].id)]):
                    product_attrib = product.attribute_value_ids.ids
                    if list(attrib_set) == product_attrib:
                        values['product_id'] = product
                        values['price'] = product.lst_price
                values['partner_id'] = request.env.user.partner_id.id
                if 'product_id' in values and values['product_id']:
                    vendor_line_ids = request.env['product.supplierinfo'].sudo().search(
                                                            [('product_id', '=', values['product_id'].id)])
                    values.update({'vendor_line_ids': vendor_line_ids})
                if 'vendor_id' in post and post['vendor_id']:
                    vendor = request.env['product.supplierinfo'].sudo().search(
                        [('product_id', '=', values['product_id'].id), ('name', '=', int(post['vendor_id']))])
                    values['price'] = vendor.price if vendor else post['price']

            taxes = request.env.user.company_id.account_purchase_tax_id.compute_all(
                values['price'],
                values['currency'],
                int(values['quantity']),
                values['product_template_id'].id,
                request.env.user.partner_id)
            values.update({
                'amount_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'amount_total': taxes['total_included'],
                'amount_untaxed': taxes['total_excluded'],
            })
            return request.render("employee_purchase_request.new_order", values)
        else:
            return request.render("employee_purchase_request.new_order", values)

    @http.route(['/order/<int:order_id>/approve'], type='http', auth="user")
    def order_approve(self, order_id=False, **post):
        order = request.env['purchase.request'].browse(int(order_id))
        order.action_approve()
        return self.order_detail(order.id)

    @http.route(['/order/<int:order_id>/reject'], type='http', auth="user")
    def order_reject(self, order_id=False, **post):
        order = request.env['purchase.request'].browse(int(order_id))
        order.action_reject()
        return self.order_detail(order.id)

    @http.route(['/order/<int:order_id>/buy-product'], type='http', auth="user", csrf=False)
    def buy_product(self, order_id=False, **post):
        order = request.env['purchase.request'].browse(int(order_id))
        order.action_buy_product()
        return self.order_detail(order.id)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        """
        Re-write to pass whether appointments are turned on in portal

        Methods:
         * _get_extra_options_ba_values
        """
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id
        purchase_request_count = request.env["purchase.request"].search_count([("partner_id", "=", partner_id)])
        values.update({
            "purchase_request_count": purchase_request_count,
        })
        return values

