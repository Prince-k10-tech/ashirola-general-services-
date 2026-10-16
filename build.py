"""Static site generator for Ashiri-Ola General Services Ltd.

Produces flat, multi-page HTML (CSS and JS embedded inline in every page), plus
sitemap.xml, robots.txt, site.webmanifest and _headers. Edit content here, then rebuild:

    SITE_URL=https://www.your-real-domain.com FORM_ENDPOINT=https://... python3 build/build.py

SITE_URL      Production origin, no trailing slash (canonical, Open Graph, JSON-LD, sitemap, robots).
              Defaults to https://ashiriolageneralservices.com.ng (the owner's domain, no www).
FORM_ENDPOINT Optional HTTPS endpoint that accepts a JSON POST (see README). If unset, the enquiry form
              falls back to opening the visitor's email app and says so honestly.
PREVIEW=1     Preview build: no CSP tag, Google Fonts link instead of self-hosted fonts (for hosts that
              block local font files). OUT=<dir> chooses the output folder. Not for production.
No secrets belong in any of these values.
"""
import base64
import datetime
import hashlib
import html
import json
import os
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(os.environ.get("OUT", str(ROOT)))
PREVIEW = os.environ.get("PREVIEW") == "1"
SITE_URL = os.environ.get("SITE_URL", "https://ashiriolageneralservices.com.ng").rstrip("/")
FORM_ENDPOINT = os.environ.get("FORM_ENDPOINT", "").strip()

NAME = "Ashiri-Ola General Services Ltd"
PHONE_DISPLAY = "+234 808 381 3441"
PHONE_TEL = "+2348083813441"
EMAIL = "ashiriolageneralservices@gmail.com"
ADDRESS_LINE = "Ikeja, Lagos State, Nigeria"
YEAR = datetime.date.today().year

NAV = [
    ("home", "index.html", "Home", "Welcome"),
    ("about", "about.html", "About", "Who we are"),
    ("services", "services.html", "Services", "What we do"),
    ("contact", "contact.html", "Contact", "Request a quote"),
]


def esc(s):
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- optional photos
def photo(name, alt, cls="", eager=False):
    """Use a real photo from assets/ if supplied; otherwise return an empty string."""
    p = ROOT / "assets" / name
    if not p.exists():
        return ""
    try:
        from PIL import Image
        with Image.open(p) as im:
            w, h = im.size
    except Exception:
        return ""
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img class="{cls}" src="assets/{name}" width="{w}" height="{h}" alt="{esc(alt)}" {load}>'


# --------------------------------------------------------------------------- inline svg
MARK_SVG = (
    '<svg class="mark" viewBox="0 0 64 64" width="44" height="44" aria-hidden="true" focusable="false">'
    '<rect x=".75" y=".75" width="62.5" height="62.5" rx="14" fill="#0B2A4A" stroke="#C8963E" stroke-opacity=".7" stroke-width="1.5"/>'
    '<path fill="#C8963E" fill-rule="evenodd" d="M32 12 51 52H43L39.2 43.5H24.8L21 52H13ZM32 27 27.6 37H36.4Z"/></svg>'
)


def hero_art():
    """Animated dusk-at-the-port scene used when no photograph has been supplied."""
    stars = [(60, 40), (140, 95), (230, 30), (330, 70), (420, 25), (520, 60), (610, 35), (700, 85),
             (90, 150), (290, 135), (660, 150), (750, 40), (40, 100), (470, 110)]
    star_svg = "".join(
        f'<circle class="star s{i % 3}" cx="{x}" cy="{y}" r="{1.2 + (i % 2) * 0.7}" fill="#F3E7CC"/>'
        for i, (x, y) in enumerate(stars))
    cols = ["#C8963E", "#F3E7CC", "#2C6AA0", "#C8963E", "#1F7A7A", "#F3E7CC", "#2C6AA0"]
    boxes = []
    for ri, (y, n, x0) in enumerate([(332, 9, 104), (311, 8, 124), (290, 6, 164)]):
        for i in range(n):
            boxes.append(f'<rect x="{x0 + i * 40}" y="{y}" width="37" height="20" fill="{cols[(i * 3 + ri * 2) % 7]}"/>')
    skyline = "".join(
        f'<rect x="{x}" y="{372 - h}" width="{w}" height="{h}" fill="#0C2038"/>'
        for x, w, h in [(600, 30, 46), (634, 22, 70), (660, 34, 52), (698, 20, 88), (722, 38, 60), (764, 36, 40)])
    wave = "M-60 394" + " q22 -7 44 0 t44 0" * 22
    wave2 = "M-60 412" + " q30 -8 60 0 t60 0" * 16
    wave3 = "M-60 436" + " q40 -9 80 0 t80 0" * 12
    reflect = "".join(
        f'<rect class="refl r{i % 3}" x="{200 - w // 2}" y="{404 + i * 15}" width="{w}" height="4" fill="#C8963E"/>'
        for i, w in enumerate([120, 90, 70, 100, 50, 76, 36, 56]))
    return (
        '<svg class="hero-art" viewBox="0 0 800 560" role="img" '
        'aria-label="Illustration of a container ship at dusk beside a quayside crane">'
        '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#050E1A"/><stop offset=".62" stop-color="#123A63"/><stop offset="1" stop-color="#3B5F86"/></linearGradient>'
        '<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E2A47"/><stop offset="1" stop-color="#06101D"/></linearGradient></defs>'
        '<rect width="800" height="560" fill="url(#sky)"/>'
        + star_svg +
        '<circle class="glow" cx="200" cy="215" r="130" fill="#C8963E"/>'
        '<circle cx="200" cy="215" r="64" fill="#E3BE76"/>'
        + skyline +
        '<rect y="372" width="800" height="188" fill="url(#sea)"/>'
        + reflect +
        '<g class="ship">' + "".join(boxes) +
        '<path d="M70 352H545L508 398H106Z" fill="#F3E7CC"/>'
        '<path d="M70 352H545L538 363H77Z" fill="#C8963E"/>'
        '<rect x="478" y="298" width="48" height="54" fill="#F3E7CC"/>'
        '<rect x="486" y="308" width="32" height="8" fill="#123A63"/>'
        '<rect x="496" y="284" width="10" height="16" fill="#C8963E"/></g>'
        f'<path class="wave" d="{wave}" fill="none" stroke="#2C6AA0" stroke-width="2" stroke-opacity=".7"/>'
        f'<path class="wave w2" d="{wave2}" fill="none" stroke="#1F5C8F" stroke-width="2" stroke-opacity=".6"/>'
        f'<path class="wave w3" d="{wave3}" fill="none" stroke="#17476F" stroke-width="2" stroke-opacity=".6"/>'
        '<rect x="586" y="372" width="214" height="20" fill="#0A1B30"/>'
        '<path d="M630 372V170M742 372V170M630 170H742M630 232H742M630 300H742" stroke="#C8963E" stroke-width="7" fill="none"/>'
        '<path d="M742 170 380 150M742 170 742 120M690 170 380 150" stroke="#F3E7CC" stroke-width="3" fill="none"/>'
        '<rect x="372" y="146" width="22" height="9" fill="#C8963E"/>'
        '<g class="hook"><path d="M436 154V248" stroke="#F3E7CC" stroke-width="2"/>'
        '<rect x="416" y="248" width="40" height="22" fill="#2C6AA0"/><rect x="416" y="248" width="40" height="5" fill="#E3BE76"/></g>'
        '</svg>'
    )


def _icon(path, size=30):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{path}</svg>')


ICONS = {
    "trade": _icon('<path d="M3 17h18l-2.2 3H5.2zM6 17v-4h12v4M8 13V9h8v4M12 9V5"/><path d="M2 21c1.5 1 3 1 4.5 0s3-1 4.5 0 3 1 4.5 0 3-1 4.5 0" opacity=".6"/>'),
    "property": _icon('<path d="M4 21V9l8-6 8 6v12M9 21v-6h6v6M3 21h18"/>'),
    "general": _icon('<rect x="3" y="7" width="18" height="13" rx="1.5"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18M11 13v2h2v-2"/>'),
    "check": _icon('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 20),
}

# --------------------------------------------------------------------------- styles
FONT_FACES = (
    '@font-face{font-family:"Cormorant Garamond";font-style:normal;font-weight:500;font-display:swap;src:url(fonts/cormorant-garamond-latin-500-normal.woff2) format("woff2")}'
    '@font-face{font-family:"Cormorant Garamond";font-style:normal;font-weight:600;font-display:swap;src:url(fonts/cormorant-garamond-latin-600-normal.woff2) format("woff2")}'
    '@font-face{font-family:"Cormorant Garamond";font-style:italic;font-weight:500;font-display:swap;src:url(fonts/cormorant-garamond-latin-500-italic.woff2) format("woff2")}'
    '@font-face{font-family:Jost;font-style:normal;font-weight:400;font-display:swap;src:url(fonts/jost-latin-400-normal.woff2) format("woff2")}'
    '@font-face{font-family:Jost;font-style:normal;font-weight:500;font-display:swap;src:url(fonts/jost-latin-500-normal.woff2) format("woff2")}'
    '@font-face{font-family:Jost;font-style:normal;font-weight:600;font-display:swap;src:url(fonts/jost-latin-600-normal.woff2) format("woff2")}'
)
GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500"
                "&family=Jost:wght@400;500;600&display=swap")

