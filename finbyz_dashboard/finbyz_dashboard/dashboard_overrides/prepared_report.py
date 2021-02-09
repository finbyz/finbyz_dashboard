from __future__ import unicode_literals
import frappe, json
from frappe import _

@frappe.whitelist()
def get_reports_in_queued_state(report_name, filters):
	reports = frappe.get_all('Prepared Report',
		filters = {
			'report_name': report_name,
			'filters': json.dumps(json.loads(filters)),
			'status': 'Queued'
		})
	return reports


@frappe.whitelist()
def delete_prepared_reports(reports):
	reports = frappe.parse_json(reports)
	for report in reports:
		frappe.delete_doc('Prepared Report', report['name'], ignore_permissions=True)