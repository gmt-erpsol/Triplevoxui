# TripleVox UI App — Simple User Guide

**App name:** `triplevox_platform`  
**What it is:** The look-and-feel layer for Desk (colors, login, icons, workspaces, branded PDF prints).  
**What it is not:** Factory / manufacturing logic. That lives in a separate optional app called `titacustom`.

You can install this UI app on **any** ERPNext + HRMS site for **any** client company. It is not locked to TITA.

---

## 1. Install from GitHub (any PC)

You need a working Frappe Bench v16 with `frappe`, `erpnext`, and `hrms` already on the site.

```bash
cd ~/frappe-bench

# 1) Download the UI app (use your real GitHub URL)
bench get-app https://github.com/YOUR_ORG/YOUR_UI_REPO.git --branch main

# If the folder name is wrong, rename it:
# mv apps/SomeOtherName apps/triplevox_platform

# 2) Install + migrate (creates print formats, branding, workspaces)
bench --site YOUR_SITE install-app triplevox_platform
bench --site YOUR_SITE migrate

# 3) Pick the client theme profile (tita, demo, or your key)
bench --site YOUR_SITE set-config triplevox_client tita

# 4) Refresh
bench build --app triplevox_platform   # optional if Node works
bench --site YOUR_SITE clear-cache
bench restart
```

Then open Desk and press **Ctrl+Shift+R** (hard refresh).

### Optional — TITA factory features

Only if you need recipes, MTO work orders, QC, etc.:

```bash
bench get-app https://github.com/YOUR_ORG/TitaCustom.git --branch main
# mv apps/TitaCustom apps/titacustom   # if needed
bench --site YOUR_SITE install-app titacustom
bench --site YOUR_SITE migrate
```

---

## 2. How branding works (multi-client)

| What you see | Where it comes from |
|--------------|---------------------|
| Desk sidebar / watermark / login | TripleVox product look + client profile in `client_theme.py` |
| PDF / Print header company name | **ERPNext Company** (the company on the document) |
| PDF logo | Company Letter Head → Company Logo → optional `print_logo_url` on the client profile |
| PDF soft watermark | Same company logo (or monogram initials) — faint in the background |
| Accent colors (green/teal…) | Active client profile theme |

### New client checklist

1. Open `triplevox_platform/client_theme.py` and copy the `demo` block → rename key (e.g. `acme`).
2. Set `client_full_name`, colors, optional `print_logo_url` / `factory_area`.
3. On the site: `bench --site SITE set-config triplevox_client acme`
4. Put the real logo on **Company** or **Letter Head** (best for prints).
5. `bench --site SITE migrate` and clear-cache.

**Important:** Desk may show the TripleVox mark. Prints show the **client company**, not TripleVox.

---

## 3. How printing works

On every `bench migrate`, the app installs:

- Print Style: **TripleVox Brand**
- Print Formats named **TripleVox …** for common DocTypes
- Sets them as the DocType default print format when possible

### Formats included

Sales Invoice, Sales Order, Quotation, Delivery Note, Purchase Order, Purchase Invoice, Purchase Receipt, Request for Quotation, Supplier Quotation, Material Request, Payment Entry, Journal Entry, Stock Entry, Expense Claim, Salary Slip, Leave Application, Work Order, Job Card, BOM.

All share the **same layout** (header, meta boxes, table, signatures). Only the fields/title change.

To reinstall prints after editing templates:

```bash
bench --site YOUR_SITE execute triplevox_platform.print_branding.run
bench --site YOUR_SITE clear-cache
```

---

## 4. Every important file (what to open when debugging)

Root: `apps/triplevox_platform/`

### Root docs / packaging

| File | Purpose |
|------|---------|
| `README.md` | Short install notes |
| `DEPLOY.md` | Deploy options |
| `USER_GUIDE.md` | This guide |
| `CODEBASE_INDEX.md` | Quick file index |
| `pyproject.toml` | Python package definition |
| `license.txt` | License |
| `scripts/install_or_update.sh` | migrate + clear-cache helper |

### Python package (`triplevox_platform/`)

