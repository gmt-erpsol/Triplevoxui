# Copyright (c) 2026, TripleVox Engineering PLC and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from frappe import _


def resolve_logo(source: str | None, image: str | None, url: str | None) -> str:
	"""Prefer uploaded Attach Image, else Logo URL. Private files → public for Guest/login."""
	source = (source or "Attach Image").strip()
	image = (image or "").strip()
	url = (url or "").strip()
	if source == "Logo URL":
		raw = url or image
	else:
		raw = image or url
	return ensure_public_file_url(raw) if raw else ""


def ensure_public_file_url(path: str | None) -> str:
	"""Guest-safe URL: promote /private/files/* File docs to public /files/*."""
	path = (path or "").strip()
	if not path:
		return ""
	if not path.startswith("/private/files/"):
		return path
	try:
		file_name = frappe.db.get_value("File", {"file_url": path}, "name")
		if not file_name:
			# Fallback match by file_name only
			leaf = path.rsplit("/", 1)[-1]
			file_name = frappe.db.get_value("File", {"file_name": leaf}, "name")
		if file_name:
			doc = frappe.get_doc("File", file_name)
			if int(doc.is_private or 0):
				doc.is_private = 0
				doc.flags.ignore_permissions = True
				doc.save(ignore_permissions=True)
				frappe.db.commit()
			return (doc.file_url or path).strip()
	except Exception:
		frappe.log_error(title="ensure_public_file_url")
	# Last resort rewrite (works only if file already exists under public/)
	return path.replace("/private/files/", "/files/", 1)


_STOCK_PRODUCT_MARKS = (
	"/assets/triplevox_platform/images/triplevox-logo.png",
	"/assets/triplevox_platform/images/triplevox-logo.svg",
)


def is_stock_product_mark(path: str | None) -> bool:
	"""True when value is the packaged TripleVox placeholder (treat as unset)."""
	p = (path or "").strip().split("?")[0]
	if not p:
		return True
	for stock in _STOCK_PRODUCT_MARKS:
		if p == stock or p.endswith(stock) or stock in p:
			return True
	return False


def resolve_chrome_logo(
	source: str | None,
	image: str | None,
	url: str | None,
	fallback: str,
) -> str:
	"""Favicon/splash: explicit upload/URL wins; stock TripleVox placeholder → Product Logo."""
	raw = resolve_logo(source, image, url)
	if not raw or is_stock_product_mark(raw):
		return fallback
	return raw


