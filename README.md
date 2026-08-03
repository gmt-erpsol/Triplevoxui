# TripleVox Platform (reusable parent Desk UI)

White-label **Frappe v16** Desk shell: CSS/JS, **Client Branding** DocType, workspaces, branded prints, Workspace Viewer.

Same app code on every site. Logos, colors, and names live in **that site’s database** — not in Python catalogs.

This app is **separate** from `titacustom`. You do **not** need `titacustom` to run the UI.

## Dependencies

- `frappe`, `erpnext`, `hrms` (v16)
- `titacustom` — **optional** (plastics / MES features only)

## Install matrix

| Site type | Install | Branding |
|-----------|---------|----------|
| Shell-only (any client) | `triplevox_platform` | Create **Client Branding** + **Company** in Desk |
| TITA manufacturing | `triplevox_platform` + `titacustom` | Client Branding rows; TITA workspaces/icons migrate only when `titacustom` is installed |
| Multi-company on one site | `triplevox_platform` only | One Client Branding per company; link `Company` field |

**Warning:** Do **not** install `titacustom` on a shared multi-company site until its domain hooks are company-scoped. Today those hooks are site-wide and would apply to every Company on that site. Prefer **one Frappe site per client** when the domain app is required.

### Optional site_config flags

```json
{
  "triplevox_client": "acme",
  "triplevox_company_profiles": {
    "Acme Plastics PLC": "acme"
  },
  "triplevox_enable_tita_workspaces": 0,
  "triplevox_seed_demo_branding": 0
}
```

- `triplevox_enable_tita_workspaces` — force TITA migrate chrome even without `titacustom` (rare).
- `triplevox_seed_demo_branding` — create a single neutral Demo Client Branding row on migrate.

## Install from GitHub

Repo: `https://github.com/gmt-erpsol/Triplevoxui`

```bash
cd ~/frappe-bench

bench get-app https://github.com/gmt-erpsol/Triplevoxui.git --branch main
mv apps/Triplevoxui apps/triplevox_platform

bench --site YOUR_SITE install-app triplevox_platform
bench --site YOUR_SITE migrate
bench --site YOUR_SITE clear-cache
```

Then in Desk: **Setup → Client Branding** → New → set key, name, company, logos, accents → Save. Hard-refresh (`Ctrl+Shift+R`).

## Theme a client site (DB only)

1. Create/edit **Client Branding** (no code edits).
2. Link the ERPNext **Company**.
3. Optional: `bench --site YOUR_SITE set-config triplevox_client your_key`
4. `bench --site YOUR_SITE execute triplevox_platform.setup.apply_branding_settings`
5. Clear cache and hard-refresh.

Print logos use **Company logo → client logo → monogram** (never TripleVox product mark on PDFs).

## One site, multiple companies

Desk chrome follows the logged-in user’s company:

1. `Employee.company` if linked  
2. else User default **Company**  
3. else Global Defaults company  

Map is automatic from Client Branding.`company`, or override in `site_config.json` via `triplevox_company_profiles`.

Ops helper (optional, not required for parent-app reuse): `triplevox_platform.setup_brg` — sister-company bootstrap scripts.

## Success checklist (parent app)

- Fresh site + platform only → no TITA/BRG rows seeded; no TITA Manufacturing icon unless `titacustom` installed  
- Admin creates one Client Branding → Desk / login / print pick up logos & colors with no code edit  
- Second Company + branding row → switcher / login cards work via DB map  
- Grep runtime for client legal names → should not hit `client_theme.py` catalogs (removed)

## License

MIT — TripleVox Engineering PLC
