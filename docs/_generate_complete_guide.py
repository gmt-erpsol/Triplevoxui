# -*- coding: utf-8 -*-
"""Generate TripleVox_UI_App_Complete_Guide.html — Frappe-docs style, multi-chapter."""
from pathlib import Path

OUT = Path("/mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/docs/TripleVox_UI_Final_Guide.html")
if not OUT.parent.exists():
    OUT = Path(r"C:\Users\Dell\Documents\TITA-ERP-BRD\apps\triplevox_platform\docs\TripleVox_UI_Final_Guide.html")
OUT_COMPLETE = Path("/mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/docs/TripleVox_UI_App_Complete_Guide.html")
if not OUT_COMPLETE.parent.exists():
    OUT_COMPLETE = Path(r"C:\Users\Dell\Documents\TITA-ERP-BRD\apps\triplevox_platform\docs\TripleVox_UI_App_Complete_Guide.html")
DL_HTML = Path("/mnt/c/Users/Dell/Downloads/TripleVox_UI_Final_Guide.html")
if not DL_HTML.parent.exists():
    DL_HTML = Path(r"C:\Users\Dell\Downloads\TripleVox_UI_Final_Guide.html")

CSS = """
:root{--accent:#2490ef;--accent-soft:#e8f4fd;--ink:#1f272e;--muted:#6c7680;--border:#e2e6eb;--bg:#fff;--code-bg:#1e293b;--warn-bg:#fff8e6;--warn-border:#f0c14b;--info-bg:#eef7ff;--card:#fafbfc}
*{box-sizing:border-box}html{font-size:15px}
body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}
.doc-wrap{max-width:920px;margin:0 auto;padding:28px 28px 80px}
.hero{border:1px solid var(--border);border-radius:10px;padding:32px 28px;background:linear-gradient(180deg,#f7fbff 0%,#fff 70%);margin-bottom:28px}
.hero .eyebrow{color:var(--accent);font-weight:600;font-size:.85rem;letter-spacing:.04em;text-transform:uppercase}
.hero h1{margin:8px 0 10px;font-size:2rem;font-weight:700;letter-spacing:-.02em}
.hero p{margin:0;color:var(--muted);max-width:62ch}
.meta-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.badge{display:inline-block;padding:4px 10px;border-radius:6px;background:var(--accent-soft);color:#0b5cab;font-size:.8rem;font-weight:600;border:1px solid #cfe6fa}
.toc{border:1px solid var(--border);border-radius:10px;padding:22px 24px 10px;background:var(--card);margin-bottom:36px}
.toc h2{margin:0 0 12px;font-size:1.15rem;color:var(--accent)}
.toc ol{margin:0;padding-left:1.35rem}.toc li{margin:0 0 8px}.toc a{color:var(--ink);text-decoration:none}.toc a:hover{color:var(--accent);text-decoration:underline}
.chapter{page-break-before:always;break-before:page;margin:0 0 36px;padding-top:8px}
.chapter:first-of-type{page-break-before:auto;break-before:auto}
.ch-header{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);font-weight:700;margin-bottom:6px}
.chapter h2{margin:0 0 14px;font-size:1.55rem;border-bottom:2px solid var(--accent);padding-bottom:10px}
.chapter h3{margin:22px 0 8px;font-size:1.12rem}.chapter h4{margin:16px 0 6px;font-size:1rem;color:#334155}
.card{border:1px solid var(--border);border-radius:8px;padding:14px 16px;background:var(--card);margin:12px 0 16px}
table{width:100%;border-collapse:collapse;margin:12px 0 18px;font-size:.92rem}
th,td{border:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#f1f5f9;font-weight:600}tr:nth-child(even) td{background:#fafbfc}
pre,code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{background:var(--code-bg);color:#e2e8f0;padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:.82rem;line-height:1.5;margin:12px 0 18px;white-space:pre-wrap;word-break:break-word}
code{font-size:.88em;background:#f1f5f9;padding:1px 5px;border-radius:4px}pre code{background:transparent;padding:0;color:inherit}
.callout{border-left:4px solid #2490ef;background:var(--info-bg);padding:12px 14px;border-radius:0 8px 8px 0;margin:14px 0}
.callout.warn{border-left-color:var(--warn-border);background:var(--warn-bg)}
.callout .label{font-weight:700;font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:#0b5cab}
.callout.warn .label{color:#8a6d1d}
ul,ol{margin:8px 0 14px;padding-left:1.35rem}li{margin-bottom:5px}
.steps{counter-reset:step;list-style:none;padding-left:0}
.steps li{counter-increment:step;position:relative;padding:10px 12px 10px 48px;margin-bottom:8px;border:1px solid var(--border);border-radius:8px;background:#fff}
.steps li::before{content:counter(step);position:absolute;left:12px;top:10px;width:26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;font-size:.85rem;line-height:26px;text-align:center}
.footer-note{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem}
a{color:var(--accent)}
@media print{body{font-size:11.5pt}.doc-wrap{max-width:none;padding:0}.chapter{page-break-before:always}.chapter:first-of-type{page-break-before:auto}.toc{page-break-after:always}a{color:inherit;text-decoration:none}pre{white-space:pre-wrap}.hero{background:#fff}}
"""

def esc(s):
    return s

def table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for r in rows:
        body.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table>"

def info(msg):
    return f'<div class="callout"><div class="label">Info</div><p>{msg}</p></div>'

def warn(msg):
    return f'<div class="callout warn"><div class="label">Warning</div><p>{msg}</p></div>'

def card(title, html):
    return f'<div class="card"><p><strong>{title}</strong></p>{html}</div>'

def code(block):
    return f"<pre><code>{block}</code></pre>"

def steps(items):
    return "<ol class='steps'>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"

