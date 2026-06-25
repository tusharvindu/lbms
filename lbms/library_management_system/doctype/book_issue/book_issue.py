# Copyright (c) 2026, Tushar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today, date_diff, getdate

class BookIssue(Document):

	def validate(self):
		self.set_due_date()
		self.validate_membership()
		self.validate_book_availability()
	def on_submit(self):
		self.update_available_copies(-1)

	def on_cancel(self):

		if self.status != "Returned":
			self.update_available_copies(1)

	def set_due_date(self):
		if not self.issue_date:
			return

		loan_period_days = frappe.db.get_single_value(
			"Library Settings",
			"loan_period_days"
		) or 14

		self.due_date = add_days(
			self.issue_date,
			int(loan_period_days)
		)

	def validate_book_availability(self):
		if not self.book:
			return

		available_copies = frappe.db.get_value(
			"Books",
			self.book,
			"available_copies"
		)

		if not available_copies or available_copies <= 0:
			frappe.throw(
				_("Book {0} is currently not available for issue.").format(
					self.book
				)
			)

	def validate_membership(self):
		if not self.member:
			return

		membership_end_date = frappe.db.get_value(
			"Library Member",
			self.member,
			"membership_end_date"
		)

		if membership_end_date and getdate(membership_end_date) < getdate():
			frappe.throw(
				_("Membership has expired for member {0}.").format(
					self.member
				)
			)
	def update_available_copies(self, qty):
		if not self.book:
			return

		book_doc = frappe.get_doc("Books", self.book)

		new_available_copies = (
			(book_doc.available_copies or 0) + qty
		)

		if new_available_copies > book_doc.total_copies:
			frappe.throw(
				_("Available Copies cannot exceed Total Copies.")
			)

		book_doc.available_copies = new_available_copies
		if book_doc.available_copies < 0:
			frappe.throw(_("Available copies cannot be negative."))

		book_doc.status = (
			"Available"
			if book_doc.available_copies > 0
			else "Out of Stock"
		)

		book_doc.save(ignore_permissions=True)


@frappe.whitelist()
def return_book(book_issue):
	book_issue_doc = frappe.get_doc("Book Issue", book_issue)

	if book_issue_doc.status == "Returned":
		frappe.throw(_("Book has already been returned."))

	return_date = today()

	# Update submitted Book Issue
	frappe.db.set_value(
		"Book Issue",
		book_issue,
		{
			"return_date": return_date,
			"status": "Returned"
		},
		update_modified=True
	)

	# Increase available copies
	book_doc = frappe.get_doc("Books", book_issue_doc.book)

	book_doc.available_copies = (
		(book_doc.available_copies or 0) + 1
	)

	book_doc.status = "Available"

	book_doc.save(ignore_permissions=True)

	# Fine calculation
	overdue_days = date_diff(
		return_date,
		book_issue_doc.due_date
	)

	if overdue_days > 0:

		fine_per_day = frappe.db.get_single_value(
			"Library Settings",
			"fine_per_day"
		) or 0

		fine_amount = overdue_days * float(fine_per_day)

		fine_doc = frappe.get_doc({
			"doctype": "Library Fine",
			"member": book_issue_doc.member,
			"book_issue": book_issue_doc.name,
			"fine_amount": fine_amount,
			"fine_days": overdue_days,
			"payment_status": "Unpaid",
			"waived_amount": 0,
			"outstanding_amount": fine_amount
		})

		fine_doc.insert(ignore_permissions=True)

	frappe.db.commit()

	return {
		"status": "success",
		"overdue_days": overdue_days if overdue_days > 0 else 0
	}

