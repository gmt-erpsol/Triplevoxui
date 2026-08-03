"""
Client theme profiles for multi-tenant / multi-client deployments.

Branding lives in the Client Branding DocType (site DB) + optional site_config:
  - triplevox_client: default client_key
  - triplevox_company_profiles: { "Company Name": "client_key" }
  - triplevox_theme: shallow/deep overrides on the active profile

Product shell defaults (_BASE) are TripleVox-only — no client names in code.
"""
from __future__ import annotations

from copy import deepcopy

import frappe
from frappe.utils import now_datetime

# Deprecated empty aliases — kept so older imports do not crash
ACTIVE_CLIENT = "default"
DEFAULT_COMPANY_PROFILES: dict = {}
CLIENTS: dict = {}

# Shared TripleVox product shell (same across all client sites)
_BASE = {
	"client_key": "default",
	"client_full_name": "TripleVox ERP",
	"product_name": "TripleVox ERP",
	"sidebar_title": "TripleVox ERP",
	"partner_name": "TripleVox Engineering PLC",
	"logo_url": "/assets/triplevox_platform/images/triplevox-logo.png",
	"default_app": "",
	"apps_title": "Operations",
	"hub_route": "",
	"hub_subtitle": "",
	"hub_icon": "Generic",
	"hub_icon_image": "",
	"spotlight_tags": "",
	"software_company_name": "",
	"navbar_logo_url": "",
	"product_logo_url": "/assets/triplevox_platform/images/triplevox-logo.png",
	"factory_area": "",
	"welcome_kicker": "Operations Desk",
	"client_logo_url": "",
	"print_logo_url": "",
	"watermark_url": "/assets/triplevox_platform/images/triplevox-watermark.png",
	"watermark_dark_url": "/assets/triplevox_platform/images/triplevox-watermark-dark.png",
	"theme": {
		"sidebar": "#f8fafc",
		"sidebar_2": "#f1f5f9",
		"green": "#15803d",
		"green_bright": "#16a34a",
		"green_soft": "#dcfce7",
		"ink": "#0f172a",
		"muted": "#64748b",
		"border": "#e2e8f0",
		"surface": "#ffffff",
		"page": "#ffffff",
		"radius": "14px",
	},
}


def _neutral_shell_profile() -> dict:
	"""In-memory fallback when no Client Branding rows exist yet."""
	p = deepcopy(_BASE)
	p["client_key"] = "default"
	return p


def _db_branding_enabled() -> bool:
	try:
		return bool(frappe.db.exists("DocType", "Client Branding"))
	except Exception:
		return False


