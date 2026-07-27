# TripleVox Platform (`triplevox_platform`) — Codebase Index

Every source file starts with a **TITA/TripleVox file identification** header.

## Core UI

| File | What it does |
|------|----------------|
| `hooks.py` | CSS/JS includes, boot_session, after_migrate |
| `boot.py` | Branding in desk bootinfo |
| `client_theme.py` | Multi-client CSS variables |
| `setup.py` | Branding settings after migrate |

## Desk assets

| File | What it does |
|------|----------------|
| `public/css/triplevox_platform.css` | Theme, sidebar, dark mode, form sidebar width |
| `public/js/triplevox_desk.js` | Watermark, sidebar brand, desktop polish |

## Workspace sync

| File | What it does |
|------|----------------|
| `sync_employee_hub.py` | Employee Hub workspace + icon |
| `sync_tita_production.py` | TITA Manufacturing workspace |
| `nest_desktop_icons.py` | Desktop icon grouping |
| `nest_manufacturing_sidebar.py` | Manufacturing sidebar routes |
| `fix_desktop_icons.py` | Repair broken SVG icons |

## Verify / diagnostic

| File | What it does |
|------|----------------|
| `verify_branding.py` | Check site branding |
| `verify_desktop.py` | Check desktop icons |
| `_check_doctypes.py` | DocType presence check |

See also: `docs/TripleVox_Platform_Developer_Guide.html`
