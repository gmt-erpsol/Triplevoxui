"""
TITA/TripleVox file identification
App: triplevox_platform
File: triplevox_platform/triplevox_platform/hooks.py
Purpose: UI app hooks: CSS/JS includes, boot_session, after_migrate sync jobs.
"""
# --- App metadata ---
app_name = "triplevox_platform"
app_title = "TripleVox Platform"
app_publisher = "TripleVox Engineering PLC"
app_description = "White-label ERP shell for Frappe v16 Desk"
app_email = "admin@triplevox.com"
app_license = "mit"
app_version = "1.0.0"
app_logo_url = "/assets/triplevox_platform/images/triplevox-logo.png"

required_apps = ["frappe", "erpnext", "hrms"]

# --- Runs after bench migrate: workspaces, icons, branding ---
# Python function(s) to run automatically after `bench migrate`.
after_migrate = [
    "triplevox_platform.setup.apply_branding_settings",
    "triplevox_platform.branding_setup.run",
    "triplevox_platform.workspace_viewer.run",
    "triplevox_platform.role_packs.run",
    "triplevox_platform.print_branding.run",
    "triplevox_platform.sync_tita_production.run",
    "triplevox_platform.sync_employee_hub.run",
    "triplevox_platform.sync_company_saas.run",
    "triplevox_platform.nest_desktop_icons.run",
    "triplevox_platform.nest_manufacturing_sidebar.run",
    "triplevox_platform.nest_workspace_menu.run",
]

# First install + whenever another app is added later
after_install = "triplevox_platform.install.after_install"
after_app_install = "triplevox_platform.install.after_app_install"

# --- Global Desk CSS/JS (bump ?v= after UI changes) ---
app_include_css = [
	"/assets/triplevox_platform/css/triplevox_platform.css?v=20260802ac",
]
# Load JavaScript file on every Desk page.
app_include_js = [
	"/assets/triplevox_platform/js/tvx_early.js?v=20260802z",
	"/assets/triplevox_platform/js/triplevox_desk.js?v=20260802z",
	"/assets/triplevox_platform/js/tvx_saas_ui.js?v=20260802z",
	"/assets/triplevox_platform/js/tvx_shell_panels.js?v=20260802z",
]

web_include_css = [
	"/assets/triplevox_platform/css/tvx_login.css?v=20260802z",
]

# Employee Checkin — hide geolocation until HR Settings confirms (no blink)
doctype_js = {
	"Employee Checkin": "public/js/tvx_employee_checkin.js",
	"Client Branding": "tvx/doctype/client_branding/client_branding.js",
}

# --- Inject branding + theme into frappe.boot ---
boot_session = "triplevox_platform.boot.boot_session"

# --- Jinja helpers for branded print formats ---
jinja = {
	"methods": [
		"triplevox_platform.print_branding.tvx_print_theme",
		"triplevox_platform.print_branding.tvx_money",
		"triplevox_platform.print_branding.tvx_date",
	],
}

# Workspace Viewer: never get edit/create flags from get_workspaces refresh
override_whitelisted_methods = {
	"frappe.desk.desktop.get_workspaces": "triplevox_platform.workspace_viewer.get_workspaces",
}

# --- Permission: Workspace Viewer = read workspaces, never edit ---
has_permission = {
	"Workspace": "triplevox_platform.workspace_viewer.workspace_has_permission",
	"Workspace Sidebar": "triplevox_platform.workspace_viewer.workspace_has_permission",
	"Workspace Sidebar Item": "triplevox_platform.workspace_viewer.workspace_has_permission",
}

doc_events = {
	"Workspace": {
		"before_insert": "triplevox_platform.workspace_viewer.block_workspace_write",
		"before_validate": "triplevox_platform.workspace_viewer.block_workspace_write",
		"on_trash": "triplevox_platform.workspace_viewer.block_workspace_write",
	},
	"Workspace Sidebar": {
		"before_insert": "triplevox_platform.workspace_viewer.block_workspace_write",
		"before_validate": "triplevox_platform.workspace_viewer.block_workspace_write",
		"on_trash": "triplevox_platform.workspace_viewer.block_workspace_write",
	},
	"Workspace Sidebar Item": {
		"before_insert": "triplevox_platform.workspace_viewer.block_workspace_write",
		"before_validate": "triplevox_platform.workspace_viewer.block_workspace_write",
		"on_trash": "triplevox_platform.workspace_viewer.block_workspace_write",
	},
	"Desktop Icon": {
		"after_insert": "triplevox_platform.nest_desktop_icons.on_desktop_icon_change",
		"on_update": "triplevox_platform.nest_desktop_icons.on_desktop_icon_change",
	},
}

# --- Apps screen / switcher labels (v16) ---
# titacustom tile is injected at boot only when domain is enabled (see boot.py)
add_to_apps_screen = [
    {
        "name": "triplevox_platform",
        "logo": "/assets/triplevox_platform/images/triplevox-logo.png",
        "title": "TripleVox ERP",
        "route": "/desk",
    },
]

website_context = {}

# Ensure Guest login pages receive a real CSRF token (fixes "Something went wrong")
# Also injects Product Logo favicon/splash from Client Branding (overrides package defaults).
update_website_context = [
	"triplevox_platform.website_csrf.update_website_context",
]
