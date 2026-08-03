/**
 * Hide Employee Checkin geolocation fields immediately on paint.
 * HRMS shows them by default, then hides after an async HR Settings fetch —
 * that causes a map/field blink. Mirror HRMS logic without the flash.
 */
frappe.ui.form.on("Employee Checkin", {
	onload(frm) {
		["fetch_geolocation", "latitude", "longitude", "geolocation"].forEach((f) => {
			frm.set_df_property(f, "hidden", 1);
		});
		frm.set_df_property("location_section", "hidden", 1);
	},
	refresh: async (frm) => {
		["fetch_geolocation", "latitude", "longitude", "geolocation"].forEach((f) => {
			frm.set_df_property(f, "hidden", 1);
		});
		frm.set_df_property("location_section", "hidden", 1);

		let allow = false;
		try {
			allow = await frappe.db.get_single_value("HR Settings", "allow_geolocation_tracking");
		} catch (e) {
			allow = false;
		}
		if (!allow) return;

		document.body.classList.add("tvx-geo-on");
		["fetch_geolocation", "latitude", "longitude", "geolocation"].forEach((f) => {
			frm.set_df_property(f, "hidden", 0);
		});
		frm.set_df_property("location_section", "hidden", 0);
	},
});

$(document).on("page-change", () => {
	if (!String((frappe.get_route_str && frappe.get_route_str()) || "").startsWith("Form/Employee Checkin")) {
		document.body.classList.remove("tvx-geo-on");
	}
});
