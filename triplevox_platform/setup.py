"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/setup.py
Purpose: Apply branding settings after migrate.
"""
"""Apply durable branding via Frappe DocTypes — not DOM hacks."""
import frappe

# Import another Python file from TripleVox platform app.
from triplevox_platform.client_theme import get_client_profile


def apply_branding_settings():
    _system_settings()
    _navbar_settings()
    _website_settings()
    frappe.db.commit()


def _system_settings():
    if not frappe.db.exists("DocType", "System Settings"):
        return
    profile = get_client_profile()
    ss = frappe.get_single("System Settings")
    changed = False
    for field, value in (
        ("enable_onboarding", 0),
        ("disable_change_log_notification", 1),
        ("disable_product_suggestion", 1),
        ("app_name", profile.get("product_name") or "TripleVox ERP"),
        ("default_app", profile.get("default_app") or "erpnext"),
    ):
        if ss.meta.get_field(field) and getattr(ss, field, None) != value:
            ss.set(field, value)
            changed = True
    if changed:
        ss.save(ignore_permissions=True)


def _navbar_settings():
    """Desktop brand logo + remove Frappe/ERPNext marketing help links."""
    if not frappe.db.exists("DocType", "Navbar Settings"):
        return
    profile = get_client_profile()
    logo = profile.get("logo_url") or "/assets/triplevox_platform/images/triplevox-logo.png"
    ns = frappe.get_single("Navbar Settings")
    changed = False
    if ns.meta.get_field("app_logo") and ns.app_logo != logo:
        ns.app_logo = logo
        changed = True

    blocked_url = ("frappe.io", "erpnext.com", "frappeframework.com", "github.com/frappe")

    def _is_vendor_row(row):
        url = (getattr(row, "url", None) or getattr(row, "route", None) or "").lower()
        item = (
            getattr(row, "item_label", None)
            or getattr(row, "label", None)
            or ""
        ).lower()
        if any(b in url for b in blocked_url):
            return True
        if "frappe" in item or "erpnext" in item:
            return True
        return False

    # Help dropdown
    if ns.meta.get_field("help_dropdown") and ns.help_dropdown:
        to_remove = [row for row in list(ns.help_dropdown) if _is_vendor_row(row)]
        for row in to_remove:
            ns.remove(row)
            changed = True

    # Settings dropdown (Frappe Support often lives here)
    if ns.meta.get_field("settings_dropdown") and ns.settings_dropdown:
        to_remove = [row for row in list(ns.settings_dropdown) if _is_vendor_row(row)]
        for row in to_remove:
            ns.remove(row)
            changed = True

    if changed:
        ns.save(ignore_permissions=True)

    # Also hide leftover standard Navbar Items that still say Frappe/ERPNext
    if frappe.db.exists("DocType", "Navbar Item"):
        for row in frappe.get_all(
            "Navbar Item",
            fields=["name", "item_label", "route", "hidden", "parent"],
        ):
            label = (row.item_label or "").lower()
            route = (row.route or "").lower()
            if (
                "frappe" in label
                or "erpnext" in label
                or "frappe.io" in route
                or "erpnext.com" in route
            ):
                if not row.hidden:
                    frappe.db.set_value("Navbar Item", row.name, "hidden", 1, update_modified=False)


def _website_settings():
    if not frappe.db.exists("DocType", "Website Settings"):
        return
    profile = get_client_profile()
    ws = frappe.get_single("Website Settings")
    changed = False
    logo = profile.get("logo_url") or "/assets/triplevox_platform/images/triplevox-logo.png"
    partner = profile.get("partner_name") or "TripleVox Engineering PLC"
    for field, value in (
        ("app_name", profile.get("product_name") or "TripleVox ERP"),
        ("app_logo", logo),
        ("favicon", logo),
        ("splash_image", logo),
        ("footer_powered", profile.get("footer_powered") or partner),
        ("copyright", profile.get("copyright") or partner),
    ):
        if ws.meta.get_field(field) and getattr(ws, field, None) != value:
            ws.set(field, value)
            changed = True
    if changed:
        ws.save(ignore_permissions=True)
