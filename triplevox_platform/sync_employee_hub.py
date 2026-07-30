"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/sync_employee_hub.py
Purpose: Create Employee Hub workspace, sidebar, desktop icon.
"""
"""Create Employee Hub workspace — common employee tools across modules."""
import json

import frappe


WORKSPACE = "Employee Hub"

SHORTCUTS = (
    ("Employee Checkin", "DocType", "Employee Checkin", "login", "Green"),
    ("ToDo", "DocType", "ToDo", "check-circle", "Blue"),
    ("Leave Application", "DocType", "Leave Application", "calendar", "Orange"),
    ("Shift Request", "DocType", "Shift Request", "clock", "Cyan"),
    ("Material Request", "DocType", "Material Request", "package", "Purple"),
    ("Expense Claim", "DocType", "Expense Claim", "expense", "Red"),
    ("Payment Request", "DocType", "Payment Request", "money-coins-1", "Yellow"),
    ("Notes", "DocType", "Note", "file-text", "Gray"),
)

# Cards grouped under parent module themes (label, icon, links)
CARDS = (
    (
        "HR & Attendance",
        "users",
        (
            ("Employee Checkin", "DocType", "Employee Checkin", "login"),
            ("Attendance", "DocType", "Attendance", "check"),
            ("Attendance Request", "DocType", "Attendance Request", "calendar"),
            ("Shift Request", "DocType", "Shift Request", "clock"),
            ("Shift Assignment", "DocType", "Shift Assignment", "assign"),
            ("Leave Application", "DocType", "Leave Application", "calendar"),
            ("Employee", "DocType", "Employee", "user"),
        ),
    ),
    (
        "My Work",
        "check-circle",
        (
            ("ToDo", "DocType", "ToDo", "check-circle"),
            ("Notes", "DocType", "Note", "file-text"),
            ("Event", "DocType", "Event", "calendar"),
            ("Task", "DocType", "Task", "task"),
            ("Timesheet", "DocType", "Timesheet", "timer"),
            ("File", "DocType", "File", "folder"),
        ),
    ),
    (
        "Requests",
        "list",
        (
            ("Material Request", "DocType", "Material Request", "package"),
            ("Payment Request", "DocType", "Payment Request", "money-coins-1"),
            ("Expense Claim", "DocType", "Expense Claim", "expense"),
            ("Employee Advance", "DocType", "Employee Advance", "money"),
        ),
    ),
    (
        "Pay & Support",
        "help",
        (
            ("Salary Slip", "DocType", "Salary Slip", "money-coins-1"),
            ("Issue", "DocType", "Issue", "ticket"),
        ),
    ),
)


# EDU: Entry point — run via bench execute (see file header).
def run():
    if not frappe.db.exists("Workspace", WORKSPACE):
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "label": WORKSPACE,
                "title": WORKSPACE,
                "module": _workspace_module(),
                "public": 1,
                "icon": "users",
            }
        ).insert(ignore_permissions=True)
    else:
        doc = frappe.get_doc("Workspace", WORKSPACE)

    doc.label = WORKSPACE
    doc.title = WORKSPACE
    doc.module = _workspace_module()
    doc.public = 1
    doc.is_hidden = 0
    if doc.meta.get_field("icon"):
        doc.icon = "users"

    valid_shortcuts = []
    for label, link_type, link_to, icon, color in SHORTCUTS:
        if _target_exists(link_type, link_to):
            valid_shortcuts.append((label, link_type, link_to, icon, color))

    doc.set("shortcuts", [])
    for label, link_type, link_to, icon, color in valid_shortcuts:
        doc.append(
            "shortcuts",
            {
                "label": label,
                "type": link_type,
                "link_to": link_to,
                "icon": icon,
                "color": color,
                "doc_view": "List",
            },
        )

    doc.set("links", [])
    valid_cards = []
    for card_label, card_icon, links in CARDS:
        card_links = [link for link in links if _target_exists(link[1], link[2])]
        if not card_links:
            continue
        valid_cards.append((card_label, card_icon, card_links))
        doc.append(
            "links",
            {
                "type": "Card Break",
                "label": card_label,
                "icon": card_icon,
                "link_count": len(card_links),
            },
        )
        for label, link_type, link_to, icon in card_links:
            doc.append(
                "links",
                {
                    "type": "Link",
                    "label": label,
                    "link_type": link_type,
                    "link_to": link_to,
                    "icon": icon,
                },
            )

    content = [
        {
            "id": "emp-hub-heading",
            "type": "header",
            "data": {
                "text": '<span class="h4"><b>Everyday Tools</b></span>',
                "col": 12,
            },
        }
    ]
    for index, (label, *_rest) in enumerate(valid_shortcuts, start=1):
        content.append(
            {
                "id": f"emp-hub-shortcut-{index}",
                "type": "shortcut",
                "data": {"shortcut_name": label, "col": 3},
            }
        )
    content.extend(
        [
            {
                "id": "emp-hub-spacer",
                "type": "spacer",
                "data": {"col": 12},
            },
            {
                "id": "emp-hub-resources",
                "type": "header",
                "data": {
                    "text": '<span class="h4"><b>By Module</b></span>',
                    "col": 12,
                },
            },
        ]
    )
    for index, (label, _icon, _links) in enumerate(valid_cards, start=1):
        content.append(
            {
                "id": f"emp-hub-card-{index}",
                "type": "card",
                "data": {"card_name": label, "col": 3},
            }
        )

    doc.content = json.dumps(content, separators=(",", ":"))
    doc.save(ignore_permissions=True)
    sidebar = _ensure_workspace_sidebar(valid_shortcuts, valid_cards)
    _ensure_desktop_icon()
    try:
        ensure_employee_hub_permissions()
    except Exception:
        frappe.log_error(title="Employee Hub permissions")
    frappe.db.commit()
    frappe.clear_cache()
    try:
        frappe.cache().delete_keys("workspace*")
        frappe.cache().delete_keys("boot*")
        frappe.cache().delete_keys("desktop*")
    except Exception:
        pass

    return {
        "workspace": WORKSPACE,
        "shortcuts": len(valid_shortcuts),
        "cards": len(valid_cards),
        "content_blocks": len(content),
        "sidebar": sidebar,
        "roles": _employee_hub_roles(),
    }


def _workspace_module():
    for name in ("HR", "HRMS", "Human Resources"):
        if frappe.db.exists("Module Def", name):
            return name
    return "HR"


def _ensure_workspace_sidebar(valid_shortcuts, valid_cards):
    items = [
        {
            "type": "Link",
            "label": "Home",
            "link_type": "Workspace",
            "link_to": WORKSPACE,
            "icon": "home",
            "show_arrow": 0,
        }
    ]

    # Section per card group + child DocType links
    for card_label, card_icon, card_links in valid_cards:
        items.append(
            {
                "type": "Section Break",
                "label": card_label,
                "icon": card_icon,
            }
        )
        for label, link_type, link_to, icon in card_links:
            items.append(
                {
                    "type": "Link",
                    "label": label,
                    "link_type": link_type,
                    "link_to": link_to,
                    "icon": icon,
                    "child": 1,
                    "show_arrow": 0,
                }
            )

    module = _workspace_module()
    if frappe.db.exists("Workspace Sidebar", WORKSPACE):
        side = frappe.get_doc("Workspace Sidebar", WORKSPACE)
        side.title = WORKSPACE
        if side.meta.get_field("module"):
            side.module = module
        if side.meta.get_field("header_icon"):
            side.header_icon = "users"
        side.set("items", [])
        for item in items:
            side.append("items", item)
        side.save(ignore_permissions=True)
        return {"name": WORKSPACE, "items": len(items), "created": False}

    frappe.get_doc(
        {
            "doctype": "Workspace Sidebar",
            "name": WORKSPACE,
            "title": WORKSPACE,
            "module": module,
            "header_icon": "users",
            "standard": 0,
            "items": items,
        }
    ).insert(ignore_permissions=True)
    return {"name": WORKSPACE, "items": len(items), "created": True}


def _ensure_desktop_icon():
    """Top-level desktop launcher → Workspace Sidebar Employee Hub."""
    logo = "/assets/triplevox_platform/images/module_icons/tabler/id-badge-2.svg"
    vals = {
        "label": WORKSPACE,
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": WORKSPACE,
        "parent_icon": "",
        "hidden": 0,
        "logo_url": logo,
        "idx": 2,
    }
    if frappe.db.exists("Desktop Icon", WORKSPACE):
        # Update field(s) directly in database without opening form.
        frappe.db.set_value("Desktop Icon", WORKSPACE, vals, update_modified=False)
    else:
        frappe.get_doc(
            {
                "doctype": "Desktop Icon",
                "label": WORKSPACE,
                "icon_type": "Link",
                "link_type": "Workspace Sidebar",
                "link_to": WORKSPACE,
                "hidden": 0,
                "logo_url": logo,
                "idx": 2,
            }
        ).insert(ignore_permissions=True)

    _grant_employee_hub_access()


def _employee_hub_roles():
    """Roles that must see / use Employee Hub."""
    wanted = (
        "Employee",
        "Employee Self Service",
        "HR User",
        "HR Manager",
        "System Manager",
        "Administrator",
    )
    return [r for r in wanted if frappe.db.exists("Role", r)]


def _grant_employee_hub_access():
    """
    Ensure every user with Employee (and related HR roles) can see the
    Employee Hub desktop icon and open the workspace.
    """
    roles = _employee_hub_roles()

    # Desktop Icon — role gate
    if frappe.db.exists("Desktop Icon", WORKSPACE):
        icon = frappe.get_doc("Desktop Icon", WORKSPACE)
        icon.hidden = 0
        if icon.meta.get_field("roles"):
            icon.set("roles", [])
            for role in roles:
                icon.append("roles", {"role": role})
        icon.save(ignore_permissions=True)

    # Workspace — role gate (public + Employee roles)
    if frappe.db.exists("Workspace", WORKSPACE):
        ws = frappe.get_doc("Workspace", WORKSPACE)
        ws.public = 1
        if hasattr(ws, "is_hidden"):
            ws.is_hidden = 0
        if ws.meta.get_field("roles"):
            ws.set("roles", [])
            for role in roles:
                ws.append("roles", {"role": role})
        ws.save(ignore_permissions=True)

    # Un-hide for users who previously removed / hid the icon
    if frappe.db.exists("DocType", "User Desktop Icon"):
        frappe.db.sql(
            """
            UPDATE `tabUser Desktop Icon`
            SET hidden = 0
            WHERE desktop_icon = %s OR label = %s
            """,
            (WORKSPACE, WORKSPACE),
        )

    # Soft-ensure Employee role users get a visible icon row if table uses per-user list
    if frappe.db.exists("DocType", "User Desktop Icon") and frappe.db.exists(
        "Desktop Icon", WORKSPACE
    ):
        users = frappe.get_all(
            "Has Role",
            filters={"role": "Employee", "parenttype": "User"},
            pluck="parent",
        )
        meta = frappe.get_meta("User Desktop Icon")
        for user in users:
            if user in ("Guest", "Administrator"):
                continue
            exists = frappe.db.exists(
                "User Desktop Icon", {"user": user, "desktop_icon": WORKSPACE}
            ) or frappe.db.exists(
                "User Desktop Icon", {"parent": user, "desktop_icon": WORKSPACE}
            )
            if exists:
                continue
            # Only create if DocType supports user + desktop_icon fields
            if not meta.get_field("desktop_icon"):
                break
            try:
                row = {"doctype": "User Desktop Icon", "desktop_icon": WORKSPACE, "hidden": 0}
                if meta.get_field("user"):
                    row["user"] = user
                if meta.get_field("label"):
                    row["label"] = WORKSPACE
                frappe.get_doc(row).insert(ignore_permissions=True)
            except Exception:
                break


def inspect_access():
    """bench --site tita.local execute triplevox_platform.sync_employee_hub.inspect_access"""
    out = {"roles_granted": _employee_hub_roles()}
    if frappe.db.exists("Desktop Icon", WORKSPACE):
        icon = frappe.get_doc("Desktop Icon", WORKSPACE)
        out["desktop_icon"] = {
            "hidden": icon.hidden,
            "roles": [r.role for r in (icon.get("roles") or [])],
            "link_to": icon.link_to,
        }
    if frappe.db.exists("Workspace", WORKSPACE):
        ws = frappe.get_doc("Workspace", WORKSPACE)
        out["workspace"] = {
            "public": ws.public,
            "roles": [r.role for r in (ws.get("roles") or [])],
        }
    out["users_with_employee"] = frappe.db.count(
        "Has Role", {"role": "Employee", "parenttype": "User"}
    )
    # Sample DocPerms for Employee role on hub DocTypes
    perms = {}
    for dt in (
        "Employee Checkin",
        "Leave Application",
        "Attendance",
        "ToDo",
        "Salary Slip",
        "Material Request",
        "Expense Claim",
    ):
        if not frappe.db.exists("DocType", dt):
            continue
        rows = frappe.get_all(
            "DocPerm",
            filters={"parent": dt, "role": "Employee"},
            fields=["read", "write", "create", "submit"],
        )
        if not rows:
            rows = frappe.get_all(
                "Custom DocPerm",
                filters={"parent": dt, "role": "Employee"},
                fields=["read", "write", "create", "submit"],
            )
        perms[dt] = rows[0] if rows else None
    out["employee_docperms"] = perms
    return out


def ensure_employee_hub_permissions():
    """
    Grant Employee role basic self-service permissions on hub DocTypes
    so the icon is usable (not just visible).
    """
    if not frappe.db.exists("Role", "Employee"):
        return {"skipped": True}

    # (doctype, read, write, create, submit, cancel, delete, if_owner)
    grants = (
        ("Employee Checkin", 1, 1, 1, 0, 0, 0, 0),
        ("Leave Application", 1, 1, 1, 1, 0, 0, 1),
        ("Attendance", 1, 0, 0, 0, 0, 0, 0),
        ("Attendance Request", 1, 1, 1, 1, 0, 0, 1),
        ("Shift Request", 1, 1, 1, 1, 0, 0, 1),
        ("ToDo", 1, 1, 1, 0, 0, 0, 1),
        ("Note", 1, 1, 1, 0, 0, 1, 1),
        ("Event", 1, 1, 1, 0, 0, 0, 1),
        ("Timesheet", 1, 1, 1, 1, 0, 0, 1),
        ("Salary Slip", 1, 0, 0, 0, 0, 0, 0),
        ("Material Request", 1, 1, 1, 1, 0, 0, 1),
        ("Expense Claim", 1, 1, 1, 1, 0, 0, 1),
        ("Employee Advance", 1, 1, 1, 1, 0, 0, 1),
        ("Payment Request", 1, 1, 1, 1, 0, 0, 1),
        ("Issue", 1, 1, 1, 0, 0, 0, 1),
        ("Employee", 1, 0, 0, 0, 0, 0, 0),
        ("File", 1, 1, 1, 0, 0, 0, 1),
    )
    created = []
    for dt, read, write, create, submit, cancel, delete, if_owner in grants:
        if not frappe.db.exists("DocType", dt):
            continue
        existing = frappe.db.exists("Custom DocPerm", {"parent": dt, "role": "Employee"})
        if existing:
            continue
        # Skip if standard DocPerm already grants read
        if frappe.db.exists("DocPerm", {"parent": dt, "role": "Employee", "read": 1}):
            continue
        try:
            frappe.get_doc(
                {
                    "doctype": "Custom DocPerm",
                    "parent": dt,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": "Employee",
                    "permlevel": 0,
                    "read": read,
                    "write": write,
                    "create": create,
                    "submit": submit,
                    "cancel": cancel,
                    "delete": delete,
                    "if_owner": if_owner,
                    "email": 1,
                    "print": 1,
                    "report": 1,
                    "share": 0,
                    "export": 0,
                }
            ).insert(ignore_permissions=True)
            created.append(dt)
        except Exception as exc:
            frappe.log_error(title=f"Employee Hub perm {dt}", message=str(exc))
            # Fallback: append on DocType if Custom DocPerm blocked
            try:
                dt_doc = frappe.get_doc("DocType", dt)
                if not any(p.role == "Employee" for p in (dt_doc.permissions or [])):
                    dt_doc.append(
                        "permissions",
                        {
                            "role": "Employee",
                            "read": read,
                            "write": write,
                            "create": create,
                            "submit": submit,
                            "cancel": cancel,
                            "delete": delete,
                            "if_owner": if_owner,
                        },
                    )
                    dt_doc.save(ignore_permissions=True)
                    created.append(f"{dt} (doctype)")
            except Exception as exc2:
                frappe.log_error(title=f"Employee Hub perm fallback {dt}", message=str(exc2))

    frappe.clear_cache()
    return {"created_custom_perms": created}


def _target_exists(link_type, link_to):
    if link_type == "Page":
        return bool(frappe.db.exists("Page", link_to))
    if link_type == "DocType":
        return bool(frappe.db.exists("DocType", link_to))
    if link_type == "Workspace":
        return bool(frappe.db.exists("Workspace", link_to))
    return True
