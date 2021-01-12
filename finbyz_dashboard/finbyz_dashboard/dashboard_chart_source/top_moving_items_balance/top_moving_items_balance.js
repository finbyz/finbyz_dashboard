frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Top Moving Items Balance"] = {
	method: "finbyz_dashboard.finbyz_dashboard.dashboard_chart_source.top_moving_items_balance.top_moving_items_balance.get",
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
		},
		{
			fieldname: "bal_or_qty",
			label: __("Display Balance or Qty"),
			fieldtype: "Select",
			options: "Balance Qty\nBalance Value",
			reqd:1
		},
		{
			fieldname:"timespan",
			label: __("Timespan"),
			fieldtype: "Select",
			width: "80",
			reqd:1,
			options:"last week\nlast month\nlast quarter\nlast 6 months\nlast year\ntoday\nthis week\nthis month\nthis quarter\n \
			this year\nthis fiscal year\nnext week\nnext month\nnext quarter\nnext 6 months\nnext year"
		},
		// {
		// 	fieldname:"to_date",
		// 	label: __("To Date"),
		// 	fieldtype: "Data",
		// 	width: "80",
		// 	default: frappe.datetime.get_today()
		// },
	]
};