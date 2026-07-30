"""
TITA/TripleVox file identification
App: triplevox_platform
File: print_branding.py
Purpose: Multi-client print theme + install branded Print Style / Print Formats.
"""
from __future__ import annotations

import os
from copy import deepcopy

import frappe
from frappe.utils import flt

from triplevox_platform.client_theme import get_client_profile

PRINT_STYLE_NAME = "TripleVox Brand"
FORMAT_PREFIX = "TripleVox"

# DocTypes that get a full payslip-quality Jinja print format
BRANDED_FORMATS = (
	{
		"doctype": "Salary Slip",
		"format_name": f"{FORMAT_PREFIX} Payslip",
		"template": "salary_slip.html",
		"title": "Salary Payslip",
	},
	{
		"doctype": "Sales Invoice",
		"format_name": f"{FORMAT_PREFIX} Sales Invoice",
		"template": "transaction.html",
		"title": "Sales Invoice",
		"party_label": "Customer",
		"party_field": "customer_name",
		"meta_extra": ("due_date", "Due Date"),
	},
	{
		"doctype": "Sales Order",
		"format_name": f"{FORMAT_PREFIX} Sales Order",
		"template": "transaction.html",
		"title": "Sales Order",
		"party_label": "Customer",
		"party_field": "customer_name",
		"meta_extra": ("delivery_date", "Delivery Date"),
	},
	{
		"doctype": "Quotation",
		"format_name": f"{FORMAT_PREFIX} Quotation",
		"template": "transaction.html",
		"title": "Quotation",
		"party_label": "Customer",
		"party_field": "customer_name",
		"meta_extra": ("valid_till", "Valid Till"),
	},
	{
		"doctype": "Delivery Note",
		"format_name": f"{FORMAT_PREFIX} Delivery Note",
		"template": "transaction.html",
		"title": "Delivery Note",
		"party_label": "Customer",
		"party_field": "customer_name",
		"meta_extra": ("posting_date", "Date"),
	},
	{
		"doctype": "Purchase Order",
		"format_name": f"{FORMAT_PREFIX} Purchase Order",
		"template": "transaction.html",
		"title": "Purchase Order",
		"party_label": "Supplier",
		"party_field": "supplier_name",
		"meta_extra": ("schedule_date", "Required By"),
	},
	{
		"doctype": "Purchase Invoice",
		"format_name": f"{FORMAT_PREFIX} Purchase Invoice",
		"template": "transaction.html",
		"title": "Purchase Invoice",
		"party_label": "Supplier",
		"party_field": "supplier_name",
		"meta_extra": ("due_date", "Due Date"),
	},
	{
		"doctype": "Purchase Receipt",
		"format_name": f"{FORMAT_PREFIX} Purchase Receipt",
		"template": "transaction.html",
		"title": "Purchase Receipt",
		"party_label": "Supplier",
		"party_field": "supplier_name",
		"meta_extra": ("posting_date", "Date"),
	},
	{
		"doctype": "Request for Quotation",
		"format_name": f"{FORMAT_PREFIX} Request for Quotation",
		"template": "transaction.html",
		"title": "Request for Quotation",
		"party_label": "Company",
		"party_field": "company",
		"meta_extra": ("transaction_date", "Date"),
		"no_money": True,
	},
	{
		"doctype": "Supplier Quotation",
		"format_name": f"{FORMAT_PREFIX} Supplier Quotation",
		"template": "transaction.html",
		"title": "Supplier Quotation",
		"party_label": "Supplier",
		"party_field": "supplier_name",
		"meta_extra": ("valid_till", "Valid Till"),
	},
	{
		"doctype": "Material Request",
		"format_name": f"{FORMAT_PREFIX} Material Request",
		"template": "transaction.html",
		"title": "Material Request",
		"party_label": "Requested By",
		"party_field": "requested_by",
		"meta_extra": ("schedule_date", "Required By"),
		"no_money": True,
	},
	{
		"doctype": "Leave Application",
		"format_name": f"{FORMAT_PREFIX} Leave Application",
		"template": "leave_application.html",
		"title": "Leave Application",
	},
	{
		"doctype": "Payment Entry",
		"format_name": f"{FORMAT_PREFIX} Payment Entry",
		"template": "payment_entry.html",
		"title": "Payment Receipt",
	},
	{
		"doctype": "Work Order",
		"format_name": f"{FORMAT_PREFIX} Work Order",
		"template": "work_order.html",
		"title": "Work Order",
	},
	{
		"doctype": "Stock Entry",
		"format_name": f"{FORMAT_PREFIX} Stock Entry",
		"template": "stock_entry.html",
		"title": "Stock Entry",
	},
	{
		"doctype": "Journal Entry",
		"format_name": f"{FORMAT_PREFIX} Journal Entry",
		"template": "journal_entry.html",
		"title": "Journal Entry",
	},
	{
		"doctype": "Expense Claim",
		"format_name": f"{FORMAT_PREFIX} Expense Claim",
		"template": "expense_claim.html",
		"title": "Expense Claim",
	},
	{
		"doctype": "Job Card",
		"format_name": f"{FORMAT_PREFIX} Job Card",
		"template": "job_card.html",
		"title": "Job Card",
	},
	{
		"doctype": "BOM",
		"format_name": f"{FORMAT_PREFIX} BOM",
		"template": "bom.html",
		"title": "Bill of Materials",
	},
)


