#!/bin/bash
APP=/home/gemtad/frappe-bench/apps/triplevox_platform
echo "=== hooks ==="
grep -n "tvx_saas_ui.js\|20260801g\|role_packs.run" "$APP/triplevox_platform/hooks.py"
echo "=== api.py ==="
grep -n "set_session_company\|onboard_sister_company" "$APP/triplevox_platform/api.py"
echo "=== files ==="
ls -la "$APP/triplevox_platform/role_packs.py" "$APP/triplevox_platform/print_pack.py"
echo "=== PDF ==="
ls -la /mnt/c/Users/Dell/Downloads/TripleVox_UI_App_Complete_Guide.pdf
stat -c "SIZE=%s" /mnt/c/Users/Dell/Downloads/TripleVox_UI_App_Complete_Guide.pdf
cat /mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/docs/_pdf_method.txt 2>/dev/null
echo
