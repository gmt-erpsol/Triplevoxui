"""
TITA/TripleVox file identification
App: triplevox_platform
File: workspace_viewer.py
Purpose: Workspace Viewer role — open & use workspaces, never edit layout.
"""
from __future__ import annotations

import frappe

ROLE = "Workspace Viewer"

# Roles that may still edit workspace layout even if they also have Viewer
EDITOR_ROLES = ("System Manager", "Administrator", "Workspace Manager")

WORKSPACE_DOCTYPES = ("Workspace", "Workspace Sidebar", "Workspace Sidebar Item")


def run():
	"""after_migrate / setup entry — create role + read-only perms."""
	ensure_role()
	ensure_readonly_permissions()
	frappe.db.commit()
	frappe.clear_cache()
	return {"role": ROLE, "status": "ok"}


def ensure_role():
	if frappe.db.exists("Role", ROLE):
		doc = frappe.get_doc("Role", ROLE)
		changed = False
		if doc.desk_access != 1:
			doc.desk_access = 1
			changed = True
		if getattr(doc, "disabled", 0):
			doc.disabled = 0
			changed = True
		# Frappe Role may not have a description field on all versions
		if hasattr(doc, "description"):
			wanted = _role_description()
			if (doc.description or "") != wanted:
				doc.description = wanted
				changed = True
		if changed:
			doc.save(ignore_permissions=True)
		return ROLE

	payload = {
		"doctype": "Role",
		"role_name": ROLE,
		"desk_access": 1,
		"is_custom": 1,
	}
	# Only set description when the DocType supports it
	meta = frappe.get_meta("Role")
	if meta.has_field("description"):
		payload["description"] = _role_description()
	frappe.get_doc(payload).insert(ignore_permissions=True)
	return ROLE


def _role_description():
	return (
		"Can open and use Desk workspaces allowed by their other roles "
		"(Employee Hub, Manufacturing, etc.). Cannot create, edit, or delete "
		"workspace layouts or sidebars."
	)


def ensure_readonly_permissions():
	"""Grant read-only Custom DocPerm on Workspace doctypes for Viewer."""
	if not frappe.db.exists("Role", ROLE):
		return

	for dt in WORKSPACE_DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			continue
		_upsert_readonly_perm(dt)


def _upsert_readonly_perm(dt):
	existing = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": dt, "role": ROLE, "permlevel": 0},
		"name",
	)
	# Use real DB columns — meta.has_field can lie for virtual/legacy perm flags
	cols = set(frappe.db.get_table_columns("Custom DocPerm") or [])
	wanted = {
		"read": 1,
		"write": 0,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"amend": 0,
		"report": 1,
		"export": 0,
		"import": 0,
		"share": 0,
		"print": 1,
		"email": 0,
		"set_user_permissions": 0,
	}
	vals = {k: v for k, v in wanted.items() if k in cols}
	if existing:
		frappe.db.set_value("Custom DocPerm", existing, vals, update_modified=False)
		return existing

	# If a standard DocPerm already exists for this role, don't duplicate
	if frappe.db.exists("DocPerm", {"parent": dt, "role": ROLE, "permlevel": 0}):
		return None

	doc = frappe.get_doc(
		{
			"doctype": "Custom DocPerm",
			"parent": dt,
			"parenttype": "DocType",
			"parentfield": "permissions",
			"role": ROLE,
			"permlevel": 0,
			**vals,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def user_is_workspace_viewer(user=None):
	"""True when user has Workspace Viewer and is not a workspace editor."""
	user = user or frappe.session.user
	if not user or user in ("Guest",):
		return False
	roles = set(frappe.get_roles(user))
	if ROLE not in roles:
		return False
	if roles.intersection(EDITOR_ROLES):
		return False
	return True


def user_can_edit_workspaces(user=None):
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if roles.intersection(EDITOR_ROLES):
		return True
	# Explicit viewer lock
	if ROLE in roles:
		return False
	return "Workspace Manager" in roles


def apply_boot_workspace_flags(bootinfo):
	"""
	Force view-only workspace flags for Workspace Viewer.
	Frappe sets has_access from Workspace Manager — we tighten for Viewer.
	"""
	if not user_is_workspace_viewer():
		# Still expose flag so Desk JS knows editors
		tvx = bootinfo.get("triplevox")
		if not isinstance(tvx, dict):
			tvx = {}
			bootinfo.triplevox = tvx
		tvx.setdefault("workspace_viewer", False)
		tvx.setdefault("can_edit_workspaces", user_can_edit_workspaces())
		return

	workspaces = bootinfo.get("workspaces")
	if isinstance(workspaces, dict):
		workspaces["has_access"] = False
		workspaces["has_create_access"] = False
		for page in workspaces.get("pages") or []:
			if isinstance(page, dict):
				# Private pages are editable by default in Frappe — lock them too
				page["is_editable"] = False

	tvx = bootinfo.get("triplevox")
	if not isinstance(tvx, dict):
		tvx = {}
		bootinfo.triplevox = tvx
	tvx["workspace_viewer"] = True
	tvx["can_edit_workspaces"] = False


def get_workspaces():
	"""
	Override frappe.desk.desktop.get_workspaces for Workspace Viewer.
	Keeps view/use access; never returns edit/create flags.
	Import the module function (not via whitelist) to avoid recursion.
	"""
	import frappe.desk.desktop as desk_desktop

	data = desk_desktop.get_workspaces()
	if not user_is_workspace_viewer():
		return data
	if isinstance(data, dict):
		data["has_access"] = False
		data["has_create_access"] = False
		for page in data.get("pages") or []:
			if isinstance(page, dict):
				page["is_editable"] = False
	elif isinstance(data, list):
		for page in data:
			if isinstance(page, dict):
				page["is_editable"] = False
	return data


def workspace_has_permission(doc, ptype="read", user=None):
	"""
	has_permission hook for Workspace / Workspace Sidebar.
	Viewer: allow read; deny write/create/delete/submit/cancel/amend.
	"""
	if not user_is_workspace_viewer(user):
		return None  # fall through to default

	ptype = (ptype or "read").lower()
	if ptype in ("read", "print", "email", "report", "select"):
		return True
	if ptype in ("write", "create", "delete", "submit", "cancel", "amend", "share", "import"):
		return False
	return None


def block_workspace_write(doc, method=None):
	"""doc_events: refuse save/delete for Workspace Viewer."""
	if frappe.flags.in_migrate or frappe.flags.in_install or frappe.flags.in_patch:
		return
	if frappe.session.user in ("Administrator",):
		# Administrator always allowed (also in EDITOR_ROLES, but belt-and-suspenders)
		if "Administrator" in frappe.get_roles():
			return
	if not user_is_workspace_viewer():
		return
	frappe.throw(
		(
			"Your role <b>Workspace Viewer</b> can open and use workspaces, "
			"but cannot create or edit workspace layouts. "
			"Ask a System Manager if a change is needed."
		),
		frappe.PermissionError,
		title="View only",
	)


def inspect():
	"""bench --site tita.local execute triplevox_platform.workspace_viewer.inspect"""
	return {
		"role_exists": bool(frappe.db.exists("Role", ROLE)),
		"users": frappe.db.count("Has Role", {"role": ROLE, "parenttype": "User"}),
		"custom_perms": frappe.get_all(
			"Custom DocPerm",
			filters={"role": ROLE},
			fields=["parent", "read", "write", "create", "delete"],
		),
	}
