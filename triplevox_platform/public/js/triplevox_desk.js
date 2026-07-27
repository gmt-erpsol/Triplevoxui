/**
 * TITA/TripleVox file identification
 * App: triplevox_platform
 * File: triplevox_platform/triplevox_platform/public/js/triplevox_desk.js
 * Purpose: Desk JS: brand strip, sidebar routes, watermark, dark-mode polish.
 */

/**
 * Hide left sidebar before first paint when landing on Desktop (prevents blink).
 * Collapse form right sidebar by default (toggle chip restores it).
 */
(function tvx_early_desktop_sidebar_hide() {
	function isDesktopRoute() {
		try {
			const hash = (location.hash || "").replace(/^#\/?/, "");
			const path = location.pathname || "";
			if (hash === "desktop" || hash.startsWith("desktop/")) return true;
			if (/\/desk\/?$/.test(path) && (!hash || hash === "desktop")) return true;
			return false;
		} catch (e) {
			return false;
		}
	}
	function sync() {
		document.documentElement.classList.toggle("tvx-on-desktop", isDesktopRoute());
	}
	sync();
	window.addEventListener("hashchange", sync);
	window.addEventListener("popstate", sync);

	// Form right sidebar: collapsed unless user opened it this session
	try {
		const open = sessionStorage.getItem("tvx_form_sidebar_open") === "1";
		document.documentElement.classList.toggle("tvx-form-sidebar-collapsed", !open);
		document.body && document.body.classList.toggle("tvx-form-sidebar-collapsed", !open);
	} catch (e) {
		document.documentElement.classList.add("tvx-form-sidebar-collapsed");
	}
})();

/**
 * TripleVox desk enhancements for Frappe v16
 * Brand strip + desktop polish. Leave default workspace sidebar-header intact.
 */
frappe.provide("triplevox.platform");

triplevox.platform.cfg = frappe.boot.triplevox || {};

triplevox.platform.go_desktop = function (e) {
	if (e) e.preventDefault();
	frappe.set_route("desktop");
};

triplevox.platform.init = function () {
	if (window.__tvx_ready) return;
	window.__tvx_ready = true;
	triplevox.platform.cfg = frappe.boot.triplevox || {};
	triplevox.platform.apply_client_theme();
	triplevox.platform.force_full_width();
	triplevox.platform.clear_stale_desktop_layout();
	triplevox.platform.ensure_watermark();
	triplevox.platform.ensure_footer();
	triplevox.platform.sync_footer_offset();
	triplevox.platform.observe_layout();
	triplevox.platform.observe_sidebar_brand();
	triplevox.platform.track_routes();
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.polish_page_chrome();
	triplevox.platform.setup_form_sidebar_toggle();
	$(window).on("resize", () => triplevox.platform.sync_footer_offset());
};

/**
 * Push client theme tokens from boot → CSS variables.
 * Profiles live in client_theme.py; site_config can override per site.
 */
triplevox.platform.apply_client_theme = function () {
	const cfg = triplevox.platform.cfg || {};
	const theme = cfg.theme || {};
	const root = document.documentElement;
	const map = {
		sidebar: "--tvx-sidebar",
		sidebar_2: "--tvx-sidebar-2",
		green: "--tvx-green",
		green_bright: "--tvx-green-bright",
		green_soft: "--tvx-green-soft",
		ink: "--tvx-ink",
		muted: "--tvx-muted",
		border: "--tvx-border",
		surface: "--tvx-surface",
		page: "--tvx-page",
		radius: "--tvx-radius",
	};
	Object.keys(map).forEach((key) => {
		if (theme[key]) root.style.setProperty(map[key], theme[key]);
	});
	if (cfg.client_key) {
		root.setAttribute("data-tvx-client", cfg.client_key);
	}
};

/** Drop cached desktop layouts that may hide nested Manufacturing icons */
triplevox.platform.clear_stale_desktop_layout = function () {
	try {
		const key = `${frappe.session.user}:desktop`;
		const raw = localStorage.getItem(key);
		if (!raw || raw === "null" || raw === "undefined") return;
		const layout = JSON.parse(raw);
		const labels = JSON.stringify(layout || "");
		// Refresh stale layouts after nesting / launcher label changes.
		if (
			labels &&
			(!labels.includes("Manufacturing Workspace") || labels.includes("TITA ERP"))
		) {
			localStorage.removeItem(key);
		}
	} catch (e) {
		/* ignore */
	}
};

/**
 * Frappe get_route() looks up workspace_sidebar_item by Desktop Icon *label*.
 * Nested icons like "Manufacturing Workspace" must use link_to ("Manufacturing").
 * Returns { route: string[], options: object } for SPA navigation (never put ?query in path).
 */
triplevox.platform.route_for_workspace_sidebar = function (sidebarName) {
	if (!sidebarName || !frappe.boot?.workspace_sidebar_item) return null;
	const sidebar = frappe.boot.workspace_sidebar_item[String(sidebarName).toLowerCase()];
	if (!sidebar?.items?.length) return null;
	const first = sidebar.items.find((i) => i.type === "Link");
	if (!first) return null;

	const options = { sidebar: sidebarName };
	try {
		if (first.link_type === "Workspace") {
			const ws = frappe.workspaces?.[frappe.router.slug(first.link_to)];
			if (!ws) return null;
			const slug = frappe.router.slug(ws.name);
			// Public → /desk/<slug>; private → /desk/private/<slug>
			if (ws.public) {
				return { route: [slug], options };
			}
			return { route: ["private", slug], options };
		}
		if (first.link_type === "DocType") {
			return { route: ["List", first.link_to], options };
		}
		if (first.link_type === "Report") {
			const is_query =
				!first.report ||
				first.report.report_type === "Query Report" ||
				first.report.report_type === "Script Report";
			if (is_query) {
				return { route: ["query-report", first.link_to], options };
			}
			return {
				route: ["List", first.report.ref_doctype, "Report", first.link_to],
				options,
			};
		}
		if (first.link_type === "Page") {
			return { route: [first.link_to], options };
		}
		if (first.link_type === "Dashboard") {
			return { route: ["dashboard-view", first.link_to], options };
		}
		if (first.link_type === "URL") {
			return { url: first.url };
		}
		return {
			route: [frappe.router.slug(String(first.link_to))],
			options,
		};
	} catch (e) {
		return null;
	}
};

triplevox.platform.navigate_to = function (target) {
	if (!target) return;
	if (target.url) {
		window.location.href = target.url;
		return;
	}
	const route = target.route || target;
	const options = target.options || null;
	if (options && typeof options === "object") {
		frappe.route_options = { ...(frappe.route_options || {}), ...options };
	}
	if (Array.isArray(route) && route.length) {
		frappe.set_route(...route);
	}
};

triplevox.platform.patch_workspace_sidebar_routes = function () {
	const icons = frappe.boot?.desktop_icons || [];
	icons.forEach((icon) => {
		if (icon.link_type !== "Workspace Sidebar" || !icon.link_to) return;
		const target = triplevox.platform.route_for_workspace_sidebar(icon.link_to);
		if (target) icon._tvx_nav = target;
	});

	const apply = () => {
		document.querySelectorAll(".desktop-icon[data-id]").forEach((node) => {
			const id = node.getAttribute("data-id");
			const icon = icons.find((i) => i.label === id);
			if (!icon?._tvx_nav) return;
			const $el = $(node);
			$el.off("click.tvxroute").on("click.tvxroute", function (e) {
				e.preventDefault();
				e.stopPropagation();
				triplevox.platform.navigate_to(icon._tvx_nav);
			});
		});
	};

	apply();
	if (!window.__tvx_route_obs) {
		let timer = null;
		const obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(apply, 250);
		});
		window.__tvx_route_obs = obs;
		const host = document.querySelector(".desktop-wrapper") || document.body;
		obs.observe(host, { childList: true, subtree: true });
	}
};

