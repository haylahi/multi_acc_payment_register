from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    @api.depends('account_multiple_ids')
    def _compute_sum_account_multiple_ids(self):
        sum = 0
        for data in self.account_multiple_ids:
            sum += data.amount
        # print(sum)
        self.sum_account_multiple_ids = sum

    account_multiple_ids = fields.One2many('account.payment.multiple', 'account_multiple_id', string="Post Difference In")
    sum_account_multiple_ids = fields.Monetary(compute='_compute_sum_account_multiple_ids', readonly=True, string="Post Difference In Total Amount")

    @api.model
    def _create_payment_entry(self,amount):
        # res = super(AccountPaymentInherit, self)._create_payment_entry(account_multiple_ids)
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
                    Return the journal entry.
                """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        # Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
                self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
                                                                                                         self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            # Set the payment diffrence at multiple account as a debit
            for data in self.account_multiple_ids:
                if amount_wo > 0:
                    # debit_wo = amount_wo
                    debit_wo = data.amount
                    credit_wo = 0.0
                    amount_currency_wo = abs(amount_currency_wo)
                else:
                    debit_wo = 0.0
                    credit_wo = -data.amount
                    amount_currency_wo = -abs(amount_currency_wo)
                writeoff_line['name'] = _('Counterpart')
                writeoff_line['account_id'] = data.account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line_obj = aml_obj.create(writeoff_line)
                if counterpart_aml['debit']:
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit']:
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo


        self.invoice_ids.register_payment(counterpart_aml)

        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    # Override the post method for checking the validation Payment Difference amount and Post Difference In amount total is same or not.
    @api.multi
    def post(self):
        if self.payment_difference_handling == 'reconcile' and self.sum_account_multiple_ids != self.payment_difference:
            raise UserError(_("Post Difference In amount total %s must be same as Payment Difference amount %s.") % (self.sum_account_multiple_ids, self.payment_difference))
        res = super(AccountPaymentInherit,self).post()
        return res


class AccountPayment(models.Model):
    _name = "account.payment.multiple"
    account_multiple_id = fields.Many2one('account.payment', string="Multiple Account")

    account_id = fields.Many2one('account.account', string="Account",
                                          domain=[('deprecated', '=', False)], copy=False,  required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)