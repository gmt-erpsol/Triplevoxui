/**
 * TripleVox desk shells (UI app only):
 *  1) Launchpad — grouped desktop folder (non-Frappe launcher UX)
 *  2) Account sheet — desktop avatar (admin-gated danger actions)
 *  3) Branded About — no Frappe wordmark; copyright from Client Branding
 *
 * Sidebar header: native Frappe .frappe-menu + soft watermark CSS only
 * (command panel removed — user preferred default + watermark).
 */
frappe.provide("triplevox.shell");

triplevox.shell.cfg = function () {
	return (window.triplevox && triplevox.platform && triplevox.platform.cfg) || frappe.boot.triplevox || {};
};

triplevox.shell.is_admin = function () {
	const cfg = triplevox.shell.cfg();
	if (cfg.is_system_manager) return true;
	try {
		return frappe.user.has_role("System Manager") || frappe.user.has_role("Administrator");
	} catch (e) {
		return false;
	}
};

triplevox.shell.support = function () {
	const cfg = triplevox.shell.cfg();
	const product = cfg.product_name || "TripleVox ERP";
	const label = (cfg.support_label || "").trim() || `${product} Support`;
	const email = (cfg.support_email || "").trim() || "gemtadebelaa@gmail.com";
	let url = (cfg.support_url || "").trim();
	if (!url) {
		url =
			"https://mail.google.com/mail/?view=cm&fs=1&to=" +
			encodeURIComponent(email) +
			"&su=" +
			encodeURIComponent(label);
	}
	return { label, email, url };
};

triplevox.shell.copyright = function () {
	const cfg = triplevox.shell.cfg();
	const who =
		(cfg.software_company_name || "").trim() ||
		(cfg.partner_name || "").trim() ||
		(cfg.product_name || "").trim() ||
		"TripleVox Engineering PLC";
	return `© ${who}`;
};

triplevox.shell.close_all = function () {
	$("#tvx-account-sheet, #tvx-shell-backdrop, #tvx-launchpad").remove();
	document.documentElement.classList.remove("tvx-shell-open", "tvx-launchpad-open");
	$(".desktop-modal.tvx-launchpad-host").removeClass("tvx-launchpad-host");
};

triplevox.shell.ensure_backdrop = function () {
	let $bg = $("#tvx-shell-backdrop");
	if (!$bg.length) {
		$bg = $(`<div id="tvx-shell-backdrop" aria-hidden="true"></div>`).appendTo(document.body);
	}
	$bg.off("click.tvxShell").on("click.tvxShell", () => triplevox.shell.close_all());
	document.documentElement.classList.add("tvx-shell-open");
	return $bg;
};

triplevox.shell.hide_native_menus = function () {
	$(".frappe-menu.context-menu").each(function () {
		$(this).hide().attr("data-tvx-suppressed", "1");
	});
};

triplevox.shell.apply_favicon = function () {
	const cfg = triplevox.shell.cfg();
	const url = cfg.favicon_url || cfg.product_logo_url || cfg.logo_url;
	if (!url) return;
	const href = url.includes("?") ? url : `${url}?v=${Date.now() % 1e8}`;
	let link = document.querySelector('link[rel="icon"]');
	if (!link) {
		link = document.createElement("link");
		link.rel = "icon";
		document.head.appendChild(link);
	}
	link.href = href;
	document.querySelectorAll('link[rel="shortcut icon"]').forEach((el) => {
		el.href = href;
	});
};

/* ------------------------------------------------------------------ */
/* 1) Launchpad — replace Frappe folder modal chrome                  */
/* ------------------------------------------------------------------ */

triplevox.shell.enhance_module_tray = function (modalEl) {
	/* Flyout replaced Launchpad — dismiss any folder modal that still appears */
	if (!modalEl) return;
	try {
		$(modalEl).modal("hide");
	} catch (e) {
		modalEl.classList.remove("show", "in");
		modalEl.style.display = "none";
	}
};

triplevox.shell.open_launchpad = function () {
	/* no-op: grouped icons use sticky flyout only */
	$("#tvx-launchpad").remove();
	document.documentElement.classList.remove("tvx-launchpad-open");
};

triplevox.shell.watch_module_trays = function () {
	const scan = () => {
		document.querySelectorAll(".desktop-modal").forEach((el) => {
			if ($(el).hasClass("show") || el.classList.contains("in") || $(el).is(":visible")) {
				triplevox.shell.enhance_module_tray(el);
			}
		});
	};
	scan();
	if (window.__tvx_tray_obs) return;
	let t = null;
	window.__tvx_tray_obs = new MutationObserver(() => {
		clearTimeout(t);
		t = setTimeout(scan, 40);
	});
	window.__tvx_tray_obs.observe(document.body, { childList: true, subtree: true });
};