/** Always use Desk full-width; disable the narrow layout toggle. */
triplevox.platform.force_full_width = function () {
	try {
		localStorage.container_fullwidth = "true";
	} catch (e) {
		/* ignore */
	}
	document.body.classList.add("full-width", "tvx-force-fullwidth");
	document.documentElement.style.setProperty("--page-max-width", "100%");
	document.documentElement.style.setProperty("--tvx-page", "#ffffff");
	document.documentElement.style.setProperty("--tvx-content-panel", "#ffffff");

	// Inject once — survives stale cached CSS until hard refresh
	if (!document.getElementById("tvx-fullbleed-css")) {
		const style = document.createElement("style");
		style.id = "tvx-fullbleed-css";
		style.textContent = `
			html { --page-max-width: 100% !important; }
			.main-section, .page-container, .page-body, .layout-main,
			.layout-main-section-wrapper, .layout-main-section, .form-layout,
			.workspace-body {
				max-width: none !important; width: 100% !important;
				margin-left: 0 !important; margin-right: 0 !important;
				padding-left: 0 !important; padding-right: 0 !important;
			}
			html, body { height: 100% !important; max-height: 100dvh !important; overflow: hidden !important; }
			.main-section {
				overflow-x: hidden !important;
				overflow-y: auto !important;
				height: calc(100dvh - var(--tvx-footer-h, 34px)) !important;
				max-height: calc(100dvh - var(--tvx-footer-h, 34px)) !important;
			}
			.body-sidebar-container {
				height: 100dvh !important;
				overflow: hidden !important;
			}
			.std-form-layout .section-head, .std-form-layout .section-body, .form-footer {
				max-width: none !important; width: 100% !important;
				margin-left: 0 !important; margin-right: 0 !important;
			}
			.desktop-wrapper.tvx-desktop { background-color: #f4f7fa !important; }
			.desktop-wrapper .desktop-container {
				max-width: none !important; width: 100% !important;
				padding: 12px 14px 14px 14px !important; gap: 12px 14px !important;
			}
			.widget, .widget.dashboard-widget-box, .widget.chart-widget {
				border-radius: 14px !important; margin: 6px !important;
			}
		`;
		document.head.appendChild(style);
	}

	if (frappe.ui?.toolbar) {
		frappe.ui.toolbar.set_fullwidth_if_enabled = function () {
			try {
				localStorage.container_fullwidth = "true";
			} catch (e) {
				/* ignore */
			}
			$(document.body).addClass("full-width");
		};
		frappe.ui.toolbar.toggle_full_width = function () {
			// Locked on — ignore toggle to non-full-width
			frappe.ui.toolbar.set_fullwidth_if_enabled();
			frappe.show_alert({
				message: __("Full width layout is enabled by default"),
				indicator: "blue",
			});
		};
		frappe.ui.toolbar.set_fullwidth_if_enabled();
	}
};