CSS = r"""
:root{--ink:#06101D;--ink2:#0A1B30;--navy:#0B2A4A;--navy2:#123A63;--gold:#C8963E;--gold2:#E3BE76;--golddk:#8A6119;--ivory:#FAF7F0;--sand:#F1EBDD;--line:#E2D9C4;--text:#17212E;--muted:#556272;--ond:#D5DEE9;--mutd:#9FB0C3;--serif:"Cormorant Garamond",Georgia,"Times New Roman",serif;--sans:Jost,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;--ease:cubic-bezier(.2,.7,.2,1)}
*,*::before,*::after{box-sizing:border-box}
@view-transition{navigation:auto}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
html.lock{overflow:hidden}
body{margin:0;font:400 1.0625rem/1.7 var(--sans);color:var(--text);background:var(--ivory);-webkit-font-smoothing:antialiased}
::selection{background:var(--gold);color:var(--ink)}
img,svg{max-width:100%;height:auto}
[hidden]{display:none!important}
h1,h2,h3{font-family:var(--serif);font-weight:500;line-height:1.06;margin:0 0 .5em;letter-spacing:-.01em;color:var(--ink);text-wrap:balance}
h1{font-size:clamp(2.8rem,7.6vw,5.7rem)}
h2{font-size:clamp(2.2rem,4.8vw,3.5rem)}
h3{font-size:1.6rem;line-height:1.15}
em{font-style:italic}
p{margin:0 0 1.1em}
a{color:var(--navy2);text-underline-offset:3px}
a:hover{color:var(--golddk)}
:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.skip{position:absolute;left:-999px;top:8px;background:var(--gold);color:var(--ink);padding:.7rem 1.1rem;z-index:200;font-weight:600}
.skip:focus{left:8px}
.wrap{width:100%;max-width:1200px;margin:0 auto;padding:0 24px}
.eyebrow{display:flex;align-items:center;gap:.9rem;font:600 .78rem/1.2 var(--sans);letter-spacing:.24em;text-transform:uppercase;color:var(--golddk);margin:0 0 1.3rem}
.eyebrow::before{content:"";flex:none;width:42px;height:1px;background:currentColor}
.hero .eyebrow,.page-hero .eyebrow,.dark .eyebrow{color:var(--gold)}
.lead{font-size:1.2rem;color:var(--muted);max-width:56ch}
.hero .lead,.page-hero .lead,.dark .lead{color:var(--ond)}
/* header */
.site-header{position:sticky;top:0;z-index:60;background:rgba(6,16,29,.94);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-bottom:1px solid rgba(200,150,62,.28);transition:background-color .3s}
.site-header.scrolled{background:rgba(6,16,29,.98)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:80px}
.brand{display:flex;align-items:center;gap:.85rem;text-decoration:none;color:#fff}
.brand:hover{color:#fff}
.brand-text{display:flex;flex-direction:column;line-height:1.1}
.brand-text strong{font:600 1.6rem/1 var(--serif);letter-spacing:.01em;color:#fff}
.brand-text span{font:500 .64rem/1.2 var(--sans);letter-spacing:.28em;text-transform:uppercase;color:var(--gold);margin-top:.35rem}
.bar-actions{display:flex;align-items:center;gap:.8rem}
.bar-cta{display:none}
.menu-btn{display:inline-flex;align-items:center;gap:.8rem;min-height:46px;padding:0 1.15rem;background:transparent;border:1px solid rgba(200,150,62,.65);color:#fff;font:600 .78rem/1 var(--sans);letter-spacing:.22em;text-transform:uppercase;cursor:pointer;transition:background-color .25s,border-color .25s}
.menu-btn:hover{background:rgba(200,150,62,.14);border-color:var(--gold)}
.burger{display:grid;gap:5px;width:22px}
.burger i{display:block;height:1.5px;background:var(--gold);transition:width .3s var(--ease)}
.burger i:nth-child(2){width:68%;margin-left:auto}
.menu-btn:hover .burger i:nth-child(2){width:100%}
/* full-screen menu (all devices) */
.menu{position:fixed;inset:0;z-index:100;display:flex;flex-direction:column;background:radial-gradient(900px 520px at 88% 8%,rgba(200,150,62,.18),transparent 62%),radial-gradient(700px 500px at 0% 100%,rgba(18,58,99,.55),transparent 60%),var(--ink);color:#fff;opacity:0;visibility:hidden;transform:translateY(-14px);transition:opacity .4s var(--ease),transform .55s var(--ease),visibility 0s .55s;overflow-y:auto}
.menu.open{opacity:1;visibility:visible;transform:none;transition-delay:0s}
.menu-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:80px;width:100%;max-width:1200px;margin:0 auto;padding:0 24px}
.menu-body{flex:1;display:grid;gap:3rem;align-content:center;width:100%;max-width:1200px;margin:0 auto;padding:1.5rem 24px 3.5rem}
.menu-links{list-style:none;margin:0;padding:0}
.menu-links li{opacity:0;transform:translateY(22px)}
.menu.open .menu-links li{opacity:1;transform:none;transition:opacity .7s var(--ease),transform .8s var(--ease)}
.menu.open .menu-links li:nth-child(1){transition-delay:.12s}
.menu.open .menu-links li:nth-child(2){transition-delay:.2s}
.menu.open .menu-links li:nth-child(3){transition-delay:.28s}
.menu.open .menu-links li:nth-child(4){transition-delay:.36s}
.menu-links a{display:flex;align-items:baseline;flex-wrap:wrap;gap:.2rem 1.4rem;padding:.12em 0;font:500 clamp(3rem,9vw,5.6rem)/1.05 var(--serif);color:#fff;text-decoration:none;transition:color .3s,transform .5s var(--ease)}
.menu-links a small{font:500 .74rem/1 var(--sans);letter-spacing:.24em;text-transform:uppercase;color:var(--mutd)}
.menu-links a:hover{color:var(--gold2);transform:translateX(12px)}
.menu-links a[aria-current="page"]{color:var(--gold)}
.menu-side{color:var(--ond);border-top:1px solid rgba(200,150,62,.3);padding-top:2rem}
.menu-side h2{font:600 .74rem/1 var(--sans);letter-spacing:.24em;text-transform:uppercase;color:var(--gold);margin:0 0 .8rem}
.menu-side p{margin:0 0 1.4rem}
.menu-side a{color:#fff}
@media (min-width:900px){.menu-body{grid-template-columns:1.35fr .65fr;align-items:center;gap:5rem}.menu-side{border-top:0;border-left:1px solid rgba(200,150,62,.3);padding:0 0 0 3rem}}
/* buttons */
.btn{position:relative;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;gap:.6rem;min-height:54px;padding:.85rem 2rem;font:600 .8rem/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;text-decoration:none;border:1px solid transparent;cursor:pointer;transition:background-color .3s,color .3s,border-color .3s}
.btn-sm{min-height:46px;padding:.7rem 1.3rem}
.btn-gold{background:var(--gold);color:var(--ink)}
.btn-gold::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 30%,rgba(255,255,255,.5) 50%,transparent 70%);transform:translateX(-130%);pointer-events:none}
.btn-gold:hover{background:var(--gold2);color:var(--ink)}
.btn-gold:hover::after{transform:translateX(130%);transition:transform .9s var(--ease)}
.btn-line{border-color:rgba(255,255,255,.42);color:#fff}
.btn-line:hover{border-color:var(--gold);color:var(--gold2)}
.btn-dark{background:var(--ink);color:#fff}
.btn-dark:hover{background:var(--navy2);color:#fff}
.btn-outline{border-color:var(--ink);color:var(--ink)}
.btn-outline:hover{background:var(--ink);color:#fff}
.actions{display:flex;flex-wrap:wrap;gap:1rem;margin-top:2.2rem}
@media (min-width:780px){.bar-cta{display:inline-flex}}
/* hero */
.hero{position:relative;overflow:hidden;background:var(--ink);color:var(--ond);padding:clamp(3.5rem,8vw,6.5rem) 0 clamp(4rem,9vw,7rem)}
.hero::before{content:"";position:absolute;inset:0;background:radial-gradient(800px 520px at 82% 18%,rgba(200,150,62,.18),transparent 62%),radial-gradient(720px 520px at 0% 100%,rgba(18,58,99,.7),transparent 62%)}
.hero::after{content:"";position:absolute;inset:0;opacity:.07;pointer-events:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
.hero-grid{position:relative;z-index:1;display:grid;gap:3.5rem;align-items:center}
.hero h1{color:#fff;margin-bottom:.45em}
.hero h1 em,.page-hero h1 em,.dark h2 em{color:var(--gold2)}
.frame{position:relative}
.frame::before{content:"";position:absolute;inset:20px -20px -20px 20px;border:1px solid rgba(200,150,62,.6)}
.frame-inner{position:relative;overflow:hidden;background:var(--navy);box-shadow:0 34px 90px rgba(0,0,0,.55)}
.frame-inner img,.frame-inner svg{display:block;width:100%;height:auto}
.kb{animation:kb 26s ease-in-out infinite alternate}
.hero-photo{display:flex;align-items:center;min-height:clamp(560px,86vh,800px)}
.hero-photo .hero-grid{grid-template-columns:1fr;width:100%}
.hero-photo .hero-grid>div{max-width:40rem}
.hero-bg{position:absolute;inset:0;z-index:0;overflow:hidden;background:var(--navy)}
.hero-bg img{display:block;width:100%;height:100%;object-fit:cover;object-position:72% 60%}
.hero-photo::before{z-index:1;background:linear-gradient(180deg,rgba(6,16,29,.9) 0%,rgba(6,16,29,.72) 55%,rgba(6,16,29,.9) 100%)}
.hero-photo::after{z-index:1}
.hero-photo .hero-grid{z-index:2}
@media (min-width:960px){.hero-photo::before{background:linear-gradient(90deg,rgba(6,16,29,.94) 0%,rgba(6,16,29,.82) 34%,rgba(6,16,29,.3) 68%,rgba(6,16,29,.08) 100%),linear-gradient(0deg,rgba(6,16,29,.7) 0%,transparent 28%)}.hero-bg img{object-position:62% 58%}}
.strip{background:var(--ink2);border-block:1px solid rgba(200,150,62,.28)}
.strip ul{list-style:none;margin:0 auto;padding:1.15rem 24px;display:flex;flex-wrap:wrap;justify-content:center;gap:.7rem 0;max-width:1200px}
.strip li{position:relative;font:600 .76rem/1 var(--sans);letter-spacing:.26em;text-transform:uppercase;color:var(--gold2);padding:0 1.7rem}
.strip li+li::before{content:"";position:absolute;left:-3px;top:50%;width:6px;height:6px;background:var(--gold);transform:translateY(-50%) rotate(45deg)}
/* inner page hero */
.page-hero{position:relative;overflow:hidden;background:var(--ink);padding:clamp(3rem,8vw,5.5rem) 0 clamp(3rem,7vw,4.8rem);color:var(--ond)}
.page-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(700px 420px at 90% 0%,rgba(200,150,62,.2),transparent 62%)}
.page-hero .wrap{position:relative}
.page-hero h1{color:#fff;font-size:clamp(2.6rem,6.6vw,4.8rem);margin-bottom:.35em}
.crumbs{font:500 .78rem/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;margin:0 0 1.6rem;color:var(--mutd)}
.crumbs a{color:var(--gold2);text-decoration:none}
.rule{display:block;height:1px;width:0;background:var(--gold);margin-top:2rem;animation:grow 1.6s var(--ease) .3s forwards}
/* sections */
section{padding:clamp(4rem,9vw,7.5rem) 0}
.alt{background:var(--sand)}
.dark{background:var(--ink);color:var(--ond)}
.dark h2,.dark h3{color:#fff}
.dark a:not(.btn){color:var(--gold2)}
.sec-head{max-width:760px;margin-bottom:clamp(2.2rem,5vw,3.6rem)}
.grid{display:grid;gap:1.4rem}
.svc{position:relative;display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);padding:2.4rem 2.1rem 2.1rem;transition:transform .5s var(--ease),box-shadow .5s var(--ease),border-color .4s}
.svc::before{content:"";position:absolute;left:0;top:0;height:2px;width:0;background:var(--gold);transition:width .7s var(--ease)}
.svc:hover{transform:translateY(-6px);box-shadow:0 28px 60px rgba(6,16,29,.13);border-color:rgba(200,150,62,.55)}
.svc:hover::before{width:100%}
.svc .ico{color:var(--golddk);margin-bottom:1.3rem}
.svc h3{margin-bottom:.35rem}
.svc .tag{font:600 .72rem/1.5 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--golddk);margin:0 0 1.1rem}
.svc p{color:var(--muted)}
.more{margin-top:auto;display:inline-flex;align-items:center;gap:.7rem;padding-top:.6rem;font:600 .78rem/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--navy);text-decoration:none}
.more::after{content:"";width:30px;height:1px;background:currentColor;transition:width .45s var(--ease)}
.more:hover::after{width:54px}
.split{display:grid;gap:3rem;align-items:center}
.split img{display:block;width:100%;height:auto}
.checks{list-style:none;padding:0;margin:1.2rem 0 1.6rem}
.checks li{display:flex;gap:.9rem;align-items:flex-start;margin:.8rem 0}
.checks svg{flex:none;color:var(--gold);margin-top:.25rem}
.alt .checks svg,section:not(.dark) .checks svg{color:var(--golddk)}
.dark .checks svg{color:var(--gold)}
.pill{display:inline-block;border:1px solid var(--gold);color:var(--gold2);padding:.45rem .95rem;font:600 .72rem/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;margin:0 0 1.6rem}
section:not(.dark) .pill{color:var(--golddk);border-color:var(--golddk)}
.panel-art{border:1px solid rgba(200,150,62,.5);padding:clamp(1.8rem,4vw,3rem);background:linear-gradient(160deg,rgba(18,58,99,.55),rgba(6,16,29,.4))}
.panel-art .ico{color:var(--gold);margin-bottom:1rem}
.panel-art h3{color:#fff}
.panel-art p{color:var(--ond);margin:0}
.steps{counter-reset:s;list-style:none;margin:0;padding:0;display:grid;border-top:1px solid var(--line)}
.steps li{counter-increment:s;display:grid;grid-template-columns:4.2rem 1fr;gap:0 1rem;padding:1.7rem 0;border-bottom:1px solid var(--line)}
.steps li::before{content:counter(s,decimal-leading-zero);grid-row:span 2;font:500 2.6rem/1 var(--serif);color:var(--golddk)}
.steps strong{font:600 1.45rem/1.2 var(--serif);color:var(--ink)}
.steps span{color:var(--muted)}
.why{display:grid;gap:2.2rem}
.why div{border-top:1px solid rgba(200,150,62,.55);padding-top:1.4rem}
.why p{color:var(--mutd);margin:0}
.faq details{border-bottom:1px solid var(--line)}
.faq details:first-of-type{border-top:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:1.5rem;min-height:64px;padding:1.1rem 0;font:600 1.5rem/1.2 var(--serif);color:var(--ink)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";flex:none;font:400 1.8rem/1 var(--sans);color:var(--golddk);transition:transform .4s var(--ease)}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{color:var(--muted);margin:0 0 1.4rem;max-width:62ch}
.cta{text-align:center;position:relative;overflow:hidden}
.cta::before{content:"";position:absolute;inset:0;background:radial-gradient(600px 300px at 50% 0%,rgba(200,150,62,.2),transparent 65%)}
.cta .wrap{position:relative}
.cta h2{max-width:20ch;margin-inline:auto}
.cta .lead{margin-inline:auto}
.cta .actions{justify-content:center}
.facts{display:grid;gap:1.4rem;grid-template-columns:1fr 1fr;margin:2rem 0 0;padding:0;list-style:none}
.facts li{border-left:1px solid var(--gold);padding-left:1rem;color:var(--muted)}
.facts strong{display:block;font:600 1.3rem/1.25 var(--serif);color:var(--ink)}
.note{font-size:.95rem;color:var(--muted)}
.prose{max-width:72ch}
.prose h2{font-size:1.9rem;margin-top:1.8em}
/* contact + form */
.contact-grid{display:grid;gap:3rem}
.info dl{margin:1.4rem 0 0}
.info dt{font:600 .74rem/1 var(--sans);letter-spacing:.22em;text-transform:uppercase;color:var(--golddk);margin-top:1.5rem}
.info dd{margin:.4rem 0 0;font-size:1.15rem}
form.enq{background:#fff;border:1px solid var(--line);padding:clamp(1.4rem,4vw,2.8rem);box-shadow:0 30px 70px rgba(6,16,29,.08)}
form.enq h2{font-size:2rem}
.step-label{font:600 .74rem/1 var(--sans);letter-spacing:.22em;text-transform:uppercase;color:var(--golddk);margin:0 0 .8rem}
.field{margin:0 0 1.3rem}
.field>label,fieldset>legend{display:block;font-weight:500;font-size:.98rem;margin:0 0 .45rem;color:var(--ink);padding:0}
.opt{font-weight:400;color:var(--muted);font-size:.88rem}
.req{color:#A12B1F}
input[type=text],input[type=tel],input[type=email],select,textarea{width:100%;min-height:52px;padding:.7rem .9rem;border:1px solid #8E9AA8;border-radius:0;font:inherit;color:var(--ink);background:#fff;transition:border-color .25s,box-shadow .25s}
input:focus,select:focus,textarea:focus{border-color:var(--gold);box-shadow:0 0 0 3px rgba(200,150,62,.3);outline:none}
textarea{min-height:130px;resize:vertical}
.row2{display:grid;gap:0 1.2rem}
fieldset{border:0;padding:0;margin:0 0 1.3rem;min-width:0}
.choices{display:grid;gap:.8rem}
.choice{position:relative;display:block;cursor:pointer}
.choice input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer}
.choice span{display:block;height:100%;padding:1.05rem 1.15rem;border:1px solid #8E9AA8;background:#fff;transition:border-color .25s,background-color .25s,box-shadow .25s}
.choice strong{display:block;font:600 1.3rem/1.2 var(--serif);color:var(--ink)}
.choice small{display:block;color:var(--muted);font-size:.88rem;line-height:1.4;margin-top:.25rem}
.choice:hover span{border-color:var(--gold)}
.choice input:checked+span{border-color:var(--gold);background:#FFF8E8;box-shadow:inset 0 0 0 1px var(--gold)}
.choice input:focus-visible+span{outline:3px solid var(--gold);outline-offset:2px}
.panel{border-top:1px solid var(--line);margin-top:1.8rem;padding-top:1.8rem;animation:rise .7s var(--ease) both}
.panel h3{font-size:1.5rem}
.check{display:flex;gap:.7rem;align-items:flex-start;margin:.5rem 0;font-weight:400}
.check input{width:1.2rem;height:1.2rem;margin-top:.3rem;flex:none;accent-color:var(--navy)}
.err{color:#A12B1F;font-size:.92rem;margin:.35rem 0 0}
[aria-invalid="true"]{border-color:#A12B1F}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.status{margin-top:1.2rem;padding:1rem 1.2rem;display:none}
.status.show{display:block}
.status.ok{background:#E6F3EA;border:1px solid #2F7D4F;color:#15432A}
.status.bad{background:#FBE9E7;border:1px solid #A12B1F;color:#6B1B12}
.status.info{background:#EEF3F9;border:1px solid var(--navy2);color:var(--navy)}
/* footer */
.site-footer{background:var(--ink);color:var(--mutd);padding:clamp(3.5rem,7vw,5.5rem) 0 1.6rem;border-top:1px solid rgba(200,150,62,.3)}
.site-footer h2{font:600 .74rem/1 var(--sans);letter-spacing:.24em;text-transform:uppercase;color:var(--gold);margin:0 0 1.1rem}
.site-footer .big{font:500 clamp(1.9rem,4vw,2.8rem)/1.1 var(--serif);color:#fff;margin:0 0 1rem}
.site-footer a{color:#fff;text-decoration:none}
.site-footer a:hover{color:var(--gold2)}
.site-footer ul{list-style:none;margin:0;padding:0}
.site-footer li{margin:.5rem 0}
.foot-grid{display:grid;gap:2.5rem}
.copy{border-top:1px solid #1B3350;margin-top:3rem;padding-top:1.3rem;font-size:.88rem;display:flex;flex-wrap:wrap;gap:.5rem 2rem;justify-content:space-between}
/* motion */
@keyframes rise{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
@keyframes grow{to{width:min(220px,40%)}}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.09)}}
@keyframes bob{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(5px) rotate(-.5deg)}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-44px)}}
@keyframes sway{0%,100%{transform:rotate(-2.2deg)}50%{transform:rotate(2.2deg)}}
@keyframes glow{0%,100%{opacity:.13}50%{opacity:.28}}
@keyframes twinkle{0%,100%{opacity:.2}50%{opacity:1}}
@keyframes shimmer{0%,100%{opacity:.25}50%{opacity:.8}}
.in{animation:rise 1.1s var(--ease) both}
.d1{animation-delay:.1s}.d2{animation-delay:.25s}.d3{animation-delay:.4s}.d4{animation-delay:.55s}.d5{animation-delay:.7s}
.ship{animation:bob 7s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
.wave{animation:drift 9s ease-in-out infinite alternate}
.wave.w2{animation-duration:11s}
.wave.w3{animation-duration:13s}
.hook{transform-box:fill-box;transform-origin:50% 0;animation:sway 5.5s ease-in-out infinite}
.glow{animation:glow 6s ease-in-out infinite}
.star{animation:twinkle 4s ease-in-out infinite}
.star.s1{animation-delay:1.3s}.star.s2{animation-delay:2.6s}
.refl{animation:shimmer 3.4s ease-in-out infinite}
.refl.r1{animation-delay:.8s}.refl.r2{animation-delay:1.6s}
@supports (animation-timeline:view()){.reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 4% cover 26%}}
@media (min-width:700px){.grid.c2{grid-template-columns:repeat(2,1fr)}.grid.c3{grid-template-columns:repeat(3,1fr)}.row2{grid-template-columns:1fr 1fr}.choices{grid-template-columns:1fr 1fr}.foot-grid{grid-template-columns:1.5fr 1fr 1fr}.why{grid-template-columns:repeat(2,1fr);gap:2.5rem 2rem}}
@media (min-width:960px){.hero-grid{grid-template-columns:1.02fr .98fr}.split{grid-template-columns:1fr 1fr;gap:5rem}.split.rev>:first-child{order:2}.contact-grid{grid-template-columns:.75fr 1.25fr}.why{grid-template-columns:repeat(4,1fr)}.steps{grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--line)}.steps li{grid-template-columns:1fr;padding:1.8rem 1.4rem 1.8rem 0;border-bottom:0}.steps li::before{grid-row:auto;margin-bottom:.9rem}}
@media (max-width:520px){.facts{grid-template-columns:1fr}.brand-text strong{font-size:1.4rem}.brand-text span{letter-spacing:.2em}.frame::before{inset:12px -10px -12px 12px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{animation:none!important;transition:none!important}.menu.open .menu-links li{opacity:1;transform:none}}
"""

