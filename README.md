# TripleVox Platform (TITA / multi-client Desk UI)

White-label **Frappe v16** Desk shell: CSS/JS, client themes, workspaces, branded prints, Workspace Viewer.

This app is **separate** from `titacustom`. You do **not** need `titacustom` to run the UI.

## Dependencies

- `frappe`, `erpnext`, `hrms` (v16)
- `titacustom` — **optional** (only for TITA manufacturing features)

## Install from GitHub (recommended)

Full guide: [`docs/Deploy_UI_App_From_GitHub.md`](../../docs/Deploy_UI_App_From_GitHub.md)

```bash
cd ~/frappe-bench

# 1) Clone UI app
bench get-app https://github.com/YOUR_ORG/triplevox_platform.git --branch main

# 2) Install + migrate
bench --site YOUR_SITE install-app triplevox_platform
bench --site YOUR_SITE migrate

# 3) Client theme (example: TITA)
bench --site YOUR_SITE set-config triplevox_client tita
bench --site YOUR_SITE execute triplevox_platform.setup.apply_branding_settings

# 4) Cache
bench build --app triplevox_platform   # optional if Node available
bench --site YOUR_SITE clear-cache
```

Hard-refresh the browser (`Ctrl+Shift+R`).

### One-shot helper script

From the monorepo (or copy the script into the bench):

```bash
export SITE=YOUR_SITE
export UI_GIT_URL=https://github.com/YOUR_ORG/triplevox_platform.git
export CLIENT=tita
bash dev-scripts/install_ui_from_github.sh
```

## Update from GitHub

```bash
cd ~/frappe-bench/apps/triplevox_platform && git pull
cd ~/frappe-bench
bench --site YOUR_SITE migrate
bench --site YOUR_SITE clear-cache
```

## Theme a client site

1. Add/edit a profile in `triplevox_platform/client_theme.py`.
2. `bench --site YOUR_SITE set-config triplevox_client your_key`
3. `bench --site YOUR_SITE execute triplevox_platform.setup.apply_branding_settings`
4. Clear cache and hard-refresh.

Print logos use **Company logo → client logo → monogram** (never TripleVox product mark on PDFs).

## License

MIT — TripleVox Engineering PLC
