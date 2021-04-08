from __future__ import unicode_literals
import frappe, json
from frappe import _

@frappe.whitelist()
def number_card_custom(filters=None):
	filters = frappe.parse_json(filters)
	where_condition = ''
	if filters.get('company'):
		where_condition += " and so.company = '{}'".format(filters.get('company'))

	sales_query = frappe.db.sql("""
		select sum(soi.qty - soi.delivered_qty) as total_qty
		from `tabSales Order Item` as soi
		JOIN `tabSales Order` as so on so.name = soi.parent
		where so.docstatus=1 and so.status='To Deliver and Bill'{}
		group by soi.item_code
		""".format(where_condition),as_dict=1)
	total = 0
	for item in sales_query:
		total += item.total_qty
	
	return {
		"value": total,
		"fieldtype": "Float"
	}