triplevox.platform.ensure_watermark = function () {
	const cfg = triplevox.platform.cfg;
	const logo =
		cfg.logo_url || "/assets/triplevox_platform/images/triplevox-logo.png";
	const client = cfg.client_full_name || cfg.product_name || "TripleVox ERP";

	document.documentElement.style.setProperty("--tvx-logo-url", `url("${logo}")`);
	document.body.classList.add("tvx-has-watermark", "tvx-readable");

	let bg = document.getElementById("tvx-watermark-bg");
	if (!bg) {
		bg = document.createElement("div");
		bg.id = "tvx-watermark-bg";
		bg.setAttribute("aria-hidden", "true");
		document.body.prepend(bg);
	}

	let el = document.getElementById("tvx-watermark");
	if (!el) {
		el = document.createElement("div");
		el.id = "tvx-watermark";
		el.setAttribute("aria-hidden", "true");
		document.body.appendChild(el);
	}
	el.innerHTML = `
		<img src="${frappe.utils.escape_html(logo)}" alt="" />
		<span class="tvx-wm-text">${frappe.utils.escape_html(client)}</span>
	`;

	// Remove any old content-injected marks that broke list layout
	document.querySelectorAll(".tvx-content-watermark").forEach((n) => n.remove());
};

/** @deprecated — content host pills broke list layout; kept as no-op cleanup */
triplevox.platform.paint_content_watermarks = function () {
	document.querySelectorAll(".tvx-content-watermark").forEach((n) => n.remove());
};

triplevox.platform.ensure_footer = function () {
	const cfg = triplevox.platform.cfg || {};
	const year = new Date().getFullYear();
	const partner = cfg.partner_name || "TripleVox Engineering PLC";
	const html = `
		<span class="tvx-footer-left">© ${year}, Powered by <strong>${frappe.utils.escape_html(
		partner.toUpperCase()
	)}</strong></span>
		<span class="tvx-footer-right">${frappe.utils.escape_html(partner)}</span>
	`;
	let el = document.getElementById("tvx-footer");
	if (!el) {
		el = document.createElement("div");
		el.id = "tvx-footer";
		document.body.appendChild(el);
		document.body.classList.add("tvx-has-footer");
	}
	el.innerHTML = html;
	triplevox.platform.sync_footer_offset();
};

triplevox.platform.sync_footer_offset = function () {
	const footer = document.getElementById("tvx-footer");
	if (!footer) return;

	let left = 0;
	const desktop = document.querySelector(".desktop-wrapper");
	const route = (frappe.get_route && frappe.get_route()) || [];
	const desktopVisible =
		desktop &&
		desktop.getClientRects().length > 0 &&
		(route[0] === "desktop" || route.length === 0);

	if (desktopVisible) {
		left = 0;
	} else {
		const side = document.querySelector(".body-sidebar-container");
		if (side && getComputedStyle(side).display !== "none") {
			left = Math.max(0, Math.round(side.getBoundingClientRect().right));
		}
		if (!left) {
			const main = document.querySelector(".main-section");
			if (main) {
				left = Math.max(0, Math.round(main.getBoundingClientRect().left));
			}
		}
	}

	document.documentElement.style.setProperty("--tvx-footer-left", `${left}px`);
	document.documentElement.style.setProperty("--tvx-content-left", `${left}px`);
	footer.style.left = `${left}px`;
};