def _load_db_profiles() -> dict:
	"""client_key → profile dict from Client Branding DocType."""
	if not _db_branding_enabled():
		return {}
	out = {}
	try:
		fields = [
			"name",
			"client_key",
			"client_full_name",
			"company",
			"factory_area",
			"welcome_kicker",
			"apps_title",
			"product_name",
			"partner_name",
			"sidebar_title",
			"client_logo_source",
			"client_logo_image",
			"client_logo",
			"print_logo_source",
			"print_logo_image",
			"print_logo",
			"accent_color",
			"accent_bright",
			"accent_soft",
			"sidebar_color",
			"sidebar_color_2",
			"sidebar_color_dark",
			"sidebar_color_2_dark",
			"watermark_source",
			"watermark_image",
			"watermark_url",
			"watermark_dark_source",
			"watermark_dark_image",
			"watermark_dark_url",
			"is_site_default",
		]
		# Optional fields added in parent-app cleanup
		for optional in (
			"default_app",
			"hub_route",
			"hub_subtitle",
			"spotlight_tags",
			"hub_icon",
			"hub_icon_image",
			"software_company_name",
			"product_logo_source",
			"product_logo_image",
			"product_logo",
			"favicon_source",
			"favicon_image",
			"favicon",
			"splash_source",
			"splash_image",
			"splash",
			"support_label",
			"support_email",
			"support_url",
		):
			try:
				if frappe.db.has_column("Client Branding", optional):
					fields.append(optional)
			except Exception:
				pass
		rows = frappe.get_all(
			"Client Branding",
			filters={"enabled": 1},
			fields=fields,
		)
	except Exception:
		return {}
	from triplevox_platform.tvx.doctype.client_branding.client_branding import (
		resolve_chrome_logo,
		resolve_logo,
	)

	for row in rows:
		key = (row.get("client_key") or row.get("name") or "").strip().lower()
		if not key:
			continue
		base = deepcopy(_BASE)
		theme = deepcopy(base.get("theme") or _BASE["theme"])
		if row.get("accent_color"):
			theme["green"] = row.accent_color
		if row.get("accent_bright"):
			theme["green_bright"] = row.accent_bright
		if row.get("accent_soft"):
			theme["green_soft"] = row.accent_soft
		if row.get("sidebar_color"):
			theme["sidebar"] = row.sidebar_color
		if row.get("sidebar_color_2"):
			theme["sidebar_2"] = row.sidebar_color_2
		if row.get("sidebar_color_dark"):
			theme["sidebar_dark"] = row.sidebar_color_dark
		if row.get("sidebar_color_2_dark"):
			theme["sidebar_2_dark"] = row.sidebar_color_2_dark
		client_logo = (
			resolve_logo(
				row.get("client_logo_source"),
				row.get("client_logo_image"),
				row.get("client_logo"),
			)
			or ""
		)
		print_logo = (
			resolve_logo(
				row.get("print_logo_source"),
				row.get("print_logo_image"),
				row.get("print_logo"),
			)
			or client_logo
			or ""
		)
		product_logo = (
			resolve_logo(
				row.get("product_logo_source"),
				row.get("product_logo_image"),
				row.get("product_logo"),
			)
			or base.get("logo_url")
			or "/assets/triplevox_platform/images/triplevox-logo.png"
		)
		favicon = resolve_chrome_logo(
			row.get("favicon_source"),
			row.get("favicon_image"),
			row.get("favicon"),
			product_logo,
		)
		splash = resolve_chrome_logo(
			row.get("splash_source"),
			row.get("splash_image"),
			row.get("splash"),
			product_logo,
		)
		watermark = (
			resolve_logo(
				row.get("watermark_source"),
				row.get("watermark_image"),
				row.get("watermark_url"),
			)
			or base.get("watermark_url")
			or "/assets/triplevox_platform/images/triplevox-watermark.png"
		)
		watermark_dark = (
			resolve_logo(
				row.get("watermark_dark_source"),
				row.get("watermark_dark_image"),
				row.get("watermark_dark_url"),
			)
			or base.get("watermark_dark_url")
			or "/assets/triplevox_platform/images/triplevox-watermark-dark.png"
		)
		# Navbar always follows client logo
		navbar_logo = client_logo or product_logo
		out[key] = {
			**base,
			"client_key": key,
			"client_full_name": row.client_full_name or key,
			"factory_area": row.factory_area or "",
			"welcome_kicker": row.welcome_kicker or "Operations Desk",
			"apps_title": row.apps_title or "Operations",
			"product_name": row.product_name or base.get("product_name") or "TripleVox ERP",
			"partner_name": row.partner_name or base.get("partner_name") or "TripleVox Engineering PLC",
			"software_company_name": row.get("software_company_name")
			or row.partner_name
			or base.get("partner_name")
			or "",
			"sidebar_title": row.sidebar_title
			or row.product_name
			or base.get("sidebar_title")
			or "TripleVox ERP",
			"default_app": "",
			"hub_route": "",
			"hub_subtitle": "",
			"hub_icon": row.get("hub_icon") or "Generic",
			"hub_icon_image": row.get("hub_icon_image") or "",
			"spotlight_tags": "",
			"client_logo_url": client_logo,
			"print_logo_url": print_logo,
			"navbar_logo_url": navbar_logo,
			"product_logo_url": product_logo,
			"logo_url": product_logo,
			"favicon_url": favicon,
			"splash_url": splash,
			"support_label": (row.get("support_label") or "").strip(),
			"support_email": (row.get("support_email") or "").strip(),
			"support_url": (row.get("support_url") or "").strip(),
			"watermark_url": watermark,
			"watermark_dark_url": watermark_dark,
			"theme": theme,
			"_company": row.company or "",
			"_is_site_default": int(row.is_site_default or 0),
			"_from_db": True,
		}
		for opt in (
			"default_app",
			"hub_route",
			"hub_subtitle",
			"spotlight_tags",
			"hub_icon",
			"hub_icon_image",
			"software_company_name",
		):
			val = row.get(opt) if hasattr(row, "get") else getattr(row, opt, None)
			if val:
				out[key][opt] = val
	return out


