"""Inspect why Manufacturing may not appear on Desk home."""
from __future__ import annotations

import frappe


def manufacturing_visibility_report():
	label = "Manufacturing"
	out = {"label": label, "exists": False}
	if not frappe.db.exists("Desktop Icon", label):
		# fall back to legacy name for diagnosis
		if frappe.db.exists("Desktop Icon", "Manufacturing Workspace"):
			label = "Manufacturing Workspace"
			out["legacy_label"] = label
		else:
			return out

	doc = frappe.get_doc("Desktop Icon", label)
	out.update(
		{
			"exists": True,
			"name": doc.name,
			"hidden": int(doc.hidden or 0),
			"parent_icon": doc.parent_icon or "",
			"icon_type": doc.icon_type,
			"link_type": doc.link_type,
			"link_to": doc.link_to,
			"app": doc.app,
			"idx": doc.idx,
			"roles": [r.role for r in (doc.roles or [])],
			"standard": getattr(doc, "standard", None),
		}
	)

	# Frappe get_desktop_icons looks up sidebar by icon.label.lower()
	sidebar_key = (doc.label or "").lower()
	sidebar = frappe.db.exists("Workspace Sidebar", doc.label) or frappe.db.exists(
		"Workspace Sidebar", doc.link_to
	)
	out["sidebar_lookup_key"] = sidebar_key
	out["sidebar_exists_for_label"] = bool(frappe.db.exists("Workspace Sidebar", doc.label))
	out["sidebar_exists_for_link_to"] = bool(
		doc.link_to and frappe.db.exists("Workspace Sidebar", doc.link_to)
	)
	out["frappe_boot_would_permit"] = bool(
		out["sidebar_exists_for_label"] and not out["hidden"] and doc.icon_type == "Link"
	)
	out["sidebar_row"] = sidebar

	user = frappe.session.user
	roles = frappe.get_roles(user)
	icon_roles = out["roles"]
	out["visible_to_session_user"] = (
		bool(set(icon_roles) & set(roles)) if icon_roles else True
	)
	out["session_user"] = user

	# Simulate boot-filtered icons
	try:
		from frappe.desk.doctype.desktop_icon.desktop_icon import (
			clear_desktop_icons_cache,
			get_desktop_icons,
		)

		clear_desktop_icons_cache(user)
		# Minimal bootinfo with workspace_sidebar_item like sessions.get
		bootinfo = frappe._dict(workspace_sidebar_item={})
		for name in frappe.get_all("Workspace Sidebar", pluck="name"):
			items = frappe.get_all(
				"Workspace Sidebar Item",
				filters={"parent": name},
				fields=["name", "type", "link_to"],
				limit=5,
			)
			bootinfo.workspace_sidebar_item[name.lower()] = {"items": items}
		icons = get_desktop_icons(user=user, bootinfo=bootinfo)
		top = [
			i
			for i in icons
			if not i.get("hidden") and not (i.get("parent_icon") or "").strip()
		]
		out["boot_top_level"] = [i.get("label") for i in top]
		out["boot_has_manufacturing"] = any(
			(i.get("label") or "") == "Manufacturing" for i in top
		)
	except Exception as e:
		out["boot_sim_error"] = str(e)

	out["top_level_visible"] = frappe.db.sql(
		"""
		SELECT name, label, icon_type, app, idx, IFNULL(parent_icon,'') as parent_icon,
		       IFNULL(hidden,0) as hidden
		FROM `tabDesktop Icon`
		WHERE IFNULL(hidden,0)=0 AND IFNULL(parent_icon,'')=''
		ORDER BY idx, label
		""",
		as_dict=True,
	)
	return out
