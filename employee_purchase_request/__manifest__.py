# -*- coding: utf-8 -*-
{
    'name': "Employee Purchase Request",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Silpa M S",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'product',
        'purchase',
        'stock',
        'sale',
        'account',
        'auth_signup',
        'portal',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/employee_view.xml',
        'views/user_view.xml',
        'views/purchase_request_view.xml',
        'views/menu.xml',
        'views/templates.xml',
        'data/data.xml',

        'views/purchase_request_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}