def get_profile_catalog() -> dict:
	"""Enabled Client Branding rows; neutral shell if none exist."""
	catalog = _load_db_profiles()
	if not catalog:
		catalog = {"default": _neutral_shell_profile()}
	return catalog


def get_company_profile_map() -> dict:
	"""Company display name → client_key (site_config + DocType company link)."""
	mapping: dict = {}
	try:
		custom = frappe.conf.get("triplevox_company_profiles") or {}
		if isinstance(custom, dict):
			for name, key in custom.items():
				if name and key:
					mapping[str(name)] = str(key).strip().lower()
	except Exception:
		pass
	for key, profile in _load_db_profiles().items():
		co = profile.get("_company")
		if co:
			mapping[str(co)] = key
	return mapping


def get_session_company() -> str | None:
	"""
	Resolve the company that drives Desk branding for the logged-in user.
	Employee.company → user default company → global default.
	"""
	user = getattr(frappe.session, "user", None) if getattr(frappe, "session", None) else None
	if not user or user in ("Guest", "Administrator"):
		if user != "Administrator":
			return _global_default_company()

	try:
		if user and frappe.db.exists("DocType", "Employee"):
			emp_company = frappe.db.get_value(
				"Employee",
				{"user_id": user, "status": "Active"},
				"company",
			)
			if not emp_company:
				emp_company = frappe.db.get_value("Employee", {"user_id": user}, "company")
			if emp_company:
				return emp_company
	except Exception:
		pass

	try:
		if user:
			ud = frappe.defaults.get_user_default("company")
			if ud:
				return ud
	except Exception:
		pass

	return _global_default_company()


def _global_default_company() -> str | None:
	try:
		return frappe.defaults.get_global_default("company") or frappe.db.get_value(
			"Company", {}, "name"
		)
	except Exception:
		return None


def get_site_client_key() -> str:
	"""site_config → is_site_default → first enabled → neutral default."""
	catalog = get_profile_catalog()
	key = None
	try:
		key = frappe.conf.get("triplevox_client")
	except Exception:
		key = None
	if not key:
		for k, p in catalog.items():
			if p.get("_is_site_default"):
				key = k
				break
	if not key:
		# Prefer first DB row (not the synthetic default if real rows exist)
		db_keys = [k for k, p in catalog.items() if p.get("_from_db")]
		key = db_keys[0] if db_keys else next(iter(catalog), "default")
	key = str(key or "default").strip().lower()
	if key not in catalog:
		return next(iter(catalog))
	return key


