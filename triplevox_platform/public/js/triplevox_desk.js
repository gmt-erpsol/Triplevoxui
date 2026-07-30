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

	function injectEarlyDesktopCss() {
		if (document.getElementById("tvx-early-desktop-css")) return;
		const style = document.createElement("style");
		style.id = "tvx-early-desktop-css";
		style.textContent = `
			/* Until route is known — hide sidebar to prevent theme/desktop flash */
			html:not(.tvx-chrome-ready) .body-sidebar-container {
				visibility: hidden !important;
				pointer-events: none !important;
			}
			html.tvx-on-desktop,
			html.tvx-on-desktop body {
				overflow: hidden !important;
			}
			/* Hide left sidebar before paint — stops blink on Desktop refresh */
			html.tvx-on-desktop .body-sidebar-container {
				display: none !important;
				visibility: hidden !important;
				width: 0 !important;
				min-width: 0 !important;
				max-width: 0 !important;
				overflow: hidden !important;
				pointer-events: none !important;
			}
			html.tvx-on-desktop .main-section {
				margin-left: 0 !important;
				width: 100% !important;
				max-width: 100% !important;
			}
			html.tvx-on-desktop .desktop-wrapper {
				height: calc(100dvh - var(--tvx-footer-h, 34px));
				max-height: calc(100dvh - var(--tvx-footer-h, 34px));
				overflow: hidden !important;
			}
			html.tvx-on-desktop .desktop-wrapper .desktop-container {
				display: grid !important;
				grid-template-columns: minmax(0, 1fr) 220px !important;
				grid-template-rows: minmax(172px, auto) minmax(0, 1fr) !important;
				overflow: hidden !important;
				min-height: 0 !important;
				max-height: calc(100dvh - var(--desktop-navbar-height, 52px) - var(--tvx-footer-h, 34px)) !important;
			}
			html.tvx-on-desktop .desktop-wrapper .desktop-container > .icons-container {
				grid-column: 1 !important;
				grid-row: 2 !important;
				align-self: stretch !important;
			}
			html.tvx-on-desktop .desktop-wrapper #tvx-welcome-card {
				grid-column: 1 / -1 !important;
				grid-row: 1 !important;
			}
			html.tvx-on-desktop .desktop-wrapper:not(.tvx-desktop-ready) .desktop-container > .icons-container {
				opacity: 0 !important;
				visibility: hidden !important;
			}
			html.tvx-on-desktop .desktop-wrapper:not(.tvx-desktop-ready) .desktop-container {
				opacity: 1;
			}
			html.tvx-on-desktop .desktop-wrapper.tvx-desktop-ready .desktop-container > .icons-container {
				opacity: 1 !important;
				visibility: visible !important;
				transition: opacity 0.15s ease;
			}
		`;
		(document.head || document.documentElement).appendChild(style);
	}

	function markDesktopEarly() {
		injectEarlyDesktopCss();
		if (isDesktopRoute()) {
			document.documentElement.classList.add("tvx-on-desktop");
		}
		document.documentElement.classList.add("tvx-chrome-ready");
	}

	function injectWelcomeSkeleton() {
		const container = document.querySelector(".desktop-wrapper .desktop-container");
		if (!container || container.querySelector("#tvx-welcome-card")) return;
		const sk = document.createElement("section");
		sk.id = "tvx-welcome-card";
		sk.className =
			"tvx-welcome-card tvx-welcome-hero tvx-desk-stage tvx-welcome-skeleton";
		sk.setAttribute("aria-hidden", "true");
		sk.innerHTML =
			'<div class="tvx-welcome-skeleton-inner" aria-hidden="true"></div>';
		container.insertBefore(sk, container.firstChild);
	}

	function primeDesktopShell() {
		if (!isDesktopRoute()) return;
		injectEarlyDesktopCss();
		document.body && document.body.classList.add("tvx-desktop-fit");
		const wrap = document.querySelector(".desktop-wrapper");
		if (wrap) {
			wrap.classList.add("tvx-desktop");
			injectWelcomeSkeleton();
		}
	}

	function sync() {
		const onDesktop = isDesktopRoute();
		document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);
		document.documentElement.classList.add("tvx-chrome-ready");
		if (onDesktop) {
			primeDesktopShell();
		} else {
			document.body && document.body.classList.remove("tvx-desktop-fit");
			document.querySelectorAll(".desktop-wrapper.tvx-desktop-ready").forEach((el) => {
				el.classList.remove("tvx-desktop", "tvx-desktop-ready");
			});
		}
	}

	// Mark desktop + inject hide-CSS before first paint when possible
	markDesktopEarly();
	sync();
	window.addEventListener("hashchange", sync);
	window.addEventListener("popstate", sync);

	if (!window.__tvx_desktop_shell_obs) {
		window.__tvx_desktop_shell_obs = new MutationObserver(() => primeDesktopShell());
		const boot = () => {
			const root = document.body || document.documentElement;
			window.__tvx_desktop_shell_obs.observe(root, { childList: true, subtree: true });
		};
		if (document.body) boot();
		else document.addEventListener("DOMContentLoaded", boot);
	}

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
	triplevox.platform.observe_frappe_theme();
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
	triplevox.platform.setup_workspace_viewer();
	$(window).on("resize", () => triplevox.platform.sync_footer_offset());
};

