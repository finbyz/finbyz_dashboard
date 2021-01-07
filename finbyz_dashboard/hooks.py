# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "finbyz_dashboard"
app_title = "Finbyz Dashboard"
app_publisher = "Finbyz Tech. Pvt. Ltd."
app_description = "Finbyz Dashboard"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@finbyz.tech"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/finbyz_dashboard/css/finbyz_dashboard.css"
# app_include_js = "/assets/finbyz_dashboard/js/finbyz_dashboard.js"

# include js, css files in header of web template
# web_include_css = "/assets/finbyz_dashboard/css/finbyz_dashboard.css"
# web_include_js = "/assets/finbyz_dashboard/js/finbyz_dashboard.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
app_include_css = ["assets/css/finbyz_dashboard.min.css"]
app_include_js = [
	"assets/js/finbyz_dashboard.min.js" 
]
fixtures = ["Custom Field"]
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "finbyz_dashboard.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "finbyz_dashboard.install.before_install"
# after_install = "finbyz_dashboard.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "finbyz_dashboard.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"finbyz_dashboard.tasks.all"
# 	],
# 	"daily": [
# 		"finbyz_dashboard.tasks.daily"
# 	],
# 	"hourly": [
# 		"finbyz_dashboard.tasks.hourly"
# 	],
# 	"weekly": [
# 		"finbyz_dashboard.tasks.weekly"
# 	]
# 	"monthly": [
# 		"finbyz_dashboard.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "finbyz_dashboard.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "finbyz_dashboard.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "finbyz_dashboard.task.get_dashboard_data"
# }
page_js = {"dashboard" : "public/js/frappe/dashboard/dashboard_page.js"}
doctype_js = {
	"Dashboard": "public/js/frappe/dashboard/dashboard.js",
	"Dashboard Chart": "public/js/frappe/dashboard/dashboard_chart.js",
}
override_whitelisted_methods = {
	"frappe.desk.doctype.dashboard_chart.dashboard_chart.get": "finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_chart.get",
}
doc_events = {
	"Dashboard":{
		"validate":"finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard.validate"
	}
}
# override_doctype_class = {
#     'Dashboard':'finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard.CustomDashboard'
# }

# import compileall, os
# compileall.compile_dir('../', force=True)

import py_compile

#Overrides py file
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/dashboard_overrides/dashboard_chart.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/dashboard_overrides/dashboard.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/dashboard_overrides/db_query.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/dashboard_overrides/boot.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/dashboard_overrides/data.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/purchase_order_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/purchase_receipt_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/purchase_invoice_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/sales_order_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/delivery_note_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/sales_invoice_trends.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/item_wise_sales_history.py')
py_compile.compile('../apps/finbyz_dashboard/finbyz_dashboard/finbyz_dashboard/report/monthly_attendance_sheet.py')

# Default py file
py_compile.compile('../apps/frappe/frappe/desk/doctype/dashboard_chart/dashboard_chart.py')
py_compile.compile('../apps/frappe/frappe/desk/doctype/dashboard/dashboard.py')
py_compile.compile('../apps/frappe/frappe/model/db_query.py')
py_compile.compile('../apps/frappe/frappe/boot.py')
py_compile.compile('../apps/frappe/frappe/utils/data.py')
py_compile.compile('../apps/erpnext/erpnext/buying/report/purchase_order_trends/purchase_order_trends.py')
py_compile.compile('../apps/erpnext/erpnext/stock/report/purchase_receipt_trends/purchase_receipt_trends.py')
py_compile.compile('../apps/erpnext/erpnext/accounts/report/purchase_invoice_trends/purchase_invoice_trends.py')
py_compile.compile('../apps/erpnext/erpnext/selling/report/sales_order_trends/sales_order_trends.py')
py_compile.compile('../apps/erpnext/erpnext/stock/report/delivery_note_trends/delivery_note_trends.py')
py_compile.compile('../apps/erpnext/erpnext/accounts/report/sales_invoice_trends/sales_invoice_trends.py')
py_compile.compile('../apps/erpnext/erpnext/selling/report/item_wise_sales_history/item_wise_sales_history.py')
py_compile.compile('../apps/erpnext/erpnext/hr/report/monthly_attendance_sheet/monthly_attendance_sheet.py')


from frappe.desk.doctype.dashboard_chart.dashboard_chart import DashboardChart
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_chart import on_update, validate
DashboardChart.on_update = on_update
DashboardChart.validate = validate

from frappe.desk.doctype.dashboard.dashboard import Dashboard
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard import on_update
Dashboard.on_update = on_update

from frappe.model.db_query import DatabaseQuery
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.db_query import prepare_filter_condition
DatabaseQuery.prepare_filter_condition = prepare_filter_condition

from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.boot import get_bootinfo_override
from frappe import boot
boot.get_bootinfo =  get_bootinfo_override

from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import add_to_date, compare, evaluate_filters, get_filter
from frappe.utils import data
data.add_to_date = add_to_date
data.compare = compare
data.evaluate_filters = evaluate_filters
data.get_filter = get_filter

# Purchase Order Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.purchase_order_trends import execute as po_execute
from erpnext.buying.report.purchase_order_trends import purchase_order_trends
purchase_order_trends.execute = po_execute

# Purchase Receipt Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.purchase_receipt_trends import execute as pr_execute
from erpnext.stock.report.purchase_receipt_trends import purchase_receipt_trends
purchase_receipt_trends.execute = pr_execute

# Purchase Invoice Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.purchase_invoice_trends import execute as pi_execute
from erpnext.accounts.report.purchase_invoice_trends import purchase_invoice_trends
purchase_invoice_trends.execute = pi_execute

# Sales Order Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.sales_order_trends import execute as so_execute
from erpnext.selling.report.sales_order_trends import sales_order_trends
sales_order_trends.execute = so_execute

# Delivery Note Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.delivery_note_trends import execute as dn_execute
from erpnext.stock.report.delivery_note_trends import delivery_note_trends
delivery_note_trends.execute = dn_execute

# Sales Invoice Trends Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.sales_invoice_trends import execute as si_execute
from erpnext.accounts.report.sales_invoice_trends import sales_invoice_trends
sales_invoice_trends.execute = si_execute

# Item-wise Sales History Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.item_wise_sales_history import execute as iws_execute
from erpnext.selling.report.item_wise_sales_history import item_wise_sales_history
item_wise_sales_history.execute = iws_execute

# Monthly Attendance Sheet Report Override For Chart
from finbyz_dashboard.finbyz_dashboard.report.monthly_attendance_sheet import execute as mas_execute
from erpnext.hr.report.monthly_attendance_sheet import monthly_attendance_sheet
monthly_attendance_sheet.execute = mas_execute

# from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.migrate import migrate as custom_migrate
# from frappe import migrate
# migrate.migrate = custom_migrate

# from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.install_fixtures import install
# # frappe.desk.page.setup_wizard.install_fixtures.install = install