triplevox.platform.observe_layout = function () {
	if (window.__tvx_layout_obs) return;

	const sync = () => window.requestAnimationFrame(triplevox.platform.sync_footer_offset);
	const obs = new MutationObserver(sync);
	window.__tvx_layout_obs = obs;
	const resizeObs =
		window.ResizeObserver &&
		new ResizeObserver(() => window.requestAnimationFrame(triplevox.platform.sync_footer_offset));
	window.__tvx_resize_obs = resizeObs;

	const attach = () => {
		const side = document.querySelector(".body-sidebar-container");
		if (side) {
			obs.observe(side, {
				attributes: true,
				attributeFilter: ["class", "style"],
				subtree: true,
				childList: false,
			});
			resizeObs?.observe(side);
			const sidebar = side.querySelector(".body-sidebar");
			if (sidebar) {
				resizeObs?.observe(sidebar);
				sidebar.addEventListener("transitionend", sync);
			}
		}
		const main = document.querySelector(".main-section");
		if (main) {
			obs.observe(main, { attributes: true, attributeFilter: ["style", "class"] });
			resizeObs?.observe(main);
		}
	};

	attach();
	$(document).on("sidebar_setup page-change", () => {
		setTimeout(attach, 50);
		[0, 60, 180, 350, 700].forEach((delay) => setTimeout(sync, delay));
	});
};

/**
 * sidebar_setup fires BEFORE SidebarHeader.make() — so we re-apply after a tick
 * and keep a MutationObserver so brand stays top without needing a full refresh.
 */
triplevox.platform.observe_sidebar_brand = function () {
	if (window.__tvx_brand_obs) return;
	const ensure = () => triplevox.platform.on_sidebar_setup();
	const obs = new MutationObserver(() => {
		const side = document.querySelector(".body-sidebar");
		if (!side) return;
		const brand = side.querySelector("#tvx-sidebar-brand");
		if (!brand || side.firstElementChild !== brand) {
			ensure();
		}
	});
	window.__tvx_brand_obs = obs;

	const attach = () => {
		const side = document.querySelector(".body-sidebar");
		if (side) {
			obs.observe(side, { childList: true });
		}
	};
	attach();
	$(document).on("sidebar_setup page-change", () => setTimeout(attach, 30));
};

triplevox.platform.on_sidebar_setup = function () {
	const cfg = triplevox.platform.cfg;
	const $sidebar = $(".body-sidebar").first();
	if (!$sidebar.length) return;

	const brand = cfg.sidebar_title || cfg.product_name || "TripleVox ERP";
	const logo =
		cfg.logo_url || "/assets/triplevox_platform/images/triplevox-logo.png";

	let $brand = $sidebar.find("#tvx-sidebar-brand");
	if (!$brand.length) {
		$brand = $(`
			<a href="#" id="tvx-sidebar-brand" class="tvx-sidebar-brand" title="Go to Desktop">
				<img class="tvx-brand-logo" src="${frappe.utils.escape_html(logo)}" alt="TripleVox" />
				<span class="tvx-brand-text">${frappe.utils.escape_html(brand)}</span>
			</a>
		`);
		$brand.on("click", triplevox.platform.go_desktop);
	} else {
		$brand.find(".tvx-brand-text").text(brand);
		$brand.find(".tvx-brand-logo").attr("src", logo);
		$brand.off("click").on("click", triplevox.platform.go_desktop);
	}
	$brand.prependTo($sidebar);

	// Keep default workspace header untouched (remove any old logo injection)
	$sidebar.find(".sidebar-header img.tvx-header-logo").remove();

	triplevox.platform.sync_footer_offset();
};

triplevox.platform.on_desktop = function () {
	const $wrap = $(".desktop-wrapper");
	if (!$wrap.length) return;

	document.documentElement.classList.add("tvx-on-desktop");
	document.body.classList.add("tvx-desktop-fit");
	$wrap.addClass("tvx-desktop");
	triplevox.platform.clear_stale_desktop_layout();
	triplevox.platform.ensure_watermark();
	triplevox.platform.polish_desktop_navbar($wrap);
	triplevox.platform.inject_desktop_clock($wrap);
	triplevox.platform.inject_welcome($wrap);
	triplevox.platform.inject_icon_heading($wrap);
	triplevox.platform.polish_desktop_icons($wrap);
	triplevox.platform.inject_recent($wrap);
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.sync_footer_offset();
};

triplevox.platform.leave_desktop = function () {
	document.documentElement.classList.remove("tvx-on-desktop");
	document.body.classList.remove("tvx-desktop-fit");
};

triplevox.platform.polish_desktop_navbar = function ($wrap) {
	const cfg = triplevox.platform.cfg;
	const $nav = $wrap.find(".desktop-navbar, .navbar-container").first();
	if (!$nav.length) return;

	// Beautify / wrap brand logo and make it route home
	let $logo = $nav.find("#brand-logo, .app-logo, img[src*='triplevox']").first();
	if (!$logo.length) {
		$logo = $nav.find("img").first();
	}
	if ($logo.length && !$logo.closest("#tvx-nav-brand").length) {
		const $brand = $(`
			<a href="#" id="tvx-nav-brand" class="tvx-nav-brand" title="Go to Desktop">
				<span class="tvx-nav-logo-wrap"></span>
				<span class="tvx-nav-company">${frappe.utils.escape_html(
					cfg.client_full_name || cfg.product_name || "TripleVox ERP"
				)}</span>
			</a>
		`);
		$logo.addClass("tvx-nav-logo");
		$brand.find(".tvx-nav-logo-wrap").append($logo);
		$nav.prepend($brand);
		$brand.on("click", triplevox.platform.go_desktop);
	} else if ($nav.find("#tvx-nav-brand").length) {
		$nav
			.find(".tvx-nav-company")
			.text(cfg.client_full_name || cfg.product_name || "TripleVox ERP");
		$nav.find("#tvx-nav-brand").off("click").on("click", triplevox.platform.go_desktop);
	}
};