def run():
	"""after_migrate entry — install print style + branded formats for this client."""
	ensure_print_style()
	installed = []
	for spec in BRANDED_FORMATS:
		if not frappe.db.exists("DocType", spec["doctype"]):
			continue
		name = ensure_print_format(spec)
		if name:
			installed.append(name)
	_set_print_settings_style()
	frappe.db.commit()
	frappe.clear_cache()
	return {
		"print_style": PRINT_STYLE_NAME,
		"formats": installed,
		"client": get_print_theme().get("client_key"),
	}


def get_print_theme(company=None, doc=None):
	"""
	Resolve print branding for any client / company.

	Priority:
	  1. Company record (name, logo, address, contact)
	  2. client_theme profile (triplevox_client / site_config)
	  3. Safe TripleVox defaults
	"""
	profile = get_client_profile()
	theme = deepcopy(profile.get("theme") or {})

	company_name = None
	if doc is not None:
		company_name = getattr(doc, "company", None) or company
	else:
		company_name = company

	if not company_name:
		company_name = frappe.defaults.get_global_default("company") or frappe.db.get_value(
			"Company", {}, "name"
		)

	company_row = {}
	if company_name and frappe.db.exists("Company", company_name):
		cols = set(frappe.db.get_table_columns("Company") or [])
		wanted = [
			"name",
			"company_name",
			"abbr",
			"email",
			"phone_no",
			"website",
			"country",
			"company_logo",
			"logo",
			"default_letter_head",
		]
		fields = [f for f in wanted if f in cols]
		if not fields:
			fields = ["name"]
		company_row = frappe.db.get_value("Company", company_name, fields, as_dict=True) or {}
		company_row["address"] = ""
		if frappe.db.exists("DocType", "Address"):
			addr = frappe.db.get_value(
				"Dynamic Link",
				{"link_doctype": "Company", "link_name": company_name, "parenttype": "Address"},
				"parent",
			)
			if addr:
				company_row["address"] = (
					frappe.db.get_value("Address", addr, "address_line1") or ""
				)

	logo = _resolve_company_logo(company_name, company_row)
	# Prints only: optional client print_logo_url (NOT Desk logo_url / TripleVox)
	if not logo:
		print_logo = profile.get("print_logo_url") or ""
		if print_logo and not _is_vendor_logo(print_logo):
			logo = print_logo
	# Absolute URL helps wkhtmltopdf
	if logo and logo.startswith("/"):
		try:
			logo = frappe.utils.get_url(logo)
		except Exception:
			pass

	display_name = (
		company_row.get("company_name")
		or company_row.get("name")
		or profile.get("client_full_name")
		or "Company"
	)

	accent = theme.get("green") or "#15803d"
	accent_deep = _darken(accent)
	accent_soft = theme.get("green_soft") or "#dcfce7"

	# Subtitle: Company address first; factory_area only if this client profile set it
	subtitle_parts = []
	addr = (company_row.get("address") or "").strip()
	country = (company_row.get("country") or "").strip()
	if addr:
		subtitle_parts.append(addr)
	if country and country not in addr:
		subtitle_parts.append(country)
	factory_area = (profile.get("factory_area") or "").strip()
	# Prefer real company address; fall back to optional client factory_area
	subtitle = " · ".join(subtitle_parts) if subtitle_parts else factory_area

	# Per-company override via site_config.triplevox_company_themes = { "COMPANY": {...} }
	company_overrides = {}
	try:
		company_overrides = (frappe.conf.get("triplevox_company_themes") or {}).get(
			company_name or "", {}
		)
	except Exception:
		company_overrides = {}

	out = {
		"client_key": profile.get("client_key") or "default",
		# Product shell name is for Desk — prints show company only
		"product_name": "",
		"partner_name": profile.get("partner_name") or "",
		"company": display_name,
		"company_abbr": company_row.get("abbr") or "",
		"factory_area": factory_area,
		"subtitle": subtitle,
		"logo_url": logo or "",
		"email": company_row.get("email") or "",
		"phone": company_row.get("phone_no") or "",
		"website": company_row.get("website") or "",
		"address": company_row.get("address") or "",
		"country": company_row.get("country") or "",
		"accent": accent,
		"accent_deep": accent_deep,
		"accent_soft": accent_soft,
		"ink": theme.get("ink") or "#0f172a",
		"muted": theme.get("muted") or "#64748b",
		"border": theme.get("border") or "#e2e8f0",
		"monogram": _monogram(display_name),
	}
	if isinstance(company_overrides, dict):
		# Allow override logo_url / accent / factory_area — never inject vendor logo
		safe = {k: v for k, v in company_overrides.items() if v is not None}
		if "logo_url" in safe and _is_vendor_logo(safe["logo_url"]):
			safe.pop("logo_url", None)
		out.update(safe)
	# Final guard: never print TripleVox / Frappe assets as company logo
	if _is_vendor_logo(out.get("logo_url")):
		out["logo_url"] = ""
	return out


