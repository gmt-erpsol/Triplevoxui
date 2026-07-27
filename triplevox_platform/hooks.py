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
    "triplevox_platform.sync_tita_production.run",
    "triplevox_platform.sync_employee_hub.run",
    "triplevox_platform.nest_desktop_icons.run",
    "triplevox_platform.nest_manufacturing_sidebar.run",
]

# --- Global Desk CSS/JS (bump ?v= after UI changes) ---
app_include_css = [
	"/assets/triplevox_platform/css/triplevox_platform.css?v=20260727z",
]
# Load JavaScript file on every Desk page.
app_include_js = [
	"/assets/triplevox_platform/js/triplevox_desk.js?v=20260727z",
]

# --- Inject branding + theme into frappe.boot ---
boot_session = "triplevox_platform.boot.boot_session"

# --- Apps screen / switcher labels (v16) ---
add_to_apps_screen = [
    {
        "name": "triplevox_platform",
        "logo": "/assets/triplevox_platform/images/triplevox-logo.png",
        "title": "TripleVox ERP",
        "route": "/desk",
    },
    {
        "name": "titacustom",
        "logo": "/assets/titacustom/images/tita-logo.svg",
        "title": "TITA Manufacturing",
        "route": "/desk/tita-manufacturing",
    },
]

website_context = {
    "favicon": "/assets/triplevox_platform/images/triplevox-logo.png",
    "splash_image": "/assets/triplevox_platform/images/triplevox-logo.png",
}
