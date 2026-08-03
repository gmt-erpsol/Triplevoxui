import frappe

# Ensure Module Def exists
if not frappe.db.exists("Module Def", "TVX"):
	doc = frappe.get_doc(
		{
			"doctype": "Module Def",
			"module_name": "TVX",
			"app_name": "triplevox_platform",
		}
	)
	doc.insert(ignore_permissions=True)
	print("created Module Def TVX")
else:
	print("Module Def TVX exists")

# Drop stale TripleVox Platform module if empty
if frappe.db.exists("Module Def", "TripleVox Platform"):
	try:
		frappe.delete_doc("Module Def", "TripleVox Platform", force=1, ignore_permissions=True)
		print("removed old Module Def")
	except Exception as e:
		print("skip remove old module", e)

frappe.reload_doc("tvx", "doctype", "client_branding", force=True)
frappe.db.commit()
print("reloaded", frappe.db.exists("DocType", "Client Branding"))

from triplevox_platform.branding_setup import run

run()
print(
	frappe.get_all(
		"Client Branding",
		fields=["name", "client_full_name", "accent_color", "company"],
		ignore_permissions=True,
	)
)