class ClientBranding(Document):
	def before_insert(self):
		# New rows inherit TripleVox product defaults when left blank
		try:
			from triplevox_platform.branding_setup import TVX_PRODUCT_DEFAULTS

			for field, value in TVX_PRODUCT_DEFAULTS.items():
				if not hasattr(self, field):
					continue
				cur = getattr(self, field)
				if cur is None or (isinstance(cur, str) and not str(cur).strip()):
					setattr(self, field, value)
		except Exception:
			pass

	def validate(self):
		self.client_key = (self.client_key or "").strip().lower().replace(" ", "_")
		if not self.client_key:
			frappe.throw(_("Client Key is required"))
		# Ensure product logo has a TripleVox fallback when empty
		if not self.get_product_logo():
			self.product_logo_source = "Logo URL"
			self.product_logo = "/assets/triplevox_platform/images/triplevox-logo.png"
		for field in (
			"client_logo_source",
			"print_logo_source",
			"product_logo_source",
			"favicon_source",
			"splash_source",
		):
			if hasattr(self, field) and not getattr(self, field):
				setattr(self, field, "Attach Image" if field != "product_logo_source" else "Logo URL")
		# If only URL filled, auto-select Logo URL source
		pairs = (
			("client_logo", "client_logo_image", "client_logo_source"),
			("print_logo", "print_logo_image", "print_logo_source"),
			("product_logo", "product_logo_image", "product_logo_source"),
			("favicon", "favicon_image", "favicon_source"),
			("splash", "splash_image", "splash_source"),
		)
		for url_f, img_f, src_f in pairs:
			if getattr(self, url_f, None) and not getattr(self, img_f, None):
				setattr(self, src_f, "Logo URL")
		# Logo attachments must be public (login page is Guest)
		self._publish_logo_files()
		if self.is_site_default and self.enabled:
			others = frappe.get_all(
				"Client Branding",
				filters={
					"is_site_default": 1,
					"enabled": 1,
					"name": ["!=", self.name or ""],
				},
				pluck="name",
			)
			for name in others:
				frappe.db.set_value("Client Branding", name, "is_site_default", 0)

	def _publish_logo_files(self):
		"""Promote attached brand images so Guest login can render them."""
		fields = (
			"client_logo_image",
			"print_logo_image",
			"product_logo_image",
			"favicon_image",
			"splash_image",
			"watermark_image",
			"watermark_dark_image",
			"client_logo",
			"print_logo",
			"product_logo",
			"favicon",
			"splash",
			"watermark_url",
			"watermark_dark_url",
		)
		for field in fields:
			if not hasattr(self, field):
				continue
			raw = (getattr(self, field) or "").strip()
			if not raw:
				continue
			pub = ensure_public_file_url(raw)
			if pub and pub != raw:
				setattr(self, field, pub)

	def get_client_logo(self) -> str:
		return resolve_logo(self.client_logo_source, self.client_logo_image, self.client_logo)

	def get_print_logo(self) -> str:
		return resolve_logo(self.print_logo_source, self.print_logo_image, self.print_logo) or self.get_client_logo()

	def get_product_logo(self) -> str:
		"""Software / ISV mark — replaces TripleVox logo everywhere."""
		return resolve_logo(
			getattr(self, "product_logo_source", None),
			getattr(self, "product_logo_image", None),
			getattr(self, "product_logo", None),
		) or "/assets/triplevox_platform/images/triplevox-logo.png"

	def get_navbar_logo(self) -> str:
		"""Navbar always follows client logo."""
		return self.get_client_logo() or self.get_product_logo()

	def get_favicon(self) -> str:
		return resolve_chrome_logo(
			getattr(self, "favicon_source", None),
			getattr(self, "favicon_image", None),
			getattr(self, "favicon", None),
			self.get_product_logo(),
		)

	def get_splash(self) -> str:
		return resolve_chrome_logo(
			getattr(self, "splash_source", None),
			getattr(self, "splash_image", None),
			getattr(self, "splash", None),
			self.get_product_logo(),
		)

	def get_watermark(self) -> str:
		return resolve_logo(self.watermark_source, self.watermark_image, self.watermark_url) or (
			"/assets/triplevox_platform/images/triplevox-watermark.png"
		)

	def get_watermark_dark(self) -> str:
		return resolve_logo(
			self.watermark_dark_source, self.watermark_dark_image, self.watermark_dark_url
		) or ("/assets/triplevox_platform/images/triplevox-watermark-dark.png")

	def on_update(self):
		self._sync_site_maps()
		try:
			from triplevox_platform.setup import apply_branding_settings

			apply_branding_settings()
		except Exception:
			frappe.log_error(title="Client Branding apply_branding_settings")
		frappe.clear_cache()

	def after_insert(self):
		self._sync_site_maps()
		frappe.clear_cache()

	def on_trash(self):
		frappe.clear_cache()

	def _sync_site_maps(self):
		if not self.enabled:
			return
		try:
			from frappe.installer import update_site_config

			if self.company:
				profiles = dict(frappe.conf.get("triplevox_company_profiles") or {})
				profiles[self.company] = self.client_key
				update_site_config("triplevox_company_profiles", profiles)
			if self.is_site_default:
				update_site_config("triplevox_client", self.client_key)

			# Keep thin company theme overlay for login/print fallbacks
			themes = dict(frappe.conf.get("triplevox_company_themes") or {})
			co = self.company or self.client_full_name
			if co:
				overlay = dict(themes.get(co) or {})
				client_logo = self.get_client_logo()
				print_logo = self.get_print_logo()
				if client_logo:
					overlay["client_logo_url"] = client_logo
				if print_logo:
					overlay["print_logo_url"] = print_logo
				if self.accent_color:
					overlay["accent"] = self.accent_color
				if self.factory_area:
					overlay["factory_area"] = self.factory_area
				themes[co] = overlay
				update_site_config("triplevox_company_themes", themes)
		except Exception:
			frappe.log_error(title="Client Branding site_config sync")
