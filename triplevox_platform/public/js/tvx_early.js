/**
 * Runs first: inject hide-sidebar CSS before paint, then mark Desktop.
 * Prefer hiding sidebar until non-desktop is confirmed (no Desktop blink).
 */
(function () {
	try {
		if (!document.getElementById("tvx-blink-guard")) {
			var s = document.createElement("style");
			s.id = "tvx-blink-guard";
			s.textContent =
				"html:not(.tvx-sidebar-ok) .body-sidebar-container," +
				"html.tvx-on-desktop .body-sidebar-container," +
				"html.tvx-prefer-desktop .body-sidebar-container{" +
				"display:none!important;visibility:hidden!important;" +
				"width:0!important;min-width:0!important;max-width:0!important;" +
				"pointer-events:none!important;overflow:hidden!important}" +
				"html.tvx-on-desktop .main-section,html.tvx-prefer-desktop .main-section{" +
				"margin-left:0!important;width:100%!important;max-width:100%!important}";
			(document.head || document.documentElement).appendChild(s);
		}

		var hash = (location.hash || "").replace(/^#\/?/, "");
		var path = (location.pathname || "").replace(/\/+$/, "") || "/";
		var lastDesktop = false;
		try {
			lastDesktop = sessionStorage.getItem("tvx_last_was_desktop") === "1";
		} catch (e) {
			/* ignore */
		}

		var clearlyNotDesktop =
			/^(Form|List|Workspaces|query-report|dashboard|Dashboard)\b/i.test(hash) ||
			(/\/(app|desk)\/.+/i.test(path) && !/\/(app|desk)\/desktop$/i.test(path));

		var onDesktop = false;
		if (hash === "desktop" || /^desktop(\/|$)/i.test(hash)) onDesktop = true;
		else if (/\/(app|desk)\/desktop$/i.test(path)) onDesktop = true;
		else if (clearlyNotDesktop) onDesktop = false;
		else if (/\/(app|desk)$/i.test(path)) onDesktop = true;
		else if (lastDesktop) onDesktop = true;

		var html = document.documentElement;
		html.classList.toggle("tvx-on-desktop", onDesktop);
		html.classList.toggle("tvx-prefer-desktop", onDesktop);
		/* Default: keep sidebar hidden. Only reveal when clearly NOT Desktop. */
		if (onDesktop || lastDesktop) {
			html.classList.remove("tvx-sidebar-ok");
		} else if (clearlyNotDesktop) {
			html.classList.add("tvx-sidebar-ok");
		} else {
			html.classList.remove("tvx-sidebar-ok");
		}
		html.classList.add("tvx-chrome-ready");
		window.__tvx_route_desktop = onDesktop;
		try {
			if (onDesktop) sessionStorage.setItem("tvx_last_was_desktop", "1");
		} catch (e2) {
			/* ignore */
		}
	} catch (err) {
		try {
			document.documentElement.classList.add("tvx-chrome-ready");
		} catch (e3) {
			/* ignore */
		}
	}
})();