triplevox.platform.inject_desktop_clock = function ($wrap) {
	if ($wrap.find("#tvx-desktop-clock").length) {
		triplevox.platform.update_desktop_clock();
		return;
	}
	const $host = $wrap.find(".desktop-notifications").parent();
	if (!$host.length) return;

	const $clock = $(`
		<div id="tvx-desktop-clock" title="Date & time">
			<span class="tvx-clock-date"></span>
			<span class="tvx-clock-time"></span>
		</div>
	`);
	$host.prepend($clock);

	triplevox.platform.update_desktop_clock();
	if (!window.__tvx_clock_timer) {
		window.__tvx_clock_timer = setInterval(
			triplevox.platform.update_desktop_clock,
			1000
		);
	}
};

triplevox.platform.update_desktop_clock = function () {
	const $clock = $("#tvx-desktop-clock");
	if (!$clock.length) return;
	const now = new Date();
	$clock.find(".tvx-clock-date").text(
		now.toLocaleDateString(undefined, {
			weekday: "short",
			month: "short",
			day: "numeric",
		})
	);
	$clock.find(".tvx-clock-time").text(
		now.toLocaleTimeString(undefined, {
			hour: "2-digit",
			minute: "2-digit",
			second: "2-digit",
		})
	);
};

triplevox.platform.inject_welcome = function ($wrap) {
	const $container = $wrap.find(".desktop-container").first();
	if (!$container.length) return;

	const cfg = triplevox.platform.cfg;
	const user = frappe.session.user_fullname || frappe.session.user || "User";
	const hour = new Date().getHours();
	const greeting =
		hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

	const html = `
		<section id="tvx-welcome-card" class="tvx-welcome-card">
			<div class="tvx-welcome-left">
				<div class="tvx-welcome-kicker">${frappe.utils.escape_html(
					cfg.welcome_kicker || "Operations Desk"
				)}</div>
				<h1 class="tvx-welcome-title">${frappe.utils.escape_html(
					cfg.client_full_name || cfg.product_name || "TripleVox ERP"
				)}</h1>
				<p class="tvx-welcome-area">${frappe.utils.escape_html(cfg.factory_area || "")}</p>
			</div>
			<div class="tvx-welcome-right">
				<div class="tvx-welcome-user-block">
					<span class="tvx-welcome-hello">${greeting}</span>
					<strong class="tvx-welcome-user">${frappe.utils.escape_html(user)}</strong>
				</div>
				<div class="tvx-welcome-chips">
					<button type="button" class="tvx-chip" data-route="Manufacturing">Manufacturing</button>
					<button type="button" class="tvx-chip" data-route="CRM">CRM</button>
					<button type="button" class="tvx-chip" data-route="HRMS">HRMS</button>
				</div>
			</div>
		</section>
	`;

	const $existing = $wrap.find("#tvx-welcome-card");
	if ($existing.length) {
		$existing.replaceWith(html);
	} else {
		$container.prepend(html);
	}

	$wrap.find(".tvx-chip").off("click").on("click", function () {
		const label = $(this).data("route");
		const $icon = $wrap.find(`.desktop-icon[data-id="${label}"]`).first();
		if ($icon.length) {
			$icon.trigger("click");
		}
	});
};

triplevox.platform.inject_icon_heading = function ($wrap) {
	const $icons = $wrap.find(".desktop-container > .icons-container").first();
	if (!$icons.length) return;
	const count = $icons.find(".icons > .desktop-icon").length;
	const heading = `
		<div class="tvx-apps-heading">
			<div>
				<strong>Modules</strong>
				<p>Open a tile — folders expand to related workspaces</p>
			</div>
			<span>${count} apps</span>
		</div>
	`;
	const $h = $icons.find(".tvx-apps-heading");
	if ($h.length) {
		$h.replaceWith(heading);
	} else {
		$icons.prepend(heading);
	}
};

