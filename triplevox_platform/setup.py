"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/setup.py
Purpose: Apply branding settings after migrate.
"""
"""Apply durable branding via Frappe DocTypes — not DOM hacks."""
import frappe

from triplevox_platform.client_theme import get_site_client_profile


def apply_branding_settings():
    _system_settings()
    _navbar_settings()
    _website_settings()
    try:
        from triplevox_platform.workspace_viewer import run as setup_workspace_viewer

        setup_workspace_viewer()
    except Exception:
        frappe.log_error(title="Workspace Viewer setup")
    try:
        from triplevox_platform.print_branding import run as setup_print_branding

        setup_print_branding()
    except Exception:
        frappe.log_error(title="Print branding setup")
    frappe.db.commit()


def _system_settings():
    if not frappe.db.exists("DocType", "System Settings"):
        return
    profile = get_site_client_profile()
    ss = frappe.get_single("System Settings")
    changed = False
    for field, value in (
        ("enable_onboarding", 0),
        ("disable_change_log_notification", 1),
        ("disable_product_suggestion", 1),
        ("app_name", profile.get("product_name") or "TripleVox ERP"),
    ):
        if ss.meta.get_field(field) and getattr(ss, field, None) != value:
            ss.set(field, value)
            changed = True

    # Default app: only set if missing. Prefer Client Branding.default_app when set.
    if ss.meta.get_field("default_app"):
        wanted = (profile.get("default_app") or "").strip() or "erpnext"
        if wanted == "titacustom" and "titacustom" not in (frappe.get_installed_apps() or []):
            wanted = "erpnext"
        current = getattr(ss, "default_app", None) or ""
        if not current and wanted:
            ss.set("default_app", wanted)
            changed = True
        elif current == "titacustom" and "titacustom" not in (frappe.get_installed_apps() or []):
            ss.set("default_app", "erpnext")
            changed = True

    if changed:
        ss.save(ignore_permissions=True)


def _navbar_settings():
    """Navbar header = client logo; remove Frappe/ERPNext marketing help links."""
    if not frappe.db.exists("DocType", "Navbar Settings"):
        return
    profile = get_site_client_profile()
    # Desk navbar header always shows the client mark (falls back to product logo).
    logo = (
        profile.get("navbar_logo_url")
        or profile.get("client_logo_url")
        or profile.get("print_logo_url")
        or profile.get("product_logo_url")
        or profile.get("logo_url")
        or "/assets/triplevox_platform/images/triplevox-logo.png"
    )
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

    # Ensure Support opens from Client Branding fields
    from urllib.parse import quote

    product = profile.get("product_name") or "TripleVox ERP"
    support_label = (profile.get("support_label") or "").strip() or f"{product} Support"
    support_email = (profile.get("support_email") or "").strip() or "gemtadebelaa@gmail.com"
    support_url = (profile.get("support_url") or "").strip() or (
        "https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={quote(support_email)}"
        f"&su={quote(support_label)}"
    )
    try:
        ns = frappe.get_single("Navbar Settings")
        added = False
        for fieldname in ("help_dropdown", "settings_dropdown"):
            if not ns.meta.get_field(fieldname):
                continue
            rows = list(getattr(ns, fieldname) or [])
            exists = False
            for row in rows:
                label = (
                    getattr(row, "item_label", None)
                    or getattr(row, "label", None)
                    or ""
                ).strip().lower()
                if "support" in label and (
                    "triplevox" in label or label.endswith("support") or label == "support"
                ):
                    if hasattr(row, "item_label"):
                        row.item_label = support_label
                    elif hasattr(row, "label"):
                        row.label = support_label
                    if hasattr(row, "url"):
                        row.url = support_url
                    if hasattr(row, "route"):
                        row.route = support_url
                    if hasattr(row, "hidden"):
                        row.hidden = 0
                    exists = True
                    added = True
            if not exists:
                meta = ns.meta.get_field(fieldname)
                child = meta.options if meta else None
                if child and frappe.db.exists("DocType", child):
                    cdf = frappe.get_meta(child)
                    payload = {
                        "parent": ns.name,
                        "parenttype": "Navbar Settings",
                        "parentfield": fieldname,
                    }
                    if cdf.has_field("item_label"):
                        payload["item_label"] = support_label
                    elif cdf.has_field("label"):
                        payload["label"] = support_label
                    else:
                        continue
                    if cdf.has_field("url"):
                        payload["url"] = support_url
                    elif cdf.has_field("route"):
                        payload["route"] = support_url
                    if cdf.has_field("hidden"):
                        payload["hidden"] = 0
                    ns.append(fieldname, payload)
                    added = True
                    break
        if added:
            ns.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(title="Product Support navbar link")

    # Company & SaaS — desktop icon under System Administration (see sync_company_saas)
    try:
        from triplevox_platform.sync_company_saas import _remove_navbar_saas_item

        _remove_navbar_saas_item()
    except Exception:
        frappe.log_error(title="Company & SaaS navbar cleanup")


def _website_settings():
    if not frappe.db.exists("DocType", "Website Settings"):
        return
    profile = get_site_client_profile()
    ws = frappe.get_single("Website Settings")
    changed = False
    # Website / login / favicon / splash — Product Logo with optional overrides.
    product_logo = (
        profile.get("product_logo_url")
        or profile.get("logo_url")
        or "/assets/triplevox_platform/images/triplevox-logo.png"
    )
    favicon = profile.get("favicon_url") or product_logo
    splash = profile.get("splash_url") or product_logo
    partner = (
        profile.get("software_company_name")
        or profile.get("partner_name")
        or "TripleVox Engineering PLC"
    )
    for field, value in (
        ("app_name", profile.get("product_name") or "TripleVox ERP"),
        ("app_logo", product_logo),
        ("favicon", favicon),
        ("splash_image", splash),
        ("footer_powered", profile.get("footer_powered") or partner),
        ("copyright", profile.get("copyright") or partner),
    ):
        if ws.meta.get_field(field) and getattr(ws, field, None) != value:
            ws.set(field, value)
            changed = True
    if changed:
        ws.save(ignore_permissions=True)
