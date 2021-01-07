# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six import iteritems, string_types

"""build query for doclistview and return results"""

import frappe.defaults
from dateutil.parser._parser import ParserError
import operator
import re, datetime, math, time
import babel.dates
from babel.core import UnknownLocaleError
from dateutil import parser
from num2words import num2words
from six.moves import html_parser as HTMLParser
from six.moves.urllib.parse import quote, urljoin
from html2text import html2text
from markdown2 import markdown, MarkdownError
from six import iteritems, text_type, string_types, integer_types
import frappe.share
from frappe import _
import frappe.permissions
import frappe, json, copy, re
from frappe.model import optional_fields
from frappe.client import check_parent_permission
from frappe.model.utils.user_settings import get_user_settings, update_user_settings
from frappe.utils import flt, cint, get_time, cstr, now_datetime, make_filter_tuple, sanitize_column, getdate, nowdate
from frappe.model.meta import get_table_columns

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

def add_to_date(date, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, as_string=False, as_datetime=False):
	"""Adds `days` to the given date"""
	from dateutil.relativedelta import relativedelta

	if date==None:
		date = now_datetime()

	if hours:
		as_datetime = True

	if isinstance(date, string_types):
		as_string = True
		if " " in date:
			as_datetime = True
		try:
			date = parser.parse(date)
		except ParserError:
			frappe.throw(frappe._("Please select a valid date filter"), title=frappe._("Invalid Date"))

	date = date + relativedelta(years=years, months=months, weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

	if as_string:
		if as_datetime:
			return date.strftime(DATETIME_FORMAT)
		else:
			return date.strftime(DATE_FORMAT)
	else:
		return date

def compare(val1, condition, val2, fieldtype=None):
	ret = False
	if fieldtype:
		val2 = cast_fieldtype(fieldtype, val2)
	if condition in operator_map:
		ret = operator_map[condition](val1, val2)

	return ret

def evaluate_filters(doc, filters):
	'''Returns true if doc matches filters'''
	if isinstance(filters, dict):
		for key, value in iteritems(filters):
			f = get_filter(None, {key:value})
			if not compare(doc.get(f.fieldname), f.operator, f.value, f.fieldtype):
				return False

	elif isinstance(filters, (list, tuple)):
		for d in filters:
			f = get_filter(None, d)
			if not compare(doc.get(f.fieldname), f.operator, f.value, f.fieldtype):
				return False

	return True

def get_filter(doctype, f, filters_config=None):
	"""Returns a _dict like
		{
			"doctype":
			"fieldname":
			"operator":
			"value":
			"fieldtype":
		}
	"""
	from frappe.model import default_fields, optional_fields

	if isinstance(f, dict):
		key, value = next(iter(f.items()))
		f = make_filter_tuple(doctype, key, value)

	if not isinstance(f, (list, tuple)):
		frappe.throw(frappe._("Filter must be a tuple or list (in a list)"))

	if len(f) == 3:
		f = (doctype, f[0], f[1], f[2])
	elif len(f) > 4:
		f = f[0:4]
	elif len(f) != 4:
		frappe.throw(frappe._("Filter must have 4 values (doctype, fieldname, operator, value): {0}").format(str(f)))

	f = frappe._dict(doctype=f[0], fieldname=f[1], operator=f[2], value=f[3])

	sanitize_column(f.fieldname)

	if not f.operator:
		# if operator is missing
		f.operator = "="

	valid_operators = ("=", "!=", ">", "<", ">=", "<=", "like", "not like", "in", "not in", "is",
		"between", "descendants of", "ancestors of", "not descendants of", "not ancestors of",
		"timespan", "previous", "next")

	if filters_config:
		additional_operators = []
		for key in filters_config:
			additional_operators.append(key.lower())
		valid_operators = tuple(set(valid_operators + tuple(additional_operators)))

	if f.operator.lower() not in valid_operators:
		frappe.throw(frappe._("Operator must be one of {0}").format(", ".join(valid_operators)))


	if f.doctype and (f.fieldname not in default_fields + optional_fields):
		# verify fieldname belongs to the doctype
		meta = frappe.get_meta(f.doctype)
		if not meta.has_field(f.fieldname):

			# try and match the doctype name from child tables
			for df in meta.get_table_fields():
				if frappe.get_meta(df.options).has_field(f.fieldname):
					f.doctype = df.options
					break

	try:
		df = frappe.get_meta(f.doctype).get_field(f.fieldname)
	except frappe.exceptions.DoesNotExistError:
		df = None

	f.fieldtype = df.fieldtype if df else None

	return f

def get_first_day(dt, d_years=0, d_months=0, as_str=False):
	"""
	 Returns the first day of the month for the date specified by date object
	 Also adds `d_years` and `d_months` if specified
	"""
	dt = getdate(dt)

	# d_years, d_months are "deltas" to apply to dt
	overflow_years, month = divmod(dt.month + d_months - 1, 12)
	year = dt.year + d_years + overflow_years

	return datetime.date(year, month + 1, 1).strftime(DATE_FORMAT) if as_str else datetime.date(year, month + 1, 1)

def get_quarter_start(dt, as_str=False):
	date = getdate(dt)
	quarter = (date.month - 1) // 3 + 1
	first_date_of_quarter = datetime.date(date.year, ((quarter - 1) * 3) + 1, 1)
	return first_date_of_quarter.strftime(DATE_FORMAT) if as_str else first_date_of_quarter

def get_first_day_of_week(dt, as_str=False):
	dt = getdate(dt)
	date = dt - datetime.timedelta(days=dt.weekday())
	return date.strftime(DATE_FORMAT) if as_str else date

def get_year_start(dt, as_str=False):
	dt = getdate(dt)
	date = datetime.date(dt.year, 1, 1)
	return date.strftime(DATE_FORMAT) if as_str else date

def get_last_day_of_week(dt):
	dt = get_first_day_of_week(dt)
	return dt + datetime.timedelta(days=6)

def get_last_day(dt):
	"""
	 Returns last day of the month using:
	 `get_first_day(dt, 0, 1) + datetime.timedelta(-1)`
	"""
	return get_first_day(dt, 0, 1) + datetime.timedelta(-1)

def get_timespan_date_range(timespan):
	date_range_map = {
		"last week": [add_to_date(nowdate(), days=-7), nowdate()],
		"last month": [add_to_date(nowdate(), months=-1), nowdate()],
		"last quarter": [add_to_date(nowdate(), months=-3), nowdate()],
		"last 6 months": [add_to_date(nowdate(), months=-6), nowdate()],
		"last year": [add_to_date(nowdate(), years=-1), nowdate()],
		"today": [nowdate(), nowdate()],
		"this week": [get_first_day_of_week(nowdate(), as_str=True), nowdate()],
		"this month": [get_first_day(nowdate(), as_str=True), nowdate()],
		"this quarter": [get_quarter_start(nowdate(), as_str=True), nowdate()],
		"this year": [get_year_start(nowdate(), as_str=True), nowdate()],
		"this fiscal year":[get_start_fiscal_year_date(nowdate(), as_str=True),get_end_fiscal_year_date(nowdate(),as_str=True)],
		"next week": [nowdate(), add_to_date(nowdate(), days=7)],
		"next month": [nowdate(), add_to_date(nowdate(), months=1)],
		"next quarter": [nowdate(), add_to_date(nowdate(), months=3)],
		"next 6 months": [nowdate(), add_to_date(nowdate(), months=6)],
		"next year": [nowdate(), add_to_date(nowdate(), years=1)],
	}
	return date_range_map.get(timespan)

def get_start_fiscal_year_date(dt,as_str= False):
	date = getdate(frappe.defaults.get_user_default("year_start_date"))
	return date.strftime(DATE_FORMAT) if as_str else date

def get_end_fiscal_year_date(dt,as_str= False):
	date = getdate(frappe.defaults.get_user_default("year_end_date"))
	return date.strftime(DATE_FORMAT) if as_str else date