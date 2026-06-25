import frappe
from frappe.utils import today


def mark_overdue_books():
	overdue_books = frappe.get_all(
		"Book Issue",
		filters={
			"docstatus": 1,
			"status": "Issued",
			"due_date": ["<", today()]
		},
		pluck="name"
	)

	for book_issue in overdue_books:
		frappe.db.set_value(
			"Book Issue",
			book_issue,
			"status",
			"Overdue",
			update_modified=False
		)

	if overdue_books:
		frappe.db.commit()