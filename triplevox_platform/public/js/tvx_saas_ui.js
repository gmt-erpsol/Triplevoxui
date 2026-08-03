/**
 * TripleVox SaaS UI — company switcher dialog, onboarding / role packs / print pack.
 * Company & SaaS lives under System Administration desktop icon (not sidebar).
 */
frappe.provide("triplevox.platform");

triplevox.platform.setup_saas_ui = function () {
	if (window.__tvx_saas_ui) return;
	window.__tvx_saas_ui = true;
	$("#tvx-company-switcher").remove();
	triplevox.platform.remove_saas_sidebar_menu_item();
	triplevox.platform.apply_pending_login_company();
	triplevox.platform.maybe_force_branding_onboarding();
	$(document).on("page-change sidebar_setup", () => {
		setTimeout(() => {
			$("#tvx-company-switcher").remove();
			triplevox.platform.remove_saas_sidebar_menu_item();
		}, 80);
	});
};

triplevox.platform.apply_pending_login_company = function () {
	let key = "";
	try {
		if (sessionStorage.getItem("tvx_login_company_applied") === "1") return;
		key = localStorage.getItem("tvx_login_company_key") || "";
	} catch (e) {
		return;
	}
	if (!key) return;
	frappe.call({
		method: "triplevox_platform.api.apply_login_company_key",
		args: { client_key: key },
		freeze: false,
		callback: (r) => {
			try {
				sessionStorage.setItem("tvx_login_company_applied", "1");
			} catch (e) {
				/* ignore */
			}
			const boot = r.message && r.message.boot;
			if (boot) {
				frappe.boot.triplevox = boot;
				triplevox.platform.cfg = boot;
				triplevox.platform.apply_client_theme();
				triplevox.platform.ensure_watermark();
				triplevox.platform.ensure_footer();
			}
		},
	});
};

/** Strip legacy Company & SaaS entry from sidebar header dropdown. */
triplevox.platform.remove_saas_sidebar_menu_item = function () {
	try {
		const hdr = frappe.app && frappe.app.sidebar && frappe.app.sidebar.sidebar_header;
		if (!hdr || !Array.isArray(hdr.dropdown_items)) return;
		const before = hdr.dropdown_items.length;
		hdr.dropdown_items = hdr.dropdown_items.filter((it) => {
			const label = (it.label || "").toLowerCase();
			return !label.includes("company & saas");
		});
		if (hdr.dropdown_items.length !== before) {
			if (typeof hdr.make_dropdown === "function") hdr.make_dropdown();
			else if (typeof hdr.setup_dropdown === "function") hdr.setup_dropdown();
		}
	} catch (e) {
		/* ignore */
	}
};

/** @deprecated — Company & SaaS is a desktop icon under System Administration */
triplevox.platform.inject_saas_menu_item = function () {
	triplevox.platform.remove_saas_sidebar_menu_item();
};

// Kept as no-op aliases so older callers do not throw
triplevox.platform.ensure_company_switcher = function () {
	$("#tvx-company-switcher").remove();
	triplevox.platform.remove_saas_sidebar_menu_item();
};
triplevox.platform.refresh_company_switcher_label = function () {
	/* floating pill removed */
};

