"""
Mirror Desktop Icon folder grouping onto Workspace.parent_page
so the avatar / Workspaces menu nests like Desktop home (see product screenshot).

Creates lightweight public parent Workspaces for folder groups when missing,
then assigns children from Desktop Icon parent_icon (and a small static map).
Orphans that live under Desktop "Other" get parent_page = "Other".
"""
from __future__ import annotations

import frappe

# Desktop folder label → list of Workspace titles that belong under it
STATIC_CHILDREN = {
	"Accounting": (
		"Invoicing",
		"Financial Reports",
		"Payments",
		"Taxes",
		"Banking",
		"Budget",
		"Accounts Setup",
		"Share Management",
		"Subscription",
	),
	"Sales & Procurement": ("Selling", "Buying"),
	"Inventory & Assets": ("Stock", "Assets"),
	"Other": (
		"Organization",
		"Projects",
		"Quality",
		"Subcontracting",
		"Support",
		"Home",
		"ERPNext Settings",
	),
	"Manufacturing": ("TITA Factory",),
}

PARENT_ICONS = {
	"Accounting": "accounting",
	"Sales & Procurement": "selling",
	"Inventory & Assets": "stock",
	"Other": "organization",
	"Manufacturing": "factory",
}


def run():
	created_parents = []
	assigned = []

	# Ensure parent shells exist
	for parent in STATIC_CHILDREN:
		if _ensure_parent_workspace(parent):
			created_parents.append(parent)

	# From Desktop Icon nesting (authoritative when present)
	desktop_map = _desktop_parent_map()
	for child, parent in desktop_map.items():
		if _set_parent(child, parent):
			assigned.append(f"{child}->{parent}")

	# Static fallbacks
	for parent, children in STATIC_CHILDREN.items():
		for child in children:
			if _set_parent(child, parent):
				assigned.append(f"{child}->{parent}")

	# Hide duplicate TITA Production from menu (Factory is the one link under Manufacturing)
	if frappe.db.exists("Workspace", "TITA Production"):
		frappe.db.set_value(
			"Workspace", "TITA Production", "is_hidden", 1, update_modified=False
		)

	frappe.db.commit()
	try:
		frappe.cache().delete_keys("workspace*")
		frappe.cache().delete_keys("boot*")
	except Exception:
		pass

	return {
		"ok": True,
		"created_parents": created_parents,
		"assigned": assigned[:40],
		"assigned_count": len(assigned),
	}


def _ensure_parent_workspace(title: str) -> bool:
	"""Create a public empty Workspace used only as a nest parent in the menu."""
	if frappe.db.exists("Workspace", title):
		# Keep visible as a folder parent
		frappe.db.set_value(
			"Workspace",
			title,
			{"public": 1, "is_hidden": 0, "parent_page": ""},
			update_modified=False,
		)
		return False

	doc = frappe.get_doc(
		{
			"doctype": "Workspace",
			"label": title,
			"title": title,
			"public": 1,
			"is_hidden": 0,
			"icon": PARENT_ICONS.get(title) or "folder",
			"content": "[]",
			"type": "Workspace",
		}
	)
	# Prefer a real module so insert validates
	if title == "Manufacturing" and frappe.db.exists("Module Def", "Manufacturing"):
		doc.module = "Manufacturing"
		doc.app = "erpnext"
	elif frappe.db.exists("Module Def", "Setup"):
		doc.module = "Setup"
		doc.app = "frappe"
	elif frappe.db.exists("Module Def", "Core"):
		doc.module = "Core"
		doc.app = "frappe"
	prev = getattr(frappe.flags, "in_import", False)
	frappe.flags.in_import = True
	try:
		doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
	finally:
		frappe.flags.in_import = prev
	return True


def _desktop_parent_map() -> dict[str, str]:
	"""Map child Desktop Icon link_to / label → parent_icon folder label."""
	out = {}
	if not frappe.db.table_exists("Desktop Icon"):
		return out
	rows = frappe.get_all(
		"Desktop Icon",
		filters={"hidden": 0},
		fields=["label", "parent_icon", "link_to", "icon_type"],
	)
	for r in rows:
		parent = (r.parent_icon or "").strip()
		if not parent or r.icon_type == "Folder":
			continue
		# Prefer Workspace name = link_to when Link to Workspace Sidebar / Workspace
		child = (r.link_to or r.label or "").strip()
		if child:
			out[child] = parent
		if r.label and r.label != child:
			out[r.label] = parent
	return out


def _set_parent(child: str, parent: str) -> bool:
	if not child or child == parent:
		return False
	if not frappe.db.exists("Workspace", child):
		return False
	if not frappe.db.exists("Workspace", parent):
		_ensure_parent_workspace(parent)
	cur = frappe.db.get_value("Workspace", child, "parent_page") or ""
	if cur == parent:
		return False
	# Don't reparent the Manufacturing core page under itself incorrectly
	if child == "Manufacturing" and parent != "":
		return False
	frappe.db.set_value("Workspace", child, "parent_page", parent, update_modified=False)
	return True