def _is_vendor_logo(url: str) -> bool:
	"""Block TripleVox/Frappe product marks only — allow client logos under this app."""
	u = str(url or "").lower()
	if not u:
		return False
	return any(
		x in u
		for x in (
			"triplevox-logo",
			"frappe-framework-logo",
			"frappe-logo",
			"erpnext-logo",
			"/assets/frappe/images/frappe-framework-logo",
			"/assets/erpnext/images/erpnext-logo",
		)
	)


def _resolve_company_logo(company_name, company_row) -> str:
	"""Company logo only — Letter Head image, then Company.company_logo. No vendor fallback."""
	# 1) Letter Head linked on Company
	lh_name = company_row.get("default_letter_head")
	if lh_name and frappe.db.exists("Letter Head", lh_name):
		img = frappe.db.get_value("Letter Head", lh_name, "image")
		if img and not _is_vendor_logo(img):
			return img
	# 2) Any enabled Letter Head for this company (common pattern)
	if company_name and frappe.db.exists("DocType", "Letter Head"):
		lh = frappe.db.get_value(
			"Letter Head",
			{"disabled": 0, "is_default": 1},
			["name", "image"],
			as_dict=True,
		)
		if lh and lh.get("image") and not _is_vendor_logo(lh.image):
			return lh.image
	# 3) Company.company_logo / logo fields
	for key in ("company_logo", "logo"):
		val = company_row.get(key)
		if val and not _is_vendor_logo(val):
			return val
	return ""


def _monogram(name: str) -> str:
	parts = [p for p in str(name or "").replace("(", " ").replace(")", " ").split() if p]
	if not parts:
		return "CO"
	if len(parts) == 1:
		return parts[0][:2].upper()
	return (parts[0][0] + parts[1][0]).upper()


def _darken(hex_color: str) -> str:
	hex_color = (hex_color or "#15803d").lstrip("#")
	if len(hex_color) != 6:
		return "#0b7a55"
	try:
		r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
		r, g, b = max(0, r - 30), max(0, g - 30), max(0, b - 30)
		return f"#{r:02x}{g:02x}{b:02x}"
	except Exception:
		return "#0b7a55"


def _templates_dir():
	return os.path.join(os.path.dirname(__file__), "print", "templates")


def _style_css_path():
	return os.path.join(os.path.dirname(__file__), "print", "css", "tvx_print_style.css")


def _read_file(path):
	if os.path.exists(path):
		with open(path, encoding="utf-8") as f:
			return f.read()
	return ""


def ensure_print_style():
	css = _read_file(_style_css_path())
	# Inject live accent tokens from current client theme
	t = get_print_theme()
	css = (
		css.replace("{{ACCENT}}", t["accent"])
		.replace("{{ACCENT_DEEP}}", t["accent_deep"])
		.replace("{{ACCENT_SOFT}}", t["accent_soft"])
		.replace("{{INK}}", t["ink"])
		.replace("{{MUTED}}", t["muted"])
		.replace("{{BORDER}}", t["border"])
	)
	if frappe.db.exists("Print Style", PRINT_STYLE_NAME):
		doc = frappe.get_doc("Print Style", PRINT_STYLE_NAME)
		doc.css = css
		doc.disabled = 0
		doc.save(ignore_permissions=True)
	else:
		frappe.get_doc(
			{
				"doctype": "Print Style",
				"print_style_name": PRINT_STYLE_NAME,
				"css": css,
				"disabled": 0,
			}
		).insert(ignore_permissions=True)
	return PRINT_STYLE_NAME