/* ------------------------------------------------------------------ */
/* 2) Account sheet — desktop avatar only                             */
/* ------------------------------------------------------------------ */

triplevox.shell.open_account_sheet = function (anchorEl) {
	triplevox.shell.close_all();
	triplevox.shell.hide_native_menus();
	triplevox.shell.ensure_backdrop();

	const support = triplevox.shell.support();
	const admin = triplevox.shell.is_admin();
	const isDark = document.documentElement.getAttribute("data-theme") === "dark";
	const cfg = triplevox.shell.cfg();
	const fullname =
		frappe.boot.user?.full_name || frappe.session.user_fullname || frappe.session.user || "";

	let dangerHtml = "";
	if (admin) {
		const hasDemo = !!(frappe.boot.sysdefaults && frappe.boot.sysdefaults.demo_company);
		dangerHtml = `
			<section class="tvx-cmd-section tvx-cmd-admin">
				<div class="tvx-cmd-heading">${__("Admin")}</div>
				<button type="button" class="tvx-cmd-item" data-action="reset-desktop">
					<span class="tvx-cmd-ico">${frappe.utils.icon("rotate-ccw", "sm")}</span>
					<span class="tvx-cmd-label">${__("Reset Desktop Layout")}</span>
				</button>
				${
					hasDemo
						? `<button type="button" class="tvx-cmd-item tvx-cmd-danger" data-action="delete-demo">
					<span class="tvx-cmd-ico">${frappe.utils.icon("trash", "sm")}</span>
					<span class="tvx-cmd-label">${__("Delete Demo Data")}</span>
				</button>`
						: ""
				}
			</section>`;
	}

	const $sheet = $(`
		<div id="tvx-account-sheet" class="tvx-shell-panel tvx-account-sheet" role="dialog" aria-label="${__(
			"Account"
		)}">
			<div class="tvx-shell-panel-inner">
				<div class="tvx-account-head">
					${frappe.avatar(frappe.session.user, "avatar-medium")}
					<div class="tvx-account-meta">
						<div class="tvx-account-name">${frappe.utils.escape_html(fullname)}</div>
						<div class="tvx-account-sub">${frappe.utils.escape_html(
							cfg.client_full_name || cfg.product_name || ""
						)}</div>
					</div>
				</div>
				<section class="tvx-cmd-section">
					<button type="button" class="tvx-cmd-item" data-action="profile">
						<span class="tvx-cmd-ico">${frappe.utils.icon("edit", "sm")}</span>
						<span class="tvx-cmd-label">${__("Edit Profile")}</span>
					</button>
					<button type="button" class="tvx-cmd-item" data-action="theme">
						<span class="tvx-cmd-ico">${frappe.utils.icon(isDark ? "sun" : "moon", "sm")}</span>
						<span class="tvx-cmd-label">${__("Toggle Theme")}</span>
					</button>
					<button type="button" class="tvx-cmd-item" data-action="about">
						<span class="tvx-cmd-ico">${frappe.utils.icon("info", "sm")}</span>
						<span class="tvx-cmd-label">${__("About")}</span>
					</button>
				</section>
				<section class="tvx-cmd-section">
					<button type="button" class="tvx-cmd-item" data-action="support">
						<span class="tvx-cmd-ico">${frappe.utils.icon("support", "sm")}</span>
						<span class="tvx-cmd-label">${frappe.utils.escape_html(support.label)}</span>
					</button>
					<button type="button" class="tvx-cmd-item tvx-cmd-danger" data-action="logout">
						<span class="tvx-cmd-ico">${frappe.utils.icon("logout", "sm")}</span>
						<span class="tvx-cmd-label">${__("Logout")}</span>
					</button>
				</section>
				${dangerHtml}
			</div>
		</div>
	`);

	$(document.body).append($sheet);

	const rect = (anchorEl || document.querySelector(".desktop-avatar"))?.getBoundingClientRect();
	if (rect) {
		const width = 300;
		let left = rect.right - width;
		if (left < 12) left = 12;
		$sheet.css({
			top: Math.min(rect.bottom + 8, window.innerHeight - 80) + "px",
			left: left + "px",
			width: width + "px",
		});
	}

	$sheet.on("click", ".tvx-cmd-item", function (e) {
		e.preventDefault();
		const action = this.getAttribute("data-action");
		triplevox.shell.close_all();
		triplevox.shell.run_action(action);
	});

	$(document)
		.off("keydown.tvxAcct")
		.on("keydown.tvxAcct", (e) => {
			if (e.key === "Escape") {
				triplevox.shell.close_all();
				$(document).off("keydown.tvxAcct");
			}
		});
};

