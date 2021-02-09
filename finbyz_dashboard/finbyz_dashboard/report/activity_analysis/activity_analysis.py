# Copyright (c) 2013, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils.user import get_user_fullname
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import get_timespan_date_range

def execute(filters=None):
	columns, data = [], []
	filters = frappe.parse_json(filters)
	if filters.get('timespan') and not filters.timespan == "":
		filters.from_date, filters.to_date = get_timespan_date_range(filters.timespan)
	if filters.show_details == 1:
		columns = get_columns_details()
		data = get_data_details(filters)
		chart = get_chart_data_details(data, filters)
		return columns, data, None, chart
	else:
		columns = get_columns()
		data, user_list,user_item_list,users = get_data(filters)
		chart = get_chart_data(user_list,user_item_list,users,filters)
		return columns, data, None, chart	

def get_columns_details():
	columns = [
		{ "label": _("Document"),"fieldname": "Document","fieldtype": "Data","width": 100},
		{ "label": _("ID"),"fieldname": "ID","fieldtype": "Dynamic Link","options":"Document","width": 100},
		{ "label": _("Date"),"fieldname": "Date","fieldtype": "Date","width": 100},
		{ "label": _("Created By"),"fieldname": "Created By","fieldtype": "Link","options":"User","width": 150},
		{ "label": _("Title"),"fieldname": "Title","fieldtype": "Data","width": 110},
		{ "label": _("Item Name"),"fieldname": "Item Name","fieldtype": "Data","width": 180},
		{ "label": _("Amount"),"fieldname": "Amount","fieldtype": "Currency","width": 150}
	]
	return columns

def get_data_details(filters):

	doctype_list = ['Quotation', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice', 'Sales Order', 'Delivery Note', 'Sales Invoice','Stock Entry']
	
	child_doctype_list = ['Quotation Item', 'Purchase Order Item', 'Purchase Receipt Item', 'Purchase Invoice Item', 'Sales Order Item', 'Delivery Note Item', 'Sales Invoice Item','Stock Entry Detail']
	doctype = []

	if filters.doctype in doctype_list:
		doctype.append(filters.doctype)
	else:
		doctype = doctype_list[:]

	transaction_date = ['Quotation', 'Sales Order', 'Purchase Order']

	data = []
	for idx,doc in enumerate(doctype):
		conditions = ''
		if filters.based_on == "Creation Date":
			date = 'CAST(creation AS DATE)'
		else:
			date = 'posting_date'
			if doc in transaction_date:
				date = 'transaction_date'

		if filters.from_date: conditions += " and {0} >= '{1}'".format(date, filters.from_date)
		if filters.to_date: conditions += " and {0} <= '{1}'".format(date, filters.to_date)
		if filters.user:conditions += " and owner = '{0}'".format(filters.user)
		
		dt = frappe.db.sql("""
			SELECT
				name as 'ID', {date} as 'Date', owner as 'Created By', title as 'Title'
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
			id = insert_items(dt, row, child_doctype_list[idx], id+1)

		data += dt

	return data

def insert_items(data, row, doc, id):

	items = frappe.db.sql("""
		SELECT
			item_code as 'Item Name', amount as 'Amount', owner as 'Owner'
		FROM
			`tab{0}`
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

def get_chart_data_details(data, filters):

	user_list = list(map(lambda u: u['Created By'] if 'Created By' in u else '', data))
	user_item_list = list(map(lambda u: u['Owner'] if 'Owner' in u else '', data))
	users = list(set(user_list))

	total_entries = []
	total_items = []
	labels = []

	for user in users:
		if user:
			total_entries.append(user_list.count(user))
			total_items.append(user_item_list.count(user))
			labels.append(get_user_fullname(user))

	datasets = []

	if total_entries:
		datasets.append({
			'title': "Total Quotation",
			'values': total_entries
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


def get_columns():
	columns = [
		{ "label": _("Created By"),"fieldname": "created_by","fieldtype": "Link","options":"User","width": 150},
		{ "label": _("Total Entries"),"fieldname": "total_entries","fieldtype": "Int","width": 100},
		{ "label": _("Total Items"),"fieldname": "total_items","fieldtype": "Int","width": 100},
	]
	return columns

def get_data(filters):

	doctype_list = ['Quotation', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice', 'Sales Order', 'Delivery Note', 'Sales Invoice','Stock Entry']
	
	child_doctype_list = ['Quotation Item', 'Purchase Order Item', 'Purchase Receipt Item', 'Purchase Invoice Item', 'Sales Order Item', 'Delivery Note Item', 'Sales Invoice Item','Stock Entry Detail']

	transaction_date = ['Quotation', 'Sales Order', 'Purchase Order']

	data,new_data = [],[]
	for idx,doc in enumerate(doctype_list):
		conditions = ''
		if filters.based_on == "Creation Date":
			date = 'CAST(creation AS DATE)'
		else:
			date = 'posting_date'
			if doc in transaction_date:
				date = 'transaction_date'

		if filters.from_date: conditions += " and {0} >= '{1}'".format(date, filters.from_date)
		if filters.to_date: conditions += " and {0} <= '{1}'".format(date, filters.to_date)
		if filters.user:conditions += " and owner = '{0}'".format(filters.user)
		
		dt = frappe.db.sql("""
			SELECT
				name, owner
			FROM
				`tab{doc}`
			WHERE
				docstatus < 2
				{conditions}
			ORDER BY
				modified DESC""".format(doc=doc, conditions=conditions), as_dict=1)
		id = 0
		for item in dt:
			items = frappe.db.sql("""
				select owner as item_owner
				from `tab{}`
				where parent = '{}'
			""".format(child_doctype_list[idx],item.name),as_dict=1)

			if items:
				item["item_owner"] = items[0]["item_owner"]
				for i in items[1:]:
					data.insert(id+1, {'item_owner': i["item_owner"]})
					id +=1
		data += dt
	
	user_list = list(map(lambda u: u['owner'] if 'owner' in u else '', data))
	user_item_list = list(map(lambda u: u['item_owner'] if 'item_owner' in u else '', data))
	users = list(set(user_list))

	total_entries,created_by = [],[]

	for user in users:
		if user:
			new_data.append({"created_by":get_user_fullname(user),"total_entries":user_list.count(user),"total_items":user_item_list.count(user)})
	# new_data.append(created_by)
	# new_data.append(total_entries)
	return new_data,user_list,user_item_list,users

def get_chart_data(user_list,user_item_list,users,filters):

	total_entries = []
	total_items = []
	labels = []

	for user in users:
		if user:
			total_entries.append(user_list.count(user))
			total_items.append(user_item_list.count(user))
			labels.append(get_user_fullname(user))

	datasets = []

	if total_entries:
		datasets.append({
			'name': "Total Entries",
			'values': total_entries
		})
	
	if total_items:
		datasets.append({
			'name': "Total Items",
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
