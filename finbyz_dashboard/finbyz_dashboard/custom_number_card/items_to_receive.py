from __future__ import unicode_literals
import frappe, json
from frappe import _

@frappe.whitelist()
def number_card_items_to_receive(filters=None):
	filters = frappe.parse_json(filters)
	where_condition = ''
	if filters.get('company'):
		where_condition += " and po.company = '{}'".format(filters.get('company'))

	sales_query = frappe.db.sql("""
		select count(poi.item_code) as total_items
		from `tabPurchase Order Item` as poi
		JOIN `tabPurchase Order` as po on po.name = poi.parent
		where po.docstatus=1 and poi.received_qty=0{}
		group by poi.item_code
		""".format(where_condition),as_dict=1)
	total = 0
	for item in sales_query:
		total += item.total_items
	
	return {
		"value": total,
		"fieldtype": "Float"
	}