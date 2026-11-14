"""Build black vellum cards from prepared artwork and a JSON layout."""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

from fontTools.ttLib import TTFont as InspectFont
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


MIN_ARTWORK_PPI = 300


def register_font(family, supplied):
    if supplied is None and shutil.which("fc-match"):
        match = subprocess.run(
            ["fc-match", "-f", "%{file}", family], check=True, capture_output=True, text=True
        ).stdout
        supplied = Path(match) if match else None
    if supplied is None or not supplied.is_file():
        raise ValueError(f"Missing {family}. Supply the exact licensed font file.")
    with InspectFont(supplied, fontNumber=0) as font:
        names = {item.toUnicode().strip().casefold() for item in font["name"].names
                 if item.nameID in (1, 4, 16)}
        allowed = {family.casefold()}
        if family == "Lucida Handwriting":
            allowed.add("lucida handwriting italic")
        if not names.intersection(allowed):
            raise ValueError(f"{supplied.name} is not {family}. Supply the exact licensed font file.")
        flags = font["OS/2"].fsType if "OS/2" in font else 0
        if flags & (0x0002 | 0x0100 | 0x0200) or (flags & 0x0004 and not flags & 0x0008):
            raise ValueError(f"{family} does not allow editable PDF subsetting in this file.")
        glyphs = set(font.getBestCmap())
    pdfmetrics.registerFont(TTFont(family, str(supplied)))
    return glyphs


def box(values, width, height):
    x, y, w, h = (float(v)*mm for v in values)
    if not all(map(math.isfinite, (x, y, w, h))) or min(x, y) < 0 or min(w, h) <= 0:
        raise ValueError("Invalid image_box or text_box.")
    if x+w > width+1e-6 or y+h > height+1e-6:
        raise ValueError("A box extends past the trim.")
    return x, y, w, h


def wrap_words(value, font, size, width):
    lines = []
    current = ""
    for word in value.split(" "):
        candidate = f"{current} {word}" if current else word
        if pdfmetrics.stringWidth(candidate, font, size) > width:
            if not current or pdfmetrics.stringWidth(word, font, size) > width:
                raise ValueError(f"Word too wide for text_box: {word}")
            lines.append(current)
            current = word
        else:
            current = candidate
    return [*lines, current]


def prepare(item, base, width, height, glyphs, image_field="image"):
    ix, iy, iw, ih = box(item["image_box"], width, height)
    tx, ty, tw, th = box(item["text_box"], width, height)
    if max(ix, tx) < min(ix+iw, tx+tw)-1e-6 and max(iy, ty) < min(iy+ih, ty+th)-1e-6:
        raise ValueError("image_box overlaps text_box.")
    align = item.get("align", "left")
    if align not in ("left", "center"):
        raise ValueError("align must be left or center.")
    with Image.open(base/item[image_field]) as source:
        image = ImageOps.exif_transpose(source).convert("RGBA")
    ratio = min(iw/image.width, ih/image.height)
    w, h = image.width*ratio, image.height*ratio
    effective_ppi = 72 / ratio
    if effective_ppi < MIN_ARTWORK_PPI - 1e-9:
        raise ValueError(
            f"Artwork is {effective_ppi:.2f} ppi at the placed size "
            f"({w/mm:.2f} × {h/mm:.2f} mm). "
            f"Use an original with at least {MIN_ARTWORK_PPI} ppi at that size."
        )
    art = (ImageReader(image), ix+(iw-w)/2, iy+(ih-h)/2, w, h)

    blocks = []
    top = ty
    for key, family, size, ink in (
        ("title", "Times New Roman", float(item.get("title_pt", 10)), "#F1EBDE"),
        ("poem", "Lucida Handwriting", float(item.get("poem_pt", 7.25)), "#D2CBC0"),
    ):
        value = item[key]
        if not isinstance(value, str) or not value or value != " ".join(value.split()):
            raise ValueError(f"{key} must be nonempty text with single spaces.")
        if not math.isfinite(size) or size <= 0:
            raise ValueError(f"{key} font size must be positive.")
        missing = sorted({char for char in value if ord(char) not in glyphs[family]})
        if missing:
            raise ValueError(f"{family} lacks glyphs: {''.join(missing)}")
        lines = wrap_words(value, family, size, tw)
        ascent, descent = pdfmetrics.getAscentDescent(family, size)
        leading = max(size*1.33, ascent-descent)
        for index, line in enumerate(lines):
            offset = (tw-pdfmetrics.stringWidth(line, family, size))/2 if align == "center" else 0
            blocks.append((line, tx+offset, top+ascent+index*leading, family, size, ink))
        top += ascent-descent + (len(lines)-1)*leading
        if top > ty+th+1e-6:
            raise ValueError(f"Text exceeds text_box: {item['title']}")
        top += 1.6*mm
    return art, blocks


