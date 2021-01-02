# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import datetime
import json
from functools import wraps
from frappe.utils import nowdate, add_to_date, getdate, get_last_day, formatdate,\
	get_datetime, cint, now_datetime, get_link_to_form
from frappe.model.naming import append_number_if_name_exists
from frappe.boot import get_allowed_reports
from frappe.model.document import Document
from frappe.modules.export_file import export_to_files
from frappe.modules.import_file import import_file_by_path
import os
from os.path import join

def on_update(self):
	frappe.cache().delete_key('chart-data:{}'.format(self.name))
	if frappe.conf.developer_mode and self.is_standard:
		export_to_files(record_list=[['Dashboard Chart', self.name]], record_module=self.module)


def validate(self):
	if frappe.session.user != 'Administrator' and self.is_standard:
		frappe.throw("Cannot edit Standard Chart. Please Contact Administrator")

	if not frappe.conf.developer_mode and self.is_standard:
		frappe.throw('Cannot edit Standard charts')
	if self.chart_type != 'Custom' and self.chart_type != 'Report':
		self.check_required_field()
		check_document_type(self)

	validate_custom_options(self)

def check_required_field(self):
	if not self.document_type:
			frappe.throw(_("Document type is required to create a dashboard chart"))

	if self.chart_type == 'Group By':
		if not self.group_by_based_on:
			frappe.throw(_("Group By field is required to create a dashboard chart"))
		if self.group_by_type in ['Sum', 'Average'] and not self.aggregate_function_based_on:
			frappe.throw(_("Aggregate Function field is required to create a dashboard chart"))
	else:
		if not self.based_on:
			frappe.throw(_("Time series based on is required to create a dashboard chart"))

def check_document_type(self):
	if frappe.get_meta(self.document_type).issingle:
		frappe.throw(_("You cannot create a dashboard chart from single DocTypes"))

def validate_custom_options(self):
	if self.custom_options:
		try:
			json.loads(self.custom_options)
		except ValueError as error:
			frappe.throw(_("Invalid json added in the custom options: {0}").format(error))

def get_permission_query_conditions(user):

	if not user:
		user = frappe.session.user

	if user == 'Administrator':
		return

	roles = frappe.get_roles(user)
	if "System Manager" in roles:
		return None

	doctype_condition = False
	report_condition = False

	allowed_doctypes = [frappe.db.escape(doctype) for doctype in frappe.permissions.get_doctypes_with_read()]
	allowed_reports = [frappe.db.escape(key) if type(key) == str else key.encode('UTF8') for key in get_allowed_reports()]

	if allowed_doctypes:
		doctype_condition = '`tabDashboard Chart`.`document_type` in ({allowed_doctypes})'.format(
			allowed_doctypes=','.join(allowed_doctypes))
	if allowed_reports:
		report_condition = '`tabDashboard Chart`.`report_name` in ({allowed_reports})'.format(
			allowed_reports=','.join(allowed_reports))

	return '''
			(`tabDashboard Chart`.`chart_type` in ('Count', 'Sum', 'Average')
			and {doctype_condition})
			or
			(`tabDashboard Chart`.`chart_type` = 'Report'
			and {report_condition})
		'''.format(
			doctype_condition=doctype_condition,
			report_condition=report_condition
		)


def has_permission(doc, ptype, user):
	roles = frappe.get_roles(user)
	if "System Manager" in roles:
		return True


	if doc.chart_type == 'Report':
		allowed_reports = [key if type(key) == str else key.encode('UTF8') for key in get_allowed_reports()]
		if doc.report_name in allowed_reports:
			return True
	else:
		allowed_doctypes = [frappe.permissions.get_doctypes_with_read()]
		if doc.document_type in allowed_doctypes:
			return True

	return False

def cache_source(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		if kwargs.get("chart_name"):
			chart = frappe.get_doc('Dashboard Chart', kwargs.get("chart_name"))
		else:
			chart = kwargs.get("chart")
		no_cache = kwargs.get("no_cache")
		if no_cache:
			return function(chart = chart, no_cache = no_cache)
		chart_name = frappe.parse_json(chart).name
		cache_key = "chart-data:{}".format(chart_name)
		if int(kwargs.get("refresh") or 0):
			results = generate_and_cache_results(kwargs, function, cache_key, chart)
		else:
			cached_results = frappe.cache().get_value(cache_key)
			if cached_results:
				results = frappe.parse_json(frappe.safe_decode(cached_results))
			else:
				results = generate_and_cache_results(kwargs, function, cache_key, chart)
		return results
	return wrapper

@frappe.whitelist()
@cache_source
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year=None, refresh = None):
	if chart_name:
		chart = frappe.get_doc('Dashboard Chart', chart_name)
	else:
		chart = frappe._dict(frappe.parse_json(chart))

	heatmap_year = heatmap_year or chart.heatmap_year
	timespan = timespan or chart.timespan

	if timespan == 'Select Date Range':
		if from_date and len(from_date):
			from_date = get_datetime(from_date)
		else:
			from_date = chart.from_date

		if to_date and len(to_date):
			to_date = get_datetime(to_date)
		else:
			to_date = get_datetime(chart.to_date)

	timegrain = time_interval or chart.time_interval
	filters = frappe.parse_json(filters) or frappe.parse_json(chart.filters_json)
	if not filters:
		filters = []

	# don't include cancelled documents
	filters.append([chart.document_type, 'docstatus', '<', 2, False])

	if chart.chart_type == 'Group By':
		chart_config = get_group_by_chart_config(chart, filters)
	else:
		if chart.type == 'Heatmap':
			chart_config = get_heatmap_chart_config(chart, filters, heatmap_year)
		else:
			chart_config =  get_chart_config(chart, filters, timespan, timegrain, from_date, to_date)

	return chart_config