/**
 * Push client theme tokens from boot → CSS variables.
 * Color tokens follow Frappe light/dark; only structural tokens stay pinned.
 * Profiles live in client_theme.py; site_config can override per site.
 */
triplevox.platform.apply_client_theme = function () {
	const cfg = triplevox.platform.cfg || {};
	const theme = cfg.theme || {};
	const root = document.documentElement;
	const structural = {
		radius: "--tvx-radius",
	};
	// Brand accent stays across modes
	if (theme.green) root.style.setProperty("--tvx-green", theme.green);
	if (theme.green_bright) root.style.setProperty("--tvx-green-bright", theme.green_bright);

	Object.keys(structural).forEach((key) => {
		if (theme[key]) root.style.setProperty(structural[key], theme[key]);
	});

	if (cfg.client_key) {
		root.setAttribute("data-tvx-client", cfg.client_key);
	}
	triplevox.platform.sync_dark_mode_tokens();
};

/** Align TripleVox tokens with native Frappe data-theme (light / dark / automatic). */
triplevox.platform.is_dark_mode = function () {
	const root = document.documentElement;
	const mode = root.getAttribute("data-theme-mode") || "";
	const theme = root.getAttribute("data-theme") || "";
	if (theme === "dark") return true;
	if (theme === "light") return false;
	if (mode === "dark") return true;
	if (mode === "light") return false;
	if (mode === "automatic") {
		try {
			return window.matchMedia("(prefers-color-scheme: dark)").matches;
		} catch (e) {
			return false;
		}
	}
	return false;
};

triplevox.platform.sync_dark_mode_tokens = function () {
	const root = document.documentElement;
	const cfg = triplevox.platform.cfg || {};
	const theme = cfg.theme || {};
	const dark = triplevox.platform.is_dark_mode();
	document.body && document.body.classList.toggle("tvx-dark", dark);

	// Clear light-mode color pins so CSS [data-theme=dark] can win
	[
		"--tvx-sidebar",
		"--tvx-sidebar-2",
		"--tvx-green-soft",
		"--tvx-ink",
		"--tvx-muted",
		"--tvx-border",
		"--tvx-surface",
		"--tvx-page",
		"--tvx-content-panel",
		"--tvx-field-bg",
		"--tvx-field-border",
	].forEach((prop) => root.style.removeProperty(prop));

	if (!dark) {
		// Re-apply light profile colors from boot (optional client branding)
		const lightMap = {
			sidebar: "--tvx-sidebar",
			sidebar_2: "--tvx-sidebar-2",
			green_soft: "--tvx-green-soft",
			ink: "--tvx-ink",
			muted: "--tvx-muted",
			border: "--tvx-border",
			surface: "--tvx-surface",
			page: "--tvx-page",
		};
		Object.keys(lightMap).forEach((key) => {
			if (theme[key]) root.style.setProperty(lightMap[key], theme[key]);
		});
	}
};

triplevox.platform.observe_frappe_theme = function () {
	if (window.__tvx_theme_obs) return;
	const root = document.documentElement;
	const sync = () => triplevox.platform.sync_dark_mode_tokens();
	window.__tvx_theme_obs = new MutationObserver(sync);
	window.__tvx_theme_obs.observe(root, {
		attributes: true,
		attributeFilter: ["data-theme", "data-theme-mode", "class"],
	});
	try {
		window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", sync);
	} catch (e) {
		/* ignore */
	}
	// Hook Frappe theme switcher if present
	if (frappe.ui && typeof frappe.ui.set_theme === "function" && !frappe.ui.__tvx_set_theme) {
		const orig = frappe.ui.set_theme.bind(frappe.ui);
		frappe.ui.__tvx_set_theme = true;
		frappe.ui.set_theme = function (theme) {
			const out = orig(theme);
			setTimeout(sync, 0);
			setTimeout(sync, 80);
			return out;
		};
	}
	sync();
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
	$wrap.addClass("tvx-desktop-ready");
};