def h3(t): return f"<h3>{t}</h3>"
def h4(t): return f"<h4>{t}</h4>"
def p(t): return f"<p>{t}</p>"
def ul(items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

CHAPTERS = []

def add(n, title, parts):
    CHAPTERS.append((n, title, "\n".join(parts)))

# ========== 01 ==========
add(1, "Welcome & what this app is / is not", [
p("<strong>TripleVox Platform</strong> (<code>triplevox_platform</code>) is the white-label Desk shell for Frappe v16 deployments used by TripleVox Engineering PLC and sister factories (TITA, BRG, and future clients)."),
card("Product identity", ul([
"App title: TripleVox Platform",
'GitHub: <a href="https://github.com/gmt-erpsol/Triplevoxui">https://github.com/gmt-erpsol/Triplevoxui</a>',
"Installed folder name <em>must</em> be <code>triplevox_platform</code> (not <code>Triplevoxui</code>)",
"Static assets: <code>/assets/triplevox_platform/...</code>",
"Publisher: TripleVox Engineering PLC · License: MIT · Requires: frappe, erpnext, hrms",
])),
h3("What this app is"),
table(["Capability", "Examples"], [
["Desk chrome &amp; theme", "CSS variables, welcome home, clock, module icons, watermark pill, footer"],
["Multi-company SaaS shell", "Company switcher, onboarding wizard, login company picker"],
["Client theme profiles", "<code>tita</code> / <code>brg</code> / <code>demo</code> in <code>client_theme.py</code>"],
["Print identity", "TripleVox Print Formats, Letter Head pack, Jinja branding helpers"],
["Role packs", "Shop Floor, QC, Ops Admin, Workspace Viewer"],
["UX polish", "Recent activity, form float rail, sidebar hide on Desktop, check-in geolocation fix"],
]),
h3("What this app is not"),
table(["Not responsible for", "Belongs in"], [
["MES / factory shop-floor workflows", "<code>titacustom</code> (or future BRG domain app)"],
["Core accounting, stock, CRM logic", "ERPNext"],
["HR / payroll / leave engines", "HRMS"],
["Full security matrix for every DocType", "ERPNext roles + Custom DocPerm (packs are starters)"],
["Infrastructure / backups / SSL", "Bench / nginx / ops runbooks"],
]),
info("Think of TripleVox Platform as the <em>skin + sister-company cockpit</em>. Domain features live in ERPNext/HRMS/titacustom; this app makes one bench site feel like a branded multi-factory product."),
h3("Audience for this guide"),
ul(["Implementers setting up a new PC or new sister company", "System Managers who assign role packs and print packs", "Support engineers debugging branding, cache, or migrate side-effects"]),
])

# ========== 02 ==========
add(2, "Architecture overview (Desk shell vs titacustom vs ERPNext/HRMS)", [
p("A TripleVox production site is a layered Frappe Bench stack. Understanding which layer owns a feature prevents wrong-repo edits and wrong-app tickets."),
h3("Layer diagram (conceptual)"),
code("""Browser (Desk / login)
    |
    v
triplevox_platform     <- CSS/JS, boot branding, switcher APIs, prints, roles
    |
    +-- titacustom     <- TITA manufacturing MES / custom DocTypes (optional)
    +-- erpnext        <- Accounting, Stock, Selling, Buying, Manufacturing base
    +-- hrms           <- HR, Payroll, Leave, Employee Checkin
    +-- frappe         <- Framework, Desk shell, Permissions, Website, Print engine
         |
         v
      MariaDB + Redis + sites/YOURSITE"""),
h3("Responsibility matrix"),
table(["Concern", "App", "Notes"], [
["Login accents / company picker", "triplevox_platform", "<code>www/login.html</code>, <code>tvx_login.css/js</code>"],
["Desk logo (product)", "triplevox_platform", "Always TripleVox mark via profile <code>logo_url</code>"],
["Watermark pill (client)", "triplevox_platform", "<code>client_logo_url</code> / company map"],
["Work Order / Job Card domain UI", "titacustom + ERPNext", "UI shell nests icons/sidebar"],
["Employee Checkin geolocation blink", "triplevox_platform", "<code>doctype_js</code> for Employee Checkin"],
["Print PDF company logo", "triplevox_platform print_branding", "Resolves from document Company"],
["Workspace edit lock", "Workspace Viewer role", "overrides <code>get_workspaces</code>"],
]),
h3("Boot payload"),
p("On every Desk session, <code>boot_session</code> injects <code>frappe.boot.triplevox</code> from <code>client_theme.get_boot_payload()</code>. Front-end scripts (<code>triplevox_desk.js</code>, <code>tvx_saas_ui.js</code>) read that object for theme CSS variables, watermark, welcome copy, and switcher company list."),
warn("Do not put sister-company logos into Desk <code>logo_url</code>. Desk product chrome stays TripleVox; client marks go to watermark / prints / login preview."),
])

# ========== 03 ==========
add(3, "Prerequisites (hardware, WSL2, Ubuntu, Node optional, Git)", [
h3("Hardware (developer / single-site)"),
table(["Item", "Recommended", "Minimum"], [
["CPU", "4+ cores", "2 cores"],
["RAM", "16 GB", "8 GB (tight)"],
["Disk", "SSD 40+ GB free", "25 GB free"],
["OS host", "Windows 10/11 + WSL2, or native Ubuntu 22.04/24.04", "Same"],
]),
h3("Software checklist"),
steps([
"<strong>WSL2</strong> enabled on Windows (<code>wsl --install</code>), Ubuntu distro set as default.",
"<strong>Ubuntu packages</strong> for Frappe: python3.11+, mariadb-server, redis-server, nginx (prod), curl, git, wkhtmltopdf (prints), yarn/npm as required by Bench.",
"<strong>Git</strong> with access to <code>github.com/gmt-erpsol/Triplevoxui</code> (HTTPS token or SSH).",
"<strong>Node / Yarn</strong> — required for <code>bench build</code> (Bench installer usually pins versions).",
"<strong>Optional on Windows host:</strong> VS Code / Cursor remote-WSL, Windows Terminal.",
]),
info('Official Frappe install docs: <a href="https://frappeframework.com/docs/user/en/installation">frappeframework.com/docs/user/en/installation</a>. Prefer the official Bench path for your OS.'),
h3("Accounts &amp; access you will need"),
ul(["MariaDB root / bench DB credentials", "Site administrator password", "GitHub read access to Triplevoxui (and titacustom if used)", "For production: DNS, TLS certificates, backup target"]),
])


# ========== 04 ==========
add(4, "Install Frappe Bench from scratch (high-level official steps + links)", [
p("Follow the official Frappe Framework installation guide for your platform. Below is the <strong>shape</strong> of a typical Linux / WSL Ubuntu flow for Frappe v16 — always verify versions against current docs."),
steps([
"Update apt and install OS dependencies listed in the official guide.",
"Install and secure MariaDB; create a DB user for Bench if required by your playbook.",
"Install Redis, Node (via nvm or nodesource as documented), Yarn.",
"Install <code>wkhtmltopdf</code> with patched Qt if you need PDF generation from Desk.",
"Install frappe-bench via the documented method (<code>pipx install frappe-bench</code> or equivalent).",
"<code>bench init --frappe-branch version-16 frappe-bench</code> (confirm branch for your target).",
"<code>cd frappe-bench &amp;&amp; bench start</code> (dev) or set up production supervisor/systemd + nginx.",
]),
code("""# Illustrative only — confirm against official docs
sudo apt update
# ... install python, mariadb, redis, curl, git, wkhtmltopdf ...
pipx install frappe-bench
bench init --frappe-branch version-16 frappe-bench
cd frappe-bench
bench start"""),
card("Official references", ul([
"Installation: https://frappeframework.com/docs/user/en/installation",
"Bench commands: https://frappeframework.com/docs/user/en/bench",
"ERPNext: https://docs.erpnext.com/",
])),
warn("Do not mix random third-party one-click installers with this guide unless you know how they name sites and apps. TripleVox assumes standard Bench: <code>~/frappe-bench/apps/</code>, <code>sites/</code>."),
])

# ========== 05 ==========
add(5, "Create site + install erpnext + hrms", [
steps([
"From the bench root: <code>bench new-site your.site.name</code> — set Administrator password when prompted.",
"Get ERPNext: <code>bench get-app erpnext --branch version-16</code> (confirm branch).",
"Get HRMS: <code>bench get-app hrms --branch version-16</code> (confirm branch).",
"Install: <code>bench --site your.site.name install-app erpnext</code> then <code>install-app hrms</code>.",
"Create at least one <strong>Company</strong> (e.g. TITA PP Plastic PLC) via Setup wizard or Company list.",
"Run <code>migrate</code> and <code>clear-cache</code>.",
]),
code("""cd ~/frappe-bench
bench new-site erp.local
bench get-app erpnext --branch version-16
bench get-app hrms --branch version-16
bench --site erp.local install-app erpnext
bench --site erp.local install-app hrms
bench --site erp.local migrate
bench --site erp.local clear-cache"""),
info("<code>triplevox_platform</code> declares <code>required_apps = [\"frappe\", \"erpnext\", \"hrms\"]</code>. Install those before TripleVox."),
])

# ========== 06 ==========
add(6, "Install triplevox_platform from GitHub (gmt-erpsol/Triplevoxui → rename folder)", [
p("The GitHub repository is named <strong>Triplevoxui</strong>, but the Frappe app package must live in a folder named <code>triplevox_platform</code>."),
steps([
"<code>cd ~/frappe-bench</code>",
"<code>bench get-app https://github.com/gmt-erpsol/Triplevoxui.git --branch main</code>",
"If Bench cloned into <code>apps/Triplevoxui</code>, rename: <code>mv apps/Triplevoxui apps/triplevox_platform</code>",
"Confirm <code>apps/triplevox_platform/triplevox_platform/hooks.py</code> exists and <code>app_name = \"triplevox_platform\"</code>.",
"<code>bench --site your.site.name install-app triplevox_platform</code>",
"<code>bench --site your.site.name migrate &amp;&amp; bench --site your.site.name clear-cache</code>",
"<code>bench build --app triplevox_platform</code> if assets did not soft-link correctly",
"Restart: <code>bench restart</code> (prod) or restart <code>bench start</code> (dev)",
]),
code("""cd ~/frappe-bench
bench get-app https://github.com/gmt-erpsol/Triplevoxui.git --branch main
mv apps/Triplevoxui apps/triplevox_platform   # if needed
bench --site erp.local install-app triplevox_platform
bench --site erp.local migrate
bench --site erp.local clear-cache
bench build --app triplevox_platform
bench restart"""),
warn("Leaving the folder as <code>Triplevoxui</code> breaks imports and asset URLs. Assets must resolve as <code>/assets/triplevox_platform/...</code>."),
])

# ========== 07 ==========
add(7, "Install from local folder / rsync / Windows path", [
h3("Option A — rsync into apps/"),
code("""# From WSL — example Windows Documents path
rsync -a /mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/ \\
  ~/frappe-bench/apps/triplevox_platform/
bench --site erp.local install-app triplevox_platform   # first time only
bench --site erp.local migrate
bench --site erp.local clear-cache
bench build --app triplevox_platform"""),
h3("Option B — symlink (dev only)"),
code("""ln -s /mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform \\
  ~/frappe-bench/apps/triplevox_platform"""),
warn("Symlinks across /mnt/c can be slower and occasionally confuse file watchers. Prefer rsync for stable demos."),
h3("Option C — Windows path awareness"),
ul([
"Edit in Cursor on Windows: <code>C:\\Users\\Dell\\Documents\\TITA-ERP-BRD\\apps\\triplevox_platform</code>",
"Run Bench commands inside WSL against <code>~/frappe-bench</code>",
"After CSS/JS edits, bump <code>?v=</code> in <code>hooks.py</code>, then clear-cache + hard refresh",
]),
])

# ========== 08 ==========
add(8, "migrate, clear-cache, build, restart — what each does", [
table(["Command", "What it does", "When to run"], [
["<code>bench --site S migrate</code>", "Applies patches, syncs DocTypes, runs <code>after_migrate</code> hooks", "After pull/install; when roles/prints missing"],
["<code>bench --site S clear-cache</code>", "Clears Redis/website/desk caches so boot &amp; assets refresh", "After theme/site_config/hooks changes"],
["<code>bench build --app triplevox_platform</code>", "Bundles/copies public assets into sites/assets", "After public JS/CSS/image changes"],
["<code>bench restart</code>", "Restarts gunicorn/workers (production)", "After Python hook/API changes in prod"],
["<code>bench --site S clear-website-cache</code>", "Website-specific cache", "Login page CSS not updating"],
]),
code("""bench --site erp.local migrate
bench --site erp.local clear-cache
bench build --app triplevox_platform
bench restart"""),
info("Browser hard refresh (Ctrl+Shift+R) is still required after cache clear — disk cache can keep old JS."),
])

# ========== 09 ==========
add(9, "First login, hard refresh, verify branding loaded", [
steps([
"Open <code>http://your.site.name:8000/login</code> (dev) or your HTTPS URL.",
"Optionally pick a company in the TripleVox login picker (TITA / BRG).",
"Sign in as Administrator or a Desk user.",
"Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (macOS).",
"Verify product logo is TripleVox in chrome; watermark pill shows client mark when mapped.",
"Open browser console — no 404s for <code>/assets/triplevox_platform/css/triplevox_platform.css</code> and JS.",
"In Desk console: confirm <code>frappe.boot.triplevox</code> exists with <code>client_key</code>, theme tokens, logos.",
]),
h3("Quick verification checklist"),
table(["Check", "Expected"], [
["CSS loaded", "<code>triplevox_platform.css?v=...</code> 200"],
["JS loaded", "<code>triplevox_desk.js</code>, <code>tvx_saas_ui.js</code> 200"],
["Company pill", "Visible top-right when companies mapped"],
["Desktop home", "Welcome + clock + icons; sidebar hidden on Desktop route"],
["Cache bump", "<code>?v=</code> in hooks matches last UI change"],
]),
])

# ========== 10 ==========
add(10, "Optional titacustom install", [
p("<code>titacustom</code> is the TITA manufacturing domain app. TripleVox lists it on the apps screen when present (<code>add_to_apps_screen</code> in hooks)."),
steps([
"Obtain titacustom from your private/internal repo (not this public UI repo).",
"<code>bench get-app &lt;titacustom-url&gt;</code> and ensure folder name <code>titacustom</code>.",
"<code>bench --site S install-app titacustom</code> then migrate + clear-cache.",
"Confirm TITA profile apps title / default_app points at Manufacturing routes as designed.",
"TITA print logos typically come from <code>/assets/titacustom/images/tita-logo.svg</code> — titacustom must be installed for those URLs to resolve.",
]),
info("BRG profile does not require titacustom. Demo profile defaults toward erpnext. Sites can run TripleVox + ERPNext + HRMS without titacustom."),
])

# ========== 11 ==========
add(11, "Client theme profiles (tita/brg/demo) in client_theme.py", [
p("Profiles live in <code>triplevox_platform/client_theme.py</code> inside the <code>CLIENTS</code> dict. Shared shell fields come from <code>_BASE</code>."),
table(["Key", "Client", "Accent feel", "Print / client logo", "Notes"], [
["<code>tita</code>", "TITA PP Plastic PLC", "Blue (#1e4d8c family)", "<code>/assets/titacustom/images/tita-logo.svg</code>", "default_app titacustom; factory area Wello Dessie"],
["<code>brg</code>", "BRG Trading PLC", "Green (#15803d family)", "<code>/assets/triplevox_platform/images/brg-logo.png</code>", "Medical gauze &amp; silken; no default_app"],
["<code>demo</code>", "Demo Client PLC", "Teal (#0f766e)", "TripleVox logo fallback", "Template — copy for new clients"],
]),
h3("Theme tokens"),
table(["Token", "Used for"], [
["green / green_bright / green_soft / green_deep", "Accent buttons, chips, selection, print accents"],
["sidebar / sidebar_2", "Left sidebar gradient ends"],
["page / surface / ink / muted / border / radius", "General chrome"],
]),
h3("How to activate a profile"),
ul([
"Site-wide: <code>\"triplevox_client\": \"tita\"</code> in site_config.json (fallback <code>ACTIVE_CLIENT</code> in Python).",
"Per company: map Company name → key via <code>triplevox_company_profiles</code> (see chapter 12).",
"Optional overlays: <code>triplevox_theme</code> and <code>triplevox_company_themes</code>.",
]),
code("""# Excerpt — DEFAULT_COMPANY_PROFILES
{
  "TITA PP Plastic PLC": "tita",
  "BRG Trading PLC": "brg"
}"""),
warn("After editing CLIENTS or site_config, run clear-cache and hard-refresh Desk."),
])


# ========== 12 ==========
add(12, "site_config keys reference (triplevox_client, company_profiles, company_themes, theme overrides)", [
p("Edit <code>sites/YOURSITE/site_config.json</code> (or use onboarding wizard APIs which write keys safely)."),
table(["Key", "Type", "Purpose"], [
["<code>triplevox_client</code>", "string", "Default profile key when no session company map hits (tita/brg/demo)"],
["<code>triplevox_company_profiles</code>", "object", "Map Company display name to profile key"],
["<code>triplevox_company_themes</code>", "object", "Per-company overlay (accent, factory_area, logos, etc.)"],
["<code>triplevox_theme</code>", "object", "Site-wide deep-merge overrides into the active profile"],
]),
h3("Example site_config fragment"),
code("""{
  "triplevox_client": "tita",
  "triplevox_company_profiles": {
    "TITA PP Plastic PLC": "tita",
    "BRG Trading PLC": "brg"
  },
  "triplevox_company_themes": {
    "BRG Trading PLC": {
      "factory_area": "Medical Gauze & Silken",
      "accent": "#15803d"
    }
  },
  "triplevox_theme": {
    "partner_name": "TripleVox Engineering PLC"
  }
}"""),
h3("Resolution order (Desk)"),
ul([
"Session company from Employee.company, else user default Company, else global default.",
"Look up company in <code>triplevox_company_profiles</code> (+ DEFAULT_COMPANY_PROFILES).",
"Load CLIENTS[key], deep-merge <code>triplevox_theme</code>, then company theme overlay.",
"If no company map: use <code>triplevox_client</code> / ACTIVE_CLIENT.",
]),
info("Onboarding wizard writes profiles/themes for you — prefer it over hand-editing JSON in production."),
])

# ========== 13 ==========
add(13, "Branding model table (Desk logo vs watermark pill vs prints vs login)", [
p("TripleVox deliberately separates <strong>product</strong> branding from <strong>sister-company</strong> branding."),
table(["Surface", "Primary source", "Typical asset"], [
["Desk sidebar / product logo", "profile <code>logo_url</code> (from _BASE)", "/assets/triplevox_platform/images/triplevox-logo.png"],
["Desk watermark pill (bottom-left)", "client_logo_url / print_logo_url + company name", "TITA SVG or BRG PNG"],
["Theme accents / CSS variables", "Active CLIENTS theme tokens", "tita blue / brg green"],
["Login accents + preview logo", "Login company picker key", "Same client logos"],
["PDF header / soft mark", "Document Company then Letter Head then Company logo then print_logo_url", "Per-document company"],
["Apps screen TripleVox tile", "hooks add_to_apps_screen", "triplevox-logo.png"],
["Favicon / splash", "website_context", "triplevox-logo.png"],
]),
warn("Never set Desk logo_url to a sister-company mark. That breaks white-label product identity across factories."),
h3("Print resolution order"),
p("Implemented in <code>print_branding.get_print_theme()</code> / Jinja helpers:"),
ul([
"Company fields (name, logo, phone, email, address) and Letter Head",
"CLIENTS profile <code>print_logo_url</code> (never Desk logo_url)",
"Monogram text if no image",
]),
])

# ========== 14 ==========
add(14, "One site two companies (TITA + BRG) full walkthrough", [
p("Goal: one Bench site hosts both factories with switchable Desk branding and correct print logos."),
steps([
"Ensure ERPNext Companies exist: <strong>TITA PP Plastic PLC</strong> and <strong>BRG Trading PLC</strong> (exact names).",
"Install/migrate <code>triplevox_platform</code> so DEFAULT_COMPANY_PROFILES and roles/prints exist.",
"Confirm site_config maps both companies (defaults already include them; onboarding also writes maps).",
"Optional BRG helper: <code>bench --site S execute triplevox_platform.setup_brg.ensure_brg_company</code>",
"Apply print pack for each company (wizard or API).",
"Assign users: set Employee.company and/or User default Company appropriately.",
"Test login picker for each company, then Desk switcher both ways.",
"Print Sales Invoice / Stock Entry for each company using TripleVox formats — verify logo.",
"clear-cache + hard refresh after config changes.",
]),
table(["Company", "Profile key", "Accent", "Client logo path"], [
["TITA PP Plastic PLC", "tita", "Blue", "titacustom tita-logo.svg (needs titacustom for asset)"],
["BRG Trading PLC", "brg", "Green", "triplevox_platform brg-logo.png"],
]),
code("""bench --site erp.local execute triplevox_platform.setup_brg.ensure_brg_company
bench --site erp.local execute triplevox_platform.print_pack.apply_print_pack --kwargs \"{'company':'TITA PP Plastic PLC'}\"
bench --site erp.local execute triplevox_platform.print_pack.apply_print_pack --kwargs \"{'company':'BRG Trading PLC'}\"
bench --site erp.local clear-cache"""),
])

# ========== 15 ==========
add(15, "Company switcher (UI location, steps, API, permissions)", [
h3("UI location"),
p("Top-right Desk chrome: a <strong>company pill</strong> rendered by <code>public/js/tvx_saas_ui.js</code>. Opening it lists switchable companies and System Manager tools."),
h3("User steps"),
steps([
"Log into Desk.",
"Click the company pill (top-right).",
"Choose TITA PP Plastic PLC or BRG Trading PLC (or other mapped companies).",
"Theme accents + watermark update; user default Company is set.",
]),
h3("What the API does"),
table(["Method", "Role"], [
["<code>triplevox_platform.api.list_switchable_companies</code>", "Lists mapped companies that exist"],
["<code>triplevox_platform.api.set_session_company</code>", "Sets user default Company; updates Employee.company when present; returns boot payload"],
["<code>triplevox_platform.api.get_client_boot_payload</code>", "Refresh branding payload"],
]),
h3("Permissions"),
ul([
"Any logged-in Desk user can switch among companies listed for the site.",
"Onboarding, role pack assign, and print pack actions require System Manager / Administrator.",
]),
h3("Menu extras (System Manager)"),
ul(["Onboard sister company…", "Apply print pack (current)…", "Assign role pack…"]),
info("If the pill is missing: hard-refresh; confirm tvx_saas_ui.js is in hooks app_include_js; confirm companies are mapped and exist."),
])

# ========== 16 ==========
add(16, "Onboarding wizard (fields, what it writes, bench alternatives)", [
p("Desk dialog for System Managers to register a new sister company on the same site."),
h3("Fields"),
table(["Field", "Purpose"], [
["Company name", "Exact legal Company name (creates Company if missing)"],
["Abbreviation", "Company abbr"],
["Theme profile", "tita / brg / demo"],
["Factory / area label", "Shown in welcome / profile factory_area"],
["Logo URL", "Optional client/print logo"],
["Apply print pack", "Recommended — Letter Head + formats"],
]),
h3("What it writes"),
ul([
"Company document (create/update)",
"<code>triplevox_company_profiles</code> entry in site config",
"Optional <code>triplevox_company_themes</code> overlay",
"Optional print pack via <code>print_pack.apply_print_pack</code>",
]),
code("""# API
triplevox_platform.api.onboard_sister_company(...)

# BRG bench alternative
bench --site YOUR_SITE execute triplevox_platform.setup_brg.ensure_brg_company"""),
p("After onboarding, use the company switcher to activate the new company. Hard-refresh if colors look stale."),
])

# ========== 17 ==========
add(17, "Role packs (table of packs, assign UI, Workspace Viewer details)", [
p("Ready-made Roles created on migrate — a fast starting point, not a full security product."),
table(["Pack key", "Role", "Purpose"], [
["shop_floor", "TripleVox Shop Floor", "Operators / floor Desk access; pair with Workspace Viewer"],
["qc", "TripleVox QC", "Quality / inspection Desk access; pair with Viewer"],
["ops_admin", "TripleVox Ops Admin", "Site champions — not full System Manager"],
["viewer", "Workspace Viewer", "Open workspaces; cannot edit layouts"],
]),
h3("Assign UI"),
steps([
"Company switcher menu → Assign role pack…",
"Pick User and Pack",
"Click Assign (System Manager)",
]),
code("""bench --site YOUR_SITE execute triplevox_platform.role_packs.run
# API: triplevox_platform.api.assign_role_pack / list_role_packs"""),
h3("Workspace Viewer details"),
ul([
"hooks override <code>frappe.desk.desktop.get_workspaces</code>",
"has_permission + doc_events block Workspace / Sidebar writes for Viewer-only users",
"User must not also be Workspace Manager / System Manager if you need a hard read-only layout experience",
]),
warn("DocType permissions still come from ERPNext/HRMS + Custom DocPerm. Packs only ensure Desk roles exist and can be assigned quickly."),
])

# ========== 18 ==========
add(18, "Branded login (picker, accents, post-login apply)", [
p("On <code>/login</code>, users pick Company (TITA / BRG). The login card accents and logo preview match that company (<code>tvx_login.css</code> / <code>tvx_login.js</code> / <code>www/login.html</code>)."),
steps([
"Open the login page.",
"Choose company from the dropdown.",
"Sign in as usual.",
"Desk applies the chosen company key once (default company + branding).",
"Company switcher remains available later.",
]),
h3("Post-login apply"),
ul([
"localStorage key <code>tvx_login_company_key</code> remembers picker choice",
"sessionStorage apply flag prevents repeated apply loops",
"API: <code>triplevox_platform.api.apply_login_company_key</code>",
]),
info("Bookmarks can still use one URL for both factories; the picker sets the front-door brand."),
h3("CSRF note"),
p("<code>update_website_context</code> → <code>website_csrf.update_website_context</code> ensures Guest login pages receive a real CSRF token (fixes vague “Something went wrong” on login)."),
])


# ========== 19 ==========
add(19, "Print pack + print_branding formats list (all DocTypes), Letter Head chain", [
p("Print pack prepares customer-facing print identity for a company. Print branding installs Jinja Print Formats prefixed <strong>TripleVox</strong>."),
h3("Print pack actions"),
ul([
"Create/update Letter Head named <code>{Company} Letter Head</code>",
"Set Company logo field when empty / when URL provided",
"Set Company <code>default_letter_head</code> when the field exists",
"Re-run <code>print_branding.run</code> (idempotent)",
]),
code("""# Desk: switcher → Apply print pack (current)…
# API: triplevox_platform.api.apply_company_print_pack
bench --site S execute triplevox_platform.print_pack.apply_print_pack --kwargs \"{'company':'BRG Trading PLC'}\"
bench --site S execute triplevox_platform.print_branding.run"""),
h3("TripleVox Print Formats (FORMAT_PREFIX = TripleVox)"),
table(["DocType", "Print Format name", "Template"], [
["Salary Slip", "TripleVox Payslip", "salary_slip.html"],
["Sales Invoice", "TripleVox Sales Invoice", "transaction.html"],
["Sales Order", "TripleVox Sales Order", "transaction.html"],
["Quotation", "TripleVox Quotation", "transaction.html"],
["Delivery Note", "TripleVox Delivery Note", "transaction.html"],
["Purchase Order", "TripleVox Purchase Order", "transaction.html"],
["Purchase Invoice", "TripleVox Purchase Invoice", "transaction.html"],
["Purchase Receipt", "TripleVox Purchase Receipt", "transaction.html"],
["Request for Quotation", "TripleVox Request for Quotation", "transaction.html"],
["Supplier Quotation", "TripleVox Supplier Quotation", "transaction.html"],
["Material Request", "TripleVox Material Request", "transaction.html"],
["Leave Application", "TripleVox Leave Application", "leave_application.html"],
["Payment Entry", "TripleVox Payment Entry", "payment_entry.html"],
["Work Order", "TripleVox Work Order", "work_order.html"],
["Stock Entry", "TripleVox Stock Entry", "stock_entry.html"],
["Journal Entry", "TripleVox Journal Entry", "journal_entry.html"],
["Expense Claim", "TripleVox Expense Claim", "expense_claim.html"],
["Job Card", "TripleVox Job Card", "job_card.html"],
["BOM", "TripleVox BOM", "bom.html"],
]),
h3("Letter Head chain"),
p("Document Company → Company default_letter_head → Letter Head image/content → Company logo field → profile print_logo_url → monogram."),
info("Jinja helpers registered in hooks: tvx_print_theme, tvx_money, tvx_date. Print CSS: print/css/tvx_print_style.css."),
])

# ========== 20 ==========
add(20, "Desktop home (sidebar hidden, welcome, clock, icons, Recent card scrollable)", [
p("On the Desk <strong>Desktop</strong> / home route, TripleVox presents a custom home experience driven by <code>triplevox_desk.js</code> + CSS."),
ul([
"<strong>Sidebar hidden</strong> on Desktop only (see chapter 23) — more horizontal room for icons.",
"<strong>Welcome block</strong> uses profile welcome_kicker, client_full_name, factory_area.",
"<strong>Clock</strong> shows local time for operators at a glance.",
"<strong>Module icons</strong> nested/arranged via <code>nest_desktop_icons</code> after_migrate (custom SVG set under public/images/module_icons).",
"<strong>Recent card</strong> is scrollable so many recent items do not blow the first viewport.",
]),
h3("Operator tips"),
steps([
"Land on Desktop after login — confirm welcome text matches active company.",
"Use module icons for primary apps (Accounting, Manufacturing, HRMS, etc.).",
"Scroll the Recent card rather than expecting an infinite list on the page.",
"Navigate into a workspace — left sidebar returns (permanent elsewhere).",
]),
])

# ========== 21 ==========
add(21, "Recent activity (Desktop + Workspace drawer toggler, max 10, labels, hide elsewhere)", [
ul([
"Recent activity surfaces on Desktop and via a Workspace drawer toggler.",
"List is capped at about <strong>max 10</strong> items for readability.",
"Labels are humanized for common DocTypes.",
"Hidden on forms/lists where it would clutter the chrome (show only where designed).",
]),
info("Implementation lives primarily in <code>triplevox_desk.js</code> with supporting CSS in <code>triplevox_platform.css</code>."),

h3("Desktop Recent card"),
ul([
"Shows the latest documents the user touched, capped near 10 entries.",
"Card body scrolls independently so the home welcome/icons stay visible.",
"Clicking an item opens the document Form.",
]),
h3("Workspace drawer toggler"),
ul([
"From workspace views, a toggler opens a compact Recent drawer.",
"Same max-item policy as Desktop for consistency.",
"Closed by default on narrow viewports to reduce chrome noise.",
]),
h3("Where Recent is hidden"),
p("On Form and dense List contexts the global Recent strip is suppressed so operators focus on the document. If you still see Recent on a Form, hard-refresh — an old JS bundle may be active."),

])

# ========== 22 ==========
add(22, "Form right rail float toggle + full width reclaim + List gap", [
p("Forms can feel cramped with Frappe's right sidebar. TripleVox adds a float toggle so users reclaim width."),
ul([
"Toggle floats the right rail / collapses it so the form body expands.",
"Full-width reclaim reduces wasted gutter on wide monitors.",
"List views get consistent gap/spacing so rows are not stuck to chrome edges.",
]),
warn("If a form looks 'broken' after a CSS cache mismatch, hard-refresh and confirm the latest ?v= CSS is loading."),

h3("Why it exists"),
p("Frappe Forms allocate a right sidebar for connections, comments, and tags. On laptop screens that rail steals horizontal space from long tables (items, operations)."),
h3("Behavior"),
ul([
"A float / collapse control lets users tuck the rail aside.",
"When collapsed, the form container expands toward full width.",
"List views get additional horizontal gap so the first column is not flush against the left chrome when the sidebar is open.",
]),
h3("Support checks"),
table(["Symptom", "Check"], [
["Toggle missing", "CSS/JS ?v= bump; tvx classes present in DOM"],
["Layout jump on load", "Cached mixed CSS — clear-cache + hard refresh"],
["Print preview affected", "No — print uses separate templates"],
]),

])

# ========== 23 ==========
add(23, "Left sidebar behavior (desktop hide only; permanent elsewhere)", [
table(["Route / context", "Left sidebar"], [
["Desktop / home", "Hidden (by design)"],
["Workspaces, List, Form, other Desk pages", "Permanent / visible as normal Frappe Desk"],
]),
p("Do not confuse 'sidebar missing on Desktop' with a bug. It is intentional for the home composition. If the sidebar is missing on Forms/Lists, check CSS regressions or cached old builds."),

h3("Design rationale"),
p("The Desktop home is a single composition (welcome, clock, icons, Recent). A permanent left sidebar competes with that composition, so TripleVox hides it only on Desktop."),
h3("Regression checklist"),
ul([
"Open Desktop — sidebar should be hidden.",
"Open Accounting workspace — sidebar visible.",
"Open a Sales Invoice Form — sidebar visible.",
"Open a List — sidebar visible.",
]),
code("""/* Conceptual — actual selectors live in triplevox_platform.css */
body[data-route^=Workspaces/] .tvx-desktop-home ...
/* Desktop-only hide; do not apply globally */"""),

])

# ========== 24 ==========
add(24, "Watermark & footer behavior", [
ul([
"Bottom-left <strong>watermark pill</strong> shows sister-company logo + name (client_logo_url / print_logo_url).",
"Product footer / copyright uses partner_name and year from profile (footer_text / footer_powered).",
"Dark mode may swap watermark asset to <code>triplevox-watermark-dark.png</code> where applicable.",
"Watermark is Desk chrome — not printed on PDFs (prints use Letter Head / print theme).",
]),

h3("Watermark pill"),
ul([
"Position: bottom-left Desk overlay.",
"Content: client logo (client_logo_url or print_logo_url) + company / client display name.",
"Updates when company switcher changes session company.",
"Not a security control — cosmetic identity only.",
]),
h3("Footer"),
ul([
"Uses profile footer_text / footer_powered / copyright with current year.",
"Partner defaults to TripleVox Engineering PLC.",
"Login page footer styling lives in tvx_login.css separately from Desk.",
]),
h3("Prints vs watermark"),
p("PDFs do not include the Desk watermark pill. Printed identity comes from Letter Head + print_branding theme for the document Company."),

])

# ========== 25 ==========
add(25, "Employee Checkin geolocation blink fix", [
p("HRMS Employee Checkin can flash a geolocation map/section before HR Settings are known, causing a UI 'blink'."),
ul([
"hooks <code>doctype_js</code> maps Employee Checkin → <code>public/js/tvx_employee_checkin.js</code>",
"Script hides geolocation UI until HR Settings confirm it should show",
"Result: no flash of irrelevant map controls for sites that disable geo check-in",
]),
code("""# hooks.py
doctype_js = {
  "Employee Checkin": "public/js/tvx_employee_checkin.js",
}"""),

h3("Problem statement"),
p("Employee Checkin forms briefly render a map / geolocation block before client scripts know whether HR Settings require location. Users see a flash (blink) of controls that then disappear."),
h3("Fix approach"),
steps([
"hooks doctype_js loads tvx_employee_checkin.js only on Employee Checkin.",
"Script starts with geolocation UI hidden.",
"After HR Settings (or equivalent flags) resolve, show geo UI only if enabled.",
]),
h3("Verification"),
ul([
"Open Employee Checkin with geo disabled in HR Settings — no map flash.",
"Enable geo requirement — map/controls appear without prior blink of the opposite state.",
"Other DocTypes unchanged (doctype_js scoped).",
]),

])

# ========== 26 ==========
add(26, "Dark mode notes", [
ul([
"Light-mode sidebar colors come from profile theme tokens (sidebar / sidebar_2).",
"Dark mode overrides are applied via CSS selectors such as <code>[data-theme=dark]</code> in triplevox_platform.css.",
"Accent greens/blues still follow the active client profile where variables are used.",
"Watermark/logo contrast: prefer dark-safe assets when Desk theme is dark.",
"After toggling Desk appearance, hard-refresh if variables look stale.",
]),
info("Client profiles document that light-mode sidebar is intentional; dark mode is CSS-driven rather than duplicating full CLIENTS theme dicts."),

h3("How dark mode interacts with profiles"),
ul([
"Accent tokens (green*) still come from the active client profile variables.",
"Sidebar background tokens are overridden under [data-theme=dark] so light greys are not forced.",
"Borders/ink/muted may shift for contrast; verify both TITA blue and BRG green accents on dark.",
]),
h3("QA matrix"),
table(["Mode", "Client", "Check"], [
["Light", "tita", "Blue accents, light sidebar, TITA watermark"],
["Light", "brg", "Green accents, BRG watermark"],
["Dark", "tita", "Readable sidebar, blue accents, logo contrast"],
["Dark", "brg", "Readable sidebar, green accents, logo contrast"],
]),
warn("If dark mode looks 'half themed', you likely have a stale CSS build — bump ?v= and clear-cache."),

])

# ========== 27 ==========
add(27, "after_migrate job list and order", [
p("From <code>hooks.py</code> — runs automatically after <code>bench migrate</code> in this order:"),
table(["#", "Callable", "Purpose"], [
["1", "triplevox_platform.setup.apply_branding_settings", "System/branding settings sync"],
["2", "triplevox_platform.branding_setup.run", "Website / chrome branding from Client Branding"],
["3", "triplevox_platform.workspace_viewer.run", "Ensure Workspace Viewer role + guards"],
["4", "triplevox_platform.role_packs.run", "Ensure Shop Floor / QC / Ops Admin / Viewer roles"],
["5", "triplevox_platform.print_branding.run", "Install Print Style + TripleVox formats"],
["6", "triplevox_platform.sync_tita_production.run", "TITA production workspace sync"],
["7", "triplevox_platform.sync_employee_hub.run", "Employee hub sync"],
["8", "triplevox_platform.sync_company_saas.run", "Company & SaaS workspace sync"],
["9", "triplevox_platform.nest_desktop_icons.run", "Desktop icon nesting"],
["10", "triplevox_platform.nest_manufacturing_sidebar.run", "Manufacturing sidebar nesting"],
]),
warn("If migrate fails midway, later jobs may not run. Re-run migrate after fixing the error; jobs are designed to be idempotent."),
])


# ========== 28 ==========
add(28, "Complete file map — purpose & what-if for every key file", [
p("Use this chapter when debugging: each path has <strong>Purpose</strong> (what it does) and <strong>What if</strong> (symptoms / when to touch it)."),
table(["File", "Purpose", "What if"], [
["hooks.py", "Registers CSS/JS (?v= bumps), after_migrate jobs, boot_session, website context, doctype_js, apps screen", "Stale UI after edit → bump ?v= + clear-cache. New migrate job missing → add here then migrate."],
["boot.py", "Injects frappe.boot.triplevox branding payload on Desk load", "Desk logos/theme wrong → check boot payload in browser console; rebuild Client Branding."],
["client_theme.py", "Loads Client Branding → profiles, login company options, site default payload, theme tokens", "Login/company logos wrong → fix Client Branding fields; private files auto-publicized."],
["website_csrf.py", "Guest CSRF + injects product/client logos into login Jinja context", "Login logos blank/broken → check tvx_product_logo / client_logo_url; clear-website-cache."],
["api.py", "Company switcher, onboarding, login company apply, role/print APIs", "Switcher fails → permission / API error in Network tab."],
["setup.py / branding_setup.py", "Apply System Settings / website chrome from branding", "Favicon/splash stale after save → re-save Client Branding or run apply_branding_settings."],
["tvx/doctype/client_branding/*", "UI form for Product/Client/Print logos, accents, sidebar dark colors, support, watermarks", "Upload logos as Attach Image (auto-public). Empty Product Logo → stock TripleVox mark."],
["nest_desktop_icons.py", "Nests Desktop Icons under hubs; clears Desktop Layouts", "Wrong icon parents after migrate → re-run nest_desktop_icons.run."],
["nest_manufacturing_sidebar.py", "Manufacturing workspace sidebar nesting", "Mfg sidebar flat → re-run after_migrate job."],
["sync_employee_hub.py", "Employee Hub workspace + desktop launcher (no HRMS kids on flyout)", "Hub missing → execute sync_employee_hub.run."],
["sync_tita_production.py / sync_company_saas.py", "TITA production workspace / Company & SaaS chrome", "Industry hub missing → re-run corresponding sync."],
["print_branding.py / print_pack.py", "Print formats + Letter Head / company print logos", "PDF shows wrong logo → print pack for that Company; never vendor marks."],
["role_packs.py / workspace_viewer.py", "Role packs + Workspace Viewer read-only guards", "Users can edit workspaces → ensure Viewer role + workspace_viewer.run."],
["public/js/triplevox_desk.js", "Desktop polish, flyouts, theme toggle, clock, watermark, canvas colors, dark tokens", "Flyout blink / wrong theme → bump desk.js ?v=; hard refresh."],
["public/js/tvx_shell_panels.js", "Account sheet, About dialog, native menu polish (Launchpad disabled — flyout only)", "Old full-screen picker flashes → CSS hides .desktop-modal on desktop."],
["public/js/tvx_saas_ui.js", "Company & SaaS dialogs, switcher, onboarding wizard", "Wizard missing → System Manager + tvx_saas_ui loaded."],
["public/js/tvx_login.js", "Login light/dark theme toggle + auth panel routing", "Theme toggle dead → check tvx_login.js include on login.html."],
["public/js/tvx_early.js", "Early Desk class hooks before full paint", "Sidebar blink on desktop → early hide classes."],
["public/js/tvx_employee_checkin.js", "Hide geolocation until HR Settings ready", "Checkin map blink → doctype_js hook present."],
["public/css/triplevox_platform.css", "Desk theme: soft canvas #f6f7f9, gray fields, dark flyout, brand navbar, sidebar select", "Styles not applying → ?v= bump + clear-cache."],
["public/css/tvx_login.css", "Login layout, company showcase, product+client marks", "Broken layout → login.css version on login.html."],
["www/login.html", "Login template: Product Logo header, Client Logo company tiles", "Wrong marks → Client Branding Product/Client Logo fields."],
["print/templates + print/css", "Jinja print chrome", "Print look wrong → print_branding.run."],
["public/images/*", "Packaged TripleVox marks, watermarks, Tabler module icons", "404 on assets → bench build / symlink apps."],
["docs/TripleVox_UI_Final_Guide.html", "This final guide (all chapters + file what-ifs)", "Regenerate via docs/_generate_complete_guide.py."],
]),
h3("Asset URL pattern"),
code("/assets/triplevox_platform/css/triplevox_platform.css?v=20260802x\n/assets/triplevox_platform/js/triplevox_desk.js?v=20260802x\n/assets/triplevox_platform/images/triplevox-logo.png"),
info("Bump the ?v= query in hooks.py (and login.html) after every UI change so browsers fetch fresh assets."),
])

# ========== 29 ==========
add(29, "Bench command cheat sheet (long)", [
h3("Site & apps"),
code("""bench new-site erp.local
bench drop-site erp.local --force          # destructive — care!
bench get-app https://github.com/gmt-erpsol/Triplevoxui.git --branch main
bench get-app erpnext --branch version-16
bench get-app hrms --branch version-16
bench --site erp.local install-app erpnext
bench --site erp.local install-app hrms
bench --site erp.local install-app triplevox_platform
bench --site erp.local list-apps
bench --site erp.local uninstall-app triplevox_platform   # rare"""),
h3("Migrate / cache / build / process"),
code("""bench --site erp.local migrate
bench --site erp.local clear-cache
bench --site erp.local clear-website-cache
bench build --app triplevox_platform
bench build
bench restart
bench --site erp.local doctor
bench --site erp.local show-config
bench --site erp.local set-config triplevox_client tita
bench --site erp.local console"""),
h3("TripleVox execute helpers"),
code("""bench --site erp.local execute triplevox_platform.role_packs.run
bench --site erp.local execute triplevox_platform.print_branding.run
bench --site erp.local execute triplevox_platform.print_pack.apply_print_pack --kwargs \"{'company':'BRG Trading PLC'}\"
bench --site erp.local execute triplevox_platform.setup_brg.ensure_brg_company
bench --site erp.local execute triplevox_platform.setup.apply_branding_settings
bench --site erp.local execute triplevox_platform.workspace_viewer.run
bench --site erp.local execute triplevox_platform.nest_desktop_icons.run
bench --site erp.local execute triplevox_platform.nest_manufacturing_sidebar.run
bench --site erp.local execute triplevox_platform.sync_tita_production.run
bench --site erp.local execute triplevox_platform.sync_employee_hub.run
bench --site erp.local execute triplevox_platform.verify_branding.run"""),
h3("Users & maintenance"),
code("""bench --site erp.local add-user user@example.com --first-name Ops --last-name User
bench --site erp.local set-admin-password 'NewStrongPassword'
bench --site erp.local backup
bench --site erp.local backup --with-files
bench --site erp.local partial-restore /path/to/sql.gz
bench update --reset          # production caution
bench switch-to-branch version-16 frappe erpnext hrms"""),
h3("Dev server"),
code("""bench start
bench --site erp.local serve --port 8000
bench watch"""),
])

# ========== 30 ==========
add(30, "Go-live checklist (new PC / new sister company / production)", [
h3("A) New PC / new Bench"),
steps([
"Install WSL2 + Ubuntu + Bench prerequisites (ch. 3–4).",
"bench init + create site + install erpnext + hrms (ch. 5).",
"Install triplevox_platform from GitHub with correct folder name (ch. 6).",
"migrate + clear-cache + build + first login verify (ch. 8–9).",
"Create Companies; map profiles; apply print packs (ch. 14–19).",
"Assign role packs; test login picker + switcher (ch. 15–18).",
"Optional: install titacustom for TITA logos/MES (ch. 10).",
"Document site URL, admin password location, backup schedule.",
]),
h3("B) New sister company on existing site"),
steps([
"Onboard via wizard OR setup_brg / manual Company + site_config map.",
"Apply print pack for the new company.",
"Upload/confirm logo URLs resolve (200).",
"Assign users' Employee.company / defaults.",
"Test switcher + one PDF per major DocType.",
"clear-cache + Ctrl+Shift+R.",
]),
h3("C) Production hardening"),
ul([
"DNS + TLS (Let's Encrypt / corporate cert)",
"bench setup production + nginx + supervisor/systemd",
"Scheduled backups off-box; restore drill once",
"Disable developer_mode; review CORS / host_name in site_config",
"Monitor disk for sites/*/private/files and logs",
"Pin app commits/tags; document upgrade window",
]),
])

# ========== 31 ==========
add(31, "Update / upgrade from GitHub", [
steps([
"cd ~/frappe-bench/apps/triplevox_platform",
"git fetch origin && git pull origin main  (or your release branch/tag)",
"Confirm folder is still named triplevox_platform",
"cd ~/frappe-bench",
"bench --site S migrate",
"bench --site S clear-cache",
"bench build --app triplevox_platform",
"Bump ?v= in hooks.py if pull did not already",
"bench restart (prod)",
"Hard-refresh browsers; spot-check switcher, login, one print",
]),
code("""cd ~/frappe-bench/apps/triplevox_platform
git pull origin main
cd ~/frappe-bench
bench --site erp.local migrate
bench --site erp.local clear-cache
bench build --app triplevox_platform
bench restart"""),
warn("If you maintain a Windows working copy + rsync, pull on the source of truth then rsync into apps/ before migrate."),
])

# ========== 32 ==========
add(32, "Troubleshooting encyclopedia (blank pages, cache, switcher missing, wrong print logo, migrate sidebar errors, CSRF login…)", [
h3("Blank Desk / white page"),
ul([
"Browser console 404/500 on JS — rebuild assets; check soft-link apps/triplevox_platform",
"Python traceback in worker logs — bench --site S console / doctor",
"Wrong app folder name (Triplevoxui) — rename to triplevox_platform",
"Hard refresh + clear-cache",
]),
h3("Cache / theme not updating"),
ul([
"bench --site S clear-cache && clear-website-cache",
"Bump hooks ?v= for CSS/JS",
"Ctrl+Shift+R; try private window",
"Confirm site_config JSON valid (trailing commas break loads)",
]),
h3("Company switcher missing"),
ul([
"tvx_saas_ui.js listed in app_include_js and loading 200",
"At least one mapped company exists in DB",
"User logged into Desk (not website)",
"No JS error before saas UI init",
]),
h3("Wrong print logo"),
ul([
"Document Company field value",
"Letter Head image for that company",
"Company logo field",
"profile print_logo_url for mapped key",
"Re-run print pack + print_branding.run",
"User selected a TripleVox … Print Format (not Standard)",
]),
h3("Migrate / sidebar nesting errors"),
ul([
"Read traceback — often Workspace Sidebar Item conflicts",
"Re-run individual after_migrate jobs via bench execute",
"Ensure Workspace Viewer / System Manager not fighting custom sidebars",
"Check sync_tita_production / nest_* scripts for missing DocTypes on sites without titacustom",
]),
h3("CSRF / login “Something went wrong”"),
ul([
"website_csrf.update_website_context should inject token for Guest",
"Confirm update_website_context hook present after pull",
"clear-website-cache; retry login",
"Clock skew / proxy stripping cookies — check site host_name and HTTPS",
]),
h3("Login brand not applied after sign-in"),
ul([
"localStorage tvx_login_company_key",
"sessionStorage apply flag stuck — clear site data for origin",
"apply_login_company_key API permissions / network tab",
]),
h3("Role pack “not permitted”"),
p("Need System Manager / Administrator for assign_role_pack and onboarding."),
h3("Workspace still editable"),
p("Assign Workspace Viewer; ensure user is not also Workspace Manager / System Manager."),
h3("Asset 404 under /assets/triplevox_platform"),
code("""bench build --app triplevox_platform
ls sites/assets/triplevox_platform
# fix app folder name if wrong"""),
])

# ========== 33 ==========
add(33, "FAQ", [
h3("Can one site serve TITA and BRG?"),
p("Yes — that is the primary SaaS shell design. Map both Companies to tita/brg profiles and use the switcher."),
h3("Do I need titacustom for BRG?"),
p("No. BRG logos ship inside triplevox_platform. titacustom is for TITA MES and TITA SVG logo asset path."),
h3("Why is the Desk logo still TripleVox after switching to BRG?"),
p("By design. Product chrome stays TripleVox; watermark/accents/prints follow the sister company."),
h3("Are role packs full permissions?"),
p("No — they are Desk roles / starters. Configure DocPerms as needed."),
h3("Where do I change accent colors?"),
p("client_theme.py CLIENTS theme dict, or site_config triplevox_theme / triplevox_company_themes overlays."),
h3("How do I force browsers to load new CSS?"),
p("Bump ?v= in hooks.py, clear-cache, hard refresh."),
h3("GitHub repo name vs app name?"),
p("Repo Triplevoxui → folder/app triplevox_platform."),
h3("Which Print Format should users pick?"),
p("Any format named TripleVox … for branded output."),
])

# ========== 34 ==========
add(34, "Glossary", [
table(["Term", "Definition"], [
["Bench", "Frappe command-line tool and project layout managing sites and apps"],
["Site", "A tenant under sites/ with its own DB and site_config.json"],
["Desk", "Frappe back-office SPA UI after login"],
["Company", "ERPNext Company DocType — legal entity / books"],
["Profile key", "CLIENTS key such as tita, brg, demo"],
["Watermark pill", "Bottom-left Desk chrome showing sister-company mark"],
["Print pack", "Letter Head + logo + print_branding refresh for one company"],
["Role pack", "Assignable TripleVox Desk role bundle"],
["Workspace Viewer", "Role that can open workspaces but not edit layouts"],
["after_migrate", "Hook list run at end of bench migrate"],
["titacustom", "Optional TITA manufacturing domain app"],
["Cache bump (?v=)", "Query string on asset URLs to bust browser cache"],
["boot.triplevox", "Branding payload injected into frappe.boot"],
["Letter Head", "ERPNext header HTML/image used on prints"],
["WSL2", "Windows Subsystem for Linux used to run Ubuntu Bench on Windows"],
]),
])

# ========== 35 ==========
add(35, "Support / credits", [
card("Support", ul([
"Internal: TripleVox Engineering PLC platform team",
"Email (hooks metadata): admin@triplevox.com",
"GitHub issues (if enabled on repo): https://github.com/gmt-erpsol/Triplevoxui",
])),
card("Credits", ul([
"Built on Frappe Framework, ERPNext, and HRMS (open source)",
"UI shell & multi-company SaaS features: TripleVox Platform (triplevox_platform)",
"Module icon set includes Tabler icons (see public/images/module_icons/tabler/LICENSE.txt)",
"Documentation style inspired by frappeframework.com docs",
])),
p("© TripleVox Engineering PLC — Platform UI final guide. App version 1.0.0 (hooks)."),
info("Canonical docs: <code>docs/TripleVox_UI_Final_Guide.html</code> (this file). Complete guide copy also kept in sync. USER_GUIDE.md is a short pointer."),
])

# ========== 36 ==========
add(36, "Client Branding DocType (source of truth for logos & colors)", [
p("All sister-company / product-owner marks are edited in Desk: <strong>Client Branding</strong> (not hard-coded in Python)."),
table(["Field group", "Purpose", "What if empty"], [
["Product Logo", "Product owner / ISV mark — login header, favicon/splash fallback, Desk product chrome", "Falls back to packaged TripleVox logo"],
["Client Logo", "Sister company mark — login company tiles, navbar, watermark pill preference", "Company tile shows initials; navbar may use product logo"],
["Print Logo", "PDF / Letter Head preference", "Print pack uses company Letter Head / company logo chain"],
["Accent + sidebar (+ dark)", "Desk CSS tokens --tvx-green*, --tvx-sidebar*", "Defaults to TITA-like blue / soft slate"],
["Watermark light/dark", "Soft full-bleed + flyout / menu backgrounds", "Packaged triplevox-watermark*.png"],
["Support label/email/URL", "Native menu foot / support chip", "Hidden if blank"],
["is_site_default", "Which branding Guest login / site payload uses", "First enabled row or neutral shell"],
]),
warn("Attach Image uploads are forced public so Guest login can load them. Private /private/files URLs break login logos."),
steps([
"Open Client Branding → New or edit row",
"Set Client Key, Company link, Product Logo, Client Logo, accents",
"Save → clear-cache / hard refresh login + Desk",
"Confirm login header = Product Logo; company tile = Client Logo",
]),
])

# ========== 37 ==========
add(37, "Desktop grouped icons — sticky flyout (no Launchpad)", [
p("Grouped Desktop Icons open a <strong>sticky flyout</strong> only. The old folder modal / Launchpad is suppressed."),
ul([
"Open on hover (or click) of a folder hub",
"Stays open until click-outside, Esc, close ×, or hover another desktop icon",
"Soft watermark inside the flyout panel (light + dark)",
"Employee Hub is a single launcher — no HRMS child strip",
"Child-count badges removed",
]),
h3("What if"),
ul([
"Blink of old modal → ensure tvx-on-desktop CSS hides .desktop-modal + capture-phase click in triplevox_desk.js",
"Flyout white in dark mode → #tvx-folder-flyout dark rules need !important (ID specificity)",
"Wrong children → check nest_desktop_icons parent_icon + boot.desktop_icons",
]),
])

# ========== 38 ==========
add(38, "Desktop navbar, theme toggle, soft canvas & fields", [
table(["Feature", "Behavior", "What if"], [
["Brand navbar", "Desktop top bar uses Client Branding accent (--tvx-desktop-nav)", "Still black → theme.green missing on boot.triplevox"],
["Notification bell", "Forced white strokes on brand navbar", "Invisible → text-muted stripped + SVG stroke CSS"],
["Half-moon toggle", "Before notifications; toggles light/dark", "Missing → inject_desktop_theme_toggle on desktop"],
["Work canvas", "Light main area #f6f7f9 (not pure white)", "Too white → check FINAL html:not(dark) --tvx-page overrides"],
["Form fields", "Light gray #f3f3f3 like Frappe control-bg", "Still white → --tvx-field-bg not applied / tvx-readable"],
["Dark sidebar select", "Soft tint + brand text (same pattern as light)", "Solid green pill → old dark active CSS; use --tvx-sidebar-active-*"],
]),
])

# ========== 39 ==========
add(39, "Login logos — Product owner + Client (always from form)", [
p("Login never prefers Company.company_logo for showcase marks."),
table(["Surface", "Source field", "What if missing"], [
["Header mark", "Client Branding → Product Logo (site default)", "Packaged TripleVox logo"],
["Header client chip", "Client Branding → Client Logo (site default)", "Chip hidden"],
["Company tiles", "Client Branding → Client Logo for mapped company", "Initials fallback"],
]),
code("bench --site S clear-website-cache\n# then hard-refresh /login"),
])

# ========== 40 ==========
add(40, "Dark mode Desk shell notes (2026 refresh)", [
ul([
"html[data-theme=dark] / tvx-frappe-dark: page canvas follows Frappe --bg-color",
"Sidebar uses Client Branding sidebar_color_dark / sidebar_color_2_dark when set",
"Flyout, About, menus use dark surfaces + dark watermark",
"sync_shell_canvas clears forced light inline backgrounds in dark",
]),
warn("If automatic theme follows OS, MutationObserver on data-theme re-syncs tokens."),
])

# Expand page count with appendix-style deep dives (still part of ch content via extra sections already generous)
# Emit HTML
def build_html():
    toc_items = []
    body = []
    for num, title, html in CHAPTERS:
        anchor = f"ch-{num:02d}"
        toc_items.append(f'<li><a href="#{anchor}">{num:02d}. {title}</a></li>')
        body.append(f'''<section class="chapter" id="{anchor}">
<div class="ch-header">TripleVox Platform Documentation</div>
<h2>{num:02d}. {title}</h2>
{html}
</section>''')
    toc = "\n".join(toc_items)
    chapters_html = "\n".join(body)
    n = len(CHAPTERS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>TripleVox Platform — Final UI Guide</title>
<style>{CSS}</style>
</head>
<body>
<div class="doc-wrap">
  <header class="hero">
    <div class="eyebrow">TripleVox Platform Documentation</div>
    <h1>Final UI Guide</h1>
    <p>Complete reference for installers, System Managers, and support engineers.
    Preserves the original Complete Guide chapters and adds Client Branding, sticky flyouts,
    login Product/Client logos, dark Desk shell, and a file-by-file Purpose / What-if map.</p>
    <div class="meta-row">
      <span class="badge">App: triplevox_platform</span>
      <span class="badge">Frappe v16 Desk</span>
      <span class="badge">GitHub: gmt-erpsol/Triplevoxui</span>
      <span class="badge">{n} chapters</span>
      <span class="badge">Final Guide 2026-08</span>
    </div>
  </header>

  <nav class="toc">
    <h2>Table of contents</h2>
    <ol>
{toc}
    </ol>
  </nav>

{chapters_html}

  <div class="footer-note">
    TripleVox Platform Documentation — Final UI Guide.
    Paths: docs/TripleVox_UI_Final_Guide.html (canonical) · docs/TripleVox_UI_App_Complete_Guide.html (synced copy).
  </div>
</div>
</body>
</html>
"""

def main():
    html = build_html()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    try:
        OUT_COMPLETE.write_text(html, encoding="utf-8")
    except Exception:
        pass
    try:
        DL_HTML.parent.mkdir(parents=True, exist_ok=True)
        DL_HTML.write_text(html, encoding="utf-8")
        dl_msg = str(DL_HTML)
    except Exception as e:
        dl_msg = f"(skip downloads copy: {e})"
    print("WROTE", OUT, "bytes", OUT.stat().st_size)
    print("CHAPTERS", len(CHAPTERS))
    print("DOWNLOADS_HTML", dl_msg)

if __name__ == "__main__":
    main()