def get_chart_config(chart, filters, timespan, timegrain, from_date, to_date):
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)
	if not to_date:
		to_date = now_datetime()

	# from_date = str(from_date)
	# date_time_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S.%f')
	
	doctype = chart.document_type
	datefield = chart.based_on
	aggregate_function = get_aggregate_function(chart.chart_type)
	value_field = chart.value_based_on or '1'
	from_date = from_date.strftime('%Y-%m-%d')
	to_date = to_date

	filters.append([doctype, datefield, '>=', from_date, False])
	filters.append([doctype, datefield, '<=', to_date, False])

	data = frappe.db.get_list(
		doctype,
		fields = [
			'{} as _unit'.format(datefield),
			'{aggregate_function}({value_field})'.format(aggregate_function=aggregate_function, value_field=value_field),
		],
		filters = filters,
		group_by = '_unit',
		order_by = '_unit asc',
		as_list = True,
		ignore_ifnull = True
	)

	result = get_result(data, timegrain, from_date, to_date)

	chart_config = {
		"labels": [formatdate(r[0].strftime('%Y-%m-%d')) for r in result],
		"datasets": [{
			"name": chart.name,
			"values": [r[1] for r in result]
		}]
	}

	return chart_config

def get_heatmap_chart_config(chart, filters, heatmap_year):
	aggregate_function = get_aggregate_function(chart.chart_type)
	value_field = chart.value_based_on or '1'
	doctype = chart.document_type
	datefield = chart.based_on
	year = cint(heatmap_year) if heatmap_year else getdate(nowdate()).year
	year_start_date = datetime.date(year, 1, 1).strftime('%Y-%m-%d')
	next_year_start_date = datetime.date(year + 1, 1, 1).strftime('%Y-%m-%d')

	filters.append([doctype, datefield, '>', "{date}".format(date=year_start_date), False])
	filters.append([doctype, datefield, '<', "{date}".format(date=next_year_start_date), False])

	if frappe.db.db_type == 'mariadb':
		timestamp_field = 'unix_timestamp({datefield})'.format(datefield=datefield)
	else:
		timestamp_field = 'extract(epoch from timestamp {datefield})'.format(datefield=datefield)

	data = dict(frappe.db.get_all(
		doctype,
		fields = [
			timestamp_field,
			'{aggregate_function}({value_field})'.format(aggregate_function=aggregate_function, value_field=value_field),
		],
		filters = filters,
		group_by = 'date({datefield})'.format(datefield=datefield),
		as_list = 1,
		order_by = '{datefield} asc'.format(datefield=datefield),
		ignore_ifnull = True
	))

	chart_config = {
		'labels': [],
		'dataPoints': data,
	}
	return chart_config

def get_group_by_chart_config(chart, filters):

	aggregate_function = get_aggregate_function(chart.group_by_type)
	value_field = chart.aggregate_function_based_on or '1'
	group_by_field = chart.group_by_based_on
	doctype = chart.document_type

	data = frappe.db.get_list(
		doctype,
		fields = [
			'{} as name'.format(group_by_field),
			'{aggregate_function}({value_field}) as count'.format(aggregate_function=aggregate_function, value_field=value_field),
		],
		filters = filters,
		group_by = group_by_field,
		order_by = 'count desc',
		ignore_ifnull = True
	)

	if data:
		if chart.number_of_groups and chart.number_of_groups < len(data):
			other_count = 0
			for i in range(chart.number_of_groups - 1, len(data)):
				other_count += data[i]['count']
			data = data[0: chart.number_of_groups - 1]
			data.append({'name': 'Other', 'count': other_count})

		chart_config = {
			"labels": [item['name'] if item['name'] else 'Not Specified' for item in data],
			"datasets": [{
				"name": chart.name,
				"values": [item['count'] for item in data]
			}]
		}

		return chart_config
	else:
		return None

def get_aggregate_function(chart_type):
	return {
		"Sum": "SUM",
		"Count": "COUNT",
		"Average": "AVG",
	}[chart_type]

def get_result(data, timegrain, from_date, to_date):
	start_date = getdate(from_date)
	end_date = getdate(to_date)

	result = [[start_date, 0.0]]

	while start_date < end_date:
		next_date = get_next_expected_date(start_date, timegrain)
		result.append([next_date, 0.0])
		start_date = next_date

	data_index = 0
	if data:
		for i, d in enumerate(result):
			while data_index < len(data) and getdate(data[data_index][0]) <= d[0]:
				d[1] += data[data_index][1]
				data_index += 1

	return result

