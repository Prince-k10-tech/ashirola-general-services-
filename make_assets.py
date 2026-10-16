"""Generate favicon set and social-sharing image for Ashiri-Ola General Services Ltd.

Run:  python3 build/make_assets.py
Needs: Pillow. Output goes to the project root.
The brand mark is a simplified "A" monogram (the live site shows an "A" mark beside the wordmark).
If the company supplies an official logo file, replace the mark geometry below or the generated files.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAVY = (11, 42, 74, 255)
GOLD = (200, 150, 62, 255)
CREAM = (245, 242, 234, 255)

# Mark geometry on a 64x64 grid (shared with favicon.svg)
OUTER = [(32, 12), (51, 52), (43, 52), (39.2, 43.5), (24.8, 43.5), (21, 52), (13, 52)]
INNER = [(32, 27), (27.6, 37), (36.4, 37)]


def mark(size, bleed=False, scale=1.0):
    """Return an RGBA image of the mark at `size` px. bleed=True fills the whole square (for iOS)."""
    ss = 8
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bleed:
        d.rectangle([0, 0, s, s], fill=NAVY)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 14 / 64), fill=NAVY)
    k = s / 64.0

    def tf(pts):
        return [(((x - 32) * scale + 32) * k, ((y - 32) * scale + 32) * k) for x, y in pts]

    d.polygon(tf(OUTER), fill=GOLD)
    d.polygon(tf(INNER), fill=NAVY)
    return img.resize((size, size), Image.LANCZOS)


def favicons():
    mark(16).save(ROOT / "favicon-16x16.png")
    mark(32).save(ROOT / "favicon-32x32.png")
    mark(180, bleed=True, scale=0.9).save(ROOT / "apple-touch-icon.png")
    mark(192).save(ROOT / "android-chrome-192x192.png")
    mark(512).save(ROOT / "android-chrome-512x512.png")
    mark(256).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def og_image():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY[:3])
    photo = ROOT / "assets" / "hero-port.jpg"
    has_photo = photo.exists()
    if has_photo:
        ph = Image.open(photo).convert("RGB")
        scale = max(W / ph.width, H / ph.height)
        ph = ph.resize((round(ph.width * scale), round(ph.height * scale)), Image.LANCZOS)
        left, top = (ph.width - W) // 2, (ph.height - H) // 2
        img = ph.crop((left, top, left + W, top + H))
        shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade)
        for x in range(W):
            a = int(235 * max(0.0, 1 - x / 860))
            sd.line([(x, 0), (x, H)], fill=(6, 16, 29, a))
        img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(img)
    # simple geometric container stack on the right (only when no photo has been supplied)
    colors = [(200, 150, 62), (245, 242, 234), (31, 92, 143), (200, 150, 62), (31, 92, 143), (245, 242, 234)]
    x0, y0 = 700, 330
    for row in range(0 if has_photo else 3):
        for col in range(4):
            c = colors[(row * 4 + col) % len(colors)]
            x = x0 + col * 110 + (row % 2) * 20
            y = y0 - row * 62
            d.rectangle([x, y, x + 100, y + 54], fill=c)
            d.line([x + 25, y, x + 25, y + 54], fill=NAVY[:3], width=3)
            d.line([x + 50, y, x + 50, y + 54], fill=NAVY[:3], width=3)
            d.line([x + 75, y, x + 75, y + 54], fill=NAVY[:3], width=3)
    if not has_photo:
        d.rectangle([660, 396, 1200, 400], fill=(200, 150, 62))
    d.rectangle([0, 0, 14, H], fill=GOLD[:3])
    img.paste(mark(120), (70, 70), mark(120))
    serif = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    sans_b = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    d.text((70, 225), "Ashiri-Ola", font=font(serif, 76), fill=CREAM[:3])
    d.text((70, 315), "General Services Ltd", font=font(serif, 44), fill=GOLD[:3])
    d.text((70, 410), "Import & Export", font=font(sans_b, 32), fill=CREAM[:3])
    d.text((70, 455), "Including clearing & forwarding", font=font(sans, 26), fill=(190, 203, 218))
    d.text((70, 495), "Real Estate Development  |  General Services", font=font(sans, 26), fill=(190, 203, 218))
    d.text((70, 560), "Ikeja, Lagos State, Nigeria", font=font(sans, 26), fill=(190, 203, 218))
    img.save(ROOT / "og-image.png", optimize=True)


if __name__ == "__main__":
    favicons()
    og_image()
    print("favicons and og-image.png written to", ROOT)
