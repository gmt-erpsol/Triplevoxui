"""Ensure Company & SaaS desktop icon under System Administration (not sidebar)."""
from __future__ import annotations

import frappe

WORKSPACE = "Company & SaaS"
ICON_URL = "/assets/triplevox_platform/images/module_icons/tabler/building-community.svg"


def run():
	"""Create workspace + desktop icon; strip leftover Navbar / sidebar menu items."""
	_ensure_workspace()
	_ensure_desktop_icon()
	_remove_navbar_saas_item()
	frappe.db.commit()
	return {"workspace": WORKSPACE, "desktop_icon": WORKSPACE}


def _ensure_workspace():
	if frappe.db.exists("Workspace", WORKSPACE):
		return
	prev = getattr(frappe.flags, "in_import", False)
	frappe.flags.in_import = True
	try:
		module = "TVX" if frappe.db.exists("Module Def", "TVX") else None
		doc = frappe.get_doc(
			{
				"doctype": "Workspace",
				"label": WORKSPACE,
				"title": WORKSPACE,
				"type": "Workspace",
				"public": 1,
				"icon": "building",
				"content": frappe.as_json(
					[
						{"type": "header", "data": {"text": "Company &amp; SaaS", "col": 12}},
						{
							"type": "paragraph",
							"data": {
								"text": "Switch companies, onboard sister companies, and manage Client Branding for this site.",
								"col": 12,
							},
						},
					]
				),
				"shortcuts": [
					{
						"type": "DocType",
						"link_to": "Client Branding",
						"label": "Client Branding",
					},
					{"type": "DocType", "link_to": "Company", "label": "Company"},
				],
			}
		)
		if module:
			doc.module = module
		doc.insert(ignore_permissions=True)
	finally:
		frappe.flags.in_import = prev


def _ensure_desktop_icon():
	parent = (
		"System Administration"
		if frappe.db.exists("Desktop Icon", "System Administration")
		else ""
	)
	prev = getattr(frappe.flags, "in_import", False)
	frappe.flags.in_import = True
	try:
		if not frappe.db.exists("Workspace Sidebar", WORKSPACE):
			sb = frappe.get_doc(
				{
					"doctype": "Workspace Sidebar",
					"title": WORKSPACE,
					"header_icon": "building",
					"app": "triplevox_platform",
					"standard": 0,
					"items": [
						{
							"label": "Home",
							"type": "Link",
							"link_type": "Workspace",
							"link_to": WORKSPACE,
							"icon": "house",
						},
						{
							"label": "Client Branding",
							"type": "Link",
							"link_type": "DocType",
							"link_to": "Client Branding",
							"icon": "palette",
						},
						{
							"label": "Company",
							"type": "Link",
							"link_type": "DocType",
							"link_to": "Company",
							"icon": "building",
						},
					],
				}
			)
			sb.insert(ignore_permissions=True)

		vals = {
			"icon_type": "Link",
			"link_type": "Workspace Sidebar",
			"link_to": WORKSPACE,
			"sidebar": WORKSPACE,
			"parent_icon": parent,
			"hidden": 0,
			"logo_url": ICON_URL,
			"app": "triplevox_platform",
			"idx": 20,
			"bg_color": "blue",
		}
		if frappe.db.exists("Desktop Icon", WORKSPACE):
			frappe.db.set_value("Desktop Icon", WORKSPACE, vals, update_modified=False)
		else:
			frappe.get_doc(
				{"doctype": "Desktop Icon", "label": WORKSPACE, "restrict_removal": 0, **vals}
			).insert(ignore_permissions=True)
	finally:
		frappe.flags.in_import = prev


def _remove_navbar_saas_item():
	try:
		ns = frappe.get_single("Navbar Settings")
		if not ns.meta.get_field("settings_dropdown"):
			return
		keep = []
		changed = False
		for row in list(ns.settings_dropdown or []):
			item = (
				getattr(row, "item_label", None) or getattr(row, "label", None) or ""
			).strip().lower()
			if "company & saas" in item:
				changed = True
				continue
			keep.append(row)
		if changed:
			ns.set("settings_dropdown", [])
			for row in keep:
				ns.append("settings_dropdown", row.as_dict())
			prev = getattr(frappe.flags, "in_import", False)
			frappe.flags.in_import = True
			try:
				ns.save(ignore_permissions=True)
			finally:
				frappe.flags.in_import = prev
	except Exception:
		frappe.log_error(title="Remove Company & SaaS navbar item")
