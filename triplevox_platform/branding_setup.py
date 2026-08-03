"""
Client Branding setup: TripleVox product defaults on install + onboarding gate.

Seeds a site-default TripleVox product profile when none exists.
Admins can change any field later in Desk (Client Branding).
Does not seed sister-client tenants (TITA/BRG) unless opted in.
"""
from __future__ import annotations

import frappe

TVX_LOGO = "/assets/triplevox_platform/images/triplevox-logo.png"
TVX_WM = "/assets/triplevox_platform/images/triplevox-watermark.png"
TVX_WM_DARK = "/assets/triplevox_platform/images/triplevox-watermark-dark.png"

# Product / ISV fields — always TripleVox out of the box (editable later)
TVX_PRODUCT_DEFAULTS = {
	"product_name": "TripleVox ERP",
	"software_company_name": "TripleVox Engineering PLC",
	"partner_name": "TripleVox Engineering PLC",
	"sidebar_title": "TripleVox ERP",
	"product_logo_source": "Logo URL",
	"product_logo": TVX_LOGO,
	"favicon_source": "Logo URL",
	"favicon": TVX_LOGO,
	"splash_source": "Logo URL",
	"splash": TVX_LOGO,
	"watermark_source": "Logo URL",
	"watermark_url": TVX_WM,
	"watermark_dark_source": "Logo URL",
	"watermark_dark_url": TVX_WM_DARK,
	"support_label": "TripleVox ERP Support",
	"welcome_kicker": "Operations Desk",
	"sidebar_color_dark": "#0f172a",
	"sidebar_color_2_dark": "#1e293b",
}


def run():
	"""after_migrate / install: seed TripleVox product defaults + normalize sources."""
	if not frappe.db.exists("DocType", "Client Branding"):
		return
	try:
		_normalize_logo_sources()
	except Exception:
		pass
	seed_triplevox_product_branding()
	seed_builtin_clients()  # opt-in demo only
	fill_product_defaults()
	frappe.db.commit()


def _normalize_logo_sources():
	if not frappe.db.has_column("Client Branding", "client_logo_source"):
		return
	frappe.db.sql(
		"""
		UPDATE `tabClient Branding`
		SET client_logo_source = 'Logo URL'
		WHERE IFNULL(client_logo_source, '') = ''
		  AND IFNULL(client_logo, '') != ''
		  AND IFNULL(client_logo_image, '') = ''
		"""
	)
	frappe.db.sql(
		"""
		UPDATE `tabClient Branding`
		SET print_logo_source = 'Logo URL'
		WHERE IFNULL(print_logo_source, '') = ''
		  AND IFNULL(print_logo, '') != ''
		  AND IFNULL(print_logo_image, '') = ''
		"""
	)
	if frappe.db.has_column("Client Branding", "product_logo_source"):
		frappe.db.sql(
			"""
			UPDATE `tabClient Branding`
			SET product_logo_source = 'Logo URL'
			WHERE IFNULL(product_logo_source, '') = ''
			  AND IFNULL(product_logo, '') != ''
			  AND IFNULL(product_logo_image, '') = ''
			"""
		)


def seed_triplevox_product_branding():
	"""
	Ensure at least one enabled Client Branding exists with TripleVox product fields.
	Created once on fresh install; never overwrites custom values already set.
	"""
	if frappe.db.exists("Client Branding", {"enabled": 1}):
		# Still ensure one site-default flag exists
		_ensure_site_default_flag()
		return

	# Prefer name/key "triplevox"
	if frappe.db.exists("Client Branding", "triplevox"):
		frappe.db.set_value(
			"Client Branding",
			"triplevox",
			{"enabled": 1, "is_site_default": 1},
			update_modified=False,
		)
		fill_product_defaults()
		return

	doc = frappe.get_doc(
		{
			"doctype": "Client Branding",
			"client_key": "triplevox",
			"enabled": 1,
			"is_site_default": 1,
			"client_full_name": "TripleVox ERP",
			"factory_area": "",
			"welcome_kicker": "Operations Desk",
			"apps_title": "Operations",
			"hub_subtitle": "Plan work, inventory, people & finance in one desk.",
			"hub_icon": "Generic",
			**{k: v for k, v in TVX_PRODUCT_DEFAULTS.items()},
			# Client marks start as TripleVox so login/Desk look complete until customized
			"client_logo_source": "Logo URL",
			"client_logo": TVX_LOGO,
			"print_logo_source": "Logo URL",
			"print_logo": TVX_LOGO,
			"accent_color": "#15803d",
			"accent_bright": "#16a34a",
			"accent_soft": "#dcfce7",
			"sidebar_color": "#f8fafc",
			"sidebar_color_2": "#f1f5f9",
		}
	)
	doc.insert(ignore_permissions=True)
	try:
		from frappe.installer import update_site_config

		update_site_config("triplevox_client", "triplevox")
	except Exception:
		pass


