#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd /home/gemtad/frappe-bench || exit 1
# activate env if present
if [ -f env/bin/activate ]; then
  # shellcheck disable=SC1091
  . env/bin/activate
fi
which bench
bench --site tita.local execute triplevox_platform.branding_setup.branding_configured
bench --site tita.local mariadb -e 'SELECT name, client_full_name, accent_color, company FROM `tabClient Branding`;'
bench --site tita.local clear-cache
echo DONE
