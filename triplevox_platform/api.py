"""
API helpers for TripleVox SaaS features:
  - company switcher
  - branded login → session company
  - onboarding wizard
  - role packs
  - print pack
"""
from __future__ import annotations

import frappe
from frappe import _

from triplevox_platform.client_theme import (
	get_boot_payload,
	get_client_profile,
	get_company_profile_map,
	get_profile_catalog,
	get_session_company,
)


@frappe.whitelist()
def get_client_boot_payload():
	"""Return current user's company-resolved branding payload for Desk refresh."""
	return get_boot_payload(company=get_session_company())


@frappe.whitelist()
def list_switchable_companies():
	"""Companies available in the Desk company switcher."""
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw(_("Login required"))

	profile_map = get_company_profile_map()
	all_cos = []
	if frappe.db.exists("DocType", "Company"):
		all_cos = frappe.get_all("Company", pluck="name", order_by="name asc")

	names = []
	seen = set()

	def _add(name: str):
		if name and name not in seen and frappe.db.exists("Company", name):
			seen.add(name)
			names.append(name)

	# 1) Exact mapped names
	for company_name in profile_map.keys():
		_add(company_name)

	# 2) Fuzzy: Company name contains / starts with a mapped name or catalog full name
	catalog = get_profile_catalog()
	for co in all_cos:
		co_l = co.lower()
		for mapped_name in profile_map.keys():
			mn = str(mapped_name).lower()
			base = mn.split(" (")[0]
			if co_l == mn or co_l.startswith(base) or base in co_l:
				_add(co)
		for p in catalog.values():
			full = str(p.get("client_full_name") or "").lower()
			if full and (full in co_l or co_l.startswith(full.split(" (")[0])):
				_add(co)

	# 3) Fallback — every company on the site
	if not names:
		for co in all_cos[:40]:
			_add(co)

	active = get_session_company() or ""
	rows = []
	for name in names:
		profile = get_client_profile(company=name)
		rows.append(
			{
				"company": name,
				"client_key": profile.get("client_key"),
				"client_full_name": profile.get("client_full_name") or name,
				"factory_area": profile.get("factory_area") or "",
				"logo": profile.get("client_logo_url")
				or profile.get("print_logo_url")
				or profile.get("logo_url")
				or "",
				"accent": (profile.get("theme") or {}).get("green") or "#1e4d8c",
				"active": name == active,
			}
		)
	return {"active": active, "companies": rows}


@frappe.whitelist()
def set_session_company(company: str):
	"""Set current user's default Company and return refreshed boot payload."""
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw(_("Login required"))
	company = (company or "").strip()
	if not company:
		frappe.throw(_("Company is required"))
	if not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found").format(company))

	# Permission: System Manager may set any; others need Company permission / user permission
	is_admin = "System Manager" in frappe.get_roles() or user == "Administrator"
	if not is_admin:
		allowed = {c.get("company") for c in (list_switchable_companies().get("companies") or [])}
		if company not in allowed:
			# Still allow if user can read the Company
			try:
				frappe.has_permission("Company", "read", company, throw=True)
			except Exception:
				frappe.throw(_("Not permitted to switch to {0}").format(company))

	frappe.defaults.set_user_default("company", company, user)
	if frappe.db.exists("DocType", "Employee"):
		emps = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
		for emp in emps:
			frappe.db.set_value("Employee", emp, "company", company, update_modified=False)
	frappe.db.commit()

	payload = get_boot_payload(company=company)
	return {"ok": True, "company": company, "boot": payload}


@frappe.whitelist()
def apply_login_company_key(client_key: str | None = None):
	"""
	After login: map login picker key (tita/brg) → Company and set session default once.
	"""
	user = frappe.session.user
	if not user or user == "Guest":
		return {"ok": False, "reason": "guest"}

	key = (client_key or "").strip().lower()
	if not key:
		return {"ok": False, "reason": "no_key"}

	# Reverse map profile key → preferred company name
	company = None
	for company_name, profile_key in get_company_profile_map().items():
		if str(profile_key).lower() == key and frappe.db.exists("Company", company_name):
			company = company_name
			break
	if not company:
		# Fallback: catalog full name / linked company
		profile = get_profile_catalog().get(key) or {}
		guess = profile.get("_company") or profile.get("client_full_name")
		if guess and frappe.db.exists("Company", guess):
			company = guess
	if not company:
		return {"ok": False, "reason": "company_missing", "client_key": key}

	return set_session_company(company)


