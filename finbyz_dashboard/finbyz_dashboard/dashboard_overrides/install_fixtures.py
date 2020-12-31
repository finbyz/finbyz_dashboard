# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.desk.doctype.global_search_settings.global_search_settings import update_global_search_doctypes

# Finbyz CHanges Import 
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_utils import sync_dashboards

def install():
	update_genders()
	update_salutations()
	update_global_search_doctypes()
	setup_email_linking()
	# Finbyz CHanges START
	sync_dashboards()
	# Finbyz CHanges END
	add_unsubscribe()