triplevox.platform.open_company_menu = function () {
	frappe.call({
		method: "triplevox_platform.api.list_switchable_companies",
		freeze: false,
		callback: (r) => {
			const data = r.message || {};
			const companies = data.companies || [];
			const actions = companies.map((c) => ({
				label: c.active ? `✓ ${c.company}` : c.company,
				description:
					(c.client_full_name && c.client_full_name !== c.company
						? c.client_full_name + " · "
						: "") + (c.factory_area || c.client_key || ""),
				action: () => {
					if (c.active) return;
					triplevox.platform.switch_company(c.company);
				},
			}));
			actions.push({ label: "────────", action: () => {} });
			actions.push({
				label: __("Onboard sister company…"),
				action: () => triplevox.platform.open_onboarding_wizard(),
			});
			actions.push({
				label: __("Apply print pack (current)…"),
				action: () => triplevox.platform.apply_print_pack_current(),
			});
			if (frappe.user.has_role("System Manager") || frappe.session.user === "Administrator") {
				actions.push({
					label: __("Client Branding (theme / logo)…"),
					action: () => {
						frappe.set_route("List", "Client Branding");
					},
				});
				actions.push({
					label: __("Assign role pack…"),
					action: () => triplevox.platform.open_role_pack_dialog(),
				});
			}
			const d = new frappe.ui.Dialog({
				title: __("Company & SaaS"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "menu",
						options: `<div class="tvx-saas-menu"></div>`,
					},
				],
			});
			d.show();
			const $host = d.$wrapper.find(".tvx-saas-menu");
			if (!companies.length) {
				$host.append(
					`<p class="text-muted">${__(
						"No companies found. Create Company records or run onboarding."
					)}</p>`
				);
			}
			actions.forEach((item) => {
				if (item.label.indexOf("──") === 0) {
					$host.append('<hr class="tvx-saas-sep"/>');
					return;
				}
				const $a = $(
					`<button type="button" class="tvx-saas-item"><span class="tvx-saas-item-label"></span><span class="tvx-saas-item-desc"></span></button>`
				);
				$a.find(".tvx-saas-item-label").text(item.label);
				$a.find(".tvx-saas-item-desc").text(item.description || "");
				$a.on("click", () => {
					d.hide();
					item.action();
				});
				$host.append($a);
			});
		},
	});
};

triplevox.platform.switch_company = function (company) {
	frappe.call({
		method: "triplevox_platform.api.set_session_company",
		args: { company },
		freeze: true,
		freeze_message: __("Switching company…"),
		callback: (r) => {
			const boot = r.message && r.message.boot;
			if (boot) {
				frappe.boot.triplevox = boot;
				triplevox.platform.cfg = boot;
				triplevox.platform.apply_client_theme();
				triplevox.platform.ensure_watermark();
				triplevox.platform.ensure_footer();
				$(".tvx-nav-company").text(
					boot.client_full_name || boot.product_name || "TripleVox ERP"
				);
				const $welcome = $("#tvx-welcome-card");
				if ($welcome.length) {
					$welcome.remove();
					if (window.__tvx_route_desktop) triplevox.platform.on_desktop();
				}
			}
			frappe.show_alert({
				message: __("Switched to {0}", [company]),
				indicator: "green",
			});
		},
	});
};

triplevox.platform.open_onboarding_wizard = function () {
	if (!(frappe.user.has_role("System Manager") || frappe.session.user === "Administrator")) {
		frappe.msgprint(__("System Manager role required"));
		return;
	}
	const open = (profileOptions, defaultKey) => {
		const d = new frappe.ui.Dialog({
			title: __("Onboard sister company"),
			fields: [
				{
					fieldtype: "Data",
					fieldname: "company_name",
					label: __("Company name"),
					reqd: 1,
				},
				{
					fieldtype: "Data",
					fieldname: "abbr",
					label: __("Abbreviation"),
				},
				{
					fieldtype: "Select",
					fieldname: "profile_key",
					label: __("Theme profile (Client Branding key)"),
					options: profileOptions,
					default: defaultKey,
					reqd: 1,
				},
				{
					fieldtype: "Data",
					fieldname: "factory_area",
					label: __("Factory / area label"),
				},
				{
					fieldtype: "Data",
					fieldname: "logo_url",
					label: __("Logo URL (optional)"),
				},
				{
					fieldtype: "Check",
					fieldname: "apply_prints",
					label: __("Apply print pack (Letter Head + formats)"),
					default: 1,
				},
			],
			primary_action_label: __("Create / update"),
			primary_action: (values) => {
				frappe.call({
					method: "triplevox_platform.api.onboard_sister_company",
					args: {
						company_name: values.company_name,
						abbr: values.abbr,
						profile_key: values.profile_key,
						factory_area: values.factory_area,
						logo_url: values.logo_url,
						apply_prints: values.apply_prints ? 1 : 0,
					},
					freeze: true,
					callback: (r) => {
						d.hide();
						const msg = (r.message && r.message.hint) || __("Company ready");
						frappe.msgprint({
							title: __("Onboarding complete"),
							message: `${frappe.utils.escape_html(values.company_name)}<br><br>${frappe.utils.escape_html(msg)}`,
							indicator: "green",
						});
					},
				});
			},
		});
		d.show();
	};

	frappe.call({
		method: "triplevox_platform.api.list_branding_profiles",
		callback: (r) => {
			const profiles = (r.message && r.message.profiles) || [];
			if (!profiles.length) {
				frappe.msgprint({
					title: __("Create Client Branding first"),
					message: __(
						"Add at least one Client Branding row (Setup → Client Branding), then run this wizard."
					),
					indicator: "orange",
				});
				frappe.set_route("List", "Client Branding");
				return;
			}
			const options = profiles.map((p) => p.key).join("\n");
			const def =
				(profiles.find((p) => p.is_site_default) || profiles[0] || {}).key || "";
			open(options, def);
		},
	});
};