triplevox.platform.polish_desktop_icons = function ($wrap) {
	const base = "/assets/triplevox_platform/images/module_icons/tabler";
	const accents = {
		"System Administration": "indigo",
		"Employee Hub": "teal",
		Accounting: "blue",
		CRM: "violet",
		"Sales & Procurement": "sky",
		"Inventory & Assets": "emerald",
		Manufacturing: "orange",
		Other: "cyan",
		HRMS: "green",
	};
	const iconUrls = {
		"System Administration": `${base}/settings-cog.svg`,
		"Employee Hub": `${base}/id-badge-2.svg`,
		Accounting: `${base}/calculator.svg`,
		CRM: `${base}/users-group.svg`,
		"Sales & Procurement": `${base}/shopping-cart-dollar.svg`,
		"Inventory & Assets": `${base}/packages.svg`,
		Manufacturing: `${base}/building-factory-2.svg`,
		Other: `${base}/apps.svg`,
		HRMS: `${base}/users.svg`,
	};
	$wrap.find(".desktop-container > .icons-container .desktop-icon").each(function () {
		const $el = $(this);
		const id = $el.attr("data-id") || $el.find(".icon-title").text().trim();
		const accent = accents[id] || "slate";
		$el.attr("data-tvx-accent", accent);
		const $well = $el.find(".icon-container").first().addClass("tvx-icon-well");
		if (iconUrls[id]) {
			$well.html(
				`<img class="tvx-tabler-icon" src="${iconUrls[id]}" alt="" aria-hidden="true" />`
			);
		}
	});
};

/** Rename HR product chrome and scrub ERPNext/Frappe from visible UI text. */
triplevox.platform.polish_page_chrome = function () {
	const scrub = () => {
		triplevox.platform.scrub_vendor_branding(document.body);
		$(".page-head").addClass("tvx-page-head");
		$(".page-head .breadcrumb").addClass("tvx-breadcrumb");
		document.querySelectorAll(".page-head .page-title").forEach((el) => {
			el.classList.add("tvx-head-left");
		});
		triplevox.platform.scrub_document_title();
	};

	scrub();
	[40, 120, 300].forEach((delay) => setTimeout(scrub, delay));

	if (!window.__tvx_hrms_obs) {
		let timer = null;
		const obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(scrub, 300);
		});
		window.__tvx_hrms_obs = obs;
		obs.observe(document.body, { childList: true, subtree: true });
	}
};

/** Map vendor product names → TripleVox / HRMS / System labels (text nodes only). */
triplevox.platform.scrub_vendor_branding = function (root) {
	const product =
		(triplevox.platform.cfg && triplevox.platform.cfg.product_name) ||
		(frappe.boot && frappe.boot.app_name) ||
		"TripleVox ERP";
	const pairs = [
		[/Frappe HRMS/gi, "HRMS"],
		[/Frappe HR/gi, "HRMS"],
		[/Frappe Framework/gi, "System Administration"],
		[/Powered by Frappe/gi, "Powered by TripleVox"],
		[/Made with Frappe/gi, "Powered by TripleVox"],
		[/Possible source of error:\s*erpnext/gi, "Possible source of error: TripleVox ERP"],
		[/Possible source of error:\s*frappe/gi, "Possible source of error: System"],
		[/Possible source of error:\s*hrms/gi, "Possible source of error: HRMS"],
		[/\bERPNext\b/g, product],
		[/\bFrappe\b/g, "TripleVox"],
		[/\berpnext\b/g, "triplevox"],
	];

	const skipTag = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, INPUT: 1, CODE: 1, PRE: 1 };
	const walk = (node) => {
		if (!node) return;
		if (node.nodeType === Node.ELEMENT_NODE) {
			if (skipTag[node.tagName]) return;
			// Skip our own brand strip / known safe areas that already say TripleVox
			if (node.id === "tvx-sidebar-brand" || node.id === "tvx-nav-brand") return;
			for (let i = 0; i < node.childNodes.length; i++) walk(node.childNodes[i]);
			return;
		}
		if (node.nodeType !== Node.TEXT_NODE) return;
		let text = node.textContent;
		if (!text || (!/frappe|erpnext/i.test(text))) return;
		let next = text;
		pairs.forEach(([re, rep]) => {
			next = next.replace(re, rep);
		});
		if (next !== text) node.textContent = next;
	};
	walk(root || document.body);

	// Hide leftover navbar / help links that still advertise Frappe/ERPNext
	document.querySelectorAll("a, button, .dropdown-item, .menu-item-label").forEach((el) => {
		const t = (el.textContent || "").trim().toLowerCase();
		const href = (el.getAttribute("href") || "").toLowerCase();
		if (
			href.includes("frappe.io") ||
			href.includes("erpnext.com") ||
			href.includes("frappeframework.com") ||
			t === "frappe support" ||
			t.includes("frappe support") ||
			t === "about erpnext" ||
			t === "about frappe"
		) {
			const row = el.closest("li, .dropdown-item, .menu-item-container") || el;
			row.style.display = "none";
		}
	});
};

triplevox.platform.scrub_document_title = function () {
	const product =
		(triplevox.platform.cfg && triplevox.platform.cfg.product_name) ||
		(frappe.boot && frappe.boot.app_name) ||
		"TripleVox ERP";
	try {
		let t = document.title || "";
		if (!t) return;
		t = t
			.replace(/Frappe HRMS/gi, "HRMS")
			.replace(/Frappe HR/gi, "HRMS")
			.replace(/Frappe Framework/gi, "System Administration")
			.replace(/\bERPNext\b/g, product)
			.replace(/\bFrappe\b/g, "TripleVox");
		if (t !== document.title) document.title = t;
	} catch (e) {
		/* ignore */
	}
};

