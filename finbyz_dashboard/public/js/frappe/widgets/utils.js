function generate_route(item) {
	const type = item.type.toLowerCase()
	if (type === "doctype") {
		item.doctype = item.name;
	}
	let route = "";
	if (!item.route) {
		if (item.link) {
			route = strip(item.link, "#");
		} else if (type === "doctype") {
			if (frappe.model.is_single(item.doctype)) {
				route = "Form/" + item.doctype;
			} else {
				if (!item.doc_view) {
					if (frappe.model.is_tree(item.doctype)) {
						item.doc_view = "Tree";
					} else {
						item.doc_view = "List";
					}
				}
				switch (item.doc_view) {
					case "List":
						if (item.filters) {
							frappe.route_options = item.filters;
						}
						route = "List/" + item.doctype;
						break;
					case "Tree":
						route = "Tree/" + item.doctype;
						break;
					case "Report Builder":
						route = "List/" + item.doctype + "/Report";
						break;
					case "Dashboard":
						route = "List/" + item.doctype + "/Dashboard";
						break;
					case "New":
						route = "Form/" + item.doctype + "/New " + item.doctype;
						break;
					case "Calendar":
						route = "List/" + item.doctype + "/Calendar/Default";
						break;
					default:
						frappe.throw({ message: __("Not a valid DocType view:") + item.doc_view, title: __("Unknown View") });
						route = "";
				}
			}
		} else if (type === "report" && item.is_query_report) {
			route = "query-report/" + item.name;
		} else if (type === "report") {
			route = "List/" + item.doctype + "/Report/" + item.name;
		} else if (type === "page") {
			route = item.name;
		} else if (type === "dashboard") {
			route = "dashboard/" + item.name;
		}

		route = "#" + route;
	} else {
		route = item.route;
	}

	if (item.route_options) {
		route +=
			"?" +
			$.map(item.route_options, function (value, key) {
				return (
					encodeURIComponent(key) + "=" + encodeURIComponent(value)
				);
			}).join("&");
	}

	// if(type==="page" || type==="help" || type==="report" ||
	// (item.doctype && frappe.model.can_read(item.doctype))) {
	//     item.shown = true;
	// }
	return route;
}

function generate_grid(data) {
	function add(a, b) {
		return a + b;
	}

	const grid_max_cols = 6

	// Split the data into multiple arrays
	// Each array will contain grid elements of one row
	let processed = []
	let temp = []
	let init = 0
	data.forEach((data) => {
		init = init + data.columns;
		if (init > grid_max_cols) {
			init = data.columns
			processed.push(temp)
			temp = []
		}
		temp.push(data)
	})

	processed.push(temp)

	let grid_template = [];

	processed.forEach((data, index) => {
		let aa = data.map(dd => {
			return Array.apply(null, Array(dd.columns)).map(String.prototype.valueOf, dd.name)
		}).flat()

		if (aa.length < grid_max_cols) {
			let diff = grid_max_cols - aa.length;
			for (let ii = 0; ii < diff; ii++) {
				aa.push(`grid-${index}-${ii}`)
			}
		}

		grid_template.push(aa.join(" "))
	})
	let grid_template_area = ""

	grid_template.forEach(temp => {
		grid_template_area += `"${temp}" `
	})

	return grid_template_area
}

const build_summary_item = (summary) => {
	let df = { fieldtype: summary.datatype };
	let doc = null;

	if (summary.datatype == "Currency") {
		df.options = "currency";
		doc = { currency: summary.currency };
	}

	let value = frappe.format(summary.value, df, null, doc);
	let indicator = summary.indicator ? `indicator ${summary.indicator.toLowerCase()}` : '';

	return $(`<div class="summary-item">
		<span class="summary-label small text-muted ${indicator}">${summary.label}</span>
		<h1 class="summary-value">${ value}</h1>
	</div>`);
};

function shorten_number(number, country) {
	country = (country == 'India') ? country : '';
	const number_system = get_number_system(country);
	let x = Math.abs(Math.round(number));
	for (const map of number_system) {
		const condition = map.condition ? map.condition(x) : x >= map.divisor;
		if (condition) {
			return (number/map.divisor).toFixed(2) + ' ' + map.symbol;
		}
	}
	return number.toFixed(2);
}

function get_number_system(country) {
	let number_system_map = {
		'India':
			[{
				divisor: 1.0e+7,
				symbol: 'Cr'
			},
			{
				divisor: 1.0e+5,
				symbol: 'Lakh'
			}],
		'':
			[{
				divisor: 1.0e+12,
				symbol: 'T'
			},
			{
				divisor: 1.0e+9,
				symbol: 'B'
			},
			{
				divisor: 1.0e+6,
				symbol: 'M'
			},
			{
				divisor: 1.0e+3,
				symbol: 'K',
				condition: (num) => num.toFixed().length > 5
			}]
	};
	return number_system_map[country];
}

export { generate_route, generate_grid, build_summary_item, shorten_number };
