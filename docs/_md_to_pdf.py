import os, re, subprocess, sys

SRC_HTML = r"/mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/docs/TripleVox_UI_App_Complete_Guide.html"
SRC_MD = r"/mnt/c/Users/Dell/Documents/TITA-ERP-BRD/apps/triplevox_platform/docs/USER_GUIDE.md"
OUT_PDF = r"/mnt/c/Users/Dell/Downloads/TripleVox_UI_App_Complete_Guide.pdf"
# Windows paths for local fallback
WIN_HTML = r"C:\Users\Dell\Documents\TITA-ERP-BRD\apps\triplevox_platform\docs\TripleVox_UI_App_Complete_Guide.html"
WIN_MD = r"C:\Users\Dell\Documents\TITA-ERP-BRD\apps\triplevox_platform\docs\USER_GUIDE.md"
WIN_PDF = r"C:\Users\Dell\Downloads\TripleVox_UI_App_Complete_Guide.pdf"

def has_mod(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def md_to_pdf_reportlab(src, out):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from xml.sax.saxutils import escape
    lines = open(src, encoding="utf-8").read().splitlines()
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1x", parent=styles["Heading1"], fontSize=16, spaceAfter=10, spaceBefore=14)
    h2 = ParagraphStyle("H2x", parent=styles["Heading2"], fontSize=13, spaceAfter=8, spaceBefore=12)
    h3 = ParagraphStyle("H3x", parent=styles["Heading3"], fontSize=11, spaceAfter=6, spaceBefore=10)
    body = ParagraphStyle("Bodyx", parent=styles["Normal"], fontSize=9, leading=12, spaceAfter=4)
    code = ParagraphStyle("Codex", parent=styles["Code"], fontSize=8, leading=10)
    story = []
    in_code = False
    code_buf = []
    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_buf)[:8000], code))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:].strip()), h1))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:].strip()), h2))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:].strip()), h3))
        elif line.strip() == "":
            story.append(Spacer(1, 4))
        else:
            t = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            t = re.sub(r"`([^`]+)`", r"\1", t)
            t = re.sub(r"^[-*]\s+", "- ", t)
            story.append(Paragraph(escape(t), body))
    doc.build(story)

def md_to_pdf_fpdf(src, out):
    from fpdf import FPDF
    lines = open(src, encoding="utf-8").read().splitlines()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in lines:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        if line.startswith("#"):
            pdf.set_font("Helvetica", "B", 12 if line.startswith("###") else 14)
            pdf.multi_cell(0, 7, safe.lstrip("# "))
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5, safe[:200])
    pdf.output(out)

def main():
    # Prefer running inside WSL paths if they exist
    html = SRC_HTML if os.path.exists(SRC_HTML) else WIN_HTML
    md = SRC_MD if os.path.exists(SRC_MD) else WIN_MD
    out = OUT_PDF if os.path.isdir(os.path.dirname(OUT_PDF)) or os.name != "nt" else WIN_PDF
    if os.name == "nt":
        html, md, out = WIN_HTML, WIN_MD, WIN_PDF

    method = None
    print("html exists", os.path.exists(html), html)
    print("md exists", os.path.exists(md), md)

    if has_mod("weasyprint"):
        from weasyprint import HTML
        HTML(filename=html).write_pdf(out)
        method = "weasyprint"
    elif has_mod("pdfkit"):
        import pdfkit
        pdfkit.from_file(html, out)
        method = "pdfkit"
    else:
        wk = subprocess.run(["which", "wkhtmltopdf"], capture_output=True, text=True)
        if wk.returncode == 0:
            subprocess.check_call(["wkhtmltopdf", html, out])
            method = "wkhtmltopdf"
        elif has_mod("reportlab"):
            md_to_pdf_reportlab(md, out)
            method = "reportlab-from-USER_GUIDE.md"
        elif has_mod("fpdf"):
            md_to_pdf_fpdf(md, out)
            method = "fpdf2-from-USER_GUIDE.md"
        else:
            print("ERROR: No PDF method available")
            sys.exit(1)

    size = os.path.getsize(out)
    print("PDF_METHOD=" + method)
    print("SIZE=" + str(size))
    print("OUT=" + out)
    open("/tmp/tvx_pdf_method.txt", "w").write(method) if os.path.isdir("/tmp") else None
    open(r"C:\Users\Dell\Documents\TITA-ERP-BRD\apps\triplevox_platform\docs\_pdf_method.txt", "w").write(method)

if __name__ == "__main__":
    main()