triplevox.shell.run_action = function (action) {
	const support = triplevox.shell.support();
	switch (action) {
		case "theme":
			try {
				new frappe.ui.ThemeSwitcher().show();
			} catch (e) {
				/* ignore */
			}
			break;
		case "support":
			window.open(support.url, "_blank", "noopener");
			break;
		case "logout":
			frappe.app.logout();
			break;
		case "profile":
			frappe.set_route("Form", "User", frappe.session.user);
			break;
		case "about":
			triplevox.shell.show_about();
			break;
		case "reset-desktop":
			if (!triplevox.shell.is_admin()) {
				frappe.show_alert({ message: __("Admins only"), indicator: "orange" });
				return;
			}
			frappe.confirm(__("Reset desktop layout to defaults?"), () => {
				try {
					if (typeof window.reset_to_default === "function") {
						window.reset_to_default();
					}
				} catch (e) {
					/* ignore */
				}
				setTimeout(() => window.location.reload(), 500);
			});
			break;
		case "delete-demo":
			if (!triplevox.shell.is_admin()) {
				frappe.show_alert({ message: __("Admins only"), indicator: "orange" });
				return;
			}
			if (!(frappe.boot.sysdefaults && frappe.boot.sysdefaults.demo_company)) {
				frappe.show_alert({ message: __("No demo data on this site"), indicator: "orange" });
				return;
			}
			if (window.erpnext?.demo?.clear_demo) {
				erpnext.demo.clear_demo();
			}
			break;
		default:
			break;
	}
};

/* ------------------------------------------------------------------ */
/* 3) Branded About (no Frappe marketing / copyright)                 */
/* ------------------------------------------------------------------ */

triplevox.shell.show_about = function () {
	const cfg = triplevox.shell.cfg();
	const product = cfg.product_name || "TripleVox ERP";
	const logo =
		cfg.product_logo_url || cfg.logo_url || "/assets/triplevox_platform/images/triplevox-logo.png";
	const tagline =
		(cfg.welcome_kicker || "").trim() || __("Business applications for your operations.");
	const copyright = triplevox.shell.copyright();

	if (frappe.ui.misc.about_dialog) {
		try {
			frappe.ui.misc.about_dialog.hide();
		} catch (e) {
			/* ignore */
		}
		frappe.ui.misc.about_dialog = null;
	}

	const dialog = new frappe.ui.Dialog({ title: __("About") });
	$(dialog.wrapper).addClass("about-dialog tvx-about-dialog");

	$(dialog.body).html(`
		<div class="about-body tvx-about-body">
			<div class="about-frappe-section tvx-about-hero">
				<img src="${frappe.utils.escape_html(logo)}" alt="${frappe.utils.escape_html(
		product
	)}" class="tvx-about-logo" onerror="this.style.display='none'">
				<h3 class="tvx-about-product">${frappe.utils.escape_html(product)}</h3>
				<p class="about-tagline">${frappe.utils.escape_html(tagline)}</p>
			</div>
			<div class="about-info-rows">
				<div class="about-info-row">
					<div class="about-info-content">
						<div class="about-info-title">${__("System Version")}</div>
						<div class="about-info-sub" id="tvx-about-system-version">${__("Loading...")}</div>
					</div>
				</div>
			</div>
			<div class="about-section-label">${__("Installed Apps")}</div>
			<div id="tvx-about-app-versions" class="about-app-list"></div>
		</div>
	`);

	$(dialog.footer).removeClass("hide").html(`<div class="about-footer">${frappe.utils.escape_html(
		copyright
	)}</div>`);

	const renameApp = (name, app) => {
		const n = (name || "").toLowerCase();
		const title = (app?.title || "").toLowerCase();
		if (n === "frappe" || title.includes("frappe framework")) {
			return { skip: false, title: __("System Administration"), name: "system" };
		}
		if (n === "erpnext" || title === "erpnext") {
			return { skip: false, title: product, name: name };
		}
		if (n === "hrms" || title.includes("frappe hr")) {
			return { skip: false, title: "HRMS", name: name };
		}
		if (n === "triplevox_platform") {
			return { skip: false, title: product + " Platform", name: name };
		}
		let cleanTitle = app?.title || name;
		cleanTitle = String(cleanTitle)
			.replace(/Frappe HRMS/gi, "HRMS")
			.replace(/Frappe HR/gi, "HRMS")
			.replace(/Frappe Framework/gi, "System Administration")
			.replace(/\bFrappe\b/gi, product)
			.replace(/\bERPNext\b/gi, product);
		return { skip: false, title: cleanTitle, name };
	};

	const show_versions = (versions) => {
		const sys = versions.frappe || versions.erpnext || Object.values(versions)[0];
		if (sys) {
			const branch = sys.branch && !/^pr-/i.test(sys.branch) ? ` (${sys.branch})` : "";
			$("#tvx-about-system-version").text(`${product}: ${sys.version || ""}${branch}`);
		} else {
			$("#tvx-about-system-version").text(product);
		}

		const $wrap = $("#tvx-about-app-versions").empty();
		for (const app_name in versions) {
			const app = versions[app_name];
			const mapped = renameApp(app_name, app);
			if (mapped.skip) continue;
			const version_text =
				app.branch && !/^pr-/i.test(app.branch)
					? `${app.version} (${app.branch})`
					: app.version;
			const letter = (mapped.title || app_name).charAt(0).toUpperCase();
			const icon = app.logo
				? `<img src="${app.logo}" class="about-app-logo" alt="">`
				: `<div class="about-app-icon">${letter}</div>`;
			$(`<div class="about-app-row">
				${icon}
				<div class="about-app-info">
					<div class="about-app-name">${frappe.utils.escape_html(mapped.title)}</div>
					<div class="about-app-version">${frappe.utils.escape_html(mapped.name)}: ${frappe.utils.escape_html(
				version_text || ""
			)}</div>
				</div>
			</div>`).appendTo($wrap);
		}
		frappe.versions = versions;
	};

	frappe.ui.misc.about_dialog = dialog;
	dialog.on_page_show = function () {
		if (!frappe.versions) {
			frappe.call({
				method: "frappe.utils.change_log.get_versions",
				callback(r) {
					show_versions(r.message || {});
				},
			});
		} else {
			show_versions(frappe.versions);
		}
	};
	dialog.show();
};

