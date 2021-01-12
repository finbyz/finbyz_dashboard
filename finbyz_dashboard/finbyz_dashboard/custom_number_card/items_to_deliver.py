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
		select count(soi.item_code) as total_items
		from `tabSales Order Item` as soi
		JOIN `tabSales Order` as so on so.name = soi.parent
		where so.docstatus=1 and soi.delivered_qty=0{}
		group by soi.item_code
		""".format(where_condition),as_dict=1)
	total = 0
	for item in sales_query:
		total += item.total_items
	
	return {
		"value": total,
		"fieldtype": "Float"
	}