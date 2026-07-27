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
    "TITA Manufacturing",
    "Manufacturing Workspace",
    "CRM",
    "System Administration",
    "Employee Hub",
}

BASE = "/assets/triplevox_platform/images/module_icons"
TABLER = f"{BASE}/tabler"

# Native ERPNext manufacturing artwork (solid)
NATIVE_MFG = "/assets/erpnext/icons/desktop_icons/solid/manufacturing.svg"

ICON = {
    "System Administration": f"{TABLER}/settings-cog.svg",
    "Accounting": f"{TABLER}/calculator.svg",
    "CRM": f"{TABLER}/users-group.svg",
    "Sales & Procurement": f"{TABLER}/shopping-cart-dollar.svg",
    "Inventory & Assets": f"{TABLER}/packages.svg",
    "Manufacturing": f"{TABLER}/building-factory-2.svg",
    "Manufacturing Workspace": NATIVE_MFG,
    "ERPNext Settings": f"{BASE}/erpnext_settings.svg",
    "Selling": "/assets/erpnext/icons/desktop_icons/solid/selling.svg",
    "Buying": "/assets/erpnext/icons/desktop_icons/solid/buying.svg",
    "Stock": "/assets/erpnext/icons/desktop_icons/solid/stock.svg",
    "Assets": "/assets/erpnext/icons/desktop_icons/solid/assets.svg",
    "TITA Manufacturing": "/assets/titacustom/images/tita-logo.svg",
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
        "TITA Manufacturing",
        "Manufacturing Workspace",
        "Other",
        "HRMS",
    )
    for idx, name in enumerate(order, start=1):
        if frappe.db.exists("Desktop Icon", name):
            frappe.db.set_value("Desktop Icon", name, "idx", idx, update_modified=False)


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
        return
    frappe.get_doc(
        {
            "doctype": "Desktop Icon",
            "label": "Employee Hub",
            **vals,
        }
    ).insert(ignore_permissions=True)


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
    """Single top-level TITA Manufacturing icon for everyone.

    - TITA Manufacturing: top-level launcher (no children / no folder)
    - TITA Production desktop icon: hidden (content lives in TITA Manufacturing sidebar)
    - Manufacturing folder: hidden
    - Native Manufacturing Workspace: Administrator only (still lists TITA apps via
      nest_manufacturing_sidebar)
    """
    if frappe.db.exists("Desktop Icon", "Manufacturing Apps"):
        frappe.db.set_value(
            "Desktop Icon", "Manufacturing Apps", "hidden", 1, update_modified=False
        )

    # Hide Manufacturing folder — not shown on desk home
    if frappe.db.exists("Desktop Icon", "Manufacturing"):
        frappe.db.set_value(
            "Desktop Icon",
            "Manufacturing",
            {
                "icon_type": "Folder",
                "parent_icon": "",
                "hidden": 1,
                "idx": 99,
                "logo_url": NATIVE_MFG,
                "app": "erpnext",
            },
            update_modified=False,
        )
    else:
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": "Manufacturing",
                "icon_type": "Folder",
                "app": "erpnext",
                "hidden": 1,
                "restrict_removal": 1,
                "idx": 99,
                "logo_url": NATIVE_MFG,
                "bg_color": "blue",
            }
        ).insert(ignore_permissions=True)

    # Hide any other manufacturing child launchers
    for label in ("TITA Production", "Manufacturing Apps"):
        if frappe.db.exists("Desktop Icon", label):
            frappe.db.set_value(
                "Desktop Icon",
                label,
                {"hidden": 1, "parent_icon": ""},
                update_modified=False,
            )

    # Ensure TITA Manufacturing is the only public manufacturing icon
    tita_vals = {
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "TITA Manufacturing",
        "sidebar": "TITA Manufacturing",
        "parent_icon": "",
        "hidden": 0,
        "logo_url": ICON["TITA Manufacturing"],
        "app": "titacustom",
        "idx": 6,
        "bg_color": "blue",
    }
    if not frappe.db.exists("Desktop Icon", "TITA Manufacturing"):
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": "TITA Manufacturing",
                "restrict_removal": 0,
                **tita_vals,
            }
        ).insert(ignore_permissions=True)
    else:
        frappe.db.set_value(
            "Desktop Icon", "TITA Manufacturing", tita_vals, update_modified=False
        )
    _set_desktop_icon_roles("TITA Manufacturing", [])  # everyone

    # Native ERPNext Manufacturing — Administrator only
    workspace_label = "Manufacturing Workspace"
    for old in (
        "Standard Manufacturing",
        "ERPNext Manufacturing",
        "Manufacturing Desk",
    ):
        if frappe.db.exists("Desktop Icon", old):
            if not frappe.db.exists("Desktop Icon", workspace_label):
                frappe.rename_doc(
                    "Desktop Icon", old, workspace_label, force=True, merge=False
                )
            else:
                frappe.db.set_value(
                    "Desktop Icon", old, "hidden", 1, update_modified=False
                )

    workspace_vals = {
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "Manufacturing",
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
    _set_desktop_icon_roles(workspace_label, ["Administrator"])

    # Detach anything still nested under Manufacturing folder
    frappe.db.sql(
        """
        UPDATE `tabDesktop Icon`
        SET parent_icon = ''
        WHERE parent_icon = 'Manufacturing'
        """
    )


def _set_desktop_icon_roles(label, roles):
    """Empty roles = visible to all; otherwise user needs one of the listed roles."""
    if not frappe.db.exists("Desktop Icon", label):
        return
    doc = frappe.get_doc("Desktop Icon", label)
    doc.set("roles", [])
    for role in roles or []:
        if frappe.db.exists("Role", role):
            doc.append("roles", {"role": role})
    doc.save(ignore_permissions=True)


def _apply_module_logos():
    for label, url in ICON.items():
        if frappe.db.exists("Desktop Icon", label):
            # Update field(s) directly in database without opening form.
            frappe.db.set_value(
                "Desktop Icon", label, "logo_url", url, update_modified=False
            )


def _ensure_primary_app_icons():
    if frappe.db.exists("Desktop Icon", "Other"):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", "Other", "hidden", 0, update_modified=False)
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", "Other", "icon_type", "App", update_modified=False)
    elif frappe.db.exists("Desktop Icon", "TITA ERP"):
        frappe.rename_doc("Desktop Icon", "TITA ERP", "Other", force=True, merge=False)
    elif frappe.db.exists("Desktop Icon", "ERPNext"):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", "ERPNext", "hidden", 0, update_modified=False)

    if frappe.db.exists("Desktop Icon", "Other") and frappe.db.exists(
        "Desktop Icon", "ERPNext"
    ):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", "ERPNext", "hidden", 1, update_modified=False)
        frappe.db.sql(
            """
            UPDATE `tabDesktop Icon`
            SET parent_icon = 'Other'
            WHERE parent_icon IN ('ERPNext', 'TITA ERP')
            """
        )


def _rename_app_labels_in_db():
    for old, new in APP_LABEL_RENAMES.items():
        if old == new:
            continue
        if not frappe.db.exists("Desktop Icon", old):
            continue

        if frappe.db.exists("Desktop Icon", new):
            frappe.db.sql(
                """
                UPDATE `tabDesktop Icon`
                SET parent_icon = %s
                WHERE parent_icon = %s
                """,
                (new, old),
            )
            if old != new:
                # Update field(s) directly in database without opening form.
                frappe.db.set_value("Desktop Icon", old, "hidden", 1, update_modified=False)
            continue

        frappe.rename_doc("Desktop Icon", old, new, force=True, merge=False)


def _nest_orphans_in_db():
    visible_apps = {
        a.name
        for a in frappe.get_all(
            "Desktop Icon",
            # Database filter — only records matching these rules.
            filters={"icon_type": "App", "hidden": 0},
            fields=["name"],
        )
    }
    # Folders also accept children
    visible_apps |= {
        a.name
        for a in frappe.get_all(
            "Desktop Icon",
            # Database filter — only records matching these rules.
            filters={"icon_type": "Folder", "hidden": 0},
            fields=["name"],
        )
    }

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
        if icon.label in TOP_LEVEL_GROUPS:
            continue
        parent = NEST_APP_TO_PARENT.get(icon.app or "")
        if not parent or parent not in visible_apps:
            continue
        if icon.name == parent or icon.label == parent:
            continue
        # Update field(s) directly in database without opening form.
        frappe.db.set_value(
            "Desktop Icon", icon.name, "parent_icon", parent, update_modified=False
        )


def _nest_known_orphans():
    if not frappe.db.exists("Desktop Icon", "Other"):
        return
    for label in ("Organization", "Subcontracting"):
        if frappe.db.exists("Desktop Icon", label):
            row = frappe.db.get_value(
                "Desktop Icon", label, ["parent_icon", "hidden"], as_dict=True
            )
            if row and not row.hidden and not row.parent_icon:
                # Update field(s) directly in database without opening form.
                frappe.db.set_value(
                    "Desktop Icon", label, "parent_icon", "Other", update_modified=False
                )


def _clear_saved_layouts():
    try:
        layouts = frappe.get_all("Desktop Layout", pluck="name")
        for name in layouts:
            frappe.delete_doc("Desktop Layout", name, ignore_permissions=True, force=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error(title="TripleVox clear desktop layouts")