triplevox.shell.patch_about = function () {
	frappe.provide("frappe.ui.misc");
	frappe.ui.misc.about = function () {
		triplevox.shell.show_about();
		return false;
	};
	frappe.ui.toolbar.show_about = function () {
		triplevox.shell.show_about();
		return false;
	};
};

/** Polish native Frappe sidebar menus (keep behavior; add foot + class). */
triplevox.shell.polish_native_menus = function () {
	const cfg = triplevox.shell.cfg();
	const support = triplevox.shell.support();
	const logo = cfg.product_logo_url || cfg.logo_url || "";
	document.querySelectorAll(".frappe-menu.context-menu").forEach((menu) => {
		if (menu.dataset.tvxPolished === "1") return;
		menu.dataset.tvxPolished = "1";
		menu.classList.add("tvx-menu-polished");
		if (menu.querySelector(".tvx-menu-foot")) return;
		const foot = document.createElement("div");
		foot.className = "tvx-menu-foot";
		foot.innerHTML = `${
			logo
				? `<img src="${frappe.utils.escape_html(logo)}" alt="" />`
				: ""
		}<span>${frappe.utils.escape_html(support.label)}</span>`;
		foot.addEventListener("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			window.open(support.url, "_blank", "noopener");
		});
		menu.appendChild(foot);
	});
};

triplevox.shell.watch_native_menus = function () {
	if (window.__tvx_native_menu_obs) return;
	let t = null;
	window.__tvx_native_menu_obs = new MutationObserver(() => {
		clearTimeout(t);
		t = setTimeout(() => triplevox.shell.polish_native_menus(), 40);
	});
	window.__tvx_native_menu_obs.observe(document.body, { childList: true, subtree: true });
};

/* ------------------------------------------------------------------ */
/* Intercepts — avatar only (sidebar stays native Frappe)             */
/* ------------------------------------------------------------------ */

triplevox.shell.bind_intercepts = function () {
	if (window.__tvx_shell_bound) return;
	window.__tvx_shell_bound = true;

	document.addEventListener(
		"click",
		(e) => {
			const avatar = e.target.closest?.(".desktop-avatar");
			if (avatar && !e.target.closest("#tvx-account-sheet")) {
				e.preventDefault();
				e.stopPropagation();
				e.stopImmediatePropagation();
				triplevox.shell.hide_native_menus();
				if ($("#tvx-account-sheet").length) {
					triplevox.shell.close_all();
				} else {
					triplevox.shell.open_account_sheet(avatar);
				}
			}
		},
		true
	);

	if (!window.__tvx_menu_hide_obs) {
		window.__tvx_menu_hide_obs = new MutationObserver(() => {
			if (!document.documentElement.classList.contains("tvx-shell-open")) return;
			triplevox.shell.hide_native_menus();
		});
		window.__tvx_menu_hide_obs.observe(document.body, { childList: true, subtree: true });
	}
};

triplevox.shell.init = function () {
	triplevox.shell.apply_favicon();
	triplevox.shell.patch_about();
	triplevox.shell.watch_module_trays();
	triplevox.shell.watch_native_menus();
	triplevox.shell.bind_intercepts();
};

$(document).on("app_ready", () => triplevox.shell.init());
$(() => setTimeout(() => triplevox.shell.init(), 200));
