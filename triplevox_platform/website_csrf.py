"""
Website context for login/marketing pages:
- ensure CSRF token exists for Guest
- inject TripleVox product branding + multi-company login picker options
"""

import json

import frappe


def update_website_context(context=None):
	try:
		token = frappe.sessions.get_csrf_token()
		if getattr(frappe.local, "session", None) and getattr(frappe.local.session, "data", None):
			frappe.local.session.data.csrf_token = token
		if context is not None:
			context["csrf_token"] = token
	except Exception:
		frappe.log_error(title="tvx csrf ensure failed")

	try:
		from triplevox_platform.client_theme import (
			get_login_company_options,
			get_site_default_boot_payload,
		)

		payload = get_site_default_boot_payload() or {}
		logo = (
			payload.get("product_logo_url")
			or payload.get("logo_url")
			or "/assets/triplevox_platform/images/triplevox-logo.png"
		)
		favicon = payload.get("favicon_url") or logo
		splash = payload.get("splash_url") or logo
		product = payload.get("product_name") or "TripleVox ERP"
		client = payload.get("client_full_name") or product
		client_logo = payload.get("client_logo_url") or ""
		theme = payload.get("theme") or {}
		options = get_login_company_options()
		if context is not None:
			# Product Logo (product owner) — header / favicon / splash
			context["logo"] = logo
			context["app_logo"] = logo
			context["tvx_product_logo"] = logo
			context["favicon"] = favicon
			context["splash_image"] = splash
			context["app_name"] = product
			context["tvx_client_name"] = client
			context["tvx_factory_area"] = payload.get("factory_area") or ""
			# Client Logo — sister company mark from Client Branding form
			context["tvx_client_logo"] = client_logo
			context["tvx_client_key"] = payload.get("client_key") or "tita"
			context["tvx_accent"] = theme.get("green") or "#1e4d8c"
			context["tvx_login_companies"] = options
			context["tvx_login_companies_json"] = json.dumps(options)
			context["tvx_contact_url"] = (
				"https://mail.google.com/mail/?view=cm&fs=1"
				"&to=gemtadebelaa@gmail.com"
				f"&su={product.replace(' ', '%20')}%20Support"
			)
			context["tvx_support_url"] = context["tvx_contact_url"]
	except Exception:
		frappe.log_error(title="tvx website branding failed")

	return context