def get_next_expected_date(date, timegrain):
	next_date = None
	# given date is always assumed to be the period ending date
	next_date = get_period_ending(add_to_date(date, days=1), timegrain)
	return getdate(next_date)

def get_period_ending(date, timegrain):
	date = getdate(date)
	if timegrain == 'Daily':
		pass
	elif timegrain == 'Weekly':
		date = get_week_ending(date)
	elif timegrain == 'Monthly':
		date = get_month_ending(date)
	elif timegrain == 'Quarterly':
		date = get_quarter_ending(date)
	elif timegrain == 'Yearly':
		date = get_year_ending(date)

	return getdate(date)

def get_week_ending(date):
	# week starts on monday
	from datetime import timedelta
	start = date - timedelta(days = date.weekday())
	end = start + timedelta(days=6)

	return end

def get_month_ending(date):
	month_of_the_year = int(date.strftime('%m'))
	# first day of next month (note month starts from 1)

	date = add_to_date('{}-01-01'.format(date.year), months = month_of_the_year)
	# last day of this month
	return add_to_date(date, days=-1)

def get_quarter_ending(date):
	date = getdate(date)

	# find the earliest quarter ending date that is after
	# the given date
	for month in (3, 6, 9, 12):
		quarter_end_month = getdate('{}-{}-01'.format(date.year, month))
		quarter_end_date = getdate(get_last_day(quarter_end_month))
		if date <= quarter_end_date:
			date = quarter_end_date
			break

	return date

def get_year_ending(date):
	''' returns year ending of the given date '''

	# first day of next year (note year starts from 1)
	date = add_to_date('{}-01-01'.format(date.year), months = 12)
	# last day of this month
	return add_to_date(date, days=-1)


@frappe.whitelist()
def create_dashboard_chart(args):
	args = frappe.parse_json(args)
	doc = frappe.new_doc('Dashboard Chart')

	doc.update(args)

	if args.get('custom_options'):
		doc.custom_options = json.dumps(args.get('custom_options'))

	if frappe.db.exists('Dashboard Chart', args.chart_name):
		args.chart_name = append_number_if_name_exists('Dashboard Chart', args.chart_name)
		doc.chart_name = args.chart_name
	doc.insert(ignore_permissions=True)
	return doc

@frappe.whitelist()
def create_report_chart(args):
	doc = create_dashboard_chart(args)
	args = frappe.parse_json(args)
	args.chart_name = doc.chart_name
	if args.dashboard:
		add_chart_to_dashboard(json.dumps(args))

@frappe.whitelist()
def add_chart_to_dashboard(args):
	args = frappe.parse_json(args)

	dashboard = frappe.get_doc('Dashboard', args.dashboard)
	dashboard_link = frappe.new_doc('Dashboard Chart Link')
	dashboard_link.chart = args.chart_name or args.name

	if args.set_standard and dashboard.is_standard:
		chart = frappe.get_doc('Dashboard Chart', dashboard_link.chart)
		chart.is_standard = 1
		chart.module = dashboard.module
		chart.save()

	dashboard.append('charts', dashboard_link)
	dashboard.save()
	frappe.db.commit()

def generate_and_cache_results(args, function, cache_key, chart):
	try:
		args = frappe._dict(args)
		results = function(
			chart_name = args.chart_name,
			filters = args.filters or None,
			from_date = args.from_date or None,
			to_date = args.to_date or None,
			time_interval = args.time_interval or None,
			timespan = args.timespan or None,
			heatmap_year = args.heatmap_year or None
		)
	except TypeError as e:
		if str(e) == "'NoneType' object is not iterable":
			# Probably because of invalid link filter
			#
			# Note: Do not try to find the right way of doing this because
			# it results in an inelegant & inefficient solution
			# ref: https://github.com/frappe/frappe/pull/9403
			frappe.throw(_('Please check the filter values set for Dashboard Chart: {}').format(
				get_link_to_form(chart.doctype, chart.name)), title=_('Invalid Filter Value'))
			return
		else:
			raise

	frappe.db.set_value("Dashboard Chart", args.chart_name, "last_synced_on", frappe.utils.now(), update_modified = False)
	return results

def get_from_date_from_timespan(to_date, timespan):
	days = months = years = 0
	if timespan == "Last Week":
		days = -7
	if timespan == "Last Month":
		months = -1
	elif timespan == "Last Quarter":
		months = -3
	elif timespan == "Last Year":
		years = -1
	elif timespan == "All Time":
		years = -50
	return add_to_date(to_date, years=years, months=months, days=days,
		as_datetime=True)
	

@frappe.whitelist()
#@frappe.validate_and_sanitize_search_inputs
def get_charts_for_user(doctype, txt, searchfield, start, page_len, filters):
	or_filters = {'owner': frappe.session.user, 'is_public': 1}
	return frappe.db.get_list('Dashboard Chart',
		fields=['name'],
		filters=filters,
		or_filters=or_filters,
		as_list = 1)