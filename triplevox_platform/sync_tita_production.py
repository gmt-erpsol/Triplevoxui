"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/sync_tita_production.py
Purpose: Nest TITA Manufacturing workspace icons and links.
"""
"""Repair and standardize the TITA Production workspace for Frappe v16."""
import json

import frappe


WORKSPACE = "TITA Production"

SHORTCUTS = (
    ("Shop Floor", "Page", "tita-shop-floor", "factory", "Blue"),
    ("Production Dashboard", "Page", "tita-production-dashboard", "dashboard", "Cyan"),
    ("Sales Orders", "DocType", "Sales Order", "shopping-cart", "Orange"),
    ("Work Orders", "DocType", "Work Order", "cog", "Blue"),
    ("Printing Jobs", "DocType", "TITA Printing Job", "print", "Purple"),
    ("Recipe Masters", "DocType", "TITA Recipe Master", "flask", "Green"),
    ("QC Tape Tests", "DocType", "TITA QC Tape Test", "check-circle", "Cyan"),
    ("Scrap Entries", "DocType", "TITA Scrap Entry", "trash-2", "Red"),
)

CARDS = (
    (
        "Production Operations",
        "factory",
        (
            ("Shop Floor", "Page", "tita-shop-floor", "factory"),
            ("Production Dashboard", "Page", "tita-production-dashboard", "dashboard"),
            ("Work Orders", "DocType", "Work Order", "cog"),
            ("Job Cards", "DocType", "Job Card", "task"),
        ),
    ),
    (
        "Orders & Planning",
        "shopping-cart",
        (
            ("Sales Orders", "DocType", "Sales Order", "shopping-cart"),
            ("Production Plans", "DocType", "Production Plan", "calendar"),
            ("Bill of Materials", "DocType", "BOM", "sitemap"),
        ),
    ),
    (
        "TITA Masters",
        "flask",
        (
            ("Recipe Masters", "DocType", "TITA Recipe Master", "flask"),
            ("Sack Specifications", "DocType", "TITA Sack Specification", "package"),
            ("Work Center Parameters", "DocType", "TITA Work Center Params", "settings"),
            ("Instrument Register", "DocType", "TITA Instrument Register", "tool"),
        ),
    ),
    (
        "Quality & Recycling",
        "recycle",
        (
            ("QC Tape Tests", "DocType", "TITA QC Tape Test", "check-circle"),
            ("Scrap Entries", "DocType", "TITA Scrap Entry", "trash-2"),
            ("Recycling Batches", "DocType", "TITA Recycling Batch", "recycle"),
        ),
    ),
)


# EDU: Entry point — run via bench execute (see file header).
def run():
    """Replace malformed legacy link blocks with native v16 shortcut/card blocks."""
    if not frappe.db.exists("Workspace", WORKSPACE):
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "label": WORKSPACE,
                "title": WORKSPACE,
                "module": "TITA Custom",
                "public": 1,
                "icon": "factory",
            }
        ).insert(ignore_permissions=True)
    else:
        doc = frappe.get_doc("Workspace", WORKSPACE)

    doc.label = WORKSPACE
    doc.title = WORKSPACE
    doc.module = "TITA Custom"
    doc.public = 1
    doc.is_hidden = 0
    if doc.meta.get_field("icon"):
        doc.icon = "factory"

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
            "id": "tita-prod-heading",
            "type": "header",
            "data": {
                "text": '<span class="h4"><b>Production Operations</b></span>',
                "col": 12,
            },
        }
    ]
    for index, (label, *_rest) in enumerate(valid_shortcuts, start=1):
        content.append(
            {
                "id": f"tita-prod-shortcut-{index}",
                "type": "shortcut",
                "data": {"shortcut_name": label, "col": 3},
            }
        )
    content.extend(
        [
            {
                "id": "tita-prod-spacer",
                "type": "spacer",
                "data": {"col": 12},
            },
            {
                "id": "tita-prod-resources",
                "type": "header",
                "data": {
                    "text": '<span class="h4"><b>Production Resources</b></span>',
                    "col": 12,
                },
            },
        ]
    )
    for index, (label, _icon, _links) in enumerate(valid_cards, start=1):
        content.append(
            {
                "id": f"tita-prod-card-{index}",
                "type": "card",
                "data": {"card_name": label, "col": 3},
            }
        )

    doc.content = json.dumps(content, separators=(",", ":"))
    doc.save(ignore_permissions=True)
    sidebar = _ensure_workspace_sidebar(valid_shortcuts)
    frappe.db.commit()
    frappe.clear_cache()
    try:
        frappe.cache().delete_keys("workspace*")
        frappe.cache().delete_keys("boot*")
    except Exception:
        pass

    return {
        "workspace": WORKSPACE,
        "shortcuts": len(valid_shortcuts),
        "cards": len(valid_cards),
        "content_blocks": len(content),
        "sidebar": sidebar,
    }


def _ensure_workspace_sidebar(valid_shortcuts):
    """Desktop Icon link_type=Workspace Sidebar requires a matching sidebar title."""
    items = [
        {
            "type": "Link",
            "label": "Home",
            "link_type": "Workspace",
            "link_to": WORKSPACE,
            "icon": "home",
            "child": 0,
            "collapsible": 1,
            "indent": 0,
            "keep_closed": 0,
            "show_arrow": 0,
        }
    ]
    for label, link_type, link_to, icon, _color in valid_shortcuts:
        items.append(
            {
                "type": "Link",
                "label": label,
                "link_type": link_type,
                "link_to": link_to,
                "icon": icon,
                "child": 0,
                "collapsible": 1,
                "indent": 0,
                "keep_closed": 0,
                "show_arrow": 0,
            }
        )

    if frappe.db.exists("Workspace Sidebar", WORKSPACE):
        side = frappe.get_doc("Workspace Sidebar", WORKSPACE)
        side.title = WORKSPACE
        if side.meta.get_field("module"):
            side.module = "TITA Custom"
        if side.meta.get_field("header_icon"):
            side.header_icon = "factory"
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
            "module": "TITA Custom",
            "header_icon": "factory",
            "standard": 0,
            "items": items,
        }
    ).insert(ignore_permissions=True)
    return {"name": WORKSPACE, "items": len(items), "created": True}


def _target_exists(link_type, link_to):
    if link_type == "Page":
        return bool(frappe.db.exists("Page", link_to))
    if link_type == "DocType":
        return bool(frappe.db.exists("DocType", link_to))
    if link_type == "Workspace":
        return bool(frappe.db.exists("Workspace", link_to))
    return True
