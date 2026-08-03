"""
Gates for optional industry / domain features.

TITA Manufacturing chrome (workspaces, desktop icon, sidebar nest, apps-screen
tile) only runs when titacustom is installed on this site, or when site_config
sets triplevox_enable_tita_workspaces = 1.
"""
from __future__ import annotations

import frappe


def tita_domain_enabled() -> bool:
	"""True when this site should get TITA Manufacturing migrate / UI chrome."""
	try:
		if frappe.conf.get("triplevox_enable_tita_workspaces"):
			return True
	except Exception:
		pass
	try:
		return "titacustom" in (frappe.get_installed_apps() or [])
	except Exception:
		return False