def _set_print_settings_style():
	if not frappe.db.exists("DocType", "Print Settings"):
		return
	ps = frappe.get_single("Print Settings")
	changed = False
	if ps.meta.get_field("print_style") and ps.print_style != PRINT_STYLE_NAME:
		ps.print_style = PRINT_STYLE_NAME
		changed = True
	# Prefer compact, modern prints
	for field, value in (
		("with_letterhead", 0),
		("add_draft_heading", 1),
		("allow_print_for_draft", 1),
	):
		if ps.meta.get_field(field) and getattr(ps, field, None) != value:
			ps.set(field, value)
			changed = True
	if changed:
		ps.save(ignore_permissions=True)


def ensure_print_format(spec: dict):
	"""Create/update a Jinja Print Format and set as DocType default."""
	dt = spec["doctype"]
	name = spec["format_name"]
	html = _build_format_html(spec)
	if not html:
		return None

	if frappe.db.exists("Print Format", name):
		doc = frappe.get_doc("Print Format", name)
		doc.html = html
		doc.doc_type = dt
		doc.custom_format = 1
		doc.print_format_type = "Jinja"
		doc.disabled = 0
		doc.standard = "No"
		# Custom Jinja HTML lives on the doc — blank module avoids filesystem lookup
		if doc.meta.get_field("module"):
			doc.module = ""
		doc.save(ignore_permissions=True)
	else:
		payload = {
			"doctype": "Print Format",
			"name": name,
			"doc_type": dt,
			"standard": "No",
			"custom_format": 1,
			"print_format_type": "Jinja",
			"html": html,
			"disabled": 0,
		}
		frappe.get_doc(payload).insert(ignore_permissions=True)
		if frappe.get_meta("Print Format").get_field("module"):
			frappe.db.set_value("Print Format", name, "module", "", update_modified=False)

	# Default for this DocType
	try:
		frappe.db.set_value("DocType", dt, "default_print_format", name)
	except Exception:
		pass
	return name


def _build_format_html(spec: dict) -> str:
	import re

	template_name = spec.get("template") or "transaction.html"
	path = os.path.join(_templates_dir(), template_name)
	raw = _read_file(path)
	if not raw:
		return ""

	# Spec tokens for transaction template
	replacements = {
		"{{DOC_TITLE}}": spec.get("title") or spec["doctype"],
		"{{PARTY_LABEL}}": spec.get("party_label") or "Party",
		"{{PARTY_FIELD}}": spec.get("party_field") or "name",
		"{{META_EXTRA_FIELD}}": (spec.get("meta_extra") or ("", ""))[0],
		"{{META_EXTRA_LABEL}}": (spec.get("meta_extra") or ("", ""))[1],
		"{{SHOW_MONEY}}": "0" if spec.get("no_money") else "1",
	}
	for k, v in replacements.items():
		raw = raw.replace(k, str(v))

	# Inline macros — printview renders from DB string (no app include path)
	macros_path = os.path.join(
		os.path.dirname(__file__), "templates", "includes", "tvx_print_macros.html"
	)
	macros = _read_file(macros_path)
	raw = re.sub(
		r"\{%\s*from\s+[\"'][^\"']+[\"']\s+import\s+[^%]+%\}",
		"",
		raw,
		flags=re.IGNORECASE,
	)
	return f"{macros}\n{raw}"


# --- Jinja helpers (registered via hooks.jinja) ---


def tvx_print_theme(doc=None, company=None):
	"""Jinja: {{ tvx_print_theme(doc) }}"""
	return get_print_theme(company=company, doc=doc)


def tvx_money(amount, currency=None, doc=None):
	currency = currency or getattr(doc, "currency", None) or "ETB"
	return frappe.utils.fmt_money(flt(amount), currency=currency)


def tvx_date(value):
	if not value:
		return "—"
	from frappe.utils import formatdate

	return formatdate(value)


def test_print(doctype="Salary Slip", name=None, format_name="TripleVox Payslip"):
	"""Smoke-test branded print HTML."""
	if not name:
		name = frappe.db.get_value(doctype, {"docstatus": ("<", 2)}, "name")
	if not name:
		return {"error": f"No {doctype} found"}
	html = frappe.get_print(doctype, name, print_format=format_name, no_letterhead=1)
	return {
		"doctype": doctype,
		"name": name,
		"format": format_name,
		"html_len": len(html),
		"has_hero": "tvx-hero" in html,
		"has_company": bool(get_print_theme().get("company")),
		"default_format": frappe.db.get_value("DocType", doctype, "default_print_format"),
		"print_style": frappe.db.get_single_value("Print Settings", "print_style"),
	}
