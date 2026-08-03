"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/nest_desktop_icons.py
Purpose: Organize desktop icons into app groups.
"""
"""Persist parent_icon nesting + module logos for Desktop Icons."""
import frappe


APP_LABEL_RENAMES = {
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
    "CRM",
    "System Administration",
    "Employee Hub",
}

BASE = "/assets/triplevox_platform/images/module_icons"
TABLER = f"{BASE}/tabler"

# Native ERPNext manufacturing artwork (solid)
NATIVE_MFG = "/assets/erpnext/icons/desktop_icons/solid/manufacturing.svg"
# Brighter stroke icon — readable on dark collapsed sidebar header
TVX_MFG = f"{TABLER}/building-factory-2.svg"

ICON = {
    "System Administration": f"{TABLER}/settings-cog.svg",
    "Accounting": f"{TABLER}/calculator.svg",
    "CRM": f"{TABLER}/users-group.svg",
    "Sales & Procurement": f"{TABLER}/shopping-cart-dollar.svg",
    "Inventory & Assets": f"{TABLER}/packages.svg",
    "Manufacturing": TVX_MFG,
    "Manufacturing Workspace": NATIVE_MFG,
    "ERPNext Settings": f"{BASE}/erpnext_settings.svg",
    "Selling": "/assets/erpnext/icons/desktop_icons/solid/selling.svg",
    "Buying": "/assets/erpnext/icons/desktop_icons/solid/buying.svg",
    "Stock": "/assets/erpnext/icons/desktop_icons/solid/stock.svg",
    "Assets": "/assets/erpnext/icons/desktop_icons/solid/assets.svg",
    "TITA Factory": TVX_MFG,
    "TITA Manufacturing": TVX_MFG,
    "TITA Production": f"{BASE}/production.svg",
    "Other": f"{TABLER}/apps.svg",
    "HRMS": f"{TABLER}/users.svg",
    "Employee Hub": f"{TABLER}/id-badge-2.svg",
}


# EDU: Entry point — run via bench execute (see file header).
def run():
    _ensure_primary_app_icons()
    _rename_app_labels_in_db()
    _nest_orphans_in_db()
    _nest_known_orphans()
    _ensure_business_groups()
    _apply_module_logos()
    _set_parent_order()
    frappe.db.commit()
    try:
        frappe.cache().delete_keys("desktop*")
    except Exception:
        pass
    _clear_saved_layouts()

    top = frappe.db.sql(
        """
        SELECT name, label, icon_type, app, logo_url
        FROM `tabDesktop Icon`
        WHERE IFNULL(hidden,0)=0 AND IFNULL(parent_icon,'')=''
        ORDER BY idx, label
        """,
        as_dict=True,
    )
    children = frappe.db.sql(
        """
        SELECT parent_icon, COUNT(*) AS n
        FROM `tabDesktop Icon`
        WHERE IFNULL(hidden,0)=0 AND IFNULL(parent_icon,'')!=''
        GROUP BY parent_icon
        """
    )
    mfg_kids = frappe.get_all(
        "Desktop Icon",
        # Database filter — only records matching these rules.
        filters={"parent_icon": "Manufacturing", "hidden": 0},
        fields=["name", "label", "logo_url", "link_to", "link_type", "idx"],
        order_by="idx asc",
    )
    return {
        "top_level": top,
        "children_by_parent": {r[0]: r[1] for r in children},
        "manufacturing_children": mfg_kids,
    }


def _set_parent_order():
    order = (
        "System Administration",
        "Employee Hub",
        "Accounting",
        "CRM",
        "Sales & Procurement",
        "Inventory & Assets",
        "Manufacturing",
        "Other",
        "HRMS",
    )
    for idx, name in enumerate(order, start=1):
        if frappe.db.exists("Desktop Icon", name):
            # Keep hub folders/apps visible on Desktop (not nested / not hidden)
            frappe.db.set_value(
                "Desktop Icon",
                name,
                {"idx": idx, "hidden": 0, "parent_icon": ""},
                update_modified=False,
            )


def _ensure_business_groups():
    _ensure_folder("Sales & Procurement", idx=4)
    _ensure_folder("Inventory & Assets", idx=5)

    if frappe.db.exists("Desktop Icon", "Accounting"):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value(
            "Desktop Icon",
            "Accounting",
            {"icon_type": "Folder", "parent_icon": None, "hidden": 0, "idx": 2},
            update_modified=False,
        )

    for child in ("Selling", "Buying"):
        _move_child(child, "Sales & Procurement")

    for child in ("Stock", "Assets"):
        _move_child(child, "Inventory & Assets")

    _ensure_crm_icon()
    _ensure_employee_hub()
    # Always promote native Manufacturing launcher (TITA hide list is a no-op if absent)
    if frappe.db.exists("Workspace Sidebar", "Manufacturing") or frappe.db.exists(
        "Desktop Icon", "Manufacturing"
    ):
        _ensure_manufacturing_group()
    _ensure_system_administration()


def _ensure_crm_icon():
    if not frappe.db.exists("Desktop Icon", "CRM"):
        return
    # Update field(s) directly in database without opening form.
    frappe.db.set_value(
        "Desktop Icon",
        "CRM",
        {
            "icon_type": "Link",
            "parent_icon": None,
            "hidden": 0,
            "idx": 4,
            "logo_url": ICON["CRM"],
        },
        update_modified=False,
    )


def _ensure_employee_hub():
    """Keep Employee Hub as a top-level Workspace Sidebar launcher."""
    if not frappe.db.exists("Workspace Sidebar", "Employee Hub") and not frappe.db.exists(
        "Workspace", "Employee Hub"
    ):
        return
    logo = ICON["Employee Hub"]
    vals = {
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "Employee Hub",
        "parent_icon": "",
        "hidden": 0,
        "logo_url": logo,
        "idx": 2,
    }
    if frappe.db.exists("Desktop Icon", "Employee Hub"):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", "Employee Hub", vals, update_modified=False)
    else:
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": "Employee Hub",
                **vals,
            }
        ).insert(ignore_permissions=True)

    hub_roles = [
        r
        for r in (
            "Employee",
            "Employee Self Service",
            "HR User",
            "HR Manager",
            "System Manager",
            "Administrator",
        )
        if frappe.db.exists("Role", r)
    ]
    _set_desktop_icon_roles("Employee Hub", hub_roles)
    try:
        from triplevox_platform.sync_employee_hub import _grant_employee_hub_access

        _grant_employee_hub_access()
    except Exception:
        pass


def _ensure_system_administration():
    if not frappe.db.exists("Desktop Icon", "System Administration"):
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": "System Administration",
                "icon_type": "App",
                "app": "frappe",
                "hidden": 0,
                "restrict_removal": 1,
                "idx": 1,
                "logo_url": ICON["System Administration"],
            }
        ).insert(ignore_permissions=True)
    else:
        # Update field(s) directly in database without opening form.
        frappe.db.set_value(
            "Desktop Icon",
            "System Administration",
            {
                "icon_type": "App",
                "parent_icon": None,
                "hidden": 0,
                "logo_url": ICON["System Administration"],
                "idx": 1,
            },
            update_modified=False,
        )

    frappe.db.sql(
        """
        UPDATE `tabDesktop Icon`
        SET parent_icon = 'System Administration'
        WHERE parent_icon IN ('TripleVox ERP', 'Framework')
        """
    )

    if frappe.db.exists("Desktop Icon", "ERPNext Settings"):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value(
            "Desktop Icon",
            "ERPNext Settings",
            {
                "parent_icon": "System Administration",
                "hidden": 0,
                "logo_url": ICON["ERPNext Settings"],
            },
            update_modified=False,
        )


def _ensure_folder(label, idx):
    if not frappe.db.exists("Desktop Icon", label):
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": label,
                "icon_type": "Folder",
                "app": "erpnext",
                "hidden": 0,
                "restrict_removal": 1,
                "bg_color": "blue",
                "idx": idx,
                "logo_url": ICON.get(label),
            }
        ).insert(ignore_permissions=True)
    else:
        # Update field(s) directly in database without opening form.
        frappe.db.set_value(
            "Desktop Icon",
            label,
            {
                "icon_type": "Folder",
                "parent_icon": None,
                "hidden": 0,
                "restrict_removal": 1,
                "idx": idx,
                "logo_url": ICON.get(label),
            },
            update_modified=False,
        )


def _move_child(label, parent):
    if frappe.db.exists("Desktop Icon", label):
        vals = {"parent_icon": parent, "hidden": 0}
        if label in ICON:
            vals["logo_url"] = ICON[label]
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", label, vals, update_modified=False)


def _ensure_manufacturing_group():
    """Native Manufacturing desktop icon for everyone; TITA workspaces live in its sidebar.

    When titacustom is installed (caller already gated):
    - Show Desktop Icon labeled exactly "Manufacturing" → Workspace Sidebar "Manufacturing"
      (Frappe get_desktop_icons looks up boot.workspace_sidebar_item by icon *label*)
    - Hide standalone TITA Manufacturing / TITA Production / Manufacturing Workspace icons
    - Sidebar links are maintained by nest_manufacturing_sidebar.run
    """
    if frappe.db.exists("Desktop Icon", "Manufacturing Apps"):
        frappe.db.set_value(
            "Desktop Icon", "Manufacturing Apps", "hidden", 1, update_modified=False
        )

    # Hide titacustom / legacy launchers — open via Manufacturing sidebar instead
    for label in (
        "TITA Factory",
        "TITA Manufacturing",
        "TITA Production",
        "TITA Custom",
        "TITA ERP",
        "Manufacturing Apps",
        "Manufacturing Workspace",
        "Standard Manufacturing",
        "ERPNext Manufacturing",
        "Manufacturing Desk",
    ):
        if frappe.db.exists("Desktop Icon", label):
            frappe.db.set_value(
                "Desktop Icon",
                label,
                {"hidden": 1, "parent_icon": ""},
                update_modified=False,
            )

    # Hide auto App icon for titacustom
    for r in frappe.get_all(
        "Desktop Icon",
        filters={"icon_type": "App"},
        fields=["name", "label", "app"],
    ):
        if (r.app or "") == "titacustom" or (r.label or "") in ("TITA Custom", "TITA ERP", "titacustom"):
            frappe.db.set_value(
                "Desktop Icon",
                r.name,
                {"hidden": 1, "parent_icon": ""},
                update_modified=False,
            )

    # Label MUST equal Workspace Sidebar name ("Manufacturing") or Frappe filters it out
    workspace_label = "Manufacturing"
    workspace_vals = {
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "Manufacturing",
        "sidebar": "Manufacturing",
        "parent_icon": "",
        "hidden": 0,
        "logo_url": NATIVE_MFG,
        "app": "erpnext",
        "idx": 7,
        "bg_color": "blue",
    }
    if not frappe.db.exists("Desktop Icon", workspace_label):
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": workspace_label,
                "restrict_removal": 0,
                **workspace_vals,
            }
        ).insert(ignore_permissions=True)
    else:
        frappe.db.set_value(
            "Desktop Icon", workspace_label, workspace_vals, update_modified=False
        )
    # Empty roles = visible to all users
    _set_desktop_icon_roles(workspace_label, [])

    # Children must not nest under the Link launcher (folder nesting is obsolete)
    frappe.db.sql(
        """
        UPDATE `tabDesktop Icon`
        SET parent_icon = ''
        WHERE parent_icon = 'Manufacturing'
        """
    )

    try:
        from frappe.desk.doctype.desktop_icon.desktop_icon import clear_desktop_icons_cache

        clear_desktop_icons_cache()
        frappe.cache.delete_key("desktop_icons")
        frappe.cache.delete_key("bootinfo")
    except Exception:
        pass


def _set_desktop_icon_roles(label, roles):
    """Empty roles = visible to all; otherwise user needs one of the listed roles."""
    if not frappe.db.exists("Desktop Icon", label):
        return
    doc = frappe.get_doc("Desktop Icon", label)
    doc.set("roles", [])
    for role in roles or []:
        if frappe.db.exists("Role", role):
            doc.append("roles", {"role": role})
    # Avoid exporting standard Desktop Icon JSON into erpnext/frappe/hrms apps
    prev_import = getattr(frappe.flags, "in_import", False)
    frappe.flags.in_import = True
    try:
        doc.save(ignore_permissions=True)
    finally:
        frappe.flags.in_import = prev_import


def _apply_module_logos():
    for label, url in ICON.items():
        if frappe.db.exists("Desktop Icon", label):
            # Update field(s) directly in database without opening form.
            frappe.db.set_value(
                "Desktop Icon", label, "logo_url", url, update_modified=False
            )


def _ensure_primary_app_icons():
    """Ensure the catch-all 'Other' App launcher exists and hides ERPNext duplicate."""
    if not frappe.db.exists("Desktop Icon", "Other"):
        _clone_or_create_app_icon(
            preferred_sources=("TITA ERP", "ERPNext"),
            label="Other",
            app="erpnext",
            logo_url=ICON["Other"],
            idx=9,
        )
    else:
        frappe.db.set_value(
            "Desktop Icon",
            "Other",
            {
                "hidden": 0,
                "icon_type": "App",
                "parent_icon": "",
                "logo_url": ICON["Other"],
                "app": "erpnext",
            },
            update_modified=False,
        )

    # Hide stock ERPNext / TITA ERP launchers; keep children under Other
    for old in ("ERPNext", "TITA ERP"):
        if frappe.db.exists("Desktop Icon", old) and old != "Other":
            frappe.db.sql(
                """
                UPDATE `tabDesktop Icon`
                SET parent_icon = 'Other'
                WHERE parent_icon = %s
                """,
                (old,),
            )
            frappe.db.set_value("Desktop Icon", old, "hidden", 1, update_modified=False)

    # Platform is the Desk shell — not a home-screen module tile
    for label in ("TripleVox Platform", "TripleVox ERP"):
        if frappe.db.exists("Desktop Icon", label):
            frappe.db.set_value(
                "Desktop Icon",
                label,
                {"hidden": 1, "parent_icon": ""},
                update_modified=False,
            )


def _clone_or_create_app_icon(preferred_sources, label, app, logo_url, idx):
    """Create a launcher without rename_doc (rename deletes core fixture JSON)."""
    if frappe.db.exists("Desktop Icon", label):
        return
    source = next((s for s in preferred_sources if frappe.db.exists("Desktop Icon", s)), None)
    vals = {
        "doctype": "Desktop Icon",
        "label": label,
        "icon_type": "App",
        "app": app,
        "hidden": 0,
        "restrict_removal": 1,
        "idx": idx,
        "logo_url": logo_url,
        "parent_icon": "",
    }
    if source:
        row = frappe.db.get_value(
            "Desktop Icon",
            source,
            ["link", "link_type", "link_to", "bg_color", "icon"],
            as_dict=True,
        )
        if row:
            for k, v in row.items():
                if v not in (None, ""):
                    vals[k] = v
    prev_import = getattr(frappe.flags, "in_import", False)
    frappe.flags.in_import = True
    try:
        frappe.get_doc(vals).insert(ignore_permissions=True)
    finally:
        frappe.flags.in_import = prev_import


def _rename_app_labels_in_db():
    """Alias stock App tiles (Framework→System Administration, Frappe HR→HRMS).

    Never use rename_doc on standard icons — with developer_mode it deletes
    fixture files under apps/frappe|erpnext|hrms.
    """
    for old, new in APP_LABEL_RENAMES.items():
        if old == new:
            continue
        if not frappe.db.exists("Desktop Icon", old):
            continue

        if not frappe.db.exists("Desktop Icon", new):
            source_app = frappe.db.get_value("Desktop Icon", old, "app") or "frappe"
            logo = ICON.get(new) or frappe.db.get_value("Desktop Icon", old, "logo_url")
            _clone_or_create_app_icon(
                preferred_sources=(old,),
                label=new,
                app=source_app,
                logo_url=logo,
                idx=1 if new == "System Administration" else 10,
            )

        if frappe.db.exists("Desktop Icon", new):
            frappe.db.sql(
                """
                UPDATE `tabDesktop Icon`
                SET parent_icon = %s
                WHERE parent_icon = %s
                """,
                (new, old),
            )
            frappe.db.set_value("Desktop Icon", old, "hidden", 1, update_modified=False)


def _nest_orphans_in_db():
    """Put every non-hub Link/Folder under its app parent, else under Other."""
    _ensure_primary_app_icons()

    visible_parents = {
        a.name
        for a in frappe.get_all(
            "Desktop Icon",
            filters={"icon_type": ["in", ["App", "Folder"]], "hidden": 0},
            fields=["name"],
        )
    }
    if "Other" not in visible_parents and frappe.db.exists("Desktop Icon", "Other"):
        visible_parents.add("Other")

    orphans = frappe.db.sql(
        """
        SELECT name, label, app, icon_type
        FROM `tabDesktop Icon`
        WHERE IFNULL(hidden,0)=0
          AND icon_type IN ('Link','Folder')
          AND IFNULL(parent_icon,'')=''
        """,
        as_dict=True,
    )

    for icon in orphans:
        label = (icon.label or "").strip()
        if label in TOP_LEVEL_GROUPS:
            continue
        parent = NEST_APP_TO_PARENT.get(icon.app or "") or "Other"
        if parent not in visible_parents:
            parent = "Other" if "Other" in visible_parents else None
        if not parent:
            continue
        if icon.name == parent or label == parent:
            continue
        frappe.db.set_value(
            "Desktop Icon", icon.name, "parent_icon", parent, update_modified=False
        )


def _nest_known_orphans():
    if not frappe.db.exists("Desktop Icon", "Other"):
        return
    for label in ("Organization", "Subcontracting", "Home", "Projects", "Quality", "Support"):
        if frappe.db.exists("Desktop Icon", label):
            row = frappe.db.get_value(
                "Desktop Icon", label, ["parent_icon", "hidden", "icon_type"], as_dict=True
            )
            if (
                row
                and not row.hidden
                and not row.parent_icon
                and (row.icon_type or "") != "App"
                and label not in TOP_LEVEL_GROUPS
            ):
                frappe.db.set_value(
                    "Desktop Icon", label, "parent_icon", "Other", update_modified=False
                )


def on_desktop_icon_change(doc, method=None):
    """Keep new / unparented icons under Other (never touch core fixture export)."""
    if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
        return
    if getattr(frappe.flags, "in_import", False):
        return
    if getattr(frappe.flags, "tvx_nesting", False):
        return
    if int(getattr(doc, "hidden", 0) or 0):
        return
    if (getattr(doc, "icon_type", None) or "") == "App":
        return
    label = (getattr(doc, "label", None) or doc.name or "").strip()
    if label in TOP_LEVEL_GROUPS:
        return
    if (getattr(doc, "parent_icon", None) or "").strip():
        return

    parent = NEST_APP_TO_PARENT.get(getattr(doc, "app", None) or "") or "Other"
    if not frappe.db.exists("Desktop Icon", parent):
        parent = "Other"
    if not frappe.db.exists("Desktop Icon", parent):
        return
    if parent == doc.name or parent == label:
        return

    frappe.flags.tvx_nesting = True
    try:
        frappe.db.set_value(
            "Desktop Icon", doc.name, "parent_icon", parent, update_modified=False
        )
    finally:
        frappe.flags.tvx_nesting = False


def _clear_saved_layouts():
    try:
        layouts = frappe.get_all("Desktop Layout", pluck="name")
        for name in layouts:
            frappe.delete_doc("Desktop Layout", name, ignore_permissions=True, force=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error(title="TripleVox clear desktop layouts")
