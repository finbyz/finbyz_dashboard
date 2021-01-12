# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
# from frappe.utils.dashboard import cache_source
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_chart import cache_source
from erpnext.stock.utils import get_stock_value_from_bin

@frappe.whitelist()
@cache_source
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):
	labels, datapoint1, datapoint2 = [], [], []
	filters = frappe.parse_json(filters)

	where_condition = ''
	if filters.get('company'):
		where_condition += " and so.company = '{}'".format(filters.get('company'))
	if filters.get('item_group'):
		where_condition += " and soi.item_group = '{}'".format(filters.get('item_group'))

	sales_query = frappe.db.sql("""
		select sum(soi.qty-soi.delivered_qty) as qty, sum((soi.qty-soi.delivered_qty)*soi.base_net_rate) as amount, soi.item_code
		from `tabSales Order Item` as soi
		JOIN `tabSales Order` as so on so.name = soi.parent
		where so.docstatus=1 and so.status not in ('Completed','Closed'){}
		group by soi.item_code
		order by amount DESC
		limit 10
	""".format(where_condition),as_dict=1)

	if not sales_query:
		return []

	# sales_map = sorted(sales_query, key = lambda i: i['amount'], reverse=True)

	# if len(sales_query) > 10:
	# 	sales_query = sales_query[:10]

	for item in sales_query:
		labels.append(_(item.get("item_code")))
		datapoint1.append(item.get("qty"))
		datapoint2.append(item.get("amount"))
	return{
		"labels": labels,
		"datasets": [{
			"name": _("Qty to Deliver"),
			"values": datapoint1
		},
		{
			"name": _("Amount"),
			"values": datapoint2
		}],
		"type": "bar"
	}