def get_site_client_profile() -> dict:
	"""Site-default profile for login, System Settings, migrate (ignore user company)."""
	catalog = get_profile_catalog()
	profile = deepcopy(catalog[get_site_client_key()])
	overrides = {}
	try:
		overrides = frappe.conf.get("triplevox_theme") or {}
	except Exception:
		overrides = {}
	if isinstance(overrides, dict) and overrides:
		_deep_merge(profile, overrides)
	year = now_datetime().year
	partner = profile.get("partner_name") or "TripleVox Engineering PLC"
	profile.setdefault("footer_text", f"© {year} {partner}. All rights reserved.")
	profile.setdefault("footer_powered", partner)
	profile.setdefault("copyright", partner)
	profile.setdefault("product_name", "TripleVox ERP")
	profile.setdefault("sidebar_title", profile["product_name"])
	profile.setdefault(
		"logo_url",
		"/assets/triplevox_platform/images/triplevox-logo.png",
	)
	profile.setdefault("welcome_kicker", "Operations Desk")
	profile.setdefault("apps_title", "Manufacturing")
	profile.setdefault("theme", deepcopy(_BASE["theme"]))
	return profile


def get_active_client_key(company: str | None = None) -> str:
	"""
	Resolve profile key from company map / catalog full name, else site default.
	"""
	catalog = get_profile_catalog()
	company_name = company
	if company_name is None:
		try:
			if getattr(frappe, "session", None) and frappe.session.user not in (None, "Guest"):
				company_name = get_session_company()
		except Exception:
			company_name = None

	if company_name:
		mapped = get_company_profile_map().get(company_name)
		if mapped and mapped in catalog:
			return mapped
		lower_map = {k.lower(): v for k, v in get_company_profile_map().items()}
		mapped = lower_map.get(str(company_name).lower())
		if mapped and mapped in catalog:
			return mapped
		cname = str(company_name).lower()
		for mapped_name, profile_key in get_company_profile_map().items():
			mn = str(mapped_name).lower()
			if cname.startswith(mn) or mn.startswith(cname.split(" (")[0]) or mn in cname:
				if profile_key in catalog:
					return profile_key
		for key, p in catalog.items():
			full = str(p.get("client_full_name") or "").lower()
			if full and (full in cname or cname.startswith(full)):
				return key

	return get_site_client_key()


def get_client_profile(company: str | None = None) -> dict:
	"""Merged profile for a company (or site default)."""
	catalog = get_profile_catalog()
	key = get_active_client_key(company)
	profile = deepcopy(catalog.get(key) or catalog[get_site_client_key()])
	overrides = {}
	try:
		overrides = frappe.conf.get("triplevox_theme") or {}
	except Exception:
		overrides = {}
	if isinstance(overrides, dict) and overrides:
		_deep_merge(profile, overrides)

	company_name = company
	if company_name is None:
		try:
			if getattr(frappe, "session", None) and frappe.session.user not in (None, "Guest"):
				company_name = get_session_company()
		except Exception:
			company_name = None
	if company_name:
		try:
			co = (frappe.conf.get("triplevox_company_themes") or {}).get(company_name) or {}
			if isinstance(co, dict) and co:
				if co.get("factory_area"):
					profile["factory_area"] = co["factory_area"]
				if co.get("logo_url") or co.get("print_logo_url"):
					profile["print_logo_url"] = co.get("print_logo_url") or co.get("logo_url")
				if co.get("client_logo_url"):
					profile["client_logo_url"] = co["client_logo_url"]
				elif co.get("print_logo_url") or co.get("logo_url"):
					profile["client_logo_url"] = co.get("print_logo_url") or co.get("logo_url")
				if co.get("accent"):
					profile.setdefault("theme", {})
					profile["theme"]["green"] = co["accent"]
				if co.get("client_full_name"):
					profile["client_full_name"] = co["client_full_name"]
		except Exception:
			pass

	year = now_datetime().year
	partner = profile.get("partner_name") or "TripleVox Engineering PLC"
	profile.setdefault(
		"footer_text",
		f"© {year} {partner}. All rights reserved.",
	)
	profile.setdefault("footer_powered", partner)
	profile.setdefault("copyright", partner)
	profile.setdefault("product_name", "TripleVox ERP")
	profile.setdefault("sidebar_title", profile["product_name"])
	profile.setdefault(
		"logo_url",
		"/assets/triplevox_platform/images/triplevox-logo.png",
	)
	profile.setdefault("welcome_kicker", "Operations Desk")
	profile.setdefault("apps_title", "Manufacturing")
	profile.setdefault("theme", deepcopy(_BASE["theme"]))
	profile["_resolved_company"] = company_name or ""
	return profile


