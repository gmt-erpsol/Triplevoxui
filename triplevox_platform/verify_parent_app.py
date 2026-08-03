"""One-shot verify helpers for parent-app cleanup (safe to leave)."""
from __future__ import annotations

import frappe


def parent_app_status():
	cols = frappe.db.get_table_columns("Client Branding") if frappe.db.exists("DocType", "Client Branding") else []
	need = ["default_app", "hub_route", "hub_subtitle", "spotlight_tags"]
	from triplevox_platform.client_theme import CLIENTS, DEFAULT_COMPANY_PROFILES, get_profile_catalog
	from triplevox_platform.domain_gates import tita_domain_enabled

	return {
		"columns_ok": all(c in cols for c in need),
		"columns_present": [c for c in need if c in cols],
		"clients_empty": CLIENTS == {},
		"map_empty": DEFAULT_COMPANY_PROFILES == {},
		"tita_domain_enabled": tita_domain_enabled(),
		"catalog_keys": list(get_profile_catalog().keys()),
	}
