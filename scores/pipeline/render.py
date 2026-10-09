"""Output rules O1-O5. See scores/RULES.md.

MusicXML clean-up (so the same input always gives the same bytes),
and PDF rendering with Verovio (default) or MuseScore, US Letter,
with a credits/rules footer and a DRAFT stamp.
"""
import io
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

LETTER = (612, 792)  # points, 8.5 x 11 in
SIZES = {"normal": {"zoom": 1.2, "mm": 8.5, "footer_pt": 8},    # staff about 8.5 mm tall
         "large": {"zoom": 1.7, "mm": 12.0, "footer_pt": 10}}  # staff about 12 mm tall


def tidy_musicxml(xml):
    """Make the MusicXML byte-for-byte repeatable (no date, fixed part ids)."""
    xml = re.sub(r"\s*<encoding-date>.*?</encoding-date>", "", xml)
    ids = []
    for pid in re.findall(r'<score-part id="([^"]+)"', xml):
        if pid not in ids:
            ids.append(pid)
    for i, pid in enumerate(ids, start=1):
        xml = xml.replace(f'"{pid}"', f'"P{i}"')
    return xml


def with_page_layout(xml, mm):
    """Add US Letter page size to the MusicXML (used by the MuseScore renderer)."""
    tenths_per_mm = 40 / mm
    h, w = 279.4 * tenths_per_mm, 215.9 * tenths_per_mm
    m = 12.7 * tenths_per_mm  # 0.5 in margins
    bottom = 30 * tenths_per_mm  # room for footer
    layout = (f"<defaults><scaling><millimeters>{mm}</millimeters><tenths>40</tenths></scaling>"
              f"<page-layout><page-height>{h:.0f}</page-height><page-width>{w:.0f}</page-width>"
              f'<page-margins type="both"><left-margin>{m:.0f}</left-margin><right-margin>{m:.0f}</right-margin>'
              f"<top-margin>{m:.0f}</top-margin><bottom-margin>{bottom:.0f}</bottom-margin></page-margins>"
              f"</page-layout></defaults>")
    xml = re.sub(r"<defaults>.*?</defaults>", "", xml, flags=re.S)
    return xml.replace("<part-list>", layout + "\n  <part-list>", 1)


def _verovio_pages(xml, size):
    import verovio
    tk = verovio.toolkit()
    z = SIZES[size]["zoom"]  # a smaller virtual page = bigger music once fitted to Letter
    tk.setOptions({
        "pageWidth": round(2159 / z), "pageHeight": round(2794 / z),  # US Letter in tenths of mm
        "pageMarginLeft": round(127 / z), "pageMarginRight": round(127 / z),
        "pageMarginTop": round(127 / z), "pageMarginBottom": round(330 / z),
        "scale": 100,
        "adjustPageHeight": False, "breaks": "auto",
        "header": "auto", "footer": "none",
        "svgViewBox": True, "xmlIdSeed": 1,
    })
    if not tk.loadData(xml):
        raise RuntimeError("Verovio could not read the MusicXML.")
    return [tk.renderToSVG(i) for i in range(1, tk.getPageCount() + 1)]


SMUFL_TEXT = {}
for _base in (0xE260, 0xED60):  # accidentals, chord-symbol accidentals: flat, natural, sharp, x, bb
    SMUFL_TEXT.update(zip(map(chr, range(_base, _base + 5)), ["b", "", "#", "x", "bb"]))
SMUFL_TEXT.update(zip(map(chr, range(0xEA63, 0xEA68)), ["bb", "b", "", "#", "x"]))  # figured-bass set


def _plain_accidentals(svg):
    """Verovio draws # and b inside chord symbols with a music font that PDF
    converters do not have. Swap them for plain '#' and 'b' text."""
    def swap(m):
        size = round(float(m.group(1)) * 0.5625)
        return f'<tspan font-size="{size}px">{SMUFL_TEXT.get(m.group(2), "")}</tspan>'
    return re.sub(r'<tspan font-family="Leipzig" font-size="([\d.]+)px">([\ue000-\uf8ff])</tspan>', swap, svg)


def _svg_to_pdf_page(svg):
    """SVG page -> PDF page with cairosvg (needs the Cairo library)."""
    svg = _plain_accidentals(svg)
    try:
        import cairosvg
    except (ImportError, OSError):
        raise SystemExit("Cairo is not installed, so Verovio pages cannot become a PDF.\n"
                         "  Mac: run  brew install cairo\n"
                         "  Windows: install MuseScore 4 and set  engine: musescore  in the recipe.")
    return cairosvg.svg2pdf(bytestring=svg.encode("utf-8"))


def _musescore_pdf(xml, mm, workdir):
    known = ["/Applications/MuseScore 4.app/Contents/MacOS/mscore",
             r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"]
    exe = next((shutil.which(x) for x in ("mscore4portable", "mscore4", "mscore", "musescore", "MuseScore4")
                if shutil.which(x)), None) or next((k for k in known if Path(k).exists()), None)
    if exe is None:
        raise RuntimeError("MuseScore not found. Install MuseScore 4, or set render.engine: verovio.")
    src = Path(workdir) / "in.musicxml"
    out = Path(workdir) / "out.pdf"
    src.write_text(with_page_layout(xml, mm), encoding="utf-8")
    subprocess.run([exe, "-o", str(out), str(src)], check=True, capture_output=True)
    return out.read_bytes()


def _footer_overlay(footer, status, page_no, page_count, size):
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER, invariant=1)
    c.setFillGray(0)
    size = SIZES[size]["footer_pt"]
    lines = simpleSplit(footer, "Helvetica", size, LETTER[0] - 72)
    y = 36 + (len(lines) - 1) * (size + 2)
    c.setFont("Helvetica", size)
    for line in lines:
        c.drawString(36, y, line)
        y -= size + 2
    c.drawRightString(LETTER[0] - 36, 22, f"Page {page_no} of {page_count}")
    if status != "approved":
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(LETTER[0] - 36, LETTER[1] - 24, "DRAFT - needs review")
    c.save()
    return buf.getvalue()


def render_pdf(xml, out_path, footer, status, size="normal", engine="verovio"):
    """O3/O4/O5: US Letter PDF, footer on every page, DRAFT stamp until approved."""
    from pypdf import PdfReader, PdfWriter, Transformation
    pages = []
    if engine == "musescore":
        with tempfile.TemporaryDirectory() as tmp:
            pdf = _musescore_pdf(xml, SIZES[size]["mm"], tmp)
        pages = list(PdfReader(io.BytesIO(pdf)).pages)
    else:
        for svg in _verovio_pages(xml, size):
            pages.append(PdfReader(io.BytesIO(_svg_to_pdf_page(svg))).pages[0])
    writer = PdfWriter()
    for i, page in enumerate(pages, start=1):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        s = min(LETTER[0] / w, LETTER[1] / h)
        page.add_transformation(Transformation().scale(s, s))
        page.mediabox.lower_left = (0, 0)
        page.mediabox.upper_right = LETTER
        page.merge_page(PdfReader(io.BytesIO(_footer_overlay(footer, status, i, len(pages), size))).pages[0])
        writer.add_page(page)
    writer.add_metadata({"/Title": Path(out_path).stem, "/Producer": "scores/pipeline (rules only)"})
    writer._ID = None
    with open(out_path, "wb") as f:
        writer.write(f)
