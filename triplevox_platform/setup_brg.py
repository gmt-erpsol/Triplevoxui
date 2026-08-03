"""
OPTIONAL ops helper — not part of the reusable parent-app core.

Ensure sister Company BRG Trading PLC exists and is mapped for UI branding.
Prefer creating Company + Client Branding in Desk for new client sites.

Run:
  bench --site SITE execute triplevox_platform.setup_brg.ensure_brg_company

Optional: set a user's default company:
  bench --site SITE execute triplevox_platform.setup_brg.set_user_company --kwargs "{'user':'user@example.com','company':'BRG Trading PLC'}"
"""
from __future__ import annotations

import frappe

BRG_COMPANY = "BRG Trading PLC"
BRG_ABBR = "BRG"
TITA_COMPANY = "TITA PP Plastic PLC"


def ensure_brg_company():
	"""Create BRG Trading PLC Company if missing; attach logo path note."""
	if not frappe.db.exists("DocType", "Company"):
		return {"ok": False, "reason": "Company DocType missing"}

	created = False
	if not frappe.db.exists("Company", BRG_COMPANY):
		# Prefer cloning currency/country from TITA when present
		defaults = {}
		if frappe.db.exists("Company", TITA_COMPANY):
			row = frappe.db.get_value(
				"Company",
				TITA_COMPANY,
				["default_currency", "country", "chart_of_accounts"],
				as_dict=True,
			) or {}
			defaults = row

		doc = frappe.new_doc("Company")
		doc.company_name = BRG_COMPANY
		doc.abbr = BRG_ABBR
		doc.default_currency = defaults.get("default_currency") or "ETB"
		doc.country = defaults.get("country") or "Ethiopia"
		# Minimal create — avoid full CoA wizard when possible
		try:
			if defaults.get("chart_of_accounts"):
				doc.chart_of_accounts = defaults["chart_of_accounts"]
		except Exception:
			pass
		doc.flags.ignore_permissions = True
		try:
			doc.insert(ignore_permissions=True)
			created = True
			frappe.db.commit()
		except Exception as exc:
			frappe.db.rollback()
			return {
				"ok": False,
				"reason": f"Could not create Company automatically: {exc}",
				"manual": f"Create Company named exactly '{BRG_COMPANY}' in Desk, then re-run.",
			}

	# Best-effort: set company logo field to BRG asset if empty
	try:
		cols = set(frappe.db.get_table_columns("Company") or [])
		logo_field = "company_logo" if "company_logo" in cols else ("logo" if "logo" in cols else None)
		if logo_field:
			current = frappe.db.get_value("Company", BRG_COMPANY, logo_field)
			if not current:
				frappe.db.set_value(
					"Company",
					BRG_COMPANY,
					logo_field,
					"/assets/triplevox_platform/images/brg-logo.png",
					update_modified=False,
				)
				frappe.db.commit()
	except Exception:
		frappe.log_error(title="BRG company logo attach failed")

	return {
		"ok": True,
		"company": BRG_COMPANY,
		"created": created,
		"profile_map": {
			TITA_COMPANY: "tita",
			BRG_COMPANY: "brg",
		},
		"hint": (
			"Set User default Company or Employee.company to "
			f"'{BRG_COMPANY}' for BRG chrome. Profile map is built into "
			"client_theme.DEFAULT_COMPANY_PROFILES; override via site_config "
			"triplevox_company_profiles if needed."
		),
	}


def set_user_company(user: str, company: str = BRG_COMPANY):
	"""Set Defaults for a user so Desk branding follows that company."""
	if not frappe.db.exists("User", user):
		return {"ok": False, "reason": f"User {user} not found"}
	if not frappe.db.exists("Company", company):
		return {"ok": False, "reason": f"Company {company} not found — run ensure_brg_company first"}

	frappe.defaults.set_user_default("company", company, user)
	# Also update Employee if linked
	if frappe.db.exists("DocType", "Employee"):
		emps = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
		for emp in emps:
			frappe.db.set_value("Employee", emp, "company", company, update_modified=False)
	frappe.db.commit()
	return {"ok": True, "user": user, "company": company}
