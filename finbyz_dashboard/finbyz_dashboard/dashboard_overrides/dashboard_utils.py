from __future__ import unicode_literals
import frappe
from frappe import _
from functools import wraps
from frappe.utils import add_to_date, cint, get_link_to_form
from frappe.modules.import_file import import_file_by_path
import os
from os.path import join


def sync_dashboards(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if not cint(frappe.db.get_single_value('System Settings', 'setup_complete')):
		return
	if app:
		apps = [app]
	else:
		apps = frappe.get_installed_apps()

	for app_name in apps:
		print("Updating Dashboard for {app}".format(app=app_name))
		for module_name in frappe.local.app_modules.get(app_name) or []:
			frappe.flags.in_import = True
			make_records_in_module(app_name, module_name)
			frappe.flags.in_import = False

def make_records_in_module(app, module):
	dashboards_path = frappe.get_module_path(module, "{module}_dashboard".format(module=module))
	charts_path = frappe.get_module_path(module, "dashboard chart")
	cards_path = frappe.get_module_path(module, "number card")

	paths = [dashboards_path, charts_path, cards_path]
	for path in paths:
		make_records(path)

def make_records(path, filters=None):
	if os.path.isdir(path):
		for fname in os.listdir(path):
			if os.path.isdir(join(path, fname)):
				if fname == '__pycache__':
					continue
				import_file_by_path("{path}/{fname}/{fname}.json".format(path=path, fname=fname))