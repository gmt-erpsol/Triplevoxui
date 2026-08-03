"""
Print pack — ensure Letter Head + company logo for a sister company.
Works with print_branding.py Jinja formats (doc company → logo).
"""
from __future__ import annotations

import frappe

from triplevox_platform.client_theme import (
	get_boot_payload,
	get_client_profile,
	get_company_profile_map,
)


def apply_print_pack(company: str | None = None) -> dict:
	"""
	Create/update Letter Head for company, attach logo, set Company defaults.
	Safe to re-run.
	"""
	frappe.only_for(("System Manager", "Administrator"))
	company = (company or "").strip()
	if not company:
		frappe.throw("Company is required")
	if not frappe.db.exists("Company", company):
		frappe.throw(f"Company not found: {company}")

	profile = get_client_profile(company=company)
	logo = (
		profile.get("print_logo_url")
		or profile.get("client_logo_url")
		or ""
	)
	# Prefer existing Company logo field if set
	try:
		cols = set(frappe.db.get_table_columns("Company") or [])
		logo_field = "company_logo" if "company_logo" in cols else ("logo" if "logo" in cols else None)
		if logo_field:
			existing = frappe.db.get_value("Company", company, logo_field)
			if existing:
				logo = existing
			elif logo:
				frappe.db.set_value("Company", company, logo_field, logo, update_modified=False)
	except Exception:
		frappe.log_error(title="Print pack company logo")

	lh_name = f"{company} Letter Head"
	created_lh = False
	if frappe.db.exists("DocType", "Letter Head"):
		if frappe.db.exists("Letter Head", lh_name):
			lh = frappe.get_doc("Letter Head", lh_name)
		else:
			lh = frappe.new_doc("Letter Head")
			lh.letter_head_name = lh_name
			created_lh = True
		lh.is_default = 0
		lh.disabled = 0
		if hasattr(lh, "company"):
			try:
				lh.company = company
			except Exception:
				pass
		if logo:
			lh.image = logo
			# Minimal HTML header so Letter Head is not empty
			lh.content = (
				f'<div style="text-align:left">'
				f'<img src="{frappe.utils.escape_html(logo)}" style="max-height:64px"/>'
				f"<div><strong>{frappe.utils.escape_html(company)}</strong></div>"
				f"</div>"
			)
		else:
			lh.content = f"<div><strong>{frappe.utils.escape_html(company)}</strong></div>"
		lh.flags.ignore_permissions = True
		if created_lh:
			lh.insert(ignore_permissions=True)
		else:
			lh.save(ignore_permissions=True)

		# Link as company default letter head when field exists
		try:
			cols = set(frappe.db.get_table_columns("Company") or [])
			if "default_letter_head" in cols:
				frappe.db.set_value(
					"Company",
					company,
					"default_letter_head",
					lh_name,
					update_modified=False,
				)
		except Exception:
			frappe.log_error(title="Print pack default_letter_head")

	# Refresh TripleVox print style/formats (idempotent)
	try:
		from triplevox_platform.print_branding import run as print_run

		print_run()
	except Exception:
		frappe.log_error(title="Print pack print_branding.run")

	frappe.db.commit()
	return {
		"ok": True,
		"company": company,
		"letter_head": lh_name if frappe.db.exists("DocType", "Letter Head") else None,
		"logo": logo,
		"client_key": profile.get("client_key"),
		"boot": get_boot_payload(company=company),
		"mapped_profiles": get_company_profile_map(),
	}