# --------------------------------------------------------------------------- script
JS = r"""
(function(){
var d=document,root=d.documentElement;
var hdr=d.querySelector('.site-header');
function onScroll(){if(hdr){hdr.classList.toggle('scrolled',window.scrollY>10);}}
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
var btn=d.getElementById('menu-btn'),menu=d.getElementById('menu'),closeBtn=d.getElementById('menu-close');
if(btn&&menu&&closeBtn){
var openMenu=function(){menu.classList.add('open');btn.setAttribute('aria-expanded','true');root.classList.add('lock');setTimeout(function(){closeBtn.focus();},80);};
var closeMenu=function(){menu.classList.remove('open');btn.setAttribute('aria-expanded','false');root.classList.remove('lock');btn.focus();};
btn.addEventListener('click',openMenu);
closeBtn.addEventListener('click',closeMenu);
d.addEventListener('keydown',function(e){
if(!menu.classList.contains('open'))return;
if(e.key==='Escape'){closeMenu();return;}
if(e.key==='Tab'){
var f=[].slice.call(menu.querySelectorAll('a[href],button'));
if(!f.length)return;
var first=f[0],last=f[f.length-1];
if(e.shiftKey&&d.activeElement===first){e.preventDefault();last.focus();}
else if(!e.shiftKey&&d.activeElement===last){e.preventDefault();first.focus();}
}
});
}
var f=d.getElementById('enquiry-form');
if(!f)return;
var endpoint=f.getAttribute('data-endpoint')||'';
var mailto=f.getAttribute('data-mailto')||'';
var phoneTxt=f.getAttribute('data-phone')||'';
var status=d.getElementById('form-status');
var panels=[].slice.call(f.querySelectorAll('.panel[data-for]'));
var RULES={
'Import & Export':{req:['direction','goods'],detailsReq:false,ph:'Anything else we should know, e.g. timing, documents you already have.'},
'Real estate development':{req:['re_interest'],detailsReq:true,ph:'Tell us about the project or property you have in mind.'},
'General services':{req:['gs_service','gs_scope'],detailsReq:false,ph:'Anything else we should know.'},
'Something else':{req:[],detailsReq:true,ph:'Tell us what you need and how we can help.'}
};
function el(n){return f.querySelector('[name="'+n+'"]');}
function curType(){var r=f.querySelector('input[name="enquiry_type"]:checked');return r?r.value:'';}
function val(n){var e=el(n);return e&&!e.disabled?String(e.value||'').trim():'';}
function setErr(n,msg){
var p=d.getElementById('err-'+n),e=el(n);
if(p)p.textContent=msg||'';
if(e&&e.type!=='radio'){if(msg){e.setAttribute('aria-invalid','true');}else{e.removeAttribute('aria-invalid');}}
}
function show(kind,msg){status.className='status show '+kind;status.textContent=msg;}
var allNames=['enquiry_type','name','phone','email','details','consent'];
panels.forEach(function(p){[].forEach.call(p.querySelectorAll('input,select,textarea'),function(c){if(c.name&&allNames.indexOf(c.name)<0)allNames.push(c.name);});});
function setPanels(){
var t=curType();
panels.forEach(function(p){
var on=p.getAttribute('data-for')===t;
p.hidden=!on;
[].forEach.call(p.querySelectorAll('input,select,textarea'),function(c){c.disabled=!on;});
});
var r=RULES[t],note=d.getElementById('details-note'),ta=el('details');
if(note)note.textContent=(r&&r.detailsReq)?'(required)':'(optional)';
if(ta)ta.setAttribute('placeholder',r?r.ph:'');
var rest=d.getElementById('after-type');
if(rest)rest.hidden=!t;
}
f.addEventListener('change',function(e){if(e.target&&e.target.name==='enquiry_type'){setErr('enquiry_type','');setPanels();}});
setPanels();
function validate(){
var t=curType(),bad=[];
allNames.forEach(function(n){setErr(n,'');});
if(!t){bad.push(['enquiry_type','Please choose what your enquiry is about.']);}
if(val('name').length<2)bad.push(['name','Please enter your name.']);
var ph=val('phone'),em=val('email');
if(!ph&&!em)bad.push(['phone','Please give a phone number or an email address so we can reply.']);
if(ph&&!/^[+()\d][\d\s().+-]{6,19}$/.test(ph))bad.push(['phone','Please enter a valid phone number, e.g. +234 800 000 0000.']);
if(em&&!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em))bad.push(['email','Please enter a valid email address.']);
var r=RULES[t];
if(r){
r.req.forEach(function(n){var c=el(n);if(c&&!val(n)){bad.push([n,c.getAttribute('data-msg')||'This field is required.']);}});
if(r.req.indexOf('goods')>=0&&val('goods')&&val('goods').length<5)bad.push(['goods','Please describe the goods in a few words.']);
if(r.req.indexOf('gs_scope')>=0&&val('gs_scope')&&val('gs_scope').length<10)bad.push(['gs_scope','Please describe the work in a little more detail.']);
if(r.detailsReq&&val('details').length<10)bad.push(['details','Please tell us a little more so we can help.']);
}
if(!el('consent').checked)bad.push(['consent','Please confirm you agree to us using your details to reply.']);
bad.forEach(function(b){setErr(b[0],b[1]);});
if(bad.length){
var first=bad[0][0],fe=first==='enquiry_type'?f.querySelector('input[name="enquiry_type"]'):el(first);
if(fe)fe.focus();
}
return bad.length===0;
}
function collect(t){
var data={enquiry_type:t,name:val('name'),phone:val('phone'),email:val('email')};
var pairs=[['Enquiry about',t],['Name',data.name],['Phone',data.phone||'-'],['Email',data.email||'-']];
var p=panels.filter(function(x){return x.getAttribute('data-for')===t;})[0];
if(p){
var groups={};
[].forEach.call(p.querySelectorAll('input,select,textarea'),function(c){
if(c.type==='checkbox'){if(c.checked){(groups[c.name]=groups[c.name]||{label:c.getAttribute('data-label')||c.name,vals:[]}).vals.push(c.value);}return;}
var v=String(c.value||'').trim();
if(v){data[c.name]=v;pairs.push([c.getAttribute('data-label')||c.name,v]);}
});
Object.keys(groups).forEach(function(k){data[k]=groups[k].vals;pairs.push([groups[k].label,groups[k].vals.join(', ')]);});
}
data.details=val('details');
pairs.push(['Additional information',data.details||'-']);
return {data:data,pairs:pairs};
}
f.addEventListener('submit',function(e){
e.preventDefault();
if(val('company_website')){return;}
if(!validate()){show('bad','Please fix the highlighted fields and try again.');return;}
var t=curType(),c=collect(t);
if(endpoint){
var b=f.querySelector('button[type="submit"]');b.disabled=true;show('info','Sending your enquiry…');
fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(c.data)})
.then(function(r){if(!r.ok)throw new Error('bad status');f.reset();setTimeout(setPanels,0);show('ok','Thank you. Your enquiry was received and we will contact you using the details you gave.');})
.catch(function(){show('bad','Sorry, your enquiry could not be sent. Please try again, or call '+phoneTxt+'.');})
.then(function(){b.disabled=false;});
}else{
var body=c.pairs.map(function(x){return x[0]+': '+x[1];}).join('\n');
window.location.href='mailto:'+mailto+'?subject='+encodeURIComponent('Website enquiry: '+t)+'&body='+encodeURIComponent(body);
show('info','Your email app should now open with your enquiry filled in. Your enquiry has NOT been sent until you press Send in that email. If nothing opened, please email '+mailto+' or call '+phoneTxt+'.');
}
});
})();
"""


