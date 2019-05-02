# -*- coding: utf-8 -*-
from odoo import http

# class AccountingMutliplePaymentRegister(http.Controller):
#     @http.route('/accounting_mutliple_payment_register/accounting_mutliple_payment_register/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_mutliple_payment_register/accounting_mutliple_payment_register/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_mutliple_payment_register.listing', {
#             'root': '/accounting_mutliple_payment_register/accounting_mutliple_payment_register',
#             'objects': http.request.env['accounting_mutliple_payment_register.accounting_mutliple_payment_register'].search([]),
#         })

#     @http.route('/accounting_mutliple_payment_register/accounting_mutliple_payment_register/objects/<model("accounting_mutliple_payment_register.accounting_mutliple_payment_register"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_mutliple_payment_register.object', {
#             'object': obj
#         })