@frappe.whitelist()
def onboard_sister_company(
	company_name: str,
	abbr: str | None = None,
	profile_key: str | None = None,
	factory_area: str | None = None,
	logo_url: str | None = None,
	apply_prints: int = 1,
):
	"""
	Onboarding wizard API — create/update Company, map profile, optional print pack.
	System Manager only.
	"""
	frappe.only_for(("System Manager", "Administrator"))
	company_name = (company_name or "").strip()
	if not company_name:
		frappe.throw(_("Company name is required"))
	profile_key = (profile_key or "").strip().lower()
	catalog = get_profile_catalog()
	if not profile_key:
		# Prefer site default / first DB profile
		for k, p in catalog.items():
			if p.get("_is_site_default") and p.get("_from_db"):
				profile_key = k
				break
		if not profile_key:
			db_keys = [k for k, p in catalog.items() if p.get("_from_db")]
			profile_key = db_keys[0] if db_keys else ""
	if profile_key and profile_key not in catalog:
		frappe.throw(
			_("Unknown profile key: {0}. Create a Client Branding row first.").format(profile_key)
		)
	if not profile_key:
		frappe.throw(_("Create at least one Client Branding row before onboarding a company."))

	abbr = (abbr or "").strip().upper() or "".join([w[0] for w in company_name.split() if w])[:5]
	created = False
	if not frappe.db.exists("Company", company_name):
		# Clone currency/country from an existing mapped company when possible
		defaults = {}
		for existing in get_company_profile_map().keys():
			if frappe.db.exists("Company", existing):
				defaults = (
					frappe.db.get_value(
						"Company",
						existing,
						["default_currency", "country"],
						as_dict=True,
					)
					or {}
				)
				break
		doc = frappe.new_doc("Company")
		doc.company_name = company_name
		doc.abbr = abbr
		doc.default_currency = defaults.get("default_currency") or "ETB"
		doc.country = defaults.get("country") or "Ethiopia"
		doc.flags.ignore_permissions = True
		try:
			doc.insert(ignore_permissions=True)
			created = True
		except Exception as exc:
			frappe.db.rollback()
			frappe.throw(_("Could not create Company: {0}").format(exc))

	# Persist company → profile mapping in site_config
	mapping = dict(frappe.conf.get("triplevox_company_profiles") or {})
	mapping[company_name] = profile_key
	_update_site_config_key("triplevox_company_profiles", mapping)

	# Optional per-company theme overlay (factory area / logo)
	themes = dict(frappe.conf.get("triplevox_company_themes") or {})
	overlay = dict(themes.get(company_name) or {})
	if factory_area:
		overlay["factory_area"] = factory_area
	if logo_url:
		overlay["print_logo_url"] = logo_url
		overlay["client_logo_url"] = logo_url
	if overlay:
		themes[company_name] = overlay
		_update_site_config_key("triplevox_company_themes", themes)

	# Company logo field
	if logo_url:
		try:
			cols = set(frappe.db.get_table_columns("Company") or [])
			logo_field = "company_logo" if "company_logo" in cols else ("logo" if "logo" in cols else None)
			if logo_field:
				frappe.db.set_value("Company", company_name, logo_field, logo_url, update_modified=False)
		except Exception:
			frappe.log_error(title="Onboard company logo")

	print_result = None
	if int(apply_prints or 0):
		from triplevox_platform.print_pack import apply_print_pack

		print_result = apply_print_pack(company_name)

	frappe.db.commit()
	# Clear cache so next boot reads new site_config mapping
	frappe.clear_cache()

	return {
		"ok": True,
		"company": company_name,
		"abbr": abbr,
		"profile_key": profile_key,
		"created": created,
		"print_pack": print_result,
		"boot": get_boot_payload(company=company_name),
		"hint": _(
			"Switch to this company from the Desk company switcher. "
			"Hard-refresh (Ctrl+Shift+R) if theme looks stale."
		),
	}


@frappe.whitelist()
def list_branding_profiles():
	"""Enabled Client Branding keys for onboarding wizard / Desk tools."""
	rows = []
	for key, p in get_profile_catalog().items():
		if not p.get("_from_db") and key == "default":
			continue
		rows.append(
			{
				"key": key,
				"client_full_name": p.get("client_full_name") or key,
				"company": p.get("_company") or "",
				"is_site_default": bool(p.get("_is_site_default")),
			}
		)
	return {"profiles": rows}


@frappe.whitelist()
def list_role_packs():
	from triplevox_platform.role_packs import list_packs

	return {"packs": list_packs()}


@frappe.whitelist()
def assign_role_pack(user: str, pack_key: str):
	from triplevox_platform.role_packs import assign_pack

	return assign_pack(user, pack_key)


@frappe.whitelist()
def apply_company_print_pack(company: str | None = None):
	from triplevox_platform.print_pack import apply_print_pack

	company = (company or get_session_company() or "").strip()
	return apply_print_pack(company)


@frappe.whitelist()
def apply_client_branding_now(client_key: str | None = None):
	"""Reload Desk boot payload after Client Branding save (Administrator)."""
	frappe.only_for(("System Manager", "Administrator"))
	try:
		from triplevox_platform.setup import apply_branding_settings

		apply_branding_settings()
	except Exception:
		frappe.log_error(title="apply_client_branding_now branding")
	company = None
	key = (client_key or "").strip().lower()
	if key:
		for co, mapped in get_company_profile_map().items():
			if mapped == key:
				company = co
				break
	frappe.clear_cache()
	return get_boot_payload(company=company or get_session_company())


@frappe.whitelist()
def branding_onboarding_status():
	"""Whether Administrator must complete Client Branding onboarding."""
	from triplevox_platform.branding_setup import needs_onboarding

	return {
		"needs_onboarding": bool(needs_onboarding()),
		"is_admin": frappe.session.user == "Administrator"
		or "System Manager" in frappe.get_roles(),
	}


def _update_site_config_key(key: str, value):
	"""Write a key into site_config.json via frappe helpers."""
	try:
		from frappe.installer import update_site_config

		update_site_config(key, value)
	except Exception:
		# Fallback: conf dict for this process (survive until restart)
		frappe.conf[key] = value
		frappe.log_error(title=f"update_site_config failed for {key}")