def get_boot_payload(company: str | None = None) -> dict:
	"""Subset of the profile that is safe to send to the browser."""
	resolved = company
	if resolved is None:
		try:
			if getattr(frappe, "session", None) and frappe.session.user not in (None, "Guest"):
				resolved = get_session_company()
		except Exception:
			resolved = None

	p = get_client_profile(company=resolved)
	client_logo = p.get("client_logo_url") or p.get("print_logo_url") or ""
	needs_onboarding = False
	try:
		from triplevox_platform.branding_setup import needs_onboarding as _needs

		needs_onboarding = bool(_needs())
	except Exception:
		needs_onboarding = False

	hub_route = (p.get("hub_route") or "").strip() or (p.get("apps_title") or "Operations")
	software_company = (
		(p.get("software_company_name") or "").strip()
		or (p.get("partner_name") or "").strip()
		or (p.get("product_name") or "").strip()
	)
	product = p.get("product_name") or "TripleVox ERP"
	support_label = (p.get("support_label") or "").strip() or f"{product} Support"
	support_email = (p.get("support_email") or "").strip() or "gemtadebelaa@gmail.com"
	support_url = (p.get("support_url") or "").strip()
	if not support_url:
		from urllib.parse import quote

		support_url = (
			"https://mail.google.com/mail/?view=cm&fs=1"
			f"&to={quote(support_email)}"
			f"&su={quote(support_label)}"
		)

	is_admin = False
	try:
		roles = set(frappe.get_roles(frappe.session.user) or [])
		is_admin = bool(roles & {"System Manager", "Administrator"})
	except Exception:
		is_admin = False

	return {
		"client_key": p.get("client_key"),
		"product_name": product,
		"software_company_name": software_company,
		"client_full_name": p.get("client_full_name"),
		"factory_area": p.get("factory_area"),
		"welcome_kicker": p.get("welcome_kicker"),
		"logo_url": p.get("logo_url"),
		"print_logo_url": p.get("print_logo_url"),
		"client_logo_url": client_logo,
		"product_logo_url": p.get("product_logo_url") or p.get("logo_url") or "",
		"navbar_logo_url": client_logo or p.get("navbar_logo_url") or p.get("logo_url") or "",
		"favicon_url": p.get("favicon_url") or p.get("product_logo_url") or p.get("logo_url") or "",
		"splash_url": p.get("splash_url") or p.get("product_logo_url") or p.get("logo_url") or "",
		"support_label": support_label,
		"support_email": support_email,
		"support_url": support_url,
		"is_system_manager": int(is_admin),
		"watermark_url": p.get("watermark_url")
		or "/assets/triplevox_platform/images/triplevox-watermark.png",
		"watermark_dark_url": p.get("watermark_dark_url")
		or "/assets/triplevox_platform/images/triplevox-watermark-dark.png",
		"footer_text": p.get("footer_text"),
		"sidebar_title": p.get("sidebar_title"),
		"partner_name": p.get("partner_name"),
		"theme": p.get("theme") or {},
		"company": resolved or p.get("_resolved_company") or "",
		"apps_title": p.get("apps_title") or "Operations",
		"default_app": p.get("default_app") or "",
		"hub_route": hub_route,
		"hub_subtitle": p.get("hub_subtitle") or "",
		"hub_icon": p.get("hub_icon") or "Generic",
		"hub_icon_image": p.get("hub_icon_image") or "",
		"spotlight_tags": p.get("spotlight_tags") or "",
		"needs_branding_onboarding": needs_onboarding,
	}


