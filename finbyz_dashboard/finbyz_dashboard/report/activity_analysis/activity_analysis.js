// Copyright (c) 2016, FinByz Tech Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Activity Analysis"] = {
	"filters": [
		{
			"fieldname":"based_on",
			"label": __("Based On"),
			"fieldtype": "Select",
			"options": ["Creation Date","Posting Date"],
			"default": "Creation Date"
		},	
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
			"options": "\nQuotation\nPurchase Order\nPurchase Receipt\nPurchase Invoice\nSales Order\nDelivery Note\nSales Invoice\nStock Entry"
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname":"timespan",
			"label": __("Timespan"),
			"fieldtype": "Select",
			"width": "80",
			"options":"\nlast week\nlast month\nlast quarter\nlast 6 months\nlast year\ntoday\nthis week\nthis month\nthis quarter\nthis year\nthis fiscal year",
			"default": "last month"
		},
		{
			"fieldname":"show_details",
			"label": __("Show Details"),
			"fieldtype": "Check",
		},		
	]
}