# --------------------------------------------------------------------------- structured data
def org_node():
    return {
        "@type": ["Organization", "LocalBusiness"],
        "@id": f"{SITE_URL}/#organization",
        "name": NAME,
        "url": f"{SITE_URL}/",
        "logo": f"{SITE_URL}/android-chrome-512x512.png",
        "image": f"{SITE_URL}/og-image.png",
        "description": "Nigerian company offering import and export (including clearing and forwarding), real estate development and general services from Ikeja, Lagos State.",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Ikeja", "addressRegion": "Lagos State", "addressCountry": "NG"},
    }


def website_node():
    return {"@type": "WebSite", "@id": f"{SITE_URL}/#website", "url": f"{SITE_URL}/", "name": NAME,
            "inLanguage": "en-NG", "publisher": {"@id": f"{SITE_URL}/#organization"}}


def breadcrumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}


def service_nodes():
    base = f"{SITE_URL}/services.html"
    defs = [
        ("import-export", "Import & Export",
         "Import and export coordination including clearing and forwarding: sourcing support, shipping and customs documentation, port clearing, customs processing and haulage."),
        ("real-estate", "Real Estate Development", "Property development, acquisition and project delivery."),
        ("general-services", "General Services", "Procurement, logistics support and general contracting."),
    ]
    return [{"@type": "Service", "@id": f"{base}#{i}", "name": n, "description": d, "serviceType": n,
             "provider": {"@id": f"{SITE_URL}/#organization"}, "areaServed": {"@type": "Country", "name": "Nigeria"}}
            for i, n, d in defs]


