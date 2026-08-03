"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/boot.py
Purpose: boot_session: inject branding, client theme tokens into desk bootinfo.
"""
"""Safe Frappe v16 boot extensions for TripleVox white-label."""
import frappe

from triplevox_platform.client_theme import get_boot_payload


APP_LAUNCHER_LABELS = {
    "ERPNext": "Other",
    "TITA ERP": "Other",
    "Frappe HR": "HRMS",
    "Frappe HRMS": "HRMS",
    "Framework": "System Administration",
    "TripleVox ERP": "System Administration",
}

NEST_APP_TO_PARENT = {
    "erpnext": "Other",
    "titacustom": "Other",
    "hrms": "HRMS",
    "frappe": "System Administration",
    "triplevox_platform": "System Administration",
}

TOP_LEVEL_GROUPS = {
    "Accounting",
    "Sales & Procurement",
    "Inventory & Assets",
    "Manufacturing",
    "TITA Manufacturing",
    "Manufacturing Workspace",
    "CRM",
    "System Administration",
    "Employee Hub",
}


def boot_session(bootinfo):
    # Per-user company → client profile (see client_theme.get_session_company)
    bootinfo.triplevox = get_boot_payload()

    bootinfo.disable_change_log_notification = 1
    bootinfo.show_system_update_notification = 0

    product = (bootinfo.triplevox or {}).get("product_name") or "TripleVox ERP"
    apps_title = (bootinfo.triplevox or {}).get("apps_title") or "Manufacturing"
    # Visible product name everywhere Desk reads app_name / sitename
    bootinfo.app_name = product
    product_logo = (bootinfo.triplevox or {}).get("product_logo_url") or (
        bootinfo.triplevox or {}
    ).get("logo_url")
    if product_logo:
        try:
            bootinfo.app_logo_url = product_logo
        except Exception:
            pass
    if getattr(bootinfo, "sysdefaults", None) is not None:
        try:
            bootinfo.sysdefaults.app_name = product
        except Exception:
            pass

    _inject_titacustom_apps_screen(bootinfo, apps_title=apps_title)
    _prefer_tita_erp_app(bootinfo)
    _rename_app_launchers_and_fix_parents(bootinfo)
    _nest_orphans_under_app_parents(bootinfo)
    _order_parent_apps(bootinfo)
    _rename_apps_screen_titles(bootinfo, apps_title=apps_title)
    _rename_hrms_navigation(bootinfo)
    _scrub_vendor_titles(bootinfo, product)

    # Workspace Viewer: view/use only — never edit layouts
    try:
        from triplevox_platform.workspace_viewer import apply_boot_workspace_flags

        apply_boot_workspace_flags(bootinfo)
    except Exception:
        frappe.log_error(title="Workspace Viewer boot flags failed")


def _inject_titacustom_apps_screen(bootinfo, apps_title="Manufacturing"):
    """Register titacustom on apps screen only when domain is enabled on this site."""
    try:
        from triplevox_platform.domain_gates import tita_domain_enabled

        if not tita_domain_enabled():
            return
    except Exception:
        return

    entry = {
        "name": "titacustom",
        "logo": "/assets/titacustom/images/tita-logo.svg",
        "title": apps_title or "Manufacturing",
        "route": "/desk/tita-manufacturing",
    }
    apps = bootinfo.get("apps")
    if isinstance(apps, list):
        if not any((a.get("name") if isinstance(a, dict) else None) == "titacustom" for a in apps):
            apps.append(dict(entry))
    app_data = bootinfo.get("app_data")
    if isinstance(app_data, dict) and "titacustom" not in app_data:
        app_data["titacustom"] = {
            "app_title": entry["title"],
            "title": entry["title"],
            "app_logo_url": entry["logo"],
        }


def _scrub_vendor_titles(bootinfo, product="TripleVox ERP"):
    """Replace leftover ERPNext / Frappe labels in boot payloads."""
    replacements = (
        ("Frappe HRMS", "HRMS"),
        ("Frappe HR", "HRMS"),
        ("Frappe Framework", "System Administration"),
        ("ERPNext", product),
        ("Frappe", "TripleVox"),
    )

    def scrub(value):
        if not isinstance(value, str) or not value:
            return value
        out = value
        for old, new in replacements:
            if old in out:
                out = out.replace(old, new)
        return out

    for app in bootinfo.get("apps") or []:
        if not isinstance(app, dict):
            continue
        for field in ("title", "app_title", "name"):
            if field == "name":
                continue
            if app.get(field):
                app[field] = scrub(app[field])

    app_data = bootinfo.get("app_data")
    entries = []
    if isinstance(app_data, dict):
        entries = list(app_data.values())
    elif isinstance(app_data, list):
        entries = app_data
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for field in ("title", "app_title"):
            if entry.get(field):
                entry[field] = scrub(entry[field])

    for icon in bootinfo.get("desktop_icons") or []:
        if not isinstance(icon, dict):
            continue
        for field in ("label", "title"):
            if icon.get(field):
                icon[field] = scrub(icon[field])


def _prefer_tita_erp_app(bootinfo):
    icons = bootinfo.get("desktop_icons") or []
    has_other = any(
        (i.get("label") or "") in ("Other", "TITA ERP")
        and (i.get("icon_type") or "") == "App"
        for i in icons
    )
    for icon in icons:
        label = (icon.get("label") or "").strip()
        if label in ("Other", "TITA ERP") and (icon.get("icon_type") or "") == "App":
            icon["label"] = "Other"
            icon["hidden"] = 0
        if has_other and label == "ERPNext" and (icon.get("icon_type") or "") == "App":
            icon["hidden"] = 1
            for child in icons:
                if (child.get("parent_icon") or "").strip() in ("ERPNext", "TITA ERP"):
                    child["parent_icon"] = "Other"


def _rename_app_launchers_and_fix_parents(bootinfo):
    icons = bootinfo.get("desktop_icons") or []
    for icon in icons:
        if (icon.get("icon_type") or "") != "App":
            continue
        old = (icon.get("label") or "").strip()
        if old in APP_LAUNCHER_LABELS:
            new = APP_LAUNCHER_LABELS[old]
            icon["label"] = new
            for child in icons:
                if (child.get("parent_icon") or "").strip() == old:
                    child["parent_icon"] = new


def _nest_orphans_under_app_parents(bootinfo):
    icons = bootinfo.get("desktop_icons") or []
    labels = {
        (icon.get("label") or "").strip()
        for icon in icons
        if not icon.get("hidden")
        and (icon.get("icon_type") or "") in ("App", "Folder")
    }
    if "Other" not in labels and any(
        (i.get("label") or "") == "Other" for i in icons
    ):
        labels.add("Other")

    for icon in icons:
        if icon.get("hidden"):
            continue
        if (icon.get("icon_type") or "") == "App":
            continue
        if icon.get("parent_icon"):
            continue
        if (icon.get("label") or "") in TOP_LEVEL_GROUPS:
            continue
        app = icon.get("app")
        parent = NEST_APP_TO_PARENT.get(app) if app else None
        if not parent:
            parent = "Other"
        # Never nest Manufacturing hub under Other / app parents
        if (icon.get("label") or "") in (
            "Manufacturing",
            "TITA Manufacturing",
            "Manufacturing Workspace",
        ):
            continue
        if parent in labels and (icon.get("label") or "") != parent:
            icon["parent_icon"] = parent
        elif "Other" in labels and (icon.get("label") or "") != "Other":
            icon["parent_icon"] = "Other"


def _order_parent_apps(bootinfo):
    order = {
        "System Administration": 1,
        "Employee Hub": 2,
        "Accounting": 3,
        "CRM": 4,
        "Sales & Procurement": 5,
        "Inventory & Assets": 6,
        "Manufacturing": 7,
        "TITA Manufacturing": 7,
        "Manufacturing Workspace": 7,
        "Other": 9,
        "HRMS": 10,
    }
    icons = bootinfo.get("desktop_icons") or []
    for icon in icons:
        label = (icon.get("label") or "").strip()
        if label in order:
            icon["idx"] = order[label]
    icons.sort(key=lambda icon: (icon.get("idx") or 9999, icon.get("label") or ""))


def _rename_apps_screen_titles(bootinfo, apps_title="Manufacturing"):
    title_map = {
        "erpnext": "TripleVox ERP",
        "hrms": "HRMS",
        "frappe": "System Administration",
        "titacustom": apps_title or "Manufacturing",
        "triplevox_platform": "TripleVox ERP",
    }
    for app in bootinfo.get("apps") or []:
        key = app.get("name") or app.get("app_name") or ""
        if key in title_map:
            app["title"] = title_map[key]
            if "app_title" in app:
                app["app_title"] = title_map[key]

    app_data = bootinfo.get("app_data")
    if isinstance(app_data, dict):
        for key, title in title_map.items():
            entry = app_data.get(key)
            if isinstance(entry, dict):
                entry["app_title"] = title
                entry["title"] = title
    elif isinstance(app_data, list):
        for entry in app_data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("app_name") or entry.get("name") or ""
            if key in title_map:
                entry["app_title"] = title_map[key]
                entry["title"] = title_map[key]


def _rename_hrms_navigation(bootinfo):
    """Use HRMS branding in v16 workspace/sidebar headers without changing routes."""
    replacements = ("Frappe HRMS", "Frappe HR")

    sidebars = bootinfo.get("workspace_sidebar_item")
    if isinstance(sidebars, dict):
        for sidebar in sidebars.values():
            if not isinstance(sidebar, dict):
                continue
            for field in ("title", "label", "header_title", "name"):
                value = (sidebar.get(field) or "").strip()
                if value in replacements:
                    sidebar[field] = "HRMS"
            # Nested items sometimes echo product title in breadcrumbs/headers
            for item in sidebar.get("items") or []:
                if not isinstance(item, dict):
                    continue
                for field in ("label", "title"):
                    value = (item.get(field) or "").strip()
                    if value in replacements:
                        item[field] = "HRMS"

    workspaces = bootinfo.get("workspaces")
    if isinstance(workspaces, dict):
        for workspace in workspaces.values():
            if not isinstance(workspace, dict):
                continue
            for field in ("title", "label"):
                value = (workspace.get(field) or "").strip()
                if value in replacements:
                    workspace[field] = "HRMS"
