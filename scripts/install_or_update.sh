#!/usr/bin/env bash
# Install or update triplevox_platform on the current Frappe bench.
# Usage:
#   cd /path/to/frappe-bench
#   bash apps/triplevox_platform/scripts/install_or_update.sh SITE_NAME
set -euo pipefail

SITE="${1:-}"
if [[ -z "$SITE" ]]; then
	echo "Usage: $0 SITE_NAME"
	echo "Example: $0 tita.local"
	exit 1
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
# When script lives in apps/triplevox_platform/scripts → bench root is ../../..
if [[ ! -f "$ROOT/sites/apps.txt" && -f "$(pwd)/sites/apps.txt" ]]; then
	ROOT="$(pwd)"
fi
cd "$ROOT"

if [[ ! -f "sites/apps.txt" ]]; then
	echo "ERROR: Run this from a Frappe bench (sites/apps.txt missing). Current: $ROOT"
	exit 1
fi

if [[ ! -d "apps/triplevox_platform" ]]; then
	echo "ERROR: apps/triplevox_platform not found under $ROOT"
	echo "Copy or: bench get-app /path/to/triplevox_platform"
	exit 1
fi

# shellcheck disable=SC1091
source env/bin/activate

if ! grep -qx "triplevox_platform" sites/apps.txt 2>/dev/null; then
	echo "Installing app on $SITE ..."
	bench --site "$SITE" install-app triplevox_platform
else
	echo "App already on site — migrating ..."
fi

bench --site "$SITE" migrate
bench --site "$SITE" execute triplevox_platform.workspace_viewer.run || true
bench --site "$SITE" execute triplevox_platform.print_branding.run || true
bench --site "$SITE" clear-cache
bench --site "$SITE" clear-website-cache || true

echo ""
echo "OK — triplevox_platform updated on $SITE"
echo "Hard-refresh browser (Ctrl+Shift+R)."
echo "Set client: bench --site $SITE set-config triplevox_client tita"
echo "See apps/triplevox_platform/DEPLOY.md"
