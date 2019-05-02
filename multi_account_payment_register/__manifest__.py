# -*- coding: utf-8 -*-
{
    'name': "Multi-Account Payment Register",

    'summary': """
       Multliple Accounts in Payment Register""",

    'description': """
        Multliple Accounts in Payment Register
    """,

    'author': "Brain Station 23 LTD.",
    'website': "http://www.brainstation-23.com/",
    'support': 'support@brainstation-23.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['account'],
    'images': ['images/main_screenshot.png'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        # 'views/register_payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'price': 15,
    'currency': 'EUR'
}