triplevox.platform.leave_desktop = function () {
	document.documentElement.classList.remove("tvx-on-desktop");
	document.body.classList.remove("tvx-desktop-fit");
	$(".desktop-wrapper").removeClass("tvx-desktop tvx-desktop-ready");
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
	const now = new Date();
	const timeStr = now.toLocaleTimeString(undefined, {
		hour: "2-digit",
		minute: "2-digit",
	});
	const dateStr = now.toLocaleDateString(undefined, {
		weekday: "short",
		month: "short",
		day: "numeric",
	});

	const hubs = [
		{
			route: "TITA Manufacturing",
			title: "Manufacturing",
			sub: "Plan production, Job Cards & QC in one flow.",
			accent: "mfg",
			alt: "Manufacturing",
		},
		{
			route: "Inventory & Assets",
			title: "Inventory",
			sub: "Manage stock, warehouses & assets with ease.",
			accent: "stock",
		},
		{
			route: "Employee Hub",
			title: "People & Finance",
			sub: "HR, payroll & accounts staying in sync.",
			accent: "people",
			alt: "Accounting",
		},
	];

	const cardHtml = (h, i) => `
		<button type="button" class="tvx-mugdha-card tvx-mugdha-card--${h.accent}" data-route="${frappe.utils.escape_html(
			h.route
		)}" ${h.alt ? `data-alt-route="${frappe.utils.escape_html(h.alt)}"` : ""}>
			<span class="tvx-mugdha-node" aria-hidden="true"></span>
			<span class="tvx-mugdha-ico" aria-hidden="true"></span>
			<span class="tvx-desk-hub-copy">
				<strong>${frappe.utils.escape_html(h.title)}</strong>
				<small>${frappe.utils.escape_html(h.sub)}</small>
			</span>
		</button>`;

	const html = `
		<section id="tvx-welcome-card" class="tvx-welcome-card tvx-welcome-hero tvx-desk-stage">
			<div class="tvx-desk-stage-top">
				<div class="tvx-welcome-left">
					<div class="tvx-welcome-kicker">${frappe.utils.escape_html(
						cfg.welcome_kicker || "Operations Desk"
					)}</div>
					<h1 class="tvx-welcome-title">${frappe.utils.escape_html(
						cfg.product_name || "TripleVox ERP"
					)}</h1>
					<p class="tvx-welcome-sub">${frappe.utils.escape_html(
						cfg.client_full_name || ""
					)}${cfg.factory_area ? " · " + frappe.utils.escape_html(cfg.factory_area) : ""}</p>
				</div>
				<div class="tvx-welcome-user-block">
					<span class="tvx-welcome-hello">${greeting}</span>
					<strong class="tvx-welcome-user">${frappe.utils.escape_html(user)}</strong>
				</div>
			</div>
			<div class="tvx-desk-stage-body">
				<div class="tvx-mugdha-hub" aria-label="All-in-One ERP">
					<div class="tvx-mugdha-core">
						<span class="tvx-mugdha-ring" aria-hidden="true"></span>
						<div class="tvx-mugdha-core-inner">
							<span class="tvx-mugdha-line">All-in-One</span>
							<strong>ERP</strong>
							<span class="tvx-mugdha-line">Solution</span>
						</div>
					</div>
					<div class="tvx-mugdha-rail" aria-hidden="true">
						<span class="tvx-mugdha-arc"></span>
					</div>
					<div class="tvx-mugdha-cards">${hubs.map(cardHtml).join("")}</div>
				</div>
				<aside class="tvx-desk-spotlight" aria-label="Factory spotlight">
					<div class="tvx-spot-time">${frappe.utils.escape_html(timeStr)}</div>
					<div class="tvx-spot-date">${frappe.utils.escape_html(dateStr)}</div>
					<p class="tvx-spot-client">${frappe.utils.escape_html(
						cfg.client_full_name || "TITA PP Plastic PLC"
					)}</p>
					<div class="tvx-spot-lines">
						<span>Tape</span>
						<span>Fabric</span>
						<span>Bag</span>
					</div>
					<p class="tvx-spot-tag">Woven precision — from resin to ready bags.</p>
				</aside>
			</div>
		</section>
	`;

	const $existing = $wrap.find("#tvx-welcome-card");
	if ($existing.length) {
		$existing.removeClass("tvx-welcome-skeleton").removeAttr("aria-hidden");
		$existing.replaceWith(html);
	} else {
		$container.prepend(html);
	}

	const openRoute = (label) => {
		if (!label) return false;
		const $icon = $wrap.find(`.desktop-icon[data-id="${label}"]`).first();
		if ($icon.length) {
			$icon.trigger("click");
			return true;
		}
		return false;
	};

	$wrap.find(".tvx-mugdha-card").off("click").on("click", function () {
		const route = $(this).data("route");
		const alt = $(this).data("alt-route");
		if (!openRoute(route)) openRoute(alt);
	});
};