triplevox.platform.apply_print_pack_current = function () {
	const company =
		(triplevox.platform.cfg && triplevox.platform.cfg.company) ||
		frappe.defaults.get_user_default("company");
	frappe.call({
		method: "triplevox_platform.api.apply_company_print_pack",
		args: { company },
		freeze: true,
		freeze_message: __("Applying print pack…"),
		callback: (r) => {
			const lh = r.message && r.message.letter_head;
			frappe.show_alert({
				message: lh
					? __("Print pack applied ({0})", [lh])
					: __("Print pack applied"),
				indicator: "green",
			});
		},
	});
};

triplevox.platform.open_role_pack_dialog = function () {
	frappe.call({
		method: "triplevox_platform.api.list_role_packs",
		callback: (r) => {
			const packs = (r.message && r.message.packs) || [];
			const options = packs.map((p) => p.key).join("\n");
			const d = new frappe.ui.Dialog({
				title: __("Assign role pack"),
				fields: [
					{
						fieldtype: "Link",
						fieldname: "user",
						options: "User",
						label: __("User"),
						reqd: 1,
					},
					{
						fieldtype: "Select",
						fieldname: "pack_key",
						label: __("Pack"),
						options,
						reqd: 1,
						default: packs[0] && packs[0].key,
					},
					{
						fieldtype: "HTML",
						fieldname: "help",
						options: `<p class="text-muted" style="margin:0">
							Shop Floor / QC / Ops Admin add Desk roles.
							Workspace Viewer blocks workspace layout edits.
						</p>`,
					},
				],
				primary_action_label: __("Assign"),
				primary_action: (values) => {
					frappe.call({
						method: "triplevox_platform.api.assign_role_pack",
						args: { user: values.user, pack_key: values.pack_key },
						freeze: true,
						callback: (res) => {
							d.hide();
							const added = res.message && res.message.added;
							frappe.show_alert({
								message: added
									? __("Role added")
									: __("User already had this role"),
								indicator: "green",
							});
						},
					});
				},
			});
			d.show();
		},
	});
};

/** Hard onboarding gate: Administrator must create Client Branding on fresh installs. */
triplevox.platform.maybe_force_branding_onboarding = function () {
	const boot = (frappe.boot && frappe.boot.triplevox) || {};
	const isAdmin =
		frappe.session.user === "Administrator" ||
		(frappe.user && frappe.user.has_role && frappe.user.has_role("System Manager"));
	if (!isAdmin) return;
	if (!boot.needs_branding_onboarding) return;
	if (window.__tvx_branding_onboarding_shown) return;
	window.__tvx_branding_onboarding_shown = true;

	const d = new frappe.ui.Dialog({
		title: __("Client Branding required"),
		static: true,
		fields: [
			{
				fieldtype: "HTML",
				options: `<div style="line-height:1.5">
					<p>${__(
						"This TripleVox site has no Client Branding yet. Add a client profile with name, logo, accent colors, and company mapping so Desk can decorate itself."
					)}</p>
					<p class="text-muted">${__(
						"Create one Client Branding row per client (or sister company). Pick accents and logos that match each brand — you can edit these anytime from System Administration → Company & SaaS → Client Branding."
					)}</p>
				</div>`,
			},
		],
		primary_action_label: __("Open Client Branding"),
		primary_action: () => {
			d.hide();
			frappe.set_route("List", "Client Branding");
		},
	});
	d.show();
	d.$wrapper.find(".btn-modal-close, .modal-header .close").hide();
};
