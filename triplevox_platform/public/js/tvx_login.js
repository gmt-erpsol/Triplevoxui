/**
 * TripleVox login — auth panels + light/dark theme.
 * Company block is a static showcase (no branding switcher).
 */
(function () {
	const THEME_KEY = "tvx_login_theme";

	function markPage() {
		document.documentElement.classList.add("tvx-login");
		if (!document.body) return;
		document.body.classList.add("tvx-login");
		document.body.setAttribute("data-path", "login");
	}

	function systemPrefersDark() {
		try {
			return window.matchMedia("(prefers-color-scheme: dark)").matches;
		} catch (e) {
			return false;
		}
	}

	function getStoredTheme() {
		try {
			return localStorage.getItem(THEME_KEY);
		} catch (e) {
			return null;
		}
	}

	function applyTheme(theme) {
		const root = document.documentElement;
		const dark = theme === "dark" || (!theme && systemPrefersDark());
		root.setAttribute("data-tvx-login-theme", dark ? "dark" : "light");
		root.classList.toggle("tvx-login-dark", dark);
		root.classList.add("tvx-login");
	}

	function initTheme() {
		applyTheme(getStoredTheme());
		const btn = document.querySelector(".tvx-login-theme-toggle");
		if (!btn) return;
		btn.addEventListener("click", function () {
			const next =
				document.documentElement.getAttribute("data-tvx-login-theme") === "dark"
					? "light"
					: "dark";
			try {
				localStorage.setItem(THEME_KEY, next);
			} catch (e) {
				/* ignore */
			}
			applyTheme(next);
		});
	}

	function activeRoute() {
		var hash = (window.location.hash || "#login").replace(/^#/, "");
		if (!hash || hash === "login") return "login";
		if (hash.indexOf("forgot") === 0) return "forgot";
		if (hash.indexOf("signup") === 0) return "signup";
		if (hash.indexOf("login-with-email-link") === 0) return "login-with-email-link";
		if (hash.indexOf("email") === 0) return "email";
		return "login";
	}

	function syncAuthPanels() {
		var shell = document.querySelector(".tvx-login-shell");
		if (!shell) return;
		var route = activeRoute();
		shell.setAttribute("data-auth", route);

		var map = {
			login: ".for-login",
			forgot: ".for-forgot",
			signup: ".for-signup",
			"login-with-email-link": ".for-login-with-email-link",
			email: ".for-email-login",
		};

		Object.keys(map).forEach(function (key) {
			var el = shell.querySelector(map[key]);
			if (!el) return;
			if (key === route) el.classList.remove("hide");
			else el.classList.add("hide");
		});

		var forgotForm = shell.querySelector(".form-forgot");
		if (forgotForm) {
			if (route === "forgot") forgotForm.classList.remove("hide");
			else forgotForm.classList.add("hide");
		}
	}

	function boot() {
		markPage();
		initTheme();
		syncAuthPanels();
	}

	applyTheme(getStoredTheme());
	markPage();

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", boot);
	} else {
		boot();
	}
	window.addEventListener("hashchange", syncAuthPanels);
	setTimeout(syncAuthPanels, 50);
	setTimeout(syncAuthPanels, 300);
})();