def get_login_company_options() -> list:
	"""Login company showcase — logos always from Client Branding (Client Logo field)."""
	from triplevox_platform.tvx.doctype.client_branding.client_branding import (
		ensure_public_file_url,
	)

	opts = []
	seen = set()

	def _add(company_name: str, profile: dict | None = None):
		name = (company_name or "").strip()
		if not name or name in seen:
			return
		seen.add(name)
		p = profile or get_client_profile(company=name)
		theme = p.get("theme") or {}
		# Strict: Client Logo (+ optional Product Logo) from Client Branding UI only
		client_logo = ensure_public_file_url(p.get("client_logo_url") or "")
		product_logo = ensure_public_file_url(
			p.get("product_logo_url") or p.get("logo_url") or ""
		)
		# Ignore stock TripleVox product mark for client tile
		from triplevox_platform.tvx.doctype.client_branding.client_branding import (
			is_stock_product_mark,
		)

		if is_stock_product_mark(client_logo):
			client_logo = ""
		opts.append(
			{
				"key": p.get("client_key") or name,
				"company": name,
				"factory_area": "",
				"client_logo_url": client_logo,
				"product_logo_url": "" if is_stock_product_mark(product_logo) else product_logo,
				"accent": theme.get("green") or "#1e4d8c",
				"accent_bright": theme.get("green_bright") or theme.get("green") or "#2563ab",
				"accent_soft": theme.get("green_soft") or "#dbeafe",
			}
		)

	# Prefer companies linked on enabled Client Branding rows (form is source of truth)
	try:
		if _db_branding_enabled():
			for row in frappe.get_all(
				"Client Branding",
				filters={"enabled": 1},
				fields=["company", "client_key", "client_full_name"],
				order_by="is_site_default desc, client_full_name asc",
			):
				co = (row.get("company") or "").strip()
				if co:
					_add(co)
	except Exception:
		pass

	# Still list every Company so empty sites show names; logos only if Branding mapped
	try:
		if frappe.db.exists("DocType", "Company"):
			for co in frappe.get_all("Company", pluck="name", order_by="name asc"):
				_add(co)
	except Exception:
		pass

	if not opts:
		for key, p in get_profile_catalog().items():
			if key == "default" and not p.get("_from_db"):
				continue
			_add(p.get("_company") or p.get("client_full_name") or key, p)

	return opts


def get_site_default_boot_payload() -> dict:
	"""Site-level branding for Guest / login (ignore session company)."""
	from triplevox_platform.tvx.doctype.client_branding.client_branding import (
		ensure_public_file_url,
		is_stock_product_mark,
	)

	p = get_site_client_profile()
	product_logo = ensure_public_file_url(
		p.get("product_logo_url") or p.get("logo_url") or ""
	)
	if not product_logo or is_stock_product_mark(product_logo):
		# Keep packaged mark only when Product Logo field is empty
		product_logo = "/assets/triplevox_platform/images/triplevox-logo.png"
	client_logo = ensure_public_file_url(
		p.get("client_logo_url") or p.get("print_logo_url") or ""
	)
	if is_stock_product_mark(client_logo):
		client_logo = ""
	return {
		"client_key": p.get("client_key"),
		"product_name": p.get("product_name") or "TripleVox ERP",
		"client_full_name": p.get("client_full_name") or p.get("product_name") or "TripleVox ERP",
		"factory_area": p.get("factory_area") or "",
		"logo_url": product_logo,
		"product_logo_url": product_logo,
		"print_logo_url": ensure_public_file_url(p.get("print_logo_url") or "") or "",
		"client_logo_url": client_logo,
		"navbar_logo_url": client_logo or product_logo,
		"favicon_url": ensure_public_file_url(p.get("favicon_url") or "") or product_logo,
		"splash_url": ensure_public_file_url(p.get("splash_url") or "") or product_logo,
		"theme": p.get("theme") or {},
	}


def _deep_merge(base: dict, overlay: dict) -> dict:
	for key, value in overlay.items():
		if isinstance(value, dict) and isinstance(base.get(key), dict):
			_deep_merge(base[key], value)
		else:
			base[key] = value
	return base
