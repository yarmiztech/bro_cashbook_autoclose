from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class SaleEstimateLines(models.Model):
    _inherit = "sale.estimate.lines"

    addition_price = fields.Float(string="Additional Price")
    basic_km = fields.Float(string="Basic KM")
    no_of_times = fields.Integer(string="No of Times", default=1)
    bag_sum = fields.Float(string="Trip Amount", compute='compute_trip_amount')
    trip_amount = fields.Float(string="Trip Amount", compute='compute_trip_amount')
    trip_config = fields.Many2one('basic.trip')

    @api.depends('trip_amount', 'no_of_times', 'addition_price', 'sub_customers', 'basic_km')
    def compute_trip_amount(self):
        for each in self:
            print('ffffff')
            each.bag_sum = 0
            each.trip_amount = 0
            for lines in each.sub_customers:
                each.bag_sum += lines.quantity
            each.trip_amount = each.bag_sum
            basic_config = self.env['basic.trip'].search(
                [('from_kilo_meter', '<=', self.basic_km), ('to_kilo_meter', '>=', self.basic_km)])
            if basic_config:
                self.trip_config = basic_config
                if each.trip_amount > basic_config.basic_bags:
                    extra_bags = each.trip_amount - basic_config.basic_bags
                    extra_add = extra_bags * basic_config.additional_price
                    self.trip_amount = basic_config.price + extra_add + each.addition_price
                if each.trip_amount < basic_config.basic_bags:
                    self.trip_amount = basic_config.price + each.addition_price


class SaleEstimate(models.Model):
    _inherit = 'sale.estimate'

    def action_approve(self):
        res = super(SaleEstimate, self).action_approve()
        for line in self.estimate_ids:
            # fleet = self.env['fleet.vehicle'].sudo().search([('license_plate', '=', line.vehicle_number)])

            self.env['brothers.trip.sheet'].create({
                'vehicle_id': line.vahicle.id,
                'vehicle_number': line.vahicle.license_plate,
                'total_bags': line.bag_sum,
                'total_kms': line.basic_km,
                # 'company_type':line.vahicle.type or False,
                'internal_company': line.vahicle.company_id.id or False,
                'partner_id': line.vahicle.company_id.partner_id.id,
                'company_id': self.company_id.id,
                'create_date': datetime.today().date(),
                # 'betta_charge':basic_config.price,
                # 'type_of_charge':fleet.type_of_charge,
                # 'km_charge':km_charge,
                'from_invoice': self.invoice_ids.filtered(lambda a: a.company_id == line.company_ids[0]).id,
                'final_invoice_amount': line.trip_amount
            })


class CashBookClosing(models.Model):
    _inherit = "cash.book.closing"
    _order = "id desc"

    def action_cash_book_close(self):
        today_data = self.env['cash.book.info'].search([('date', '=', self.date)])
        self.write({'state':'validate'})
        for each in today_data:
            each.closed = True
        if not today_data:
            if self.env['cash.book.info'].search([]):
                today_data = self.env['cash.book.info'].search([])[-1]
                for each in today_data:
                    each.closed = True
        if today_data:
            self.env['cash.book.info'].create({
                'date': datetime.today().date() + relativedelta(days=1),
                'account_journal': today_data[-1].account_journal.id,
                # 'partner_id': self.partner_id.id,
                'company_id': 1,
                'description': 'Opening Balance/Cash',
                'payment_type': 'inbound',
                # 'partner_type': self.partner_type,
                'debit': today_data[-1].balance,
                'credit': 0,
                'account': today_data[-1].account.id,
                # 'payment_id': self.id,
                'balance': today_data[-1].balance
            })

    def dailyclosecash(self):
        date = datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
        dailyclosecash = self.env['cash.book.closing'].create({'date': datetime.now().date()})
        dailyclosecash.onchange_date()
        dailyclosecash.action_cash_book_close()
