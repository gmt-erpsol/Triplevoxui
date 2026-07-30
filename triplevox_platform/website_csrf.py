"""
Website context for login/marketing pages:
- ensure CSRF token exists for Guest
- inject TripleVox logo + client branding into template context
"""

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
		from triplevox_platform.client_theme import get_boot_payload

		payload = get_boot_payload() or {}
		logo = payload.get("logo_url") or "/assets/triplevox_platform/images/triplevox-logo.png"
		product = payload.get("product_name") or "TripleVox ERP"
		client = payload.get("client_full_name") or product
		if context is not None:
			# Frappe login template uses `logo` and `app_name`
			context["logo"] = logo
			context["app_logo"] = logo
			context["app_name"] = product
			context["tvx_client_name"] = client
			context["tvx_factory_area"] = payload.get("factory_area") or ""
			# Open Gmail compose to TripleVox support inbox
			context["tvx_contact_url"] = (
				"https://mail.google.com/mail/?view=cm&fs=1"
				"&to=gemtadebelaa@gmail.com"
				"&su=TripleVox%20ERP%20%2F%20TITA%20Support"
			)
			context["tvx_support_url"] = context["tvx_contact_url"]
	except Exception:
		frappe.log_error(title="tvx website branding failed")

	return context
