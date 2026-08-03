/**
 * TITA/TripleVox file identification
 * App: triplevox_platform
 * File: triplevox_platform/triplevox_platform/public/js/triplevox_desk.js
 * Purpose: Desk JS: brand strip, sidebar routes, watermark, dark-mode polish.
 */

/**
 * Hide left sidebar before first paint when landing on Desktop (prevents blink).
 * Uses path/hash + session hint from last route (refresh often has no hash yet).
 */
(function tvx_early_desktop_sidebar_hide() {
	function isDesktopRoute() {
		try {
			if (typeof window.__tvx_route_desktop === "boolean" && window.frappe) {
				return window.__tvx_route_desktop;
			}
			if (window.frappe && typeof frappe.get_route === "function") {
				try {
					const r = frappe.get_route();
					if (r && r.length) return String(r[0]).toLowerCase() === "desktop";
				} catch (e) {
					/* fall through */
				}
			}
			const hash = (location.hash || "").replace(/^#\/?/, "");
			const path = (location.pathname || "").replace(/\/+$/, "") || "/";
			if (hash === "desktop" || /^desktop\//i.test(hash)) return true;
			if (/\/(app|desk)\/desktop$/i.test(path)) return true;
			// Deeper desk routes are never desktop home
			if (/\/(app|desk)\/.+/i.test(path) && !/\/(app|desk)\/desktop$/i.test(path)) {
				return false;
			}
			// Bare /app or /desk (or empty hash) → desktop home
			if (/\/(app|desk)$/i.test(path) && (!hash || hash === "desktop")) return true;
			// Refresh flash: last page was Desktop and hash not yet a Form/List route
			try {
				if (
					sessionStorage.getItem("tvx_last_was_desktop") === "1" &&
					(!hash || hash === "desktop")
				) {
					return true;
				}
			} catch (e) {
				/* ignore */
			}
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
			/* Hide sidebar until non-desktop confirmed — kills Desktop refresh blink */
			html:not(.tvx-sidebar-ok) .body-sidebar-container {
				display: none !important;
				visibility: hidden !important;
				width: 0 !important;
				min-width: 0 !important;
				pointer-events: none !important;
			}
			html.tvx-on-desktop,
			html.tvx-on-desktop body {
				overflow: hidden !important;
			}
			html.tvx-on-desktop .body-sidebar-container,
			html.tvx-prefer-desktop .body-sidebar-container {
				display: none !important;
				visibility: hidden !important;
				width: 0 !important;
				min-width: 0 !important;
				max-width: 0 !important;
				overflow: hidden !important;
				pointer-events: none !important;
			}
			html.tvx-on-desktop .main-section,
			html.tvx-prefer-desktop .main-section {
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
			}
			html.tvx-on-desktop .desktop-wrapper .desktop-container > .icons-container {
				grid-column: 1 !important;
				grid-row: 2 !important;
			}
			html.tvx-on-desktop .desktop-wrapper #tvx-welcome-card {
				grid-column: 1 / -1 !important;
				grid-row: 1 !important;
			}
			html.tvx-on-desktop .desktop-wrapper:not(.tvx-desktop-ready) .desktop-container > .icons-container {
				opacity: 0 !important;
				visibility: hidden !important;
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
		const onDesktop = isDesktopRoute();
		document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);
		document.documentElement.classList.toggle("tvx-prefer-desktop", onDesktop);
		document.documentElement.classList.toggle("tvx-sidebar-ok", !onDesktop);
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
		window.__tvx_route_desktop = onDesktop;
		document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);
		document.documentElement.classList.toggle("tvx-prefer-desktop", onDesktop);
		document.documentElement.classList.toggle("tvx-sidebar-ok", !onDesktop);
		document.documentElement.classList.add("tvx-chrome-ready");
		try {
			sessionStorage.setItem("tvx_last_was_desktop", onDesktop ? "1" : "0");
		} catch (e) {
			/* ignore */
		}
		if (onDesktop) {
			primeDesktopShell();
		} else {
			document.body && document.body.classList.remove("tvx-desktop-fit");
			document.querySelectorAll(".desktop-wrapper.tvx-desktop-ready").forEach((el) => {
				el.classList.remove("tvx-desktop", "tvx-desktop-ready");
			});
		}
	}

	markDesktopEarly();
	sync();
	window.addEventListener("hashchange", sync);
	window.addEventListener("popstate", sync);

	// Form right sidebar: default CLOSED so List/Form reclaim the right gap
	try {
		const open = sessionStorage.getItem("tvx_form_sidebar_open") === "1";
		document.documentElement.classList.toggle("tvx-form-sidebar-collapsed", !open);
		document.body && document.body.classList.toggle("tvx-form-sidebar-collapsed", !open);
	} catch (e) {
		document.documentElement.classList.add("tvx-form-sidebar-collapsed");
		document.body && document.body.classList.add("tvx-form-sidebar-collapsed");
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
	triplevox.platform.polish_navbar_header();
	triplevox.platform.sync_footer_offset();
	triplevox.platform.observe_layout();
	triplevox.platform.observe_sidebar_brand();
	triplevox.platform.track_routes();
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.polish_page_chrome();
	triplevox.platform.setup_form_sidebar_toggle();
	triplevox.platform.setup_recent_toggle();
	triplevox.platform.setup_workspace_viewer();
	triplevox.platform.watch_company_branding();
	if (typeof triplevox.platform.setup_saas_ui === "function") {
		triplevox.platform.setup_saas_ui();
	}
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

	// Brand accent always (TITA blue / BRG green / custom)
	if (theme.green) root.style.setProperty("--tvx-green", theme.green);
	if (theme.green_bright) root.style.setProperty("--tvx-green-bright", theme.green_bright);
	if (theme.green) {
		root.style.setProperty("--tvx-desktop-nav", theme.green);
	}
	if (cfg.client_key) root.setAttribute("data-tvx-client", cfg.client_key);

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
	} else {
		// Soft accent for dark chips / Recent count (brand-tinted)
		const soft =
			"color-mix(in srgb, var(--tvx-green, #15803d) 28%, transparent)";
		root.style.setProperty("--tvx-green-soft", soft);
		if (theme.green_bright) {
			root.style.setProperty("--tvx-green-bright", theme.green_bright);
		}
		// Client Branding dark sidebar colors (DocType + Desk chrome)
		root.style.setProperty(
			"--tvx-sidebar",
			theme.sidebar_dark || theme.sidebar || "#0f172a"
		);
		root.style.setProperty(
			"--tvx-sidebar-2",
			theme.sidebar_2_dark || theme.sidebar_2 || "#1e293b"
		);
	}
};

triplevox.platform.observe_frappe_theme = function () {
	if (window.__tvx_theme_obs) return;
	const root = document.documentElement;
	const sync = () => {
		triplevox.platform.sync_dark_mode_tokens();
		if (triplevox.platform.refresh_desktop_theme_toggle_icon) {
			triplevox.platform.refresh_desktop_theme_toggle_icon();
		}
	};
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

/** Drop cached desktop layouts that may hide the Manufacturing launcher */
triplevox.platform.clear_stale_desktop_layout = function () {
	try {
		const key = `${frappe.session.user}:desktop`;
		const raw = localStorage.getItem(key);
		if (!raw || raw === "null" || raw === "undefined") return;
		const labels = JSON.stringify(JSON.parse(raw) || "");
		// Icon label must be "Manufacturing" (matches Workspace Sidebar). Bust old layouts.
		const needsRefresh =
			!labels.includes('"Manufacturing"') ||
			labels.includes("Manufacturing Workspace") ||
			labels.includes("TITA ERP") ||
			labels.includes("TITA Manufacturing");
		if (labels && needsRefresh) {
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
	document.documentElement.style.setProperty("--tvx-page", "#fbfbfc");
	document.documentElement.style.setProperty("--tvx-canvas", "#fbfbfc");
	document.documentElement.style.setProperty("--tvx-content-panel", "#ffffff");

	// Inject / refresh — survives stale cached CSS until hard refresh
	let style = document.getElementById("tvx-fullbleed-css");
	if (!style) {
		style = document.createElement("style");
		style.id = "tvx-fullbleed-css";
		document.head.appendChild(style);
	}
	style.textContent = `
			html { --page-max-width: 100% !important; }
			.main-section, .page-container, .page-body, .layout-main,
			.layout-main-section-wrapper, .layout-main-section, .form-layout,
			.workspace-body {
				max-width: none !important; width: 100% !important;
				margin-left: 0 !important; margin-right: 0 !important;
				padding-left: 0 !important; padding-right: 0 !important;
			}
			/* Do not force body flex / 100dvh sidebar — Frappe owns that layout */
			html.tvx-on-desktop, html.tvx-on-desktop body { overflow: hidden !important; }
			html.tvx-on-desktop .main-section,
			body.tvx-desktop-fit:not([data-route^="Form"]):not([data-route^="List"]) .main-section {
				overflow: hidden !important;
			}
			body[data-route^="Form"] .main-section,
			body[data-route^="List"] .main-section,
			body[data-route^="dashboard"] .main-section,
			body[data-route^="Dashboard"] .main-section,
			body[data-route^="query-report"] .main-section {
				overflow-y: auto !important;
			}
			.body-sidebar-container .body-sidebar {
				height: 100dvh !important;
				min-height: 100dvh !important;
				overflow: visible !important;
				display: flex !important;
				flex-direction: column !important;
			}
			.body-sidebar-container .body-sidebar-top {
				flex: 1 1 auto !important;
				min-height: 0 !important;
				overflow-y: auto !important;
				overflow-x: hidden !important;
			}
			.body-sidebar-container .body-sidebar-bottom {
				flex: 0 0 auto !important;
				margin-top: auto !important;
			}
			.layout-main-section-wrapper {
				width: 100% !important;
				max-width: none !important;
				flex: 1 1 auto !important;
				min-width: 0 !important;
			}
			html.tvx-form-sidebar-collapsed { --form-sidebar-width: 0px !important; }
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
	const cfg = triplevox.platform.cfg || {};
	const productLogo =
		cfg.product_logo_url ||
		cfg.logo_url ||
		"/assets/triplevox_platform/images/triplevox-logo.png";
	/* Bottom-left pill: sister-company / client mark */
	const clientMark =
		cfg.client_logo_url ||
		cfg.print_logo_url ||
		productLogo;
	/* Soft full-bleed + dropdown background mark */
	const watermarkBg =
		cfg.watermark_url ||
		"/assets/triplevox_platform/images/triplevox-watermark.png";
	const watermarkBgDark =
		cfg.watermark_dark_url ||
		"/assets/triplevox_platform/images/triplevox-watermark-dark.png";
	const client = cfg.client_full_name || cfg.company || cfg.product_name || "ERP";

	document.documentElement.style.setProperty("--tvx-logo-url", `url("${productLogo}")`);
	document.documentElement.style.setProperty(
		"--tvx-client-logo-url",
		`url("${clientMark}")`
	);
	document.documentElement.style.setProperty(
		"--tvx-watermark-url",
		`url("${watermarkBg}?v=20260802r")`
	);
	document.documentElement.style.setProperty(
		"--tvx-watermark-dark-url",
		`url("${watermarkBgDark}?v=20260802r")`
	);
	document.body.classList.add("tvx-has-watermark", "tvx-readable");
	if (cfg.client_key) {
		document.documentElement.setAttribute("data-tvx-client", cfg.client_key);
	}

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
		<img src="${frappe.utils.escape_html(clientMark)}" alt="" />
		<span class="tvx-wm-text">${frappe.utils.escape_html(client)}</span>
	`;

	// Remove any old content-injected marks that broke list layout
	document.querySelectorAll(".tvx-content-watermark").forEach((n) => n.remove());
	$("#tvx-company-chip").remove();
};

/** @deprecated — content host pills broke list layout; kept as no-op cleanup */
triplevox.platform.paint_content_watermarks = function () {
	document.querySelectorAll(".tvx-content-watermark").forEach((n) => n.remove());
};

triplevox.platform.ensure_footer = function () {
	const cfg = triplevox.platform.cfg || {};
	const year = new Date().getFullYear();
	const partner =
		cfg.software_company_name || cfg.partner_name || "TripleVox Engineering PLC";
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

	const brand = cfg.sidebar_title || cfg.product_name || "ERP";
	const logo =
		cfg.product_logo_url ||
		cfg.logo_url ||
		"/assets/triplevox_platform/images/triplevox-logo.png";

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

	window.__tvx_route_desktop = true;
	document.documentElement.classList.add("tvx-on-desktop", "tvx-prefer-desktop");
	document.documentElement.classList.remove("tvx-sidebar-ok");
	document.body.classList.add("tvx-desktop-fit");
	try {
		sessionStorage.setItem("tvx_last_was_desktop", "1");
	} catch (e) {
		/* ignore */
	}
	$wrap.addClass("tvx-desktop");
	triplevox.platform.clear_stale_desktop_layout();
	triplevox.platform.ensure_watermark();
	triplevox.platform.polish_desktop_navbar($wrap);
	triplevox.platform.inject_desktop_theme_toggle($wrap);
	triplevox.platform.inject_desktop_clock($wrap);
	triplevox.platform.inject_welcome($wrap);
	triplevox.platform.inject_icon_heading($wrap);
	triplevox.platform.polish_desktop_icons($wrap);
	triplevox.platform.enhance_desktop_modals();
	triplevox.platform.inject_recent($wrap);
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.sync_footer_offset();
	$wrap.addClass("tvx-desktop-ready");
};

triplevox.platform.leave_desktop = function () {
	window.__tvx_route_desktop = false;
	document.documentElement.classList.remove("tvx-on-desktop", "tvx-prefer-desktop");
	document.documentElement.classList.add("tvx-sidebar-ok");
	document.body.classList.remove("tvx-desktop-fit");
	try {
		sessionStorage.setItem("tvx_last_was_desktop", "0");
	} catch (e) {
		/* ignore */
	}
	$(".desktop-wrapper").removeClass("tvx-desktop tvx-desktop-ready");

	// Park Recent off the desktop grid (Workspace drawer or hide will reconfigure)
	const $card = $("#tvx-recent-card");
	if ($card.length) {
		$card
			.removeClass("tvx-recent-drawer")
			.addClass("tvx-recent-hidden")
			.attr("aria-hidden", "true");
		if ($card[0]) {
			$card[0].style.setProperty("display", "none", "important");
		}
		$("body").append($card);
	}
	document.documentElement.classList.remove("tvx-recent-open", "tvx-has-workspace-recent");
	$(".tvx-recent-toggle").removeClass("tvx-float-visible is-open").hide();
};

triplevox.platform.polish_desktop_navbar = function ($wrap) {
	const cfg = triplevox.platform.cfg || {};
	const theme = cfg.theme || {};
	const $nav = $wrap.find(".desktop-navbar, .navbar-container").first();
	if (!$nav.length) return;

	if (theme.green) {
		document.documentElement.style.setProperty("--tvx-desktop-nav", theme.green);
	}

	const clientLogo =
		cfg.navbar_logo_url || cfg.client_logo_url || cfg.print_logo_url || "";
	const clientName =
		cfg.client_full_name ||
		cfg.product_name ||
		cfg.software_company_name ||
		"ERP";

	let $logo = $nav.find("#tvx-nav-brand .tvx-nav-logo, #brand-logo, .app-logo").first();
	if (!$logo.length) {
		$logo = $nav.find("img").first();
	}
	if ($logo.length && !$logo.closest("#tvx-nav-brand").length) {
		const $brand = $(`
			<a href="#" id="tvx-nav-brand" class="tvx-nav-brand" title="Go to Desktop">
				<span class="tvx-nav-logo-wrap"></span>
				<span class="tvx-nav-company">${frappe.utils.escape_html(clientName)}</span>
			</a>
		`);
		$logo.addClass("tvx-nav-logo");
		if (clientLogo) {
			$logo.attr("src", clientLogo);
			$logo.attr("alt", clientName);
		}
		$brand.find(".tvx-nav-logo-wrap").append($logo);
		$nav.prepend($brand);
		$brand.on("click", triplevox.platform.go_desktop);
	} else if ($nav.find("#tvx-nav-brand").length) {
		$nav.find(".tvx-nav-company").text(clientName);
		if (clientLogo) {
			$nav.find("#tvx-nav-brand .tvx-nav-logo, #tvx-nav-brand img").attr("src", clientLogo).attr("alt", clientName);
		}
		$nav.find("#tvx-nav-brand").off("click").on("click", triplevox.platform.go_desktop);
	}

	// Keep notification bell contrast on brand navbar
	$nav.find(".desktop-notifications .nav-link, .desktop-notifications button")
		.removeClass("text-muted")
		.css({ color: "#ffffff", opacity: 1, visibility: "visible" });
};

/** Half-moon theme toggle — placed immediately before desktop notifications. */
triplevox.platform.inject_desktop_theme_toggle = function ($wrap) {
	if ($wrap.find("#tvx-desktop-theme").length) {
		triplevox.platform.refresh_desktop_theme_toggle_icon();
		return;
	}
	const $notif = $wrap.find(".desktop-notifications").first();
	if (!$notif.length) return;

	const $btn = $(`
		<button type="button" id="tvx-desktop-theme" title="${__("Toggle theme")}" aria-label="${__("Toggle theme")}">
			<svg viewBox="0 0 24 24" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
			</svg>
		</button>
	`);
	$notif.before($btn);
	$btn.on("click", function (e) {
		e.preventDefault();
		e.stopPropagation();
		triplevox.platform.toggle_desk_theme();
	});
	triplevox.platform.refresh_desktop_theme_toggle_icon();
};

triplevox.platform.refresh_desktop_theme_toggle_icon = function () {
	const $btn = $("#tvx-desktop-theme");
	if (!$btn.length) return;
	const dark = triplevox.platform.is_dark_mode();
	// Half-moon in light mode (switch to dark); sun in dark mode (switch to light)
	const svg = dark
		? `<svg viewBox="0 0 24 24" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
			<circle cx="12" cy="12" r="4"></circle>
			<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path>
		</svg>`
		: `<svg viewBox="0 0 24 24" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
			<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
		</svg>`;
	$btn.html(svg);
	$btn.attr("title", dark ? __("Switch to light") : __("Switch to dark"));
};

triplevox.platform.toggle_desk_theme = function () {
	const dark = triplevox.platform.is_dark_mode();
	const next = dark ? "light" : "dark";
	try {
		document.documentElement.setAttribute("data-theme", next);
		document.documentElement.setAttribute("data-theme-mode", next);
		if (document.body) {
			document.body.setAttribute("data-theme", next);
		}
		if (frappe.ui && typeof frappe.ui.set_theme === "function") {
			frappe.ui.set_theme(next);
		}
		if (frappe.boot && frappe.boot.user) {
			frappe.boot.user.desk_theme = next;
		}
		try {
			localStorage.setItem("desk_theme", next);
		} catch (e) {
			/* ignore */
		}
		// Persist for User when API exists (ignore failures)
		frappe.call({
			method: "frappe.core.doctype.user.user.switch_theme",
			args: { theme: next.charAt(0).toUpperCase() + next.slice(1) },
			freeze: false,
			error: () => {},
		});
	} catch (err) {
		document.documentElement.setAttribute("data-theme", next);
	}
	triplevox.platform.sync_dark_mode_tokens();
	triplevox.platform.refresh_desktop_theme_toggle_icon();
	if (triplevox.platform.sync_shell_canvas) {
		triplevox.platform.sync_shell_canvas();
	}
};

/** Force Desk navbar header image to Client Logo on every route. */
triplevox.platform.polish_navbar_header = function () {
	const cfg = triplevox.platform.cfg || {};
	const clientLogo =
		cfg.navbar_logo_url || cfg.client_logo_url || cfg.print_logo_url || "";
	if (!clientLogo) return;
	const clientName = cfg.client_full_name || cfg.product_name || "ERP";
	document
		.querySelectorAll(
			".navbar .app-logo, .navbar #brand-logo, header .app-logo, .navbar-brand img, #tvx-nav-brand .tvx-nav-logo, #tvx-nav-brand img"
		)
		.forEach((img) => {
			if (!(img instanceof HTMLImageElement)) return;
			if (img.getAttribute("src") !== clientLogo) {
				img.setAttribute("src", clientLogo);
				img.setAttribute("alt", clientName);
			}
		});
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

	const appsTitle = (cfg.apps_title || "Operations").trim();
	const hubRoute = (cfg.hub_route || appsTitle || "Home").trim();
	const hubSub =
		(cfg.hub_subtitle || "").trim() ||
		"Plan work, inventory, people & finance in one flow.";
	const hubIconRaw = (cfg.hub_icon || "Generic").trim();
	const hubAccentMap = {
		Manufacturing: "mfg",
		Education: "education",
		Healthcare: "healthcare",
		Retail: "retail",
		Services: "services",
		Generic: "generic",
		Custom: "custom",
	};
	const hubAccent = hubAccentMap[hubIconRaw] || "generic";
	const hubCustomIcon = (cfg.hub_icon_image || "").trim();
	const hubs = [
		{
			route: hubRoute,
			title: appsTitle || "Operations",
			sub: hubSub,
			accent: hubAccent,
			customIcon: hubCustomIcon,
			alt: hubRoute !== appsTitle ? appsTitle : "",
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
		)}" ${h.alt ? `data-alt-route="${frappe.utils.escape_html(h.alt)}"` : ""}${
			h.customIcon
				? ` style="--tvx-hub-custom-icon:url('${frappe.utils.escape_html(h.customIcon)}')"`
				: ""
		}>
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
						cfg.client_full_name || cfg.product_name || "TripleVox ERP"
					)}</p>
					<div class="tvx-spot-lines">
						${(function () {
							const tags = String(cfg.spotlight_tags || "")
								.split(",")
								.map((t) => t.trim())
								.filter(Boolean)
								.slice(0, 4);
							const list = tags.length
								? tags
								: ["Ops", "Stock", "People"];
							return list
								.map(
									(t) =>
										`<span>${frappe.utils.escape_html(t)}</span>`
								)
								.join("");
						})()}
					</div>
					<p class="tvx-spot-tag">${frappe.utils.escape_html(
						cfg.factory_area ||
							cfg.welcome_kicker ||
							"One desk for manufacturing, stock, people, and finance."
					)}</p>
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
				<p>Hover a folder for quick apps · click for full view</p>
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
		"Company & SaaS": "indigo",
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
		"Company & SaaS": `${base}/building-community.svg`,
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
	// Display-only: show industry hub title on the matching desktop icon when configured
	const appsTitle = (triplevox.platform.cfg || {}).apps_title || "";
	if (appsTitle) {
		$wrap
			.find(`.desktop-icon[data-id="${appsTitle}"] .icon-title`)
			.text(appsTitle);
	}

	// Company & SaaS — open SaaS dialog instead of only routing
	$wrap
		.find('.desktop-icon[data-id="Company & SaaS"]')
		.off("click.tvxSaas")
		.on("click.tvxSaas", function (e) {
			e.preventDefault();
			e.stopPropagation();
			if (triplevox.platform.open_company_menu) {
				triplevox.platform.open_company_menu();
			}
		});

	triplevox.platform.setup_folder_flyouts($wrap);
};

/** Children of a folder icon from boot (for hover strip + launchpad). */
triplevox.platform.folder_children = function (parentLabel) {
	const icons = frappe.boot.desktop_icons || [];
	const kids = icons.filter(
		(i) =>
			!i.hidden &&
			i.parent_icon === parentLabel &&
			i.label &&
			i.label !== parentLabel
	);
	// Manufacturing Link — surface nested manufacturing / TITA children when present
	if (parentLabel === "Manufacturing") {
		["Manufacturing", "TITA Manufacturing", "Manufacturing Workspace"].forEach((p) => {
			icons.forEach((i) => {
				if (
					!i.hidden &&
					i.parent_icon === p &&
					i.label !== parentLabel &&
					!kids.find((k) => k.label === i.label)
				) {
					kids.push(i);
				}
			});
		});
	}
	return kids;
};

/**
 * Folder flyout only (no Launchpad / modal select).
 * Capture-phase click blocks Frappe modal blink.
 * Open on hover; stay until click-outside / Esc / another icon hover.
 */
triplevox.platform.setup_folder_flyouts = function ($wrap) {
	const container = $wrap.find(".desktop-container > .icons-container")[0];
	if (!container) return;

	// One capture listener kills Frappe folder click before modal opens
	if (!container.__tvxFlyCapture) {
		container.__tvxFlyCapture = true;
		container.addEventListener(
			"click",
			(e) => {
				const icon = e.target.closest(".desktop-icon.tvx-has-children");
				if (!icon || !container.contains(icon)) return;
				e.preventDefault();
				e.stopPropagation();
				e.stopImmediatePropagation();
				const id = (icon.getAttribute("data-id") || "").trim();
				const kids = triplevox.platform.folder_children(id);
				if (kids.length) {
					triplevox.platform.show_folder_flyout(icon, kids, id);
				}
			},
			true
		);
	}

	const $icons = $wrap.find(".desktop-container > .icons-container .desktop-icon");

	$icons.each(function () {
		const $el = $(this);
		if ($el.data("tvxFlyBound")) return;
		const id = ($el.attr("data-id") || $el.find(".icon-title").text() || "").trim();
		if (!id) return;
		// Employee Hub stays a single launcher — no nested child strip
		if (id === "Employee Hub") {
			$el.data("tvxFlyBound", 1);
			$el.off(".tvxFly").on("mouseenter.tvxFly", () => {
				triplevox.platform.hide_folder_flyout();
			});
			return;
		}
		const kids = triplevox.platform.folder_children(id);
		$el.data("tvxFlyBound", 1);

		if (!kids.length) {
			$el.off(".tvxFly").on("mouseenter.tvxFly", () => {
				triplevox.platform.hide_folder_flyout();
			});
			return;
		}

		$el.addClass("tvx-has-children");
		$el.removeAttr("data-tvx-child-count");

		let openTimer = null;
		const show = () => {
			clearTimeout(openTimer);
			openTimer = setTimeout(() => {
				triplevox.platform.show_folder_flyout($el[0], kids, id);
			}, 90);
		};

		$el.off(".tvxFly")
			.on("mouseenter.tvxFly", show)
			.on("focusin.tvxFly", show)
			.on("mouseleave.tvxFly", () => clearTimeout(openTimer));
	});

	if (!window.__tvx_fly_outside) {
		window.__tvx_fly_outside = true;
		$(document).on("mousedown.tvxFlyOut", (e) => {
			const tip = document.getElementById("tvx-folder-flyout");
			if (!tip) return;
			const t = e.target;
			if (tip.contains(t)) return;
			if (tip._tvxAnchor && tip._tvxAnchor.contains(t)) return;
			triplevox.platform.hide_folder_flyout();
		});
		$(document).on("keydown.tvxFlyOut", (e) => {
			if (e.key === "Escape") triplevox.platform.hide_folder_flyout();
		});
	}
};

triplevox.platform.hide_folder_flyout = function (anchorEl) {
	const tip = document.getElementById("tvx-folder-flyout");
	if (!tip) return;
	if (anchorEl && tip._tvxAnchor && tip._tvxAnchor !== anchorEl) return;
	if (tip._tvxAnchor) {
		tip._tvxAnchor.classList.remove("tvx-fly-open");
	}
	tip.remove();
};

triplevox.platform.show_folder_flyout = function (anchorEl, kids, parentLabel) {
	if (!anchorEl || !kids || !kids.length) return;
	const existing = document.getElementById("tvx-folder-flyout");
	if (existing && existing._tvxAnchor === anchorEl) return;
	triplevox.platform.hide_folder_flyout();

	const title = parentLabel || anchorEl.getAttribute("data-id") || __("Apps");
	const tip = document.createElement("div");
	tip.id = "tvx-folder-flyout";
	tip.className = "tvx-folder-flyout";
	tip._tvxAnchor = anchorEl;
	tip.setAttribute("role", "dialog");
	tip.setAttribute("aria-label", title);
	anchorEl.classList.add("tvx-fly-open");
	tip.innerHTML = `
		<div class="tvx-fly-head">
			<div>
				<p class="tvx-fly-title">${frappe.utils.escape_html(title)}</p>
				<p class="tvx-fly-sub">${__("{0} apps — pick one to open", [String(kids.length)])}</p>
			</div>
			<button type="button" class="tvx-fly-close" aria-label="${__("Close")}">&times;</button>
		</div>
		<div class="tvx-fly-track" role="list">
			${kids
				.map((k) => {
					let ico = "";
					try {
						const src = frappe.utils.get_desktop_icon(
							k.label,
							frappe.boot.desktop_icon_style
						);
						if (src) {
							ico = `<img src="${frappe.utils.escape_html(src)}" alt="" />`;
						} else if (k.logo_url) {
							ico = `<img src="${frappe.utils.escape_html(k.logo_url)}" alt="" />`;
						} else {
							ico = `<span>${frappe.utils.escape_html((k.label || "?").slice(0, 1))}</span>`;
						}
					} catch (e) {
						ico = `<span>${frappe.utils.escape_html((k.label || "?").slice(0, 1))}</span>`;
					}
					return `<button type="button" class="tvx-fly-chip" role="listitem" data-label="${frappe.utils.escape_html(
						k.label
					)}" title="${frappe.utils.escape_html(k.label)}">
						<span class="tvx-fly-ico">${ico}</span>
						<span class="tvx-fly-name">${frappe.utils.escape_html(k.label)}</span>
					</button>`;
				})
				.join("")}
		</div>
	`;
	document.body.appendChild(tip);

	const place = () => {
		const r = anchorEl.getBoundingClientRect();
		const tw = tip.offsetWidth || 320;
		let left = r.left + r.width / 2 - tw / 2;
		left = Math.max(12, Math.min(left, window.innerWidth - tw - 12));
		let top = r.bottom + 10;
		if (top + tip.offsetHeight > window.innerHeight - 10) {
			top = Math.max(10, r.top - tip.offsetHeight - 10);
		}
		tip.style.left = `${left}px`;
		tip.style.top = `${top}px`;
	};
	place();
	requestAnimationFrame(place);

	const closeBtn = tip.querySelector(".tvx-fly-close");
	if (closeBtn) {
		closeBtn.addEventListener("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			triplevox.platform.hide_folder_flyout(anchorEl);
		});
	}

	tip.querySelectorAll(".tvx-fly-chip").forEach((btn) => {
		btn.addEventListener("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			const label = btn.getAttribute("data-label");
			const icon = (frappe.boot.desktop_icons || []).find((i) => i.label === label);
			triplevox.platform.hide_folder_flyout();
			if (!icon) return;
			try {
				const url = frappe.utils.get_route_for_icon(icon);
				if (url) {
					window.location.href = url.startsWith("/") ? url : `/desk/${url}`;
				}
			} catch (err) {
				/* ignore */
			}
		});
	});
};

