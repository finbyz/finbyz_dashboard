# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils import flt, cint, getdate, now, date_diff
# from frappe.utils.dashboard import cache_source
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_chart import cache_source
from erpnext.stock.utils import get_stock_value_from_bin
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import get_timespan_date_range
@frappe.whitelist()
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):
	labels, datapoints = [], []
	filters = frappe.parse_json(filters)
	from_date, to_date = get_timespan_date_range(filters.timespan)
	bal_or_qty = 'actual_qty' if filters.get('bal_or_qty') == "Balance Qty" else 'stock_value'
	# stock_ledger_entries = frappe.get_list("Stock Ledger Entry", fields=['item_code','actual_qty'], filters=extra_filters, order_by='posting_date,posting_time,creation,actual_qty')

	where_con = where_con_bin = join_con = join_con_bin = ''
	if filters.get('company'):
		where_con += " and sle.company = '{}'".format(filters.get('company'))
		join_con_bin += " JOIN `tabWarehouse` as w on w.name = bin.warehouse"
		where_con_bin += " and w.company = '{}'".format(filters.get('company'))

	if filters.get('item_group'):
		join_con = " JOIN `tabItem` as i on i.name = sle.item_code"
		where_con += " and i.item_group = '{}'".format(filters.get('item_group'))
		join_con_bin = " JOIN `tabItem` as i on i.name = bin.item_code"
		where_con_bin += " and i.item_group = '{}'".format(filters.get('item_group'))
	
	stock_ledger_entries = frappe.db.sql("""
		select sle.item_code, sum(abs(sle.stock_value_difference)) as stock_value_difference
		from `tabStock Ledger Entry` as sle
		{join_con}
		where sle.actual_qty < 0 and sle.docstatus < 2 and is_cancelled = 0 and sle.posting_date between '{from_date}' AND '{to_date}'{where_con}
		group by sle.item_code
		order by stock_value_difference DESC
		limit 10
	""".format(join_con=join_con, from_date=from_date,to_date=to_date,where_con=where_con), as_dict=1)

	if not stock_ledger_entries:
		return []
	item_code_tuple = []
	for sle in stock_ledger_entries:
		item_code_tuple.append(sle.item_code)

	tuple_item_code = tuple(item_code_tuple)
	balance_qty_dict = frappe.db.sql("""
		select bin.item_code, sum(bin.{bal_or_qty}) as balance
		from `tabBin` as bin
		{join_con_bin}
		where bin.item_code in {tuple_item_code}{where_con_bin}
		group by bin.item_code
	""".format(bal_or_qty=bal_or_qty, join_con_bin=join_con_bin, tuple_item_code=tuple_item_code,where_con_bin=where_con_bin), as_dict=1)	

	datapoint2 = []
	for sle in balance_qty_dict:
		labels.append(_(sle.get("item_code")))
		datapoints.append(sle.get("balance"))
	return{
		"labels": labels,
		"datasets": [{
			"name": filters.get('bal_or_qty'),
			"values": datapoints
		}],
		"type": "bar"
	}