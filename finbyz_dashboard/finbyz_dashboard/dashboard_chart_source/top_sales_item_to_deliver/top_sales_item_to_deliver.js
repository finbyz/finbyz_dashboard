frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Top Sales Item To Deliver"] = {
	method: "finbyz_dashboard.finbyz_dashboard.dashboard_chart_source.top_sales_item_to_deliver.top_sales_item_to_deliver.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group"
		}
	]
};