/** Soft-brand child-icons folder popups — flyout replaces Launchpad/modal select. */
triplevox.platform.enhance_desktop_modals = function () {
	const decorate = (root) => {
		const modal = root.closest
			? root.closest(".desktop-modal") || (root.classList && root.classList.contains("desktop-modal") ? root : null)
			: null;
		const nodes = modal
			? [modal]
			: Array.from(document.querySelectorAll(".desktop-modal.show, .desktop-modal:not(.fade)"));
		nodes.forEach((el) => {
			if (!el) return;
			// Prefer flyout: dismiss native folder modal if it appears
			try {
				$(el).modal("hide");
			} catch (e) {
				el.classList.remove("show", "in");
				el.style.display = "none";
			}
		});
	};

	decorate(document.body);

	if (!window.__tvx_desktop_modal_obs) {
		let timer = null;
		window.__tvx_desktop_modal_obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(() => decorate(document.body), 40);
		});
		window.__tvx_desktop_modal_obs.observe(document.body, {
			childList: true,
			subtree: true,
		});
	}
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
		triplevox.platform.sync_shell_canvas();
	};

	scrub();
	[40, 120, 300, 600].forEach((delay) => setTimeout(scrub, delay));

	if (!window.__tvx_hrms_obs) {
		let timer = null;
		const obs = new MutationObserver(() => {
			clearTimeout(timer);
			timer = setTimeout(scrub, 200);
		});
		window.__tvx_hrms_obs = obs;
		obs.observe(document.body, { childList: true, subtree: true });
	}

	if (!window.__tvx_shell_canvas_router && frappe.router && frappe.router.on) {
		window.__tvx_shell_canvas_router = true;
		frappe.router.on("change", () => {
			[0, 80, 200, 450].forEach((ms) =>
				setTimeout(() => triplevox.platform.sync_shell_canvas(), ms)
			);
		});
	}
};

