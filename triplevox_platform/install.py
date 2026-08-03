"""Install / app-install hooks for TripleVox Platform (Desk shell only)."""
from __future__ import annotations

import frappe


def after_install():
	"""Run as soon as triplevox_platform is installed on a site."""
	try:
		from triplevox_platform.branding_setup import run as branding_run

		branding_run()
	except Exception:
		frappe.log_error(title="triplevox after_install branding_setup")
	_apply_desk_layout()


def after_app_install(app_name: str | None = None):
	"""Re-apply icon grouping whenever another app is installed later."""
	# Skip our own install — after_install already ran (and migrate will too).
	if app_name == "triplevox_platform":
		return
	try:
		from triplevox_platform.branding_setup import run as branding_run

		branding_run()
	except Exception:
		frappe.log_error(title="triplevox after_app_install branding_setup")
	_apply_desk_layout()


def _apply_desk_layout():
	try:
		from triplevox_platform.sync_employee_hub import run as sync_hub

		sync_hub()
	except Exception:
		frappe.log_error(title="triplevox after_install employee hub")

	try:
		from triplevox_platform.sync_company_saas import run as sync_saas

		sync_saas()
	except Exception:
		frappe.log_error(title="triplevox after_install company saas")

	try:
		from triplevox_platform.nest_desktop_icons import run as nest_icons

		nest_icons()
	except Exception:
		frappe.log_error(title="triplevox after_install nest icons")

	try:
		from triplevox_platform.domain_gates import tita_domain_enabled
		from triplevox_platform.nest_manufacturing_sidebar import run as nest_mfg

		if tita_domain_enabled():
			nest_mfg()
	except Exception:
		frappe.log_error(title="triplevox after_install nest manufacturing")

	try:
		from triplevox_platform.nest_workspace_menu import run as nest_ws

		nest_ws()
	except Exception:
		frappe.log_error(title="triplevox after_install nest workspace menu")
