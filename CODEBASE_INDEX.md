# TripleVox Platform (`triplevox_platform`) — Codebase Index

White-label Frappe v16 Desk shell. Full plain-language guide: **USER_GUIDE.md**.

## Core

| File | What it does |
|------|----------------|
| `hooks.py` | CSS/JS includes, boot_session, after_migrate, Jinja print helpers |
| `boot.py` | Branding payload in desk bootinfo |
| `client_theme.py` | Multi-client profiles → CSS tokens + print accents |
| `setup.py` | Branding into System / Navbar / Website Settings (safe default_app) |
| `print_branding.py` | Print Style + Print Formats; `get_print_theme()` (Company-first) |
| `workspace_viewer.py` | Read-only Workspace Viewer role |
| `website_csrf.py` | Login CSRF / website context |

## Desk assets (`public/`)

| File | What it does |
|------|----------------|
| `public/css/triplevox_platform.css` | Theme, forms, Quill/Text Editor, Link dropdowns, dark mode |
| `public/css/tvx_login.css` | Login styling |
| `public/js/triplevox_desk.js` | Watermark, desktop polish, navbar brand |
| `public/js/tvx_login.js` | Login JS |
| `public/images/` | Logo + module icons |

## Workspace sync

| File | What it does |
|------|----------------|
| `sync_employee_hub.py` | Employee Hub workspace + icon |
| `sync_tita_production.py` | TITA Manufacturing workspace |
| `nest_desktop_icons.py` | Desktop icon grouping |
| `nest_manufacturing_sidebar.py` | Manufacturing sidebar routes |

## Prints

| Path | What it does |
|------|----------------|
| `templates/includes/tvx_print_macros.html` | Shared header, footer, CSS, watermark |
| `print/css/tvx_print_style.css` | Print Style CSS |
| `print/templates/transaction.html` | Shared commercial docs |
| `print/templates/*.html` | Payslip, PE, Leave, WO, Stock Entry, JE, Expense, Job Card, BOM |

## Login

| Path | What it does |
|------|----------------|
| `www/login.html` | Custom login page |

## Docs / scripts

| Path | What it does |
|------|----------------|
| `USER_GUIDE.md` | Layman install + file map + troubleshooting |
| `DEPLOY.md` | Deploy notes |
| `README.md` | Short overview |
| `scripts/install_or_update.sh` | Install/update helper |