triplevox.platform.inject_icon_heading = function ($wrap) {
	const $icons = $wrap.find(".desktop-container > .icons-container").first();
	if (!$icons.length) return;
	const count = $icons.find(".icons > .desktop-icon").length;
	const heading = `
		<div class="tvx-apps-heading">
			<div>
				<strong>Your workspace</strong>
				<p>Tap a module — folders open nested apps</p>
			</div>
			<span>${count}</span>
		</div>
	`;
	const $h = $icons.find(".tvx-apps-heading");
	if ($h.length) {
		if ($h.find("span").last().text() !== String(count)) {
			$h.replaceWith(heading);
		}
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
		if ($el.attr("data-tvx-polished") === "1") return;
		const id = $el.attr("data-id") || $el.find(".icon-title").text().trim();
		const accent = accents[id] || "slate";
		$el.attr("data-tvx-accent", accent);
		const $well = $el.find(".icon-container").first().addClass("tvx-icon-well");
		if (iconUrls[id] && !$well.find(".tvx-tabler-icon").length) {
			$well.html(
				`<img class="tvx-tabler-icon" src="${iconUrls[id]}" alt="" aria-hidden="true" />`
			);
		}
		$el.attr("data-tvx-polished", "1");
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
	const TOGGLE_SVG = `
		<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
			<rect x="3" y="4" width="18" height="16" rx="2"/>
			<path d="M15 4v16"/>
		</svg>
	`;

	const isFormRoute = () => {
		try {
			const route = frappe.get_route && frappe.get_route();
			if (route && route[0] === "Form") return true;
		} catch (e) {
			/* ignore */
		}
		const dataRoute = document.body && document.body.getAttribute("data-route");
		return Boolean(dataRoute && String(dataRoute).indexOf("Form") === 0);
	};

	const hasSidebar = () =>
		Boolean(
			document.querySelector(
				".layout-side-section .form-sidebar, .layout-side-section .form-assignments, .form-sidebar"
			)
		);

	const apply = (open) => {
		document.documentElement.classList.toggle("tvx-form-sidebar-collapsed", !open);
		document.body.classList.toggle("tvx-form-sidebar-collapsed", !open);
		try {
			sessionStorage.setItem(KEY, open ? "1" : "0");
		} catch (e) {
			/* ignore */
		}
		const $btns = $(".tvx-form-sidebar-toggle");
		$btns.toggleClass("is-open", open);
		$btns.attr("title", open ? __("Hide side panel") : __("Show side panel"));
		$btns.attr("aria-pressed", open ? "true" : "false");
		const onForm = isFormRoute();
		$(".tvx-form-sidebar-toggle-float").toggle(onForm && !open);
	};

	const toggleSidebar = (e) => {
		if (e) {
			e.preventDefault();
			e.stopPropagation();
		}
		const open = document.body.classList.contains("tvx-form-sidebar-collapsed");
		apply(open);
	};

	const ensureBtn = () => {
		if (!isFormRoute()) {
			$(".tvx-form-sidebar-toggle").hide();
			$(".tvx-form-sidebar-toggle-float").hide();
			return;
		}

		const $hosts = $(
			".page-head .page-actions, .page-head .standard-actions, .page-head .custom-actions, .page-head .page-head-content .flex"
		).filter(":visible");
		const $host = $hosts.last().length ? $hosts.last() : $(".page-head").first();

		let $btn = $(".tvx-form-sidebar-toggle:not(.tvx-form-sidebar-toggle-float)");
		if (!$btn.length) {
			$btn = $(`
				<button type="button" class="tvx-form-sidebar-toggle" aria-label="Toggle side panel">
					${TOGGLE_SVG}
				</button>
			`);
			$btn.on("click", toggleSidebar);
			if ($host.length) $host.append($btn);
			else $(".page-head").first().append($btn);
		} else if ($host.length && !$host.find(".tvx-form-sidebar-toggle:not(.tvx-form-sidebar-toggle-float)").length) {
			$host.append($btn.first());
		}
		$btn.show();

		let $float = $(".tvx-form-sidebar-toggle-float");
		if (!$float.length) {
			$float = $(`
				<button type="button" class="tvx-form-sidebar-toggle tvx-form-sidebar-toggle-float" aria-label="Show side panel" title="Show side panel">
					${TOGGLE_SVG}
				</button>
			`);
			$float.on("click", toggleSidebar);
			$("body").append($float);
		}

		let open = false;
		try {
			open = sessionStorage.getItem(KEY) === "1";
		} catch (e) {
			open = false;
		}
		apply(open);
	};

	ensureBtn();
	[40, 120, 280, 600, 1200].forEach((ms) => setTimeout(ensureBtn, ms));

	if (frappe.router && frappe.router.on) {
		frappe.router.on("change", () => setTimeout(ensureBtn, 60));
	}

	if (!window.__tvx_form_side_obs) {
		let timer = null;
		window.__tvx_form_side_obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(ensureBtn, 150);
		});
		window.__tvx_form_side_obs.observe(document.body, { childList: true, subtree: true });
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

triplevox.platform.is_workspace_viewer = function () {
	const cfg = frappe.boot.triplevox || triplevox.platform.cfg || {};
	// Only the explicit Workspace Viewer flag/role — do NOT treat every non-editor as viewer
	if (cfg.workspace_viewer === true) return true;
	try {
		const roles = frappe.boot.user?.roles || frappe.user_roles || [];
		const hasViewer = roles.includes("Workspace Viewer");
		const editors = ["System Manager", "Administrator", "Workspace Manager"];
		if (hasViewer && !roles.some((r) => editors.includes(r))) return true;
	} catch (e) {
		/* ignore */
	}
	return false;
};

/**
 * Frappe sets is_editable = !public || has_access — so private pages stay editable.
 * Patch Workspace class so Workspace Viewer never gets Edit/New.
 */
triplevox.platform.patch_workspace_class_for_viewer = function () {
	if (!frappe.views || !frappe.views.Workspace) return false;
	if (frappe.views.Workspace.__tvx_viewer_patched) return true;

	const proto = frappe.views.Workspace.prototype;
	const lock = function (ctx, pages) {
		if (!triplevox.platform.is_workspace_viewer()) return;
		ctx.has_access = false;
		ctx.has_create_access = false;
		(pages || ctx.workspaces || []).forEach((p) => {
			if (p) p.is_editable = false;
		});
	};

	const orig_setup = proto.setup;
	proto.setup = function () {
		lock(this);
		const out = orig_setup.apply(this, arguments);
		lock(this);
		return out;
	};

	const orig_setup_pages = proto.setup_pages;
	proto.setup_pages = function (all_pages) {
		const out = orig_setup_pages.apply(this, arguments);
		lock(this, all_pages);
		return out;
	};

	if (proto.setup_actions) {
		const orig_setup_actions = proto.setup_actions;
		proto.setup_actions = function (page) {
			lock(this);
			if (page) page.is_editable = false;
			return orig_setup_actions.apply(this, arguments);
		};
	}

	if (proto.show) {
		const orig_show = proto.show;
		proto.show = function () {
			lock(this);
			const out = orig_show.apply(this, arguments);
			lock(this);
			return out;
		};
	}

	frappe.views.Workspace.__tvx_viewer_patched = true;
	return true;
};

/**
 * Workspace Viewer: can open/use workspaces, cannot edit layout.
 * Hide Edit / New Workspace controls and force read-only boot flags.
 */
triplevox.platform.setup_workspace_viewer = function () {
	const enforce = () => {
		if (!triplevox.platform.is_workspace_viewer()) return false;
		document.documentElement.classList.add("tvx-workspace-viewer");
		document.body && document.body.classList.add("tvx-workspace-viewer");
		triplevox.platform.patch_workspace_class_for_viewer();

		if (frappe.boot.triplevox) {
			frappe.boot.triplevox.workspace_viewer = true;
			frappe.boot.triplevox.can_edit_workspaces = false;
		}
		if (frappe.boot.workspaces && typeof frappe.boot.workspaces === "object") {
			frappe.boot.workspaces.has_access = false;
			frappe.boot.workspaces.has_create_access = false;
			(frappe.boot.workspaces.pages || []).forEach((p) => {
				if (p) p.is_editable = false;
			});
		}
		if (frappe.workspace) {
			frappe.workspace.has_access = false;
			frappe.workspace.has_create_access = false;
			(frappe.workspace.workspaces || []).forEach((w) => {
				if (w) w.is_editable = false;
			});
			if (frappe.workspace.body) {
				frappe.workspace.body.removeClass("edit-mode");
			}
		}
		return true;
	};

	if (!enforce()) return;

	const hideEditChrome = () => {
		if (!enforce()) return;
		const sel =
			".btn-edit-workspace, .btn-new-workspace, .edit-mode-actions, " +
			"button[data-label='Edit'], .page-icon-group button[title*='Edit'], " +
			".layout-side-section .btn-edit-workspace";
		$(sel).addClass("hide").attr("disabled", true).hide();
		// Also hide Frappe "Edit" in workspace page actions by label
		$(".page-actions .btn, .standard-actions .btn, .custom-actions .btn").each(function () {
			const label = (($(this).text() || "") + ($(this).attr("title") || "")).toLowerCase();
			if (
				label.includes("edit") ||
				label.includes("new workspace") ||
				label.includes("create workspace")
			) {
				$(this).addClass("hide").hide();
			}
		});
		// Hide ellipsis menu Edit entries
		$(".dropdown-menu .dropdown-item, .menu-item, .popover .menu-item-label").each(function () {
			const t = ($(this).text() || "").trim().toLowerCase();
			if (t === "edit" || t === "new") {
				$(this).closest(".dropdown-item, .menu-item, li, button").hide();
			}
		});
	};

	hideEditChrome();
	[80, 250, 600, 1200, 2500].forEach((ms) => setTimeout(hideEditChrome, ms));
	// Workspace class may load after desk.js
	[100, 500, 1500, 3000].forEach((ms) =>
		setTimeout(() => triplevox.platform.patch_workspace_class_for_viewer(), ms)
	);

	if (frappe.router && frappe.router.on) {
		frappe.router.on("change", () => setTimeout(hideEditChrome, 80));
	}

	// Block client-side save attempts
	if (frappe.call && !frappe.call.__tvx_viewer_wrapped) {
		const orig = frappe.call;
		frappe.call = function (opts) {
			const method = (opts && (opts.method || opts)) || "";
			const m = String(method);
			if (
				triplevox.platform.is_workspace_viewer() &&
				(m.includes("frappe.desk.doctype.workspace.workspace") ||
					m.includes("new_page") ||
					m.includes("update_page") ||
					m.includes("delete_page") ||
					m.includes("save_customization"))
			) {
				frappe.show_alert({
					message: __("Workspace Viewer cannot edit workspace layouts"),
					indicator: "orange",
				});
				return null;
			}
			return orig.apply(this, arguments);
		};
		frappe.call.__tvx_viewer_wrapped = true;
	}

	if (!window.__tvx_ws_viewer_obs) {
		let timer = null;
		window.__tvx_ws_viewer_obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(hideEditChrome, 120);
		});
		window.__tvx_ws_viewer_obs.observe(document.body, { childList: true, subtree: true });
	}
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
	triplevox.platform.on_desktop();
	requestAnimationFrame(() => triplevox.platform.on_desktop());
	setTimeout(() => triplevox.platform.fix_app_subtitles(), 0);
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
		triplevox.platform.on_desktop();
		requestAnimationFrame(() => triplevox.platform.on_desktop());
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
	triplevox.platform.init();
	triplevox.platform.hide_frappe_promos();
	if ($(".body-sidebar").length) {
		triplevox.platform.on_sidebar_setup();
	}
	if ($(".desktop-wrapper").length) {
		triplevox.platform.on_desktop();
		requestAnimationFrame(() => triplevox.platform.on_desktop());
	}
});
