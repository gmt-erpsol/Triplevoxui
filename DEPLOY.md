# Deploy TripleVox Platform (UI app) on any PC

This app is a normal Frappe app. You do **not** need the Windows `TITA-ERP-BRD` folder layout — only a Frappe bench.

## Prerequisites (once per machine)

1. WSL2 Ubuntu (or Linux / macOS)
2. [Frappe Bench](https://frappeframework.com/docs/user/en/installation) with a site
3. Apps already on the site: `frappe`, `erpnext`, `hrms` (and usually `titacustom`)

## Option A — From Git (recommended)

```bash
cd ~/frappe-bench   # or your bench path

# Get the UI app
bench get-app triplevox_platform /path/or/git/url/to/triplevox_platform
# Example if the app lives inside your monorepo:
#   bench get-app /mnt/c/Users/YOU/Documents/TITA-ERP-BRD/apps/triplevox_platform

bench --site YOUR_SITE.local install-app triplevox_platform
bench --site YOUR_SITE.local migrate
bench --site YOUR_SITE.local clear-cache
bench --site YOUR_SITE.local clear-website-cache
```

Hard-refresh the browser (`Ctrl+Shift+R`).

## Option B — Copy folder into an existing bench

```bash
# From the PC that already has the app
cp -a apps/triplevox_platform /path/to/other-bench/apps/

cd /path/to/other-bench
bench setup requirements
bench --site YOUR_SITE.local install-app triplevox_platform   # skip if already installed
bench --site YOUR_SITE.local migrate
bench --site YOUR_SITE.local clear-cache
```

## One-shot sync (after code changes)

From the machine that has the source + WSL bench:

```bash
bash apps/triplevox_platform/scripts/install_or_update.sh YOUR_SITE.local
```

Or from this monorepo:

```bash
bash dev-scripts/install_triplevox_platform.sh YOUR_SITE.local
```

## Client branding (any company)

```bash
# Pick client profile (tita | demo | your_key in client_theme.py)
bench --site YOUR_SITE.local set-config triplevox_client tita

# Optional per-company print overrides
# bench --site YOUR_SITE.local set-config -p triplevox_company_themes '{"Acme PLC":{"accent":"#0e7490"}}'

bench --site YOUR_SITE.local execute triplevox_platform.setup.apply_branding_settings
bench --site YOUR_SITE.local execute triplevox_platform.print_branding.run
bench --site YOUR_SITE.local clear-cache
```

### Company logo on prints

Prints use **only** company branding:

1. **Letter Head** image (Company → Default Letter Head), or  
2. **Company → Company Logo**

If neither is set, prints show the company **monogram** (initials) — never the TripleVox logo.

## Workspace Viewer role

```bash
bench --site YOUR_SITE.local execute triplevox_platform.workspace_viewer.run
```

Then on a User: tick **Workspace Viewer** (+ roles that define which hubs they see, e.g. Employee).  
They can open/use workspaces; Edit / New Workspace is blocked.

## What “deploy UI app” means

| Step | Why |
|------|-----|
| App files under `bench/apps/triplevox_platform` | Python/JS/CSS source |
| `install-app` | Registers app on the site |
| `migrate` | Runs `after_migrate` (branding, prints, Employee Hub, icons) |
| `clear-cache` | Boots new JS/CSS and print formats |

Desk assets are served from `/assets/triplevox_platform/...` after migrate/build. On production also run:

```bash
bench build --app triplevox_platform
bench restart
```
