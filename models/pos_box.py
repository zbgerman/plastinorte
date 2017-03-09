# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2016  Dominic Krimmer                                         #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

# Extended Product Template
from openerp import models, fields, api, exceptions
import string

from openerp.addons.account.wizard.pos_box import CashBox
import logging
_logger = logging.getLogger(__name__)

class inherit_PosBoxOut(CashBox):
    _name = 'cash.box.out'
    _inherit = 'cash.box.out'
    
    @api.onchange('product_expenses') 
    def on_product_expenses(self):
        if self.product_expenses:
            self.name = self.product_expenses.name
 

class inherit_hr_expense(models.Model):
    _name = 'hr.expense'
    _inherit = 'hr.expense'
   
    provider_id = fields.Many2one('res.partner', 'Proveedor')
    nroinvoice = fields.Char('Number Invoice')
    reason = fields.Char('Reason')

    @api.multi
    def register_expense(self):   
       
        model_cash_box_out = self.env['cash.box.out']

        cash_id = model_cash_box_out.create({
            'name' : self.name,
            'amount' : self.unit_amount
            })
        if cash_id:
            cash_id.run()

        model_pos_session = self.env['pos.session']   
        model_account_journal = self.env['account.journal']
        model_hr_employee = self.env['hr.employee']


        active_id = self.env.context.get('active_id')
        pos = model_pos_session.search([('id', '=' , active_id)])
        account_journal_id = model_account_journal.search([('type', '=', 'cash'),('name', 'ilike', 'Control')], limit = 1)
        query = model_hr_employee.search([('user_id', '=' ,  self.env.uid)])   

        self.write({
            'description' : pos.config_id.name if pos else False,
            'payment_mode' : 'company_account',
            'bank_journal_id' : account_journal_id.id if account_journal_id else False,
            'employee_id' : query.id if query else False,
            'department_id' : query.department_id.id
            })

        """model_hr_employee = self.env['hr.employee']
        model_pos_session = self.env['pos.session']
        model_hr_expenses = self.env['hr.expense']
        model_account_journal = self.env['account.journal']

        query = model_hr_employee.search([('user_id', '=' ,  self.env.uid)])            
        active_id = self.env.context.get('active_id')
        pos = model_pos_session.search([('id', '=' , active_id)])
        account_journal_id = model_account_journal.search([('type', '=', 'cash'),('name', 'ilike', 'Control')], limit = 1)
        
        
        res_expense = model_hr_expenses.create({
            'name' : res.name,
            'product_id' : res.product_expenses.id,
            'unit_amount' : res.amount,
            'quantity' : 1,
            'employee_id' : query.id if query else False,
            'payment_mode' : 'company_account',
            'bank_journal_id' : account_journal_id.id if account_journal_id else False,
            'state' : 'draft',
            'provider_id' : res.partner_id.id if res.partner_id else False,
            'nroinvoice' : res.nroinvoice if res.nroinvoice else False,
            'reason' : res.reason if res.reason else False,
            'description' : pos.config_id.name if pos else False,
            })
        if res_expense:
            res_expense.tax_ids = res.product_expenses.supplier_taxes_id"""
            

class pos_session(models.Model):
    _name = 'pos.session'
    _inherit = 'pos.session'
   
    @api.multi
    def expense_control(self, values):

        view_ref = self.env['ir.model.data'].get_object_reference('plastinorte', 'register_expense_form')
        view_id = view_ref[ 1 ] if view_ref else False

        return {
               'context': {},
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'hr.expense',
               'res_id': False,
               'view_id': view_id,
               'type': 'ir.actions.act_window',
               'target': 'new',
              }