# --------------------------------------------------------------------------- layout
def css_text():
    return CSS + ("" if PREVIEW else FONT_FACES)


def layout(page, title, desc, path, body, schema, noindex=False):
    canonical = f"{SITE_URL}{path}"
    robots = ('<meta name="robots" content="noindex, follow">' if noindex
              else '<meta name="robots" content="index, follow, max-image-preview:large">')
    css = css_text()
    links = []
    menu_items = []
    for key, href, label, sub in NAV:
        cur = ' aria-current="page"' if key == page else ""
        menu_items.append(f'<li><a href="{href}"{cur}>{label}<small>{sub}</small></a></li>')
    ld = json.dumps({"@context": "https://schema.org", "@graph": schema}, ensure_ascii=False, indent=1).replace("</", "<\\/")

    def sha(s):
        return "'sha256-" + base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode() + "'"

    connect = "'self'"
    if FORM_ENDPOINT:
        u = urllib.parse.urlparse(FORM_ENDPOINT)
        connect += f" {u.scheme}://{u.netloc}"
    csp_tag = ""
    if not PREVIEW:
        csp = (f"default-src 'self'; img-src 'self' data:; font-src 'self'; style-src {sha(css)}; script-src {sha(JS)}; "
               f"connect-src {connect}; base-uri 'self'; form-action 'self'; object-src 'none'")
        csp_tag = f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
        links.append('<link rel="preload" href="fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>')
        links.append('<link rel="preload" href="fonts/jost-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>')
    else:
        links.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
        links.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        links.append(f'<link rel="stylesheet" href="{GOOGLE_FONTS}">')
    return f"""<!doctype html>
<html lang="en-NG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{canonical}">
{csp_tag}
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="theme-color" content="#06101D">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
{chr(10).join(links)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="en_NG">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NAME}: import and export, real estate development and general services">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE_URL}/og-image.png">
<script type="application/ld+json">
{ld}
</script>
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header">
<div class="wrap bar">
<a class="brand" href="index.html" aria-label="{NAME}, home">{MARK_SVG}<span class="brand-text"><strong>Ashiri-Ola</strong><span>General Services Ltd</span></span></a>
<div class="bar-actions">
<a class="btn btn-gold btn-sm bar-cta" href="contact.html">Request a quote</a>
<button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="burger" aria-hidden="true"><i></i><i></i><i></i></span><span>Menu</span></button>
</div>
</div>
</header>
<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Site menu">
<div class="menu-top">
<a class="brand" href="index.html" aria-label="{NAME}, home">{MARK_SVG}<span class="brand-text"><strong>Ashiri-Ola</strong><span>General Services Ltd</span></span></a>
<button class="menu-btn" id="menu-close" type="button"><span class="burger" aria-hidden="true"><i></i><i></i><i></i></span><span>Close</span></button>
</div>
<div class="menu-body">
<nav aria-label="Main"><ul class="menu-links">{''.join(menu_items)}</ul></nav>
<div class="menu-side">
<h2>Speak to us</h2>
<p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<h2>Office</h2>
<p>{ADDRESS_LINE}</p>
<a class="btn btn-gold" href="contact.html">Request a quote</a>
</div>
</div>
</div>
<main id="main">
{body}
</main>
{footer_html()}
<script>{JS}</script>
</body>
</html>
"""


