// Copyright (c) 2016, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Activity Analysis"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "doctype",
			"label": __("DocType"),
			"fieldtype": "Select",
			"options": "\nQuotation\nSales Order\nSales Invoice\nPurchase Order\nPurchase Invoice\nDelivery Note\nPurchase Receipt"
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			fieldname:"timespan",
			label: __("Timespan"),
			fieldtype: "Select",
			width: "80",
			options:"last week\nlast month\nlast quarter\nlast 6 months\nlast year\ntoday\nthis week\nthis month\nthis quarter\nthis year\nthis fiscal year\nnext week\nnext month\nnext quarter\nnext 6 months\nnext year"
		},
		{
			fieldname:"use_timespan",
			label: __("Use Timespan"),
			fieldtype: "Check",
			default:0
		},
	]
}