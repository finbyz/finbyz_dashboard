import frappe

@frappe.whitelist()
def after_install():
	from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.dashboard_utils import sync_dashboards
	sync_dashboards('finbyz_dashboard')

	from finbyz_dashboard.patches.property_setter.property_setter import execute
	execute()