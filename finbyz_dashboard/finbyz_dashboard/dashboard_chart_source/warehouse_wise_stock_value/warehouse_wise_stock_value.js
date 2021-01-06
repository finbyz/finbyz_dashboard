frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Warehouse wise Stock Value"] = {
	method: "finbyz_dashboard.finbyz_dashboard.dashboard_chart_source.warehouse_wise_stock_value.warehouse_wise_stock_value.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		}
	]
};