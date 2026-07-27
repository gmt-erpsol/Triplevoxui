# TripleVox Platform

White-label Frappe **v16** Desk shell: global CSS/JS, client theming, desktop icon nesting, Employee Hub sync, and manufacturing sidebar layout.

## Dependencies

- `frappe`, `erpnext`, `hrms`
- **titacustom** (recommended — apps screen links to TITA Manufacturing)

## Install

```bash
cd $PATH_TO_YOUR_BENCH
# Copy or get-app this folder into apps/triplevox_platform
bench --site YOUR_SITE install-app triplevox_platform
bench --site YOUR_SITE migrate
bench --site YOUR_SITE clear-cache
```

Hard-refresh the browser after install (`Ctrl+Shift+R`).

## Structure

```
triplevox_platform/
├── pyproject.toml
├── license.txt
├── README.md
└── triplevox_platform/
    ├── hooks.py
    ├── boot.py
    ├── client_theme.py
    ├── setup.py
    ├── modules.txt
    ├── patches.txt
    └── public/
        ├── css/triplevox_platform.css
        ├── js/triplevox_desk.js
        └── images/
```

## Theme a client site

1. Add a profile in `triplevox_platform/client_theme.py`.
2. `bench --site YOUR_SITE set-config triplevox_client your_key`
3. `bench --site YOUR_SITE execute triplevox_platform.setup.apply_branding_settings`
4. Clear cache and hard-refresh.

## License

MIT — TripleVox Engineering PLC
