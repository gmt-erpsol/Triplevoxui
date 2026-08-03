"""
TripleVox role packs — quick assignable Desk roles for multi-factory SaaS.

Packs (created on migrate):
  - Workspace Viewer (existing module)
  - TripleVox Shop Floor
  - TripleVox QC
  - TripleVox Ops Admin
"""
from __future__ import annotations

import frappe

PACKS = {
	"shop_floor": {
		"role": "TripleVox Shop Floor",
		"label": "Shop Floor",
		"description": (
			"Operators: open Desk, use manufacturing / stock workspaces and documents "
			"allowed by other roles. Prefer pairing with Workspace Viewer so layouts stay read-only."
		),
	},
	"qc": {
		"role": "TripleVox QC",
		"label": "Quality Control",
		"description": (
			"QC staff: Desk access for quality / inspection workflows. "
			"Pair with Workspace Viewer for read-only workspace layouts."
		),
	},
	"ops_admin": {
		"role": "TripleVox Ops Admin",
		"label": "Ops Admin",
		"description": (
			"Factory admins: Desk access for day-to-day operations setup. "
			"Does not replace System Manager — use for site champions, not full ERP admin."
		),
	},
	"viewer": {
		"role": "Workspace Viewer",
		"label": "Workspace Viewer",
		"description": "Open workspaces; cannot edit workspace layouts.",
	},
}


def run():
	"""after_migrate — ensure pack roles exist."""
	created = []
	for key, meta in PACKS.items():
		if key == "viewer":
			try:
				from triplevox_platform.workspace_viewer import ensure_role

				ensure_role()
			except Exception:
				frappe.log_error(title="Workspace Viewer role ensure")
			created.append(meta["role"])
			continue
		created.append(_ensure_role(meta["role"], meta["description"]))
	frappe.db.commit()
	return {"ok": True, "roles": created}


def _ensure_role(role_name: str, description: str) -> str:
	if frappe.db.exists("Role", role_name):
		doc = frappe.get_doc("Role", role_name)
		changed = False
		if doc.desk_access != 1:
			doc.desk_access = 1
			changed = True
		if getattr(doc, "disabled", 0):
			doc.disabled = 0
			changed = True
		meta = frappe.get_meta("Role")
		if meta.has_field("description") and (doc.description or "") != description:
			doc.description = description
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
		return role_name

	payload = {
		"doctype": "Role",
		"role_name": role_name,
		"desk_access": 1,
		"is_custom": 1,
	}
	meta = frappe.get_meta("Role")
	if meta.has_field("description"):
		payload["description"] = description
	frappe.get_doc(payload).insert(ignore_permissions=True)
	return role_name


def list_packs() -> list[dict]:
	out = []
	for key, meta in PACKS.items():
		out.append(
			{
				"key": key,
				"role": meta["role"],
				"label": meta["label"],
				"description": meta["description"],
				"exists": bool(frappe.db.exists("Role", meta["role"])),
			}
		)
	return out


def assign_pack(user: str, pack_key: str) -> dict:
	"""Assign a pack role to a user (System Manager)."""
	frappe.only_for(("System Manager", "Administrator"))
	meta = PACKS.get(str(pack_key or "").strip().lower())
	if not meta:
		frappe.throw(f"Unknown role pack: {pack_key}")
	if not frappe.db.exists("User", user):
		frappe.throw(f"User not found: {user}")

	role = meta["role"]
	if pack_key == "viewer":
		from triplevox_platform.workspace_viewer import ensure_role

		ensure_role()
	else:
		_ensure_role(role, meta["description"])

	user_doc = frappe.get_doc("User", user)
	existing = {r.role for r in (user_doc.roles or [])}
	if role not in existing:
		user_doc.append("roles", {"role": role})
		user_doc.save(ignore_permissions=True)
		frappe.db.commit()
		return {"ok": True, "user": user, "role": role, "added": True}
	return {"ok": True, "user": user, "role": role, "added": False}