def _ensure_site_default_flag():
	"""If branding rows exist but none is site default, promote TripleVox or first."""
	if frappe.db.exists("Client Branding", {"enabled": 1, "is_site_default": 1}):
		return
	name = None
	if frappe.db.exists("Client Branding", {"client_key": "triplevox", "enabled": 1}):
		name = frappe.db.get_value(
			"Client Branding", {"client_key": "triplevox", "enabled": 1}, "name"
		)
	if not name:
		name = frappe.db.get_value("Client Branding", {"enabled": 1}, "name")
	if name:
		frappe.db.set_value("Client Branding", name, "is_site_default", 1, update_modified=False)


def fill_product_defaults():
	"""Fill empty TripleVox product fields on existing rows (never overwrite set values)."""
	try:
		rows = frappe.get_all("Client Branding", pluck="name")
	except Exception:
		return
	for name in rows:
		doc = frappe.get_doc("Client Branding", name)
		changed = False
		for field, value in TVX_PRODUCT_DEFAULTS.items():
			if not hasattr(doc, field):
				continue
			cur = getattr(doc, field)
			if cur is None or (isinstance(cur, str) and not str(cur).strip()):
				setattr(doc, field, value)
				changed = True
		# If product source is Attach but no image, fall back to Logo URL + TripleVox
		if (
			hasattr(doc, "product_logo_source")
			and (doc.product_logo_source or "") == "Attach Image"
			and not (doc.product_logo_image or "").strip()
			and not (doc.product_logo or "").strip()
		):
			doc.product_logo_source = "Logo URL"
			doc.product_logo = TVX_LOGO
			changed = True
		if changed:
			doc.flags.ignore_permissions = True
			doc.flags.ignore_validate = True
			doc.save(ignore_permissions=True)


def seed_builtin_clients():
	"""
	Opt-in only: site_config.triplevox_seed_demo_branding = 1
	creates a Demo Client Branding row (still no TITA/BRG names).
	"""
	try:
		if not frappe.conf.get("triplevox_seed_demo_branding"):
			return
	except Exception:
		return
	if frappe.db.exists("Client Branding", "demo"):
		return
	doc = frappe.get_doc(
		{
			"doctype": "Client Branding",
			"client_key": "demo",
			"enabled": 1,
			"is_site_default": 0,
			"client_full_name": "Demo Client",
			"factory_area": "",
			"welcome_kicker": "Operations Desk",
			"apps_title": "Manufacturing",
			"hub_subtitle": "Plan production, inventory, people & finance in one desk.",
			**{k: v for k, v in TVX_PRODUCT_DEFAULTS.items()},
			"client_logo_source": "Logo URL",
			"client_logo": TVX_LOGO,
			"print_logo_source": "Logo URL",
			"print_logo": TVX_LOGO,
			"accent_color": "#0f766e",
			"accent_bright": "#14b8a6",
			"accent_soft": "#ccfbf1",
			"sidebar_color": "#f8fafc",
			"sidebar_color_2": "#f1f5f9",
			"sidebar_color_dark": "#0f172a",
			"sidebar_color_2_dark": "#1e293b",
		}
	)
	doc.insert(ignore_permissions=True)


def branding_configured() -> bool:
	"""True when at least one enabled Client Branding exists."""
	if not frappe.db.exists("DocType", "Client Branding"):
		return False
	return bool(frappe.db.exists("Client Branding", {"enabled": 1}))


def needs_onboarding() -> bool:
	"""
	Administrator onboarding when no branding configured.
	After install seed, TripleVox default exists → no forced gate
	(admins still edit Client Branding anytime).
	"""
	return not branding_configured()
