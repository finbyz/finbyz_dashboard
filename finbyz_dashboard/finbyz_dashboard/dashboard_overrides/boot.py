# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six import iteritems, text_type

"""
bootstrap client session
"""

import frappe
import frappe.defaults
import frappe.desk.desk_page
from frappe.desk.form.load import get_meta_bundle
from frappe.utils.change_log import get_versions
from frappe.translate import get_lang_dict
from frappe.email.inbox import get_email_accounts
from frappe.social.doctype.energy_point_settings.energy_point_settings import is_energy_point_enabled
from frappe.social.doctype.energy_point_log.energy_point_log import get_energy_points
from frappe.social.doctype.post.post import frequently_visited_links
from frappe.boot import get_user, load_desktop_icons, get_fullnames, get_letter_heads, add_home_page, load_translations, \
		add_timezone_info, load_conf_settings, load_print, get_success_action, get_link_preview_doctypes, get_allowed_pages

def get_bootinfo_override():
	"""build and return boot info"""
	frappe.set_user_lang(frappe.session.user)
	bootinfo = frappe._dict()
	hooks = frappe.get_hooks()
	doclist = []

	# user
	get_user(bootinfo)

	# system info
	bootinfo.sitename = frappe.local.site
	bootinfo.sysdefaults = frappe.defaults.get_defaults()
	bootinfo.server_date = frappe.utils.nowdate()

	if frappe.session['user'] != 'Guest':
		bootinfo.user_info = get_fullnames()
		bootinfo.sid = frappe.session['sid']

	bootinfo.modules = {}
	bootinfo.module_list = []
	load_desktop_icons(bootinfo)
	bootinfo.letter_heads = get_letter_heads()
	bootinfo.active_domains = frappe.get_active_domains()
	bootinfo.all_domains = [d.get("name") for d in frappe.get_all("Domain")]

	bootinfo.module_app = frappe.local.module_app
	bootinfo.single_types = [d.name for d in frappe.get_all('DocType', {'issingle': 1})]
	bootinfo.nested_set_doctypes = [d.parent for d in frappe.get_all('DocField', {'fieldname': 'lft'}, ['parent'])]
	add_home_page(bootinfo, doclist)
	bootinfo.page_info = get_allowed_pages()
	load_translations(bootinfo)
	add_timezone_info(bootinfo)
	load_conf_settings(bootinfo)
	load_print(bootinfo, doclist)
	doclist.extend(get_meta_bundle("Page"))
	bootinfo.home_folder = frappe.db.get_value("File", {"is_home_folder": 1})

	# ipinfo
	if frappe.session.data.get('ipinfo'):
		bootinfo.ipinfo = frappe.session['data']['ipinfo']

	# add docs
	bootinfo.docs = doclist

	for method in hooks.boot_session or []:
		frappe.get_attr(method)(bootinfo)

	if bootinfo.lang:
		bootinfo.lang = text_type(bootinfo.lang)
	bootinfo.versions = {k: v['version'] for k, v in get_versions().items()}

	bootinfo.error_report_email = frappe.conf.error_report_email
	bootinfo.calendars = sorted(frappe.get_hooks("calendars"))
	bootinfo.treeviews = frappe.get_hooks("treeviews") or []
	bootinfo.lang_dict = get_lang_dict()
	bootinfo.success_action = get_success_action()
	bootinfo.update(get_email_accounts(user=frappe.session.user))
	bootinfo.energy_points_enabled = is_energy_point_enabled()
	bootinfo.points = get_energy_points(frappe.session.user)
	bootinfo.frequently_visited_links = frequently_visited_links()
	bootinfo.link_preview_doctypes = get_link_preview_doctypes()
	# Finbyz Changes:
	bootinfo.additional_filters_config = get_additional_filters_from_hooks()

	return bootinfo

def get_additional_filters_from_hooks():
	filter_config = frappe._dict()
	filter_hooks = frappe.get_hooks('filters_config')
	for hook in filter_hooks:
		filter_config.update(frappe.get_attr(hook)())

	return filter_config