triplevox.platform.inject_recent = function ($wrap) {
	const $container = $wrap.find(".desktop-container").first();
	if (!$container.length) return;

	let $card = $wrap.find("#tvx-recent-card");
	if (!$card.length) {
		$card = $(`
			<aside id="tvx-recent-card" class="tvx-recent-card" aria-label="Recent Activity">
				<div class="tvx-recent-head">
					<h3>Recent</h3>
					<span class="tvx-recent-count">0</span>
				</div>
				<ul class="tvx-recent-list"></ul>
			</aside>
		`);
	}
	// Keep recent inside the fit-to-screen grid (not absolutely overlaid)
	if (!$card.parent().is($container)) {
		$container.append($card);
	}
	triplevox.platform.render_recent();
};

triplevox.platform.track_routes = function () {
	const KEY = "tvx_recent_routes_v16";
	const remember = () => {
		const parts = frappe.get_route() || [];
		const route = parts.join("/");
		if (!route || route === "desktop") return;
		let list = [];
		try {
			list = JSON.parse(localStorage.getItem(KEY) || "[]");
		} catch (e) {
			list = [];
		}
		const label = parts.filter(Boolean).slice(-1)[0] || route;
		list = list.filter((x) => x.route !== route);
		list.unshift({ route, label, ts: Date.now() });
		localStorage.setItem(KEY, JSON.stringify(list.slice(0, 6)));
		triplevox.platform.render_recent();
		setTimeout(() => triplevox.platform.sync_footer_offset(), 60);
	};
	frappe.router.on("change", remember);
};

triplevox.platform.render_recent = function () {
	const $list = $("#tvx-recent-card .tvx-recent-list");
	if (!$list.length) return;
	let list = [];
	try {
		list = JSON.parse(localStorage.getItem("tvx_recent_routes_v16") || "[]");
	} catch (e) {
		list = [];
	}
	$list.empty();
	$("#tvx-recent-card .tvx-recent-count").text(String(list.length));
	if (!list.length) {
		$list.append(`<li class="tvx-empty">No recent pages yet</li>`);
		return;
	}
	list.forEach((item) => {
		const $li = $(
			`<li><a href="#"><span class="tvx-recent-label">${frappe.utils.escape_html(item.label)}</span></a></li>`
		);
		$li.find("a").on("click", (e) => {
			e.preventDefault();
			frappe.set_route(...String(item.route).split("/"));
		});
		$list.append($li);
	});
};

triplevox.platform.setup_form_sidebar_toggle = function () {
	const KEY = "tvx_form_sidebar_open";
	const apply = (open) => {
		document.documentElement.classList.toggle("tvx-form-sidebar-collapsed", !open);
		document.body.classList.toggle("tvx-form-sidebar-collapsed", !open);
		try {
			sessionStorage.setItem(KEY, open ? "1" : "0");
		} catch (e) {
			/* ignore */
		}
		const $btn = $(".tvx-form-sidebar-toggle");
		$btn.toggleClass("is-open", open);
		$btn.attr("title", open ? __("Hide side panel") : __("Show side panel"));
		$btn.attr("aria-pressed", open ? "true" : "false");
	};

	const ensureBtn = () => {
		const $head = $(".page-head .page-head-content, .page-head .flex").last();
		const $actions =
			$(".page-head .page-actions, .page-head .standard-actions, .page-head .flex.col").last() ||
			$(".page-head").first();
		const $host = $actions.length ? $actions : $head;
		if (!$host.length) return;

		const hasSidebar = Boolean(
			document.querySelector(".layout-side-section .form-sidebar, .form-sidebar")
		);
		let $btn = $(".tvx-form-sidebar-toggle");
		if (!hasSidebar) {
			$btn.hide();
			return;
		}
		if (!$btn.length) {
			$btn = $(`
				<button type="button" class="tvx-form-sidebar-toggle" aria-label="Toggle side panel">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
						<rect x="3" y="4" width="18" height="16" rx="2"/>
						<path d="M15 4v16"/>
					</svg>
				</button>
			`);
			$btn.on("click", (e) => {
				e.preventDefault();
				e.stopPropagation();
				const open = document.body.classList.contains("tvx-form-sidebar-collapsed");
				apply(open);
			});
			// Prefer far right of header actions
			$host.append($btn);
		}
		$btn.show();
		let open = false;
		try {
			open = sessionStorage.getItem(KEY) === "1";
		} catch (e) {
			open = false;
		}
		apply(open);
	};

	ensureBtn();
	[40, 120, 280].forEach((ms) => setTimeout(ensureBtn, ms));

	if (!window.__tvx_form_side_obs) {
		let timer = null;
		window.__tvx_form_side_obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(ensureBtn, 200);
		});
		window.__tvx_form_side_obs.observe(document.body, { childList: true, subtree: false });
	}
};

