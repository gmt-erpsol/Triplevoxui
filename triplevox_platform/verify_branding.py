"""Verify company branding payloads (bench execute)."""
from triplevox_platform.client_theme import get_boot_payload, get_site_default_boot_payload


def run():
	out = []
	for company in ("TITA PP Plastic PLC", "BRG Trading PLC"):
		p = get_boot_payload(company=company)
		out.append(
			{
				"company": company,
				"client_key": p.get("client_key"),
				"client_full_name": p.get("client_full_name"),
				"apps_title": p.get("apps_title"),
				"accent": (p.get("theme") or {}).get("green"),
			}
		)
	out.append({"site_default": get_site_default_boot_payload().get("client_full_name")})
	return out
