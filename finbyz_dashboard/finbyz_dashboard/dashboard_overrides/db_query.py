# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six import iteritems, string_types

"""build query for doclistview and return results"""

import frappe.defaults
import frappe.share
from frappe import _
import frappe.permissions
from datetime import datetime
import frappe, json, copy, re
from frappe.model import optional_fields
from frappe.client import check_parent_permission
from frappe.model.utils.user_settings import get_user_settings, update_user_settings
from frappe.utils import flt, cint, get_time, cstr
from frappe.model.meta import get_table_columns
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import get_timespan_date_range, get_filter
from frappe.model.db_query import get_between_date_filter

def prepare_filter_condition(self, f):
    """Returns a filter condition in the format:
            ifnull(`tabDocType`.`fieldname`, fallback) operator "value"
    """

    from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.boot import get_additional_filters_from_hooks
    additional_filters_config = get_additional_filters_from_hooks()
    f = get_filter(self.doctype, f, additional_filters_config)

    tname = ('`tab' + f.doctype + '`')
    if not tname in self.tables:
        self.append_table(tname)

    if 'ifnull(' in f.fieldname:
        column_name = f.fieldname
    else:
        column_name = '{tname}.{fname}'.format(tname=tname,
            fname=f.fieldname)

    can_be_null = True

    if f.operator.lower() in additional_filters_config:
        f.update(get_additional_filter_field(additional_filters_config, f, f.value))

    # prepare in condition
    if f.operator.lower() in ('ancestors of', 'descendants of', 'not ancestors of', 'not descendants of'):
        values = f.value or ''

        # TODO: handle list and tuple
        # if not isinstance(values, (list, tuple)):
        # 	values = values.split(",")

        ref_doctype = f.doctype

        if frappe.get_meta(f.doctype).get_field(f.fieldname) is not None :
            ref_doctype = frappe.get_meta(f.doctype).get_field(f.fieldname).options

        result=[]

        lft, rgt = '', ''
        if f.value:
            lft, rgt = frappe.db.get_value(ref_doctype, f.value, ["lft", "rgt"])

        # Get descendants elements of a DocType with a tree structure
        if f.operator.lower() in ('descendants of', 'not descendants of') :
            result = frappe.get_all(ref_doctype, filters={
                'lft': ['>', lft],
                'rgt': ['<', rgt]
            }, order_by='`lft` ASC')
        else :
            # Get ancestor elements of a DocType with a tree structure
            result = frappe.get_all(ref_doctype, filters={
                'lft': ['<', lft],
                'rgt': ['>', rgt]
            }, order_by='`lft` DESC')

        fallback = "''"
        value = [frappe.db.escape((v.name or '').strip(), percent=False) for v in result]
        if len(value):
            value = "({0})".format(", ".join(value))
        else:
            value = "('')"
        # changing operator to IN as the above code fetches all the parent / child values and convert into tuple
        # which can be directly used with IN operator to query.
        f.operator = 'not in' if f.operator.lower() in ('not ancestors of', 'not descendants of') else 'in'


    elif f.operator.lower() in ('in', 'not in'):
        values = f.value or ''
        if isinstance(values, frappe.string_types):
            values = values.split(",")

        fallback = "''"
        value = [frappe.db.escape((v or '').strip(), percent=False) for v in values]
        if len(value):
            value = "({0})".format(", ".join(value))
        else:
            value = "('')"
    else:
        df = frappe.get_meta(f.doctype).get("fields", {"fieldname": f.fieldname})
        df = df[0] if df else None

        if df and df.fieldtype in ("Check", "Float", "Int", "Currency", "Percent"):
            can_be_null = False

        if f.operator.lower() in ('previous', 'next', 'timespan'):
            date_range = get_date_range(f.operator.lower(), f.value)
            f.operator = "Between"
            f.value = date_range
            fallback = "'0001-01-01 00:00:00'"

        if f.operator in ('>', '<') and (f.fieldname in ('creation', 'modified')):
            value = cstr(f.value)
            fallback = "NULL"

        elif f.operator.lower() in ('between') and \
            (f.fieldname in ('creation', 'modified') or (df and (df.fieldtype=="Date" or df.fieldtype=="Datetime"))):

            value = get_between_date_filter(f.value, df)
            fallback = "'0001-01-01 00:00:00'"

        elif f.operator.lower() == "is":
            if f.value == 'set':
                f.operator = '!='
            elif f.value == 'not set':
                f.operator = '='

            value = ""
            fallback = "''"
            can_be_null = True

            if 'ifnull' not in column_name:
                column_name = 'ifnull({}, {})'.format(column_name, fallback)

        elif df and df.fieldtype=="Date":
            value = frappe.db.format_date(f.value)
            fallback = "'0001-01-01'"

        elif (df and df.fieldtype=="Datetime") or isinstance(f.value, datetime):
            value = frappe.db.format_datetime(f.value)
            fallback = "'0001-01-01 00:00:00'"

        elif df and df.fieldtype=="Time":
            value = get_time(f.value).strftime("%H:%M:%S.%f")
            fallback = "'00:00:00'"

        elif f.operator.lower() in ("like", "not like") or (isinstance(f.value, string_types) and
            (not df or df.fieldtype not in ["Float", "Int", "Currency", "Percent", "Check"])):
                value = "" if f.value==None else f.value
                fallback = "''"

                if f.operator.lower() in ("like", "not like") and isinstance(value, string_types):
                    # because "like" uses backslash (\) for escaping
                    value = value.replace("\\", "\\\\").replace("%", "%%")

        elif f.operator == '=' and df and df.fieldtype in ['Link', 'Data']: # TODO: Refactor if possible
            value = f.value or "''"
            fallback = "''"

        elif f.fieldname == 'name':
            value = f.value or "''"
            fallback = "''"

        else:
            value = flt(f.value)
            fallback = 0

        # escape value
        if isinstance(value, string_types) and not f.operator.lower() == 'between':
            value = "{0}".format(frappe.db.escape(value, percent=False))

    if (self.ignore_ifnull
        or not can_be_null
        or (f.value and f.operator.lower() in ('=', 'like'))
        or 'ifnull(' in column_name.lower()):
        if f.operator.lower() == 'like' and frappe.conf.get('db_type') == 'postgres':
            f.operator = 'ilike'
        condition = '{column_name} {operator} {value}'.format(
            column_name=column_name, operator=f.operator,
            value=value)
    else:
        condition = 'ifnull({column_name}, {fallback}) {operator} {value}'.format(
            column_name=column_name, fallback=fallback, operator=f.operator,
            value=value)

    return condition

def get_date_range(operator, value):
	timespan_map = {
		'1 week': 'week',
		'1 month': 'month',
		'3 months': 'quarter',
		'6 months': '6 months',
		'1 year': 'year',
	}
	period_map = {
		'previous': 'last',
		'next': 'next',
	}

	timespan = period_map[operator] + ' ' + timespan_map[value] if operator != 'timespan' else value

	return get_timespan_date_range(timespan)