# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils.user import get_user_fullname
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import get_timespan_date_range

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	filters = frappe.parse_json(filters)
	if filters.get('timespan') and not filters.timespan == "":
		filters.from_date, filters.to_date = get_timespan_date_range(filters.timespan)
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart

def get_columns():
	columns = [
		{ "label": _("Document"),"fieldname": "Document","fieldtype": "Data","width": 100},
		{ "label": _("ID"),"fieldname": "ID","fieldtype": "Dynamic Link","options":"Document","width": 100},
		{ "label": _("Date"),"fieldname": "Date","fieldtype": "Date","width": 100},
		{ "label": _("Created By"),"fieldname": "Created By","fieldtype": "Link","options":"User","width": 120},
		{ "label": _("Title"),"fieldname": "Title","fieldtype": "Data","width": 110},
		{ "label": _("Contact Person"),"fieldname": "Contact Person","fieldtype": "Link","options":"Contact","width": 120},
		{ "label": _("Mobile No"),"fieldname": "Mobile No","fieldtype": "Data","width": 100},
		{ "label": _("Item Name"),"fieldname": "Item Name","fieldtype": "Data","width": 150},
		{ "label": _("Amount"),"fieldname": "Amount","fieldtype": "Currency","width": 120},
		{ "label": _("Status"),"fieldname": "Status","fieldtype": "Data","width": 100},

	]
	# columns = [
	# 	_("Document") + ":Data:100",
	# 	_("ID") + ":Dynamic Link/"+ _("Document") +":100",
	# 	_("Date") + ":Date:100",
	# 	_("Created By") + ":Link/User:120",
	# 	_("Title") + ":Data:110",
	# 	_("Contact Person") + ":Link/Contact:120",
	# 	_("Mobile No") + "::100",
	# 	_("Item Name") + ":Data:150",
	# 	_("Amount") + ":Currency:120",
	# 	_("Status") + "::100", 
	# ]
	return columns

def get_data(filters):

	doctype_list = ['Quotation', 'Sales Order', 'Sales Invoice', 'Purchase Invoice', 'Purchase Order', 'Delivery Note', 'Purchase Receipt']

	doctype = []

	if filters.doctype in doctype_list:
		doctype.append(filters.doctype)
	else:
		doctype = doctype_list[:]

	transaction_date = ['Quotation', 'Sales Order', 'Purchase Order']

	data = []
	for doc in doctype:
		conditions = ''
		date = 'posting_date'
		if doc in transaction_date:
			date = 'transaction_date'

		if filters.from_date: conditions += " and {0} >= '{1}'".format(date, filters.from_date)
		if filters.to_date: conditions += " and {0} <= '{1}'".format(date, filters.to_date)
		if filters.user:conditions += " and owner = '{0}'".format(filters.user)
		
		dt = frappe.db.sql("""
			SELECT
				name as 'ID', {date} as 'Date', owner as 'Created By', title as 'Title', contact_person as 'Contact Person', contact_mobile as 'Mobile No', status as 'Status'
			FROM
				`tab{doc}`
			WHERE
				docstatus < 2
				{conditions}

			ORDER BY
				modified DESC""".format(date=date, doc=doc, conditions=conditions), as_dict=1)

		d = dt[:]
		id = 0

		for row in d:
			row["Document"] = doc
			id = insert_items(dt, row, doc, id+1)

		data += dt

	return data

def insert_items(data, row, doc, id):

	items = frappe.db.sql("""
		SELECT
			item_code as 'Item Name', amount as 'Amount', owner as 'Owner'
		FROM
			`tab{0} Item`
		WHERE
			parent = '{1}' """.format(doc, row['ID']), as_dict=1)

	if items:
		row["Item Name"] = items[0]["Item Name"]
		row["Amount"] = items[0]["Amount"]
		row["Owner"] = items[0]["Owner"]

	for i in items[1:]:
		data.insert(id, {'Item Name': i['Item Name'], 'Amount': i["Amount"], 'Owner': i["Owner"]})
		id +=1

	return id

def get_chart_data(data, filters):

	user_list = list(map(lambda u: u['Created By'] if 'Created By' in u else '', data))
	user_item_list = list(map(lambda u: u['Owner'] if 'Owner' in u else '', data))
	users = list(set(user_list))

	total_quote = []
	total_items = []
	labels = []

	for user in users:
		if user:
			total_quote.append(user_list.count(user))
			total_items.append(user_item_list.count(user))
			labels.append(get_user_fullname(user))

	datasets = []

	if total_quote:
		datasets.append({
			'title': "Total Quotation",
			'values': total_quote
		})
	
	if total_items:
		datasets.append({
			'title': "Total Items",
			'values': total_items
		})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}
	chart["type"] = "bar"
	return chart