/**
 * Force header + main shell canvas.
 * Light: keep a calm shared canvas. Dark: defer to Frappe theme tokens —
 * do not paint over cards/lists with custom colors (matches default Frappe dark).
 */
triplevox.platform.sync_shell_canvas = function () {
	const dark =
		document.documentElement.getAttribute("data-theme") === "dark" ||
		document.body.getAttribute("data-theme") === "dark" ||
		triplevox.platform.is_dark_mode?.();
	const rootStyle = getComputedStyle(document.documentElement);
	const canvas = dark
		? rootStyle.getPropertyValue("--bg-color").trim() ||
			rootStyle.getPropertyValue("--neutral-bg-color").trim() ||
			""
		: "#fbfbfc";

	document.documentElement.classList.toggle("tvx-frappe-dark", !!dark);
	document.body && document.body.classList.toggle("tvx-frappe-dark", !!dark);

	if (canvas) {
		document.documentElement.style.setProperty("--tvx-canvas", canvas);
		document.documentElement.style.setProperty("--tvx-page", canvas);
		document.body && document.body.style.setProperty("--tvx-canvas", canvas);
		document.body && document.body.style.setProperty("--tvx-page", canvas);
	}

	// Dark mode: clear any leftover inline backgrounds we forced earlier
	const shell =
		".page-head, .page-head.tvx-page-head, .page-container > .page-head," +
		".page-head .container, .page-head .container-fluid, .page-head .page-head-content," +
		".page-head .page-head-content > .row, .page-head .page-title, .page-head .page-title.tvx-head-left," +
		".main-section, .body-sidebar-container + .main-section," +
		".page-container, .content.page-container, .page-body," +
		".layout-main, .layout-main-section-wrapper, .layout-main-section," +
		".layout-main-section.frappe-card, .form-layout, .std-form-layout," +
		".page-form, .list-filters, .frappe-list, .frappe-list .result-container," +
		".frappe-list .result, .form-section, .form-section .section-head, .form-section .section-body," +
		".workspace-body, .codex-editor, .report-wrapper, .dashboard-page";

	if (dark) {
		document.querySelectorAll(shell).forEach((el) => {
			el.style.removeProperty("background");
			el.style.removeProperty("background-color");
			el.style.removeProperty("background-image");
			el.style.removeProperty("border-bottom-color");
			el.style.removeProperty("box-shadow");
		});
		return;
	}

	document.querySelectorAll(shell).forEach((el) => {
		el.style.setProperty("background", canvas, "important");
		el.style.setProperty("background-color", canvas, "important");
		el.style.setProperty("background-image", "none", "important");
		el.style.setProperty("border-bottom-color", "transparent", "important");
		el.style.setProperty("box-shadow", "none", "important");
	});
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

triplevox.platform.RECENT_MAX = 10;
triplevox.platform.RECENT_TITLE = "Your recent activities";
triplevox.platform.RECENT_KEY = "tvx_recent_routes_v16";

triplevox.platform.format_recent_label = function (parts) {
	const p = (parts || []).map((x) => String(x || "").trim()).filter(Boolean);
	if (!p.length) return "Page";
	const r0 = p[0];
	if (/^list$/i.test(r0) && p[1]) return `List · ${p[1]}`;
	if (/^form$/i.test(r0) && p[1]) {
		return p[2] ? `${p[1]} · ${p[2]}` : p[1];
	}
	if (/^workspaces?$/i.test(r0)) return p[1] ? `Workspace · ${p[1]}` : "Workspace";
	if (/^query-report$/i.test(r0) && p[1]) return `Report · ${p[1]}`;
	if (/^dashboard/i.test(r0)) return p[1] ? `Dashboard · ${p[1]}` : "Dashboard";
	return p.slice(-2).join(" · ");
};

triplevox.platform.ensure_recent_shell = function () {
	let $card = $("#tvx-recent-card");
	if ($card.length) {
		$card.find(".tvx-recent-head h3").text(triplevox.platform.RECENT_TITLE);
		return $card;
	}
	$card = $(`
		<aside id="tvx-recent-card" class="tvx-recent-card" aria-label="Your recent activities">
			<div class="tvx-recent-head">
				<h3>${frappe.utils.escape_html(triplevox.platform.RECENT_TITLE)}</h3>
				<span class="tvx-recent-count">0</span>
			</div>
			<ul class="tvx-recent-list"></ul>
		</aside>
	`);
	$("body").append($card);
	return $card;
};

/** Desktop home — embed Recent in the right grid column. */
triplevox.platform.inject_recent = function ($wrap) {
	const $container = ($wrap && $wrap.find ? $wrap : $(".desktop-wrapper"))
		.find(".desktop-container")
		.first();
	if (!$container.length) return;

	document.documentElement.classList.remove("tvx-recent-open", "tvx-has-workspace-recent");
	$(".tvx-recent-toggle").removeClass("tvx-float-visible is-open").hide();

	const $card = triplevox.platform.ensure_recent_shell();
	$card
		.removeClass("tvx-recent-drawer tvx-recent-hidden")
		.attr("aria-hidden", "false");
	if ($card[0]) {
		$card[0].style.removeProperty("display");
	}
	if (!$card.parent().is($container)) {
		$container.append($card);
	}
	triplevox.platform.render_recent();
};

triplevox.platform.is_workspace_route = function () {
	const route = (frappe.get_route && frappe.get_route()) || [];
	const route0 = String(route[0] || "");
	if (/^workspaces?$/i.test(route0)) return true;
	const pageRoute = (document.body && document.body.getAttribute("data-page-route")) || "";
	if (/^Workspaces(\/|$)/i.test(pageRoute) || /^workspace(\/|$)/i.test(pageRoute)) return true;
	const dataRoute = (document.body && document.body.getAttribute("data-route")) || "";
	if (/^Workspaces(\/|$)/i.test(dataRoute) || /^workspaces?(\/|$)/i.test(dataRoute)) return true;
	return false;
};

triplevox.platform.recent_context_ok = function () {
	// Desktop embeds Recent in the home grid — no floating toggler there
	const route0 = String(((frappe.get_route && frappe.get_route()) || [])[0] || "").toLowerCase();
	if (route0 === "desktop" || window.__tvx_route_desktop === true) return false;
	if (document.documentElement.classList.contains("tvx-on-desktop")) return false;
	if ($(".desktop-wrapper .desktop-container").length && route0 === "desktop") return false;
	// All other Desk pages (Form, List, Workspace, Report, Dashboard, …)
	return true;
};

/** Recent drawer toggler — every Desk page except Desktop home. */
triplevox.platform.setup_recent_toggle = function () {
	const KEY = "tvx_recent_drawer_open";
	const TOGGLE_SVG = `
		<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
			<circle cx="12" cy="12" r="9"/>
			<path d="M12 7v5l3 2"/>
		</svg>
	`;

	const preferredOpen = () => {
		try {
			return sessionStorage.getItem(KEY) === "1";
		} catch (e) {
			return false;
		}
	};

	const apply = (open) => {
		const onDesktop =
			window.__tvx_route_desktop === true ||
			String(((frappe.get_route && frappe.get_route()) || [])[0] || "").toLowerCase() ===
				"desktop" ||
			document.documentElement.classList.contains("tvx-on-desktop");

		if (onDesktop && $(".desktop-wrapper .desktop-container").length) {
			document.documentElement.classList.remove("tvx-recent-open", "tvx-has-workspace-recent");
			$(".tvx-recent-toggle").removeClass("tvx-float-visible is-open").hide();
			return;
		}

		const ok = triplevox.platform.recent_context_ok();
		const $card = triplevox.platform.ensure_recent_shell();

		if (!ok) {
			document.documentElement.classList.remove("tvx-recent-open", "tvx-has-workspace-recent");
			$card.removeClass("tvx-recent-drawer").attr("aria-hidden", "true");
			if ($card[0]) $card[0].style.setProperty("display", "none", "important");
			$(".tvx-recent-toggle").removeClass("tvx-float-visible is-open").hide();
			return;
		}

		$card.removeClass("tvx-recent-hidden").addClass("tvx-recent-drawer");
		if (!$card.parent().is(document.body)) {
			$("body").append($card);
		}

		const show = !!open;
		document.documentElement.classList.toggle("tvx-recent-open", show);
		document.documentElement.classList.toggle("tvx-has-workspace-recent", show);
		$card.attr("aria-hidden", show ? "false" : "true");
		if ($card[0]) {
			if (show) $card[0].style.removeProperty("display");
			else $card[0].style.setProperty("display", "none", "important");
		}
		try {
			sessionStorage.setItem(KEY, open ? "1" : "0");
		} catch (e) {
			/* ignore */
		}

		let $btn = $(".tvx-recent-toggle");
		if (!$btn.length) {
			$btn = $(`
				<button type="button" class="tvx-recent-toggle" aria-label="Recent activity" title="Recent activity">
					${TOGGLE_SVG}
					<span class="tvx-recent-toggle-label">Recent</span>
				</button>
			`);
			$btn.on("click.tvxRecent", (e) => {
				e.preventDefault();
				e.stopPropagation();
				if (!triplevox.platform.recent_context_ok()) return;
				const next = !document.documentElement.classList.contains("tvx-recent-open");
				triplevox.platform._recent_drawer_apply(next);
			});
			$("body").append($btn);
		}
		$btn.show().addClass("tvx-float-visible");
		$btn.toggleClass("is-open", show);
		$btn.attr("aria-pressed", show ? "true" : "false");
		$btn.attr("title", show ? __("Hide recent activity") : __("Recent activity"));
		$btn.attr("aria-label", show ? __("Hide recent activity") : __("Recent activity"));

		triplevox.platform.render_recent();
	};

	triplevox.platform._recent_drawer_apply = apply;

	if (window.__tvx_recent_toggle_ready) {
		apply(preferredOpen());
		return;
	}
	window.__tvx_recent_toggle_ready = true;
	apply(preferredOpen());
	setTimeout(() => apply(preferredOpen()), 150);
};

triplevox.platform.hide_recent_outside_home = function () {
	// No longer hide on Form/List — Recent toggler is global except Desktop.
	// Keep helper for route hooks; only park drawer when entering Desktop.
	const route0 = String(((frappe.get_route && frappe.get_route()) || [])[0] || "").toLowerCase();
	const onDesktop =
		route0 === "desktop" ||
		window.__tvx_route_desktop === true ||
		document.documentElement.classList.contains("tvx-on-desktop");
	if (!onDesktop) return;

	document.documentElement.classList.remove("tvx-recent-open", "tvx-has-workspace-recent");
	$(".tvx-recent-toggle").removeClass("tvx-float-visible is-open").hide();
};

triplevox.platform.track_routes = function () {
	const KEY = triplevox.platform.RECENT_KEY;
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
		const label = triplevox.platform.format_recent_label(parts);
		list = list.filter((x) => x.route !== route);
		list.unshift({ route, label, parts: parts.slice(), ts: Date.now() });
		localStorage.setItem(
			KEY,
			JSON.stringify(list.slice(0, triplevox.platform.RECENT_MAX || 10))
		);
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
		list = JSON.parse(localStorage.getItem(triplevox.platform.RECENT_KEY) || "[]");
	} catch (e) {
		list = [];
	}
	list = (list || []).slice(0, triplevox.platform.RECENT_MAX || 10);
	$list.empty();
	$("#tvx-recent-card .tvx-recent-count").text(String(list.length));
	$("#tvx-recent-card .tvx-recent-head h3").text(triplevox.platform.RECENT_TITLE);
	if (!list.length) {
		$list.append(`<li class="tvx-empty">No recent pages yet</li>`);
		return;
	}
	list.forEach((item) => {
		let label = item.label || "";
		if (item.parts && item.parts.length) {
			label = triplevox.platform.format_recent_label(item.parts);
		} else if (item.route) {
			label = triplevox.platform.format_recent_label(String(item.route).split("/"));
		}
		const $li = $(
			`<li><a href="#" title="${frappe.utils.escape_html(label)}"><span class="tvx-recent-label">${frappe.utils.escape_html(label)}</span></a></li>`
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
		const onForm = isFormRoute() && hasSidebar();
		const $float = $(".tvx-form-sidebar-toggle-float");
		$float.toggleClass("is-open", open);
		$float.toggleClass("tvx-float-visible", onForm);
		$float.attr("title", open ? __("Hide side panel") : __("Show side panel"));
		$float.attr("aria-label", open ? __("Hide side panel") : __("Show side panel"));
		$float.attr("aria-pressed", open ? "true" : "false");
		if (onForm) {
			$float.show();
		} else {
			$float.hide();
		}
		// Erase legacy top-right header chip if any remains
		$(".tvx-form-sidebar-toggle:not(.tvx-form-sidebar-toggle-float)").remove();
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
		// Remove top-right header toggle permanently
		$(".tvx-form-sidebar-toggle:not(.tvx-form-sidebar-toggle-float)").remove();

		if (!isFormRoute() || !hasSidebar()) {
			$(".tvx-form-sidebar-toggle-float").hide();
			return;
		}

		let $float = $(".tvx-form-sidebar-toggle-float");
		if (!$float.length) {
			$float = $(`
				<button type="button" class="tvx-form-sidebar-toggle tvx-form-sidebar-toggle-float" aria-label="Toggle side panel" title="Toggle side panel">
					${TOGGLE_SVG}
				</button>
			`);
			$float.on("click", toggleSidebar);
			$("body").append($float);
		}

		let open = false;
		try {
			// Default CLOSED — reclaim right gap; open only when user set "1"
			open = sessionStorage.getItem(KEY) === "1";
		} catch (e) {
			open = false;
		}
		apply(open);
	};

	ensureBtn();
	setTimeout(ensureBtn, 150);

	if (frappe.router && frappe.router.on && !window.__tvx_form_side_router) {
		window.__tvx_form_side_router = true;
		frappe.router.on("change", () => setTimeout(ensureBtn, 80));
	}
	// No body MutationObserver — slows workspace / blanks pages
};

triplevox.platform.hide_frappe_promos = function () {
	$(".promotional-banners, .promotional-banner").remove();
	if (frappe.ui?.sidebar?.setup_promotional_banners) {
		frappe.ui.sidebar.setup_promotional_banners = function () {
			/* disabled — TripleVox white-label */
		};
	}
	triplevox.platform.wire_support_menu();
};

/** Product Support → email compose (from Client Branding). */
triplevox.platform.get_support_mail_url = function () {
	const cfg = triplevox.platform.cfg || {};
	if (cfg.support_url) return cfg.support_url;
	const product = cfg.product_name || "TripleVox ERP";
	const label = (cfg.support_label || "").trim() || `${product} Support`;
	const email = (cfg.support_email || "").trim() || "gemtadebelaa@gmail.com";
	return (
		"https://mail.google.com/mail/?view=cm&fs=1&to=" +
		encodeURIComponent(email) +
		"&su=" +
		encodeURIComponent(label)
	);
};
triplevox.platform.SUPPORT_MAIL_URL =
	"https://mail.google.com/mail/?view=cm&fs=1&to=gemtadebelaa@gmail.com&su=TripleVox%20ERP%20Support";

triplevox.platform.wire_support_menu = function () {
	const url = triplevox.platform.get_support_mail_url();
	const cfg = triplevox.platform.cfg || {};
	const product = (cfg.product_name || "TripleVox ERP").trim().toLowerCase();
	const supportLabel = ((cfg.support_label || "").trim() || `${cfg.product_name || "TripleVox ERP"} Support`)
		.toLowerCase();
	const match = (t) => {
		const s = String(t || "")
			.trim()
			.toLowerCase();
		return (
			s === "support" ||
			s === supportLabel ||
			s.includes("triplevox support") ||
			(product && s.includes(product) && s.includes("support")) ||
			s.endsWith(" support") ||
			s === "help"
		);
	};
	document.querySelectorAll("a, button, .dropdown-item, .menu-item-label, .item-anchor").forEach((el) => {
		if (el.dataset.tvxSupportWired) return;
		const text = (el.textContent || "") + " " + (el.getAttribute("aria-label") || "");
		if (!match(text)) return;
		el.dataset.tvxSupportWired = "1";
		$(el)
			.off("click.tvxSupport")
			.on("click.tvxSupport", (e) => {
				e.preventDefault();
				e.stopPropagation();
				window.open(url, "_blank", "noopener");
			});
	});
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
	setTimeout(hideEditChrome, 200);
	setTimeout(() => triplevox.platform.patch_workspace_class_for_viewer(), 300);

	if (frappe.router && frappe.router.on && !window.__tvx_ws_viewer_router) {
		window.__tvx_ws_viewer_router = true;
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
};

$(document).on("app_ready", () => {
	triplevox.platform.init();
	triplevox.platform.hide_frappe_promos();
	triplevox.platform.fix_app_subtitles();
});

/**
 * Re-fetch company-resolved branding (e.g. after user default company change).
 */
triplevox.platform.reload_client_profile = function () {
	return frappe
		.call({
			method: "triplevox_platform.api.get_client_boot_payload",
			freeze: false,
		})
		.then((r) => {
			const payload = r.message || {};
			frappe.boot.triplevox = payload;
			triplevox.platform.cfg = payload;
			triplevox.platform.apply_client_theme();
			triplevox.platform.ensure_watermark();
			triplevox.platform.ensure_footer();
			$(".tvx-nav-company").text(
				payload.client_full_name || payload.product_name || "TripleVox ERP"
			);
			const clientLogo = payload.client_logo_url || payload.print_logo_url || "";
			if (clientLogo) {
				$("#tvx-nav-brand .tvx-nav-logo, #tvx-nav-brand img").attr("src", clientLogo);
			}
			const $wrap = $(".desktop-wrapper");
			if ($wrap.length) {
				triplevox.platform.polish_desktop_navbar($wrap);
				triplevox.platform.inject_desktop_theme_toggle($wrap);
			}
			const $welcome = $("#tvx-welcome-card");
			if ($welcome.length) {
				$welcome.remove();
				triplevox.platform.on_desktop();
			}
			return payload;
		});
};

/** When user default company changes in Defaults, refresh chrome. */
triplevox.platform.watch_company_branding = function () {
	if (window.__tvx_company_brand_watch) return;
	window.__tvx_company_brand_watch = true;
	$(document).on("form-refresh", function (_e, frm) {
		if (!frm || !frm.doctype) return;
		if (frm.doctype !== "User" && frm.doctype !== "Employee") return;
		setTimeout(() => triplevox.platform.reload_client_profile(), 400);
	});
	// Defaults dialog / company switcher often updates localStorage + boot
	$(document).on("change", '[data-fieldname="company"]', function () {
		setTimeout(() => triplevox.platform.reload_client_profile(), 500);
	});
};

$(document).on("sidebar_setup", () => {
	setTimeout(() => {
		triplevox.platform.on_sidebar_setup();
		triplevox.platform.hide_frappe_promos();
		triplevox.platform.fix_app_subtitles();
	}, 40);
});
$(document).on("desktop_screen", () => {
	window.__tvx_route_desktop = true;
	document.documentElement.classList.add("tvx-on-desktop", "tvx-prefer-desktop");
	document.documentElement.classList.remove("tvx-sidebar-ok");
	try {
		sessionStorage.setItem("tvx_last_was_desktop", "1");
	} catch (e) {
		/* ignore */
	}
	triplevox.platform.on_desktop();
	requestAnimationFrame(() => {
		if (window.__tvx_route_desktop) triplevox.platform.on_desktop();
	});
	setTimeout(() => triplevox.platform.fix_app_subtitles(), 0);
});
$(document).on("page-change", () => {
	setTimeout(() => triplevox.platform.fix_app_subtitles(), 80);
	setTimeout(() => triplevox.platform.setup_form_sidebar_toggle(), 100);
	const route0 = frappe.get_route()?.[0];
	const onDesktop = String(route0 || "").toLowerCase() === "desktop";
	window.__tvx_route_desktop = onDesktop;
	document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);
	document.documentElement.classList.toggle("tvx-prefer-desktop", onDesktop);
	document.documentElement.classList.toggle("tvx-sidebar-ok", !onDesktop);
	try {
		sessionStorage.setItem("tvx_last_was_desktop", onDesktop ? "1" : "0");
	} catch (e) {
		/* ignore */
	}

	triplevox.platform.ensure_footer();
	triplevox.platform.ensure_watermark();
	triplevox.platform.polish_navbar_header();
	triplevox.platform.sync_footer_offset();
	triplevox.platform.hide_frappe_promos();
	triplevox.platform.paint_content_watermarks();
	triplevox.platform.wire_support_menu();
	triplevox.platform.patch_workspace_sidebar_routes();
	triplevox.platform.polish_page_chrome();
	if (onDesktop) {
		triplevox.platform.on_desktop();
		requestAnimationFrame(() => {
			if (window.__tvx_route_desktop) triplevox.platform.on_desktop();
		});
	} else {
		triplevox.platform.leave_desktop();
		document.documentElement.classList.remove("tvx-on-desktop", "tvx-prefer-desktop");
		document.documentElement.classList.add("tvx-sidebar-ok");
		document.body.classList.remove("tvx-desktop-fit");
		triplevox.platform.hide_recent_outside_home();
		triplevox.platform.setup_recent_toggle();
		if ($(".body-sidebar").length) {
			setTimeout(() => triplevox.platform.on_sidebar_setup(), 40);
		}
	}
});

$(() => {
	triplevox.platform.init();
	triplevox.platform.hide_frappe_promos();
	if ($(".body-sidebar").length) {
		triplevox.platform.on_sidebar_setup();
	}
	/* Do NOT call leave_desktop() before route is settled — that briefly
	   adds tvx-sidebar-ok and causes Desktop hard-refresh sidebar blink. */
	const route0 = frappe.get_route()?.[0];
	const routeDesktop = String(route0 || "").toLowerCase() === "desktop";
	let lastDesktop = false;
	try {
		lastDesktop = sessionStorage.getItem("tvx_last_was_desktop") === "1";
	} catch (e) {
		/* ignore */
	}
	const hasDesktopShell = !!document.querySelector(".desktop-wrapper");
	const earlyDesktop = window.__tvx_route_desktop === true;
	const onDesktop =
		routeDesktop ||
		earlyDesktop ||
		hasDesktopShell ||
		(lastDesktop && (!route0 || routeDesktop));

	window.__tvx_route_desktop = onDesktop;
	document.documentElement.classList.toggle("tvx-prefer-desktop", onDesktop);
	document.documentElement.classList.toggle("tvx-on-desktop", onDesktop);
	document.documentElement.classList.toggle("tvx-sidebar-ok", !onDesktop);
	if (onDesktop) {
		document.documentElement.classList.remove("tvx-sidebar-ok");
		document.body.classList.add("tvx-desktop-fit");
		try {
			sessionStorage.setItem("tvx_last_was_desktop", "1");
		} catch (e2) {
			/* ignore */
		}
		if (hasDesktopShell) {
			triplevox.platform.on_desktop();
			requestAnimationFrame(() => {
				if (window.__tvx_route_desktop) triplevox.platform.on_desktop();
			});
		}
	} else {
		triplevox.platform.leave_desktop();
		document.documentElement.classList.remove("tvx-on-desktop", "tvx-prefer-desktop");
		document.documentElement.classList.add("tvx-sidebar-ok");
		document.body.classList.remove("tvx-desktop-fit");
		triplevox.platform.hide_recent_outside_home();
		triplevox.platform.setup_recent_toggle();
	}
});
