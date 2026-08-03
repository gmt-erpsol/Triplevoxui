import frappe

print("exists", frappe.db.exists("DocType", "Client Branding"))
print(frappe.get_all("Client Branding", fields=["name", "client_full_name", "accent_color", "company", "is_site_default"]))
from triplevox_platform.client_theme import get_boot_payload, get_client_profile

for co in ("TITA PP Plastic PLC (TITA PLC)", "BRG Trading PLC", None):
	p = get_client_profile(company=co)
	print(co, "->", p.get("client_key"), (p.get("theme") or {}).get("green"))
print("boot", get_boot_payload().get("client_key"), get_boot_payload().get("needs_branding_onboarding"))