| File | Purpose | If broken… |
|------|---------|------------|
| `hooks.py` | Loads CSS/JS, boot, after_migrate jobs, print Jinja helpers | CSS/JS not loading? Check paths and `?v=` bump |
| `boot.py` | Injects branding into Desk every login | Wrong product name on Desk |
| `client_theme.py` | Client profiles (tita / demo / …) | Wrong client name or colors |
| `setup.py` | Writes System / Navbar / Website settings on migrate | Branding not applying; also protects default_app / company |
| `print_branding.py` | Installs Print Style + Formats; `get_print_theme()` | Wrong print logo/company |
| `workspace_viewer.py` | Read-only Workspace Viewer role | Users can/cannot edit workspaces |
| `website_csrf.py` | Login page CSRF / logo context | Login “Something went wrong” |
| `sync_employee_hub.py` | Employee Hub workspace | Hub missing |
| `sync_tita_production.py` | Manufacturing workspace | MFG icons missing |
| `nest_desktop_icons.py` | Groups Desktop icons | Icons in wrong folders |
| `nest_manufacturing_sidebar.py` | Manufacturing sidebar links | Sidebar routes wrong |
| `patches.txt` | DB patches (currently empty) | — |

### Desk look (`public/`)

| Path | Purpose | If broken… |
|------|---------|------------|
| `public/css/triplevox_platform.css` | Whole Desk theme, forms, Quill, dark mode | Ugly forms, Text Editor white bar, Link dropdown clipped |
| `public/css/tvx_login.css` | Login page style | Ugly login |
| `public/js/triplevox_desk.js` | Watermark, desktop polish, navbar text | Watermark gone / wrong |
| `public/js/tvx_login.js` | Login JS | Login quirks |
| `public/images/triplevox-logo.png` | Desk / login logo | Broken image |
| `public/images/module_icons/` | Desktop icon SVGs | Missing icons |

Served in browser as `/assets/triplevox_platform/...` (symlink to `public/`).

### Login

| Path | Purpose |
|------|---------|
| `www/login.html` | Custom login page template |

### Prints

| Path | Purpose |
|------|---------|
| `templates/includes/tvx_print_macros.html` | Shared header / footer / CSS / watermark |
| `print/css/tvx_print_style.css` | Print Style CSS tokens |
| `print/templates/transaction.html` | Shared SO/SI/PO/… layout |
| `print/templates/salary_slip.html` | Payslip |
| `print/templates/payment_entry.html` | Payment receipt |
| `print/templates/leave_application.html` | Leave form |
| `print/templates/work_order.html` | Work Order |
| `print/templates/stock_entry.html` | Stock Entry |
| `print/templates/journal_entry.html` | Journal Entry |
| `print/templates/expense_claim.html` | Expense Claim |
| `print/templates/job_card.html` | Job Card |
| `print/templates/bom.html` | BOM |

Print HTML is **not** under `sites/assets/`. It lives in the app package and is stored into Print Format records on migrate.

---

## 5. What to do if…

| Problem | Fix |
|---------|-----|
| Desk unchanged after install | Confirm `list-apps` shows `triplevox_platform` (not only `titacustom`). Hard refresh. |
| Old CSS / Text Editor still broken | `clear-cache` + Ctrl+Shift+R. Confirm `hooks.py` has a new `?v=` value. |
| Link suggestions hidden under next section | CSS fix in `triplevox_platform.css` (overflow visible + awesomplete z-index). Redeploy CSS. |
| Print formats missing on another PC | Those files must be **committed and pushed** to GitHub, then `git pull` + `migrate`. |
| Print shows wrong company | Check document Company field + Global Defaults. Logo = Company / Letter Head. |
| Print shows TripleVox logo | Remove vendor logo from Company/Letter Head; set a real company logo. |
| Default company “gone” after install | Check **Setup → Global Defaults**. UI app must not clear it; `setup.py` no longer overwrites `default_app` blindly. |
| Default app opens broken “titacustom” | Install `titacustom` or set System Settings Default App to `erpnext`. |
| Private GitHub clone fails | Use SSH URL or a personal access token. |
| Watermark missing | Check `triplevox_desk.js` ran; body should have `#tvx-watermark` and `#tvx-watermark-bg`. |

---

## 6. Update checklist (after new UI commits)

```bash
cd ~/frappe-bench/apps/triplevox_platform
git pull origin main

cd ~/frappe-bench
bench setup requirements
bench build --app triplevox_platform
bench --site YOUR_SITE migrate
bench --site YOUR_SITE clear-cache
```

Hard-refresh the browser.

---

## 7. Safe commands for checks

```bash
bench --site YOUR_SITE list-apps
bench --site YOUR_SITE execute triplevox_platform.print_branding.get_print_theme
bench --site YOUR_SITE execute triplevox_platform.workspace_viewer.inspect
```

In console:

```python
frappe.db.get_single_value("Global Defaults", "default_company")
frappe.db.get_single_value("System Settings", "default_app")
frappe.conf.get("triplevox_client")
```

---

TripleVox Engineering PLC · `triplevox_platform` · keep this file with the app so other PCs can debug without Cursor.