triplevox.platform.hide_frappe_promos = function () {
	$(".promotional-banners, .promotional-banner").remove();
	if (frappe.ui?.sidebar?.setup_promotional_banners) {
		frappe.ui.sidebar.setup_promotional_banners = function () {
			/* disabled — TripleVox white-label */
		};
	}
};

/** Sidebar header/app-switcher small text: Other → TripleVox ERP; scrub vendor names */
triplevox.platform.fix_app_subtitles = function () {
	const product =
		(triplevox.platform.cfg && triplevox.platform.cfg.product_name) || "TripleVox ERP";
	const replace = (s) => {
		const v = String(s || "").trim();
		if (v === "Other" || v === "ERPNext" || v === "Frappe") return product;
		if (v === "Frappe HR" || v === "Frappe HRMS") return "HRMS";
		if (v === "Frappe Framework") return "System Administration";
		return s;
	};
	try {
		(frappe.boot.apps || []).forEach((a) => {
			if (!a) return;
			if (replace(a.title) !== a.title) a.title = replace(a.title);
			if (replace(a.app_title) !== a.app_title) a.app_title = replace(a.app_title);
		});
		const data = frappe.boot.app_data;
		if (Array.isArray(data)) {
			data.forEach((a) => {
				if (!a) return;
				if (replace(a.app_title) !== a.app_title) a.app_title = replace(a.app_title);
				if (replace(a.title) !== a.title) a.title = replace(a.title);
			});
		} else if (data && typeof data === "object") {
			Object.values(data).forEach((a) => {
				if (!a || typeof a !== "object") return;
				if (replace(a.app_title) !== a.app_title) a.app_title = replace(a.app_title);
				if (replace(a.title) !== a.title) a.title = replace(a.title);
			});
		}
		if (frappe.boot.app_name && /erpnext|frappe/i.test(frappe.boot.app_name)) {
			frappe.boot.app_name = product;
		}
	} catch (e) {
		/* ignore */
	}
	document
		.querySelectorAll(
			".sidebar-header .subtitle, .sidebar-header .header-subtitle, .app-switcher-menu .subtitle, .workspace-switcher .subtitle, .sidebar-item-subtitle, .app-switcher-menu .title, .sidebar-header .title, .sidebar-header .header-title"
		)
		.forEach((el) => {
			const t = (el.textContent || "").trim();
			const n = replace(t);
			if (n !== t) el.textContent = n;
		});
	document.querySelectorAll(".sidebar-header, .app-switcher-dropdown, .app-switcher-menu").forEach((root) => {
		root.querySelectorAll("div, span, p, small").forEach((el) => {
			if ((el.childNodes || []).length !== 1) return;
			const t = (el.textContent || "").trim();
			const n = replace(t);
			if (n !== t) el.textContent = n;
		});
	});
	triplevox.platform.scrub_vendor_branding(document.body);
};

$(document).on("app_ready", () => {
	triplevox.platform.init();
	triplevox.platform.hide_frappe_promos();
	triplevox.platform.fix_app_subtitles();
});
$(document).on("sidebar_setup", () => {
	// Header is created AFTER this event — apply immediately and again shortly after
	[0, 30, 120, 300].forEach((ms) =>
		setTimeout(() => {
			triplevox.platform.on_sidebar_setup();
			triplevox.platform.hide_frappe_promos();
			triplevox.platform.fix_app_subtitles();
		}, ms)
	);
});
$(document).on("desktop_screen", () => {
	setTimeout(() => triplevox.platform.on_desktop(), 60);
	setTimeout(() => triplevox.platform.fix_app_subtitles(), 80);
});
$(document).on("page-change", () => {
	setTimeout(() => triplevox.platform.fix_app_subtitles(), 80);
	setTimeout(() => triplevox.platform.setup_form_sidebar_toggle(), 100);
	const route0 = frappe.get_route()?.[0];
	const onDesktop =
		Boolean($(".desktop-wrapper").length) &&
		(route0 === "desktop" || !route0);
	document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);

	triplevox.platform.ensure_footer();
	triplevox.platform.ensure_watermark();
	triplevox.platform.sync_footer_offset();
	triplevox.platform.hide_frappe_promos();
	triplevox.platform.paint_content_watermarks();
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.polish_page_chrome();
	if (onDesktop) {
		setTimeout(() => triplevox.platform.on_desktop(), 80);
	} else {
		triplevox.platform.leave_desktop();
		if ($(".body-sidebar").length) {
			[0, 40, 160].forEach((ms) =>
				setTimeout(() => triplevox.platform.on_sidebar_setup(), ms)
			);
		}
	}
});

$(() => {
	setTimeout(() => {
		triplevox.platform.init();
		triplevox.platform.hide_frappe_promos();
		if ($(".body-sidebar").length) {
			triplevox.platform.on_sidebar_setup();
		}
		if ($(".desktop-wrapper").length) {
			triplevox.platform.on_desktop();
		}
	}, 300);
});