def footer_html():
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="foot-grid">
<div>
<p class="big">{NAME}</p>
<p>Excellence | Reliability | Integrity.<br>Import &amp; export, real estate development and general services.</p>
</div>
<div>
<h2>Explore</h2>
<ul>
<li><a href="index.html">Home</a></li>
<li><a href="about.html">About us</a></li>
<li><a href="services.html">Services</a></li>
<li><a href="contact.html">Contact &amp; quotes</a></li>
<li><a href="privacy.html">Privacy notice</a></li>
</ul>
</div>
<div>
<h2>Contact</h2>
<ul>
<li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>{ADDRESS_LINE}</li>
</ul>
</div>
</div>
<div class="copy"><span>&copy; {YEAR} {NAME}. All rights reserved.</span><span>We deliver solutions that move the world.</span></div>
</div>
</footer>"""


# --------------------------------------------------------------------------- page bodies
def cta_band(text="Tell us what you need to import, export, build or source and we will come back to you."):
    return f"""<section class="dark cta">
<div class="wrap">
<p class="eyebrow">Begin an enquiry</p>
<h2 class="reveal">Ready to talk about your cargo or project?</h2>
<p class="lead">{text}</p>
<div class="actions"><a class="btn btn-gold" href="contact.html">Request a quote</a><a class="btn btn-line" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div>
</div>
</section>"""


def import_export_visual(kind="home"):
    img = photo("haulage.jpg", "Truck carrying a shipping container on a highway beside a container port at sunset")
    if img:
        return img
    return (f'<div class="panel-art"><div class="ico">{ICONS["trade"]}</div><h3>One team, start to finish</h3>'
            '<p>From the first enquiry to delivery, your goods and documents stay with a single point of contact.</p></div>')


def home():
    hero_photo = photo("hero-port.jpg", "Container ship loading at a port at dusk beneath quayside cranes", cls="kb", eager=True)
    hero_cls = "hero hero-photo" if hero_photo else "hero"
    hero_bg = f'<div class="hero-bg">{hero_photo}</div>' if hero_photo else ""
    hero_side = "" if hero_photo else f'<div class="frame in d3"><div class="frame-inner">{hero_art()}</div></div>'
    faqs = [
        ("Does Import &amp; Export include clearing and forwarding?",
         "Yes. Clearing and forwarding is part of our import and export service, so one team coordinates the documentation, port clearing and onward movement of your goods."),
        ("How do I get a quote?",
         "Send an enquiry through the contact page, or call us. Tell us what the goods are, where they are coming from or going to, and roughly how much there is. Pricing depends on those details, so we do not publish fixed rates."),
        ("What details should I have ready?",
         "A description of the goods, the origin and destination, approximate weight or volume, and any supplier or buyer documents you already have. If you are unsure, send what you have and we will tell you what else is needed."),
        ("Do you only handle shipping?",
         "No. Ashiri-Ola also delivers real estate development and general services such as procurement, logistics support and general contracting. The contact form adapts to whichever you choose."),
        ("Where are you based?", "Our office is in Ikeja, Lagos State, Nigeria."),
    ]
    faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)
    body = f"""<section class="{hero_cls}">{hero_bg}
<div class="wrap hero-grid">
<div>
<p class="eyebrow in d1">Excellence | Reliability | Integrity</p>
<h1 class="in d2">Import &amp; Export, <em>handled with care.</em></h1>
<p class="lead in d3">Clearing &amp; forwarding is part of the service. From shipping documents to port clearing and delivery, {NAME} gives you one accountable team in Lagos.</p>
<div class="actions in d4"><a class="btn btn-gold" href="contact.html">Request a quote</a><a class="btn btn-line" href="services.html">Our services</a></div>
</div>
{hero_side}
</div>
</section>
<div class="strip"><ul><li>Import &amp; Export</li><li>Real Estate Development</li><li>General Services</li></ul></div>

<section>
<div class="wrap">
<div class="sec-head reveal"><p class="eyebrow">What we do</p><h2>Three ways we work for you</h2><p class="lead">Trade and logistics sit at the heart of the company. Property and general services complete it.</p></div>
<div class="grid c3">
<article class="svc reveal"><div class="ico">{ICONS['trade']}</div><h3>Import &amp; Export</h3><p class="tag">Includes clearing &amp; forwarding</p><p>Sourcing support, shipping and customs documentation, port clearing and haulage, coordinated by one team.</p><a class="more" href="services.html#import-export">Learn more</a></article>
<article class="svc reveal"><div class="ico">{ICONS['property']}</div><h3>Real Estate Development</h3><p class="tag">Development &middot; Acquisition &middot; Delivery</p><p>Property development, acquisition and project delivery, from land to finished, liveable spaces.</p><a class="more" href="services.html#real-estate">Learn more</a></article>
<article class="svc reveal"><div class="ico">{ICONS['general']}</div><h3>General Services</h3><p class="tag">Procurement &middot; Logistics support &middot; Contracting</p><p>Procurement, logistics support and general contracting, tailored to the needs of each client.</p><a class="more" href="services.html#general-services">Learn more</a></article>
</div>
</div>
</section>

<section class="dark">
<div class="wrap split">
<div class="reveal">
<p class="eyebrow">Trade &amp; logistics</p>
<h2>Import &amp; Export, <em>end to end</em></h2>
<p class="pill">Clearing &amp; forwarding included</p>
<p>Moving goods in or out of Nigeria means arranging the shipment, preparing the paperwork, clearing the cargo through customs and the port, and getting it delivered. We coordinate those steps together so you deal with one team instead of several.</p>
<ul class="checks">
<li>{ICONS['check']}<span>Sourcing support and cross-border movement of goods</span></li>
<li>{ICONS['check']}<span>Shipping and customs documentation</span></li>
<li>{ICONS['check']}<span>Port clearing and customs processing</span></li>
<li>{ICONS['check']}<span>Haulage and delivery of cleared cargo</span></li>
</ul>
<a class="btn btn-gold" href="services.html#import-export">How it works</a>
</div>
<div class="reveal">{import_export_visual()}</div>
</div>
</section>

<section>
<div class="wrap">
<div class="sec-head reveal"><p class="eyebrow">How we work</p><h2>How we handle your enquiry</h2></div>
<ol class="steps reveal">
<li><strong>Send your details</strong><span>Use the form or call us with a description of your goods or project.</span></li>
<li><strong>We review it</strong><span>We look at what you need and ask for anything that is missing.</span></li>
<li><strong>We confirm the scope</strong><span>You hear back on what is required and how we can help.</span></li>
<li><strong>We coordinate</strong><span>We work through the steps with you until the job is done.</span></li>
</ol>
</div>
</section>

<section class="dark">
<div class="wrap">
<div class="sec-head reveal"><p class="eyebrow">Why choose us</p><h2>Built on four <em>commitments</em></h2></div>
<div class="why reveal">
<div><h3>International trade</h3><p>Import and export coordination in one place.</p></div>
<div><h3>Reliable service</h3><p>Honest updates and a clear point of contact.</p></div>
<div><h3>Professional team</h3><p>Experience across trade, logistics and property.</p></div>
<div><h3>Client focus</h3><p>Long-term relationships built on results.</p></div>
</div>
</div>
</section>

<section class="alt">
<div class="wrap faq prose">
<div class="sec-head reveal"><p class="eyebrow">Questions</p><h2>Frequently asked questions</h2></div>
{faq_html}
</div>
</section>

{cta_band()}"""
    return {"page": "home", "path": "/",
            "title": f"{NAME} | Import & Export, Lagos",
            "desc": "Import and export, including clearing and forwarding, from Ikeja, Lagos. Also real estate development and general services from Ashiri-Ola General Services Ltd.",
            "body": body, "schema": [org_node(), website_node()]}


def about():
    body = f"""<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / About</p>
