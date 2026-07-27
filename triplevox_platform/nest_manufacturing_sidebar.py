"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/nest_manufacturing_sidebar.py
Purpose: Manufacturing sidebar nesting and route fixes.
"""
"""Ensure TITA workspaces appear under the native Manufacturing sidebar."""
import frappe

PARENT_SIDEBAR = "Manufacturing"
TITA_SECTION = "TITA Apps"

TITA_LINKS = (
    {
        "label": "TITA Manufacturing",
        "link_to": "TITA Manufacturing",
        "icon": "tool",
    },
    {
        "label": "TITA Production",
        "link_to": "TITA Production",
        "icon": "organization",
    },
)


# EDU: Entry point — run via bench execute (see file header).
def run():
    if not frappe.db.exists("Workspace Sidebar", PARENT_SIDEBAR):
        return {"ok": False, "reason": "Manufacturing sidebar missing"}

    # Skip links whose target workspace is missing
    links = [
        L
        for L in TITA_LINKS
        if frappe.db.exists("Workspace", L["link_to"])
    ]
    if not links:
        return {"ok": False, "reason": "No TITA workspaces found"}

    doc = frappe.get_doc("Workspace Sidebar", PARENT_SIDEBAR)
    by_label = {(row.label or "").strip(): row for row in (doc.items or [])}
    changed = False

    # Ensure / update link rows
    for link in links:
        label = link["label"]
        row = by_label.get(label)
        if row:
            if row.type != "Link" or row.link_type != "Workspace" or row.link_to != link["link_to"]:
                row.type = "Link"
                row.link_type = "Workspace"
                row.link_to = link["link_to"]
                changed = True
            if link.get("icon") and getattr(row, "icon", None) != link["icon"]:
                row.icon = link["icon"]
                changed = True
        else:
            doc.append(
                "items",
                {
                    "label": label,
                    "type": "Link",
                    "link_type": "Workspace",
                    "link_to": link["link_to"],
                    "icon": link.get("icon"),
                },
            )
            changed = True

    if TITA_SECTION not in by_label and TITA_SECTION not in {
        (r.label or "").strip() for r in doc.items
    }:
        doc.append("items", {"label": TITA_SECTION, "type": "Section Break"})
        changed = True

    # Reorder: Home, Dashboard, TITA Apps section, TITA links, then the rest
    desired_front = ["Home", "Dashboard", TITA_SECTION] + [L["label"] for L in links]
    rows = list(doc.items)
    front = []
    rest = []
    seen = set()
    for name in desired_front:
        for row in rows:
            lab = (row.label or "").strip()
            if lab == name and lab not in seen:
                front.append(row)
                seen.add(lab)
                break
    for row in rows:
        lab = (row.label or "").strip()
        if lab not in seen:
            rest.append(row)
            seen.add(lab)

    new_order = front + rest
    # Detect order change
    old_labels = [(r.label or "").strip() for r in rows]
    new_labels = [(r.label or "").strip() for r in new_order]
    if old_labels != new_labels:
        doc.set("items", [])
        for row in new_order:
            doc.append(
                "items",
                {
                    "label": row.label,
                    "type": row.type,
                    "link_type": getattr(row, "link_type", None),
                    "link_to": getattr(row, "link_to", None),
                    "icon": getattr(row, "icon", None),
                    "url": getattr(row, "url", None),
                    "child": getattr(row, "child", 0),
                    "indent": getattr(row, "indent", 0),
                    "collapsible": getattr(row, "collapsible", 0),
                    "keep_closed": getattr(row, "keep_closed", 0),
                    "show_arrow": getattr(row, "show_arrow", 0),
                    "filters": getattr(row, "filters", None),
                    "route_options": getattr(row, "route_options", None),
                },
            )
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        try:
            frappe.cache().delete_keys("workspace*")
            frappe.cache().delete_keys("boot*")
        except Exception:
            pass

    verify = [
        {
            "label": r.label,
            "type": r.type,
            "link_type": getattr(r, "link_type", None),
            "link_to": getattr(r, "link_to", None),
        }
        for r in frappe.get_doc("Workspace Sidebar", PARENT_SIDEBAR).items[:8]
    ]
    return {"ok": True, "changed": changed, "sidebar_head": verify}
