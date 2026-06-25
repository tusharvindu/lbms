# Copyright (c) 2026, Tushar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LibraryFine(Document):

	def validate(self):
		self.calculate_outstanding_amount()
		self.set_payment_status()

	def on_update(self):
		self.update_member_outstanding_fine()

	def on_submit(self):
		self.update_member_outstanding_fine()
		self.create_journal_entry()

	def on_cancel(self):
		self.update_member_outstanding_fine()

	def calculate_outstanding_amount(self):
		self.outstanding_amount = (
			(self.fine_amount or 0)
			- (self.waived_amount or 0)
			- (self.paid_amount or 0)
		)

		if self.outstanding_amount < 0:
			self.outstanding_amount = 0

	def set_payment_status(self):

		if self.outstanding_amount <= 0:
			self.payment_status = "Paid"

		elif (self.paid_amount or 0) > 0:
			self.payment_status = "Partially Paid"

		else:
			self.payment_status = "Unpaid"

	def update_member_outstanding_fine(self):

		if not self.member:
			return

		total_outstanding = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(outstanding_amount), 0)
			FROM `tabLibrary Fine`
			WHERE member = %s
			AND docstatus != 2
			""",
			(self.member,),
		)[0][0]

		frappe.db.set_value(
			"Library Member",
			self.member,
			"outstanding_fine",
			total_outstanding,
			update_modified=False
		)

	def create_journal_entry(self):

		if not self.paid_amount:
			return

		if self.journal_entry:
			return

		company = frappe.defaults.get_user_default("Company")

		fine_receivable_account = frappe.db.get_single_value(
			"Library Settings",
			"fine_receivable_account"
		)

		fine_income_account = frappe.db.get_single_value(
			"Library Settings",
			"fine_income_account"
		)

		if not fine_receivable_account:
			frappe.throw(_("Please configure Fine Receivable Account in Library Settings."))

		if not fine_income_account:
			frappe.throw(_("Please configure Fine Income Account in Library Settings."))

		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": company,
			"posting_date": self.payment_date or frappe.utils.today(),
			"user_remark": f"Library Fine Payment - {self.name}",
			"accounts": [
				{
					"account": fine_receivable_account,
					"credit_in_account_currency": self.paid_amount
				},
				{
					"account": fine_income_account,
					"debit_in_account_currency": self.paid_amount
				}
			]
		})

		je.insert(ignore_permissions=True)
		je.submit()

		self.db_set("journal_entry", je.name)