<h1 class="in d1">About <em>{NAME}</em></h1>
<p class="lead in d2">A Nigerian company working across international trade, logistics and real estate from Ikeja, Lagos.</p>
<span class="rule"></span>
</div></section>
<section>
<div class="wrap split">
<div class="reveal">
<p class="eyebrow">Who we are</p>
<h2>A trusted partner for growth and success</h2>
<p>{NAME} operates across international trade, logistics and real estate. We handle the movement of goods through Nigeria's ports and develop property that is meant to hold long-term value, bringing the same standards of excellence, reliability and integrity to every engagement.</p>
<p>We work as a single team, so clients deal with one accountable partner instead of many moving parts.</p>
<ul class="facts">
<li><strong>Import &amp; Export</strong>Including clearing &amp; forwarding</li>
<li><strong>Real Estate Development</strong>Development and acquisition</li>
<li><strong>General Services</strong>Procurement and contracting</li>
<li><strong>Based in</strong>Ikeja, Lagos State</li>
</ul>
</div>
<div class="reveal">{photo("real-estate.jpg", "Residential apartment development with palm trees and landscaped grounds") or '<div class="panel-art"><h3>Excellence | Reliability | Integrity</h3><p>These three words guide how we treat every enquiry, shipment and project.</p></div>'}</div>
</div>
</section>
<section class="dark"><div class="wrap">
<div class="sec-head reveal"><p class="eyebrow">Our values</p><h2>What you can <em>expect</em> from us</h2></div>
<div class="why reveal">
<div><h3>Excellence</h3><p>Careful handling of documents, cargo and projects, with attention to detail.</p></div>
<div><h3>Reliability</h3><p>Honest updates and a clear point of contact from enquiry to completion.</p></div>
<div><h3>Integrity</h3><p>Plain communication about what we can do, and what we need from you.</p></div>
</div>
</div></section>
{cta_band("Send us the details and we will tell you how we can help.")}"""
    bc = breadcrumbs([("Home", "/"), ("About", "/about.html")])
    return {"page": "about", "path": "/about.html", "title": f"About Us | {NAME}",
            "desc": "Learn about Ashiri-Ola General Services Ltd, a Lagos-based Nigerian company in import and export, real estate development and general services.",
            "body": body, "schema": [org_node(), website_node(), bc]}


def services():
    body = f"""<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / Services</p>
<h1 class="in d1">Our <em>services</em></h1>
<p class="lead in d2">Import &amp; Export (with clearing &amp; forwarding), real estate development and general services.</p>
<span class="rule"></span>
</div></section>

<section id="import-export">
<div class="wrap split">
<div class="reveal">
<p class="eyebrow">Trade &amp; logistics</p>
<h2>Import &amp; Export</h2>
<p class="pill">Includes clearing &amp; forwarding</p>
<p>Importing or exporting goods and clearing and forwarding them are parts of the same journey. Shipments have to be arranged, documents prepared, cargo cleared through customs and the port, and goods moved on to their destination. We coordinate these steps together so you have one team to speak to.</p>
<h3>What this covers</h3>
<ul class="checks">
<li>{ICONS['check']}<span><strong>Sourcing and cross-border movement:</strong> support for getting goods from where they are to where they need to be.</span></li>
<li>{ICONS['check']}<span><strong>Documentation:</strong> shipping and customs paperwork prepared and checked.</span></li>
<li>{ICONS['check']}<span><strong>Clearing:</strong> port clearing and customs processing to get cargo released.</span></li>
<li>{ICONS['check']}<span><strong>Forwarding:</strong> haulage and delivery of cleared cargo onward.</span></li>
</ul>
<h3>What to have ready for a quote</h3>
<ul class="checks">
<li>{ICONS['check']}<span>A description of the goods</span></li>
<li>{ICONS['check']}<span>Where they are coming from and where they are going</span></li>
<li>{ICONS['check']}<span>Approximate weight or volume</span></li>
<li>{ICONS['check']}<span>Any supplier, buyer or shipping documents you already have</span></li>
</ul>
<p class="note">Requirements vary with the type of goods and the route. Send what you have and we will tell you what else is needed.</p>
<div class="actions"><a class="btn btn-dark" href="contact.html">Request a quote</a></div>
</div>
<div class="reveal">{import_export_visual("services")}</div>
</div>
</section>

<section class="alt" id="real-estate">
<div class="wrap split rev">
<div class="reveal">{photo("real-estate.jpg", "Residential apartment development with palm trees and landscaped grounds") or '<div class="panel-art"><div class="ico">' + ICONS['property'] + '</div><h3>From land to finished spaces</h3><p>Development, acquisition and delivery handled with the same standards we apply to cargo.</p></div>'}</div>
<div class="reveal">
<p class="eyebrow">Property</p>
<h2>Real Estate Development</h2>
<p class="pill">Development &middot; Acquisition &middot; Delivery</p>
<p>We develop and acquire property and deliver projects from land through to finished, liveable spaces. If you are looking to develop or acquire, tell us about the project and we will respond.</p>
<div class="actions"><a class="btn btn-outline" href="contact.html">Enquire about property</a></div>
</div>
</div>
</section>

<section class="dark" id="general-services">
<div class="wrap split">
<div class="reveal">
<p class="eyebrow">Support</p>
<h2>General Services</h2>
<p class="pill">Procurement &middot; Logistics support &middot; Contracting</p>
<p>Procurement, logistics support and general contracting, tailored to the needs of each client. Describe the work you need done and we will let you know how we can help.</p>
<div class="actions"><a class="btn btn-gold" href="contact.html">Enquire about general services</a></div>
</div>
<div class="reveal"><div class="panel-art"><div class="ico">{ICONS['general']}</div><h3>Tailored to the client</h3><p>Every brief is different, so we start by understanding what you need.</p></div></div>
</div>
</section>
{cta_band()}"""
    bc = breadcrumbs([("Home", "/"), ("Services", "/services.html")])
    return {"page": "services", "path": "/services.html",
            "title": f"Import & Export Services | {NAME}",
            "desc": "Import and export with clearing and forwarding, plus real estate development and general services from Ashiri-Ola General Services Ltd in Ikeja, Lagos.",
            "body": body, "schema": [org_node(), website_node(), bc] + service_nodes()}


def sel(name, label, options, required=False, msg="", optional=False):
    opts = "".join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in options)
    star = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    opt = ' <span class="opt">(optional)</span>' if optional else ""
    dm = f' data-msg="{esc(msg)}"' if msg else ""
    return (f'<div class="field"><label for="{name}">{label}{star}{opt}</label>'
            f'<select id="{name}" name="{name}" data-label="{esc(label)}"{dm} aria-describedby="err-{name}"><option value="">Choose one</option>{opts}</select>'
            f'<p class="err" id="err-{name}"></p></div>')


def txt(name, label, placeholder="", required=False, msg="", optional=True):
    star = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    opt = ' <span class="opt">(optional)</span>' if optional and not required else ""
    dm = f' data-msg="{esc(msg)}"' if msg else ""
    ph = f' placeholder="{esc(placeholder)}"' if placeholder else ""
    return (f'<div class="field"><label for="{name}">{label}{star}{opt}</label>'
            f'<input type="text" id="{name}" name="{name}" data-label="{esc(label)}"{ph}{dm} aria-describedby="err-{name}">'
            f'<p class="err" id="err-{name}"></p></div>')


def area(name, label, required=False, msg="", hint=""):
    star = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    h = f' <span class="opt">{hint}</span>' if hint else ""
    dm = f' data-msg="{esc(msg)}"' if msg else ""
    return (f'<div class="field"><label for="{name}">{label}{star}{h}</label>'
            f'<textarea id="{name}" name="{name}" data-label="{esc(label)}"{dm} aria-describedby="err-{name}"></textarea>'
            f'<p class="err" id="err-{name}"></p></div>')


def contact():
    choices = [
        ("Import & Export", "Import &amp; Export", "Including clearing &amp; forwarding"),
        ("Real estate development", "Real Estate", "Development or acquisition"),
        ("General services", "General Services", "Procurement, logistics support, contracting"),
        ("Something else", "Something else", "Any other enquiry"),
    ]
    radios = "".join(
        f'<label class="choice"><input type="radio" name="enquiry_type" value="{esc(v)}" aria-describedby="err-enquiry_type"><span><strong>{t}</strong><small>{s}</small></span></label>'
        for v, t, s in choices)
    svcs = ["Clearing & forwarding", "Shipping documentation", "Haulage / delivery", "Sourcing support"]
    svc_html = "".join(
        f'<label class="check"><input type="checkbox" name="services" value="{esc(s)}" data-label="Services needed"><span>{esc(s)}</span></label>'
        for s in svcs)
    trade = (
        '<div class="panel" data-for="Import &amp; Export" hidden><h3>Import &amp; Export details</h3>'
        + sel("direction", "Is this an import or an export?", ["Import", "Export", "Both"], True, "Please say whether this is an import or an export.")
        + '<div class="row2">'
        + txt("origin", "Origin", "Where the goods are coming from")
        + txt("destination", "Destination", "Where the goods are going")
        + '</div>'
        + area("goods", "Description of goods", True, "Please briefly describe the goods.")
        + txt("cargo_size", "Approximate weight or volume", "e.g. 2 tonnes, or 1 x 20ft container")
        + f'<fieldset><legend>Services needed <span class="opt">(optional)</span></legend>{svc_html}</fieldset></div>')
    prop = (
        '<div class="panel" data-for="Real estate development" hidden><h3>Property details</h3>'
        + sel("re_interest", "What are you looking for?", ["Development", "Acquisition (buying land or property)", "Something else"], True, "Please choose what you are looking for.")
        + '<div class="row2">'
        + sel("re_property_type", "Property type", ["Residential", "Commercial", "Land", "Mixed use", "Not sure yet"], optional=True)
        + sel("re_timeline", "Timeline", ["As soon as possible", "Within 3 months", "3 to 12 months", "Just exploring"], optional=True)
        + '</div>'
        + txt("re_location", "Location", "Area or state of the property")
        + txt("re_budget", "Approximate budget", "Optional, in naira")
        + '</div>')
    gen = (
        '<div class="panel" data-for="General services" hidden><h3>General services details</h3>'
        + sel("gs_service", "What do you need?", ["Procurement", "Logistics support", "General contracting", "Something else"], True, "Please choose the service you need.")
        + area("gs_scope", "Describe the work or items", True, "Please describe the work or items you need.")
        + '<div class="row2">'
        + txt("gs_location", "Where is the work needed?", "Optional")
        + sel("gs_timeline", "Timeline", ["As soon as possible", "Within 3 months", "3 to 12 months", "Just exploring"], optional=True)
        + '</div></div>')
    other = '<div class="panel" data-for="Something else" hidden><h3>Tell us more</h3><p class="note">Use the message box below to describe what you need.</p></div>'
    body = f"""<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / Contact</p>
<h1 class="in d1">Request a <em>quote</em></h1>
<p class="lead in d2">Choose what your enquiry is about and the form will ask only what we need.</p>
<span class="rule"></span>
</div></section>
<section>
<div class="wrap contact-grid">
<div class="info reveal">
<p class="eyebrow">Get in touch</p>
<h2>Speak to us directly</h2>
<dl>
<dt>Phone</dt><dd><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd>
<dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
<dt>Office</dt><dd>{ADDRESS_LINE}</dd>
</dl>
<p class="note">See our <a href="privacy.html">privacy notice</a> for how we use the details you send.</p>
</div>
<form class="enq" id="enquiry-form" novalidate data-endpoint="{esc(FORM_ENDPOINT)}" data-mailto="{EMAIL}" data-phone="{PHONE_DISPLAY}" aria-describedby="form-status">
<div class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="company_website" tabindex="-1" autocomplete="off"></label></div>
<p class="step-label">Step 1</p>
<fieldset><legend>What is your enquiry about? <span class="req" aria-hidden="true">*</span></legend>
<div class="choices">{radios}</div>
<p class="err" id="err-enquiry_type"></p></fieldset>
{trade}{prop}{gen}{other}
<div id="after-type" hidden>
<div class="panel">
<p class="step-label">Step 2</p>
<h3>Your details</h3>
<div class="field"><label for="name">Full name <span class="req" aria-hidden="true">*</span></label><input type="text" id="name" name="name" autocomplete="name" aria-describedby="err-name"><p class="err" id="err-name"></p></div>
<div class="row2">
<div class="field"><label for="phone">Phone <span class="opt">(phone or email needed)</span></label><input type="tel" id="phone" name="phone" autocomplete="tel" inputmode="tel" aria-describedby="err-phone"><p class="err" id="err-phone"></p></div>
<div class="field"><label for="email">Email</label><input type="email" id="email" name="email" autocomplete="email" aria-describedby="err-email"><p class="err" id="err-email"></p></div>
</div>
<div class="field"><label for="details">Additional information <span class="opt" id="details-note">(optional)</span></label><textarea id="details" name="details" aria-describedby="err-details"></textarea><p class="err" id="err-details"></p></div>
<div class="field"><label class="check"><input type="checkbox" id="consent" name="consent" aria-describedby="err-consent"><span>I agree that Ashiri-Ola may use these details to reply to my enquiry. <span class="req" aria-hidden="true">*</span></span></label><p class="err" id="err-consent"></p></div>
<button class="btn btn-dark" type="submit">Send enquiry</button>
</div>
</div>
<div class="status" id="form-status" role="status" aria-live="polite"></div>
</form>
</div>
</section>"""
    bc = breadcrumbs([("Home", "/"), ("Contact", "/contact.html")])
    cp = {"@type": "ContactPage", "@id": f"{SITE_URL}/contact.html#page", "url": f"{SITE_URL}/contact.html",
          "name": f"Contact {NAME}", "about": {"@id": f"{SITE_URL}/#organization"}}
    return {"page": "contact", "path": "/contact.html", "title": f"Contact & Request a Quote | {NAME}",
            "desc": "Request a quote for import and export, real estate development or general services. Ashiri-Ola General Services Ltd, Ikeja, Lagos.",
            "body": body, "schema": [org_node(), website_node(), bc, cp]}


def privacy():
    handling = ("Enquiries submitted through the form are sent to our enquiry-handling service and delivered to us."
                if FORM_ENDPOINT else
                "The form opens your own email app with your enquiry filled in. Nothing is sent to us until you press Send in that email.")
    updated = datetime.date.today().strftime("%d %B %Y").lstrip("0")
    body = f"""<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="index.html">Home</a> / Privacy notice</p>
<h1 class="in d1">Privacy <em>notice</em></h1>
<p class="lead in d2">Last updated {updated}.</p>
<span class="rule"></span>
</div></section>
<section><div class="wrap prose">
<h2>Who we are</h2>
<p>{NAME}, {ADDRESS_LINE}. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>, <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
<h2>What we collect</h2>
<p>Only what you type into the enquiry form: your name, phone number and/or email, the type of enquiry, and the details relevant to it, such as a description of goods, origin and destination, property type and location, or the work you need done, plus any additional information. If you phone or email us, we receive the details you give us.</p>
<h2>How we use it</h2>
<p>To reply to your enquiry, prepare a quote and, if you go ahead, carry out the work. We do not sell your details.</p>
<h2>How the form works</h2>
<p>{handling}</p>
<h2>Cookies, fonts and tracking</h2>
<p>This website does not use advertising or analytics cookies or tracking scripts. Fonts are served from this website and not from a third party.</p>
<h2>How long we keep it</h2>
<p>We keep enquiry details for as long as needed to deal with your enquiry and any resulting work, and as required by law.</p>
<h2>Your rights</h2>
<p>Under the Nigeria Data Protection Act 2023 you may ask to see, correct or delete the personal data we hold about you. Email <a href="mailto:{EMAIL}">{EMAIL}</a> to make a request.</p>
</div></section>"""
    bc = breadcrumbs([("Home", "/"), ("Privacy notice", "/privacy.html")])
    return {"page": "privacy", "path": "/privacy.html", "title": f"Privacy Notice | {NAME}",
            "desc": "How Ashiri-Ola General Services Ltd collects and uses the details you send through our enquiry form or by phone and email.",
            "body": body, "schema": [org_node(), website_node(), bc]}


def notfound():
    body = """<section class="page-hero"><div class="wrap">
<h1 class="in d1">Page <em>not found</em></h1>
<p class="lead in d2">The page you were looking for does not exist or has moved.</p>
<div class="actions in d3"><a class="btn btn-gold" href="index.html">Go to the homepage</a><a class="btn btn-line" href="contact.html">Contact us</a></div>
</div></section>"""
    return {"page": "", "path": "/404.html", "title": f"Page not found | {NAME}",
            "desc": "The page you requested could not be found.", "body": body,
            "schema": [org_node(), website_node()], "noindex": True}


# --------------------------------------------------------------------------- build
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [home(), about(), services(), contact(), privacy(), notfound()]
    indexable = []
    for p in pages:
        doc = layout(p["page"], p["title"], p["desc"], p["path"], p["body"], p["schema"], p.get("noindex", False))
        fname = "404.html" if p["path"] == "/404.html" else ("index.html" if p["path"] == "/" else p["path"].lstrip("/"))
        (OUT / fname).write_text(doc, encoding="utf-8")
        if not p.get("noindex"):
            indexable.append(p["path"])
    if PREVIEW:
        print("preview built to", OUT)
        return
    urls = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc></url>" for u in indexable)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / "site.webmanifest").write_text(json.dumps({
        "name": NAME, "short_name": "Ashiri-Ola",
        "description": "Import and export, real estate development and general services.",
        "start_url": "/", "display": "browser", "theme_color": "#06101D", "background_color": "#06101D",
        "icons": [{"src": "android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2) + "\n",
        encoding="utf-8")
    (OUT / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n  Strict-Transport-Security: max-age=31536000; includeSubDomains\n"
        "\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n\n/*.png\n  Cache-Control: public, max-age=2592000\n"
        "\n/*.svg\n  Cache-Control: public, max-age=2592000\n", encoding="utf-8")
    print("built:", ", ".join(indexable), "| SITE_URL =", SITE_URL, "| FORM_ENDPOINT =", FORM_ENDPOINT or "(none, mailto fallback)")


if __name__ == "__main__":
    main()
