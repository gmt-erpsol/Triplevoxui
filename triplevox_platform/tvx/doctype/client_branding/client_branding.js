// Copyright (c) 2026, TripleVox Engineering PLC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Branding", {
	refresh(frm) {
		frm.trigger("toggle_logo_fields");
		frm.add_custom_button(__("Apply to Desk now"), () => {
			frappe.call({
				method: "triplevox_platform.api.apply_client_branding_now",
				args: { client_key: frm.doc.client_key },
				freeze: true,
				freeze_message: __("Refreshing branding…"),
				callback(r) {
					if (r.message) {
						frappe.boot.triplevox = r.message;
						if (window.triplevox && triplevox.platform) {
							triplevox.platform.cfg = r.message;
							triplevox.platform.apply_client_theme();
							triplevox.platform.ensure_watermark();
							triplevox.platform.polish_navbar_header();
							if (typeof triplevox.platform.reload_client_profile === "function") {
								triplevox.platform.reload_client_profile();
							}
							if ($(".desktop-wrapper").length) {
								triplevox.platform.polish_desktop_navbar($(".desktop-wrapper"));
							}
						}
						frappe.show_alert({ message: __("Desk branding updated"), indicator: "green" });
					}
				},
			});
		});
		if (frm.doc.accent_color) {
			frm.dashboard.clear_comment && frm.dashboard.clear_comment();
			frm.dashboard.add_comment(
				__("Accent preview: ") +
					`<span style="display:inline-block;width:14px;height:14px;border-radius:4px;background:${frappe.utils.escape_html(
						frm.doc.accent_color
					)};vertical-align:middle;margin:0 6px;"></span>` +
					frappe.utils.escape_html(frm.doc.accent_color),
				"blue",
				true
			);
		}
	},
	product_logo_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	client_logo_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	print_logo_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	favicon_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	splash_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	watermark_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	watermark_dark_source(frm) {
		frm.trigger("toggle_logo_fields");
	},
	toggle_logo_fields(frm) {
		const pairs = [
			["product_logo_source", "product_logo_image", "product_logo"],
			["client_logo_source", "client_logo_image", "client_logo"],
			["print_logo_source", "print_logo_image", "print_logo"],
			["favicon_source", "favicon_image", "favicon"],
			["splash_source", "splash_image", "splash"],
			["watermark_source", "watermark_image", "watermark_url"],
			["watermark_dark_source", "watermark_dark_image", "watermark_dark_url"],
		];
		pairs.forEach(([src, attach, url]) => {
			if (!frm.fields_dict[src]) return;
			const attachMode = (frm.doc[src] || "Attach Image") === "Attach Image";
			frm.toggle_display(attach, attachMode);
			frm.toggle_display(url, !attachMode);
		});
	},
	accent_color(frm) {
		if (!frm.doc.accent_bright && frm.doc.accent_color) {
			frm.set_value("accent_bright", frm.doc.accent_color);
		}
	},
});
