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
		data = get_data(filters)
		chart = get_chart_data(data,filters)
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

	if filters.get('doctype'):
		doctype = [filters.doctype]
		if not filters.doctype == "Stock Entry":
			child_doctype_list = [filters.doctype + " Item"]
		else:
			child_doctype_list = [filters.doctype + " Detail"]

	data = []
	for idx,doc in enumerate(doctype):
		title_field = frappe.db.get_value("Property Setter",{"doc_type":doc,"property":'title_field'},'value')
		if not title_field:
			title_field = frappe.db.get_value("DocType",doc,'title_field')
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
				name as 'ID', {date} as 'Date', owner as 'Created By', {title_field} as 'Title'
			FROM
				`tab{doc}`
			WHERE
				docstatus < 2
				{conditions}

			ORDER BY
				modified DESC""".format(date=date, title_field=title_field,doc=doc, conditions=conditions), as_dict=1)

		d = dt[:]
		id = 0

		for row in d:
			row["Document"] = doc
			row["Created By"] = get_user_fullname(row["Created By"])
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
		row["Owner"] = get_user_fullname(items[0]["Owner"])

	for i in items[1:]:
		data.insert(id, {'Item Name': i['Item Name'], 'Amount': i["Amount"], 'Owner': get_user_fullname(i["Owner"])})
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
			labels.append((user))

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


def get_columns():
	columns = [
		{ "label": _("Created By"),"fieldname": "created_by","fieldtype": "Link","options":"User","width": 200},
		{ "label": _("Total Entries"),"fieldname": "total_entries","fieldtype": "Int","width": 150},
		{ "label": _("Total Items"),"fieldname": "total_items","fieldtype": "Int","width": 150},
	]
	return columns

def get_data(filters):

	doctype_list = ['Quotation', 'Purchase Order', 'Purchase Receipt', 'Purchase Invoice', 'Sales Order', 'Delivery Note', 'Sales Invoice','Stock Entry']
	
	child_doctype_list = ['Quotation Item', 'Purchase Order Item', 'Purchase Receipt Item', 'Purchase Invoice Item', 'Sales Order Item', 'Delivery Note Item', 'Sales Invoice Item','Stock Entry Detail']

	transaction_date = ['Quotation', 'Sales Order', 'Purchase Order']

	data,new_data,entries_list,items_list,owner_list = [],[],[],[],[]

	if filters.get('doctype'):
		doctype_list = [filters.doctype]
		if not filters.doctype == "Stock Entry":
			child_doctype_list = [filters.doctype + " Item"]
		else:
			child_doctype_list = [filters.doctype + " Detail"]

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
				owner, count(name) as total_entries
			FROM
				`tab{doc}`
			WHERE
				docstatus < 2
				{conditions}
			GROUP BY
				owner
			ORDER BY
				modified DESC
		""".format(doc=doc, conditions=conditions), as_dict=1)
		
		dt_map = {}
		user_tuple = '('
		if dt:
			for row in dt:
				if user_tuple.find(row.owner) == -1:
					user_tuple += "'{}',".format(row.owner)
				if (row.owner) in dt_map:
					dt_map[(row.owner)] += row.total_entries
				else:
					dt_map[(row.owner)] = row.total_entries
			user_tuple = user_tuple[:-1]
			user_tuple += ")"
			conditions = ""
			if filters.based_on == "Creation Date":
				date = 'CAST(p.creation AS DATE)'
			else:
				date = 'p.posting_date'
				if doc in transaction_date:
					date = 'p.transaction_date'

			if filters.from_date: conditions += " and {0} >= '{1}'".format(date, filters.from_date)
			if filters.to_date: conditions += " and {0} <= '{1}'".format(date, filters.to_date)
			if filters.user:conditions += " and p.owner = '{0}'".format(filters.user)

			items = frappe.db.sql("""
				select child.owner,count(child.name) as total_items
				from `tab{}` as child
				JOIN `tab{}` as p on p.name = child.parent and p.owner = child.owner
				where child.docstatus < 2 {}
				group by child.owner
				ORDER BY child.modified desc
			""".format(child_doctype_list[idx],doc,conditions),as_dict=1)

# Below Code is for Merge Multiple owners with its keys and values 
# Example: items = [{"admin":{"total_entries":5,"total_items":10}},
#	{"admin":{"total_entries":10,"total_items":15}},{"user":{"total_entries":2,"total_items":1}}]
# in above example list it needs to merge same keys('admin') with its value(which also a dict)

			for row in items:
				owner_list.append(row.owner)	# Owner List
				entries_list.append({row.owner:dt_map[(row.owner)]})
				items_list.append({row.owner:row.total_items})

	entries_sum = {}
	for d in entries_list:
		for k in d.keys():
			entries_sum[k] = entries_sum.get(k, 0) + d[k]

	items_sum = {}
	for d in items_list:
		for k in d.keys():
			items_sum[k] = items_sum.get(k, 0) + d[k]

	owner_list = list(set(owner_list))

	for row in owner_list:
		data.append({"created_by":get_user_fullname(row),"total_entries":entries_sum[row],"total_items":items_sum[row]})

	return data

def get_chart_data(data,filters):

	total_entries = []
	total_items = []
	labels = []
	for row in data:
		total_entries.append(row['total_entries'])
		total_items.append(row['total_items'])
		labels.append(row['created_by'])
		#labels.append(row['created_by'])
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