def crop_marks(pdf, x, y, w, h):
    pdf.setStrokeGray(.25)
    pdf.setLineWidth(.35)
    for cx, cy, dx, dy in ((x,y,-1,-1),(x+w,y,1,-1),(x,y+h,-1,1),(x+w,y+h,1,1)):
        pdf.line(cx+dx*3.4*mm, cy, cx+dx*6*mm, cy)
        pdf.line(cx, cy+dy*3.4*mm, cx, cy+dy*6*mm)


def export(output, items, width, height, a4):
    pw, ph = A4 if a4 else (width, height)
    margin, gap, bleed = (15*mm, 15*mm, 3*mm) if a4 else (0, 0, 0)
    columns = int((pw-2*margin+gap+1e-6)//(width+gap))
    rows = int((ph-2*margin+gap+1e-6)//(height+gap))
    if not columns or not rows:
        raise ValueError("Card size does not fit this page.")
    per_page = columns*rows
    pdf = canvas.Canvas(str(output), pagesize=(pw,ph), pdfVersion=(1,4), pageCompression=1)
    pdf.setTitle("Black Vellum Cards")
    for index, (art, blocks) in enumerate(items):
        row, col = divmod(index % per_page, columns)
        x = (pw-columns*width-(columns-1)*gap)/2 + col*(width+gap)
        y = ph-margin-height-row*(height+gap)
        pdf.setFillGray(0)
        pdf.rect(x-bleed,y-bleed,width+2*bleed,height+2*bleed,stroke=0,fill=1)
        image, ax, ay, aw, ah = art
        pdf.drawImage(image,x+ax,y+height-ay-ah,aw,ah,mask="auto")
        for line, tx, ty, family, size, ink in blocks:
            pdf.setFont(family,size)
            pdf.setFillColor(ink)
            pdf.drawString(x+tx,y+height-ty,line)
        if a4:
            crop_marks(pdf,x,y,width,height)
        if index % per_page == per_page-1 or index == len(items)-1:
            pdf.showPage()
    pdf.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title-font", type=Path)
    parser.add_argument("--poem-font", type=Path)
    parser.add_argument("--size-mm", nargs=2, type=float, default=(50,100))
    parser.add_argument("--a4", action="store_true")
    parser.add_argument(
        "--palette", choices=("low-saturation", "original-color", "both"),
        default="low-saturation",
        help="Select the artwork palette. Both writes two PDFs with palette suffixes.",
    )
    args = parser.parse_args()
    try:
        width, height = (value*mm for value in args.size_mm)
        if not all(math.isfinite(v) and v>0 for v in (width,height)):
            raise ValueError("Card dimensions must be positive.")
        glyphs = {
            "Times New Roman": register_font("Times New Roman",args.title_font),
            "Lucida Handwriting": register_font("Lucida Handwriting",args.poem_font),
        }
        cards = json.loads(args.manifest.read_text(encoding="utf-8"))["cards"]
        if not cards or not isinstance(cards,list):
            raise ValueError("cards must be a nonempty list.")
        variants = {
            "low-saturation": "image",
            "original-color": "image_color",
        }
        if args.palette != "both":
            variants = {args.palette: variants[args.palette]}
        exports = []
        for palette, image_field in variants.items():
            items = []
            for index, card in enumerate(cards, 1):
                try:
                    if image_field == "image_color":
                        with Image.open(args.manifest.parent / card["image"]) as low:
                            with Image.open(args.manifest.parent / card[image_field]) as color:
                                if ImageOps.exif_transpose(low).size != ImageOps.exif_transpose(color).size:
                                    raise ValueError("Both artwork palettes must share the same canvas size.")
                    items.append(prepare(card, args.manifest.parent, width, height, glyphs, image_field))
                except (ValueError, TypeError, KeyError, OSError) as exc:
                    raise ValueError(f"{palette}, card {index}: {exc}") from exc
            destination = args.output
            if args.palette == "both":
                destination = args.output.with_name(f"{args.output.stem}-{palette}{args.output.suffix}")
            exports.append((destination, items))
        for destination, items in exports:
            export(destination, items, width, height, args.a4)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(1,f"{exc}\n")


if __name__ == "__main__":
    main()
