// Copyright (c) 2026, Tushar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Book Issue", {
	refresh(frm) {
		if (
			frm.doc.docstatus === 1 &&
			frm.doc.status === "Issued"
		) {
			frm.add_custom_button(__("Return Book"), function () {
				frappe.call({
					method: "lbms.library_management_system.doctype.book_issue.book_issue.return_book",
					args: {
						book_issue: frm.doc.name
					},
					callback: function () {
						frm.reload_doc();
					}
				});
			});
		}
	},

	issue_date(frm) {
		set_due_date(frm);
	}
});

function set_due_date(frm) {
	if (!frm.doc.issue_date) {
		return;
	}

	frappe.db.get_single_value(
		"Library Settings",
		"loan_period_days"
	).then((loan_days) => {

		loan_days = loan_days || 14;

		let due_date = frappe.datetime.add_days(
			frm.doc.issue_date,
			parseInt(loan_days)
		);

		frm.set_value("due_date", due_date);
	});
}