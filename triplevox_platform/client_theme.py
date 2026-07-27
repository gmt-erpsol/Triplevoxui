"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/client_theme.py
Purpose: Multi-client theme profiles → CSS variables for white-label.
"""
from __future__ import annotations

"""
Client theme profiles for multi-tenant / multi-client deployments.

HOW TO USE
----------
1. Pick or add a profile in CLIENTS below.
2. Set the active client for this site in either:
     a) site_config.json  →  "triplevox_client": "tita"
     b) ACTIVE_CLIENT below (fallback when site_config has no key)
3. Optional per-site overrides in site_config.json:
     "triplevox_theme": {
         "client_full_name": "Acme Plastics PLC",
         "theme": { "green": "#0e7490" }
     }
4. bench --site YOURSITE clear-cache && hard-refresh Desk.

THEME TOKENS (theme dict)
-------------------------
green / green_bright / green_soft  → accent (buttons, chips, selection)
sidebar / sidebar_2                → left sidebar gradient ends
page / surface / ink / muted / border / radius → general chrome
"""

from copy import deepcopy

import frappe
from frappe.utils import now_datetime

# Fallback when site_config does not set "triplevox_client"
ACTIVE_CLIENT = "tita"

# Shared TripleVox product shell (usually stays the same across clients)
_BASE = {
    "product_name": "TripleVox ERP",
    "sidebar_title": "TripleVox ERP",
    "partner_name": "TripleVox Engineering PLC",
    "logo_url": "/assets/triplevox_platform/images/triplevox-logo.png",
    "default_app": "titacustom",
    "theme": {
        "sidebar": "#0b1220",
        "sidebar_2": "#111827",
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

CLIENTS = {
    # ------------------------------------------------------------------
    # TITA PP Plastic PLC (current reference deployment)
    # ------------------------------------------------------------------
    "tita": {
        **_BASE,
        "client_key": "tita",
        "client_full_name": "TITA PP Plastic PLC",
        "factory_area": "Wello Dessie — TITA Area",
        "welcome_kicker": "Factory Operations Desk",
        "default_app": "titacustom",
        "theme": {
            **_BASE["theme"],
            "green": "#15803d",
            "green_bright": "#16a34a",
            "green_soft": "#dcfce7",
        },
    },
    # ------------------------------------------------------------------
    # Template — copy this block for each new client
    # ------------------------------------------------------------------
    "demo": {
        **_BASE,
        "client_key": "demo",
        "client_full_name": "Demo Client PLC",
        "factory_area": "Demo Factory — Sample Area",
        "welcome_kicker": "Operations Desk",
        "default_app": "erpnext",
        "logo_url": "/assets/triplevox_platform/images/triplevox-logo.png",
        "theme": {
            **_BASE["theme"],
            # Example: teal accent instead of green
            "green": "#0f766e",
            "green_bright": "#14b8a6",
            "green_soft": "#ccfbf1",
            "sidebar": "#0b1220",
            "sidebar_2": "#111827",
        },
    },
}


def get_active_client_key() -> str:
    """Resolve which CLIENTS profile this site should use."""
    key = None
    try:
        key = frappe.conf.get("triplevox_client")
    except Exception:
        key = None
    key = (key or ACTIVE_CLIENT or "tita").strip().lower()
    if key not in CLIENTS:
        return "tita" if "tita" in CLIENTS else next(iter(CLIENTS))
    return key


def get_client_profile() -> dict:
    """
    Return the merged profile for this site.
    site_config.triplevox_theme (dict) deep-merges on top of the profile.
    """
    profile = deepcopy(CLIENTS[get_active_client_key()])
    overrides = {}
    try:
        overrides = frappe.conf.get("triplevox_theme") or {}
    except Exception:
        overrides = {}
    if isinstance(overrides, dict) and overrides:
        _deep_merge(profile, overrides)

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
    profile.setdefault("theme", deepcopy(_BASE["theme"]))
    return profile


def get_boot_payload() -> dict:
    """Subset of the profile that is safe to send to the browser."""
    p = get_client_profile()
    return {
        "client_key": p.get("client_key"),
        "product_name": p.get("product_name"),
        "client_full_name": p.get("client_full_name"),
        "factory_area": p.get("factory_area"),
        "welcome_kicker": p.get("welcome_kicker"),
        "logo_url": p.get("logo_url"),
        "footer_text": p.get("footer_text"),
        "sidebar_title": p.get("sidebar_title"),
        "partner_name": p.get("partner_name"),
        "theme": p.get("theme") or {},
    }


def _deep_merge(base: dict, overlay: dict) -> dict:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
