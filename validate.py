"""Offline checks for the built site. Run after build.py:  python3 build/validate.py"""
import base64, hashlib, json, pathlib, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors, notes = [], []


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0; self.ids = []; self.links = []; self.imgs = []; self.srcs = []
        self.labels_for = set(); self.fields = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "h1": self.h1 += 1
        if "id" in a: self.ids.append(a["id"])
        if tag == "a" and "href" in a: self.links.append(a["href"])
        if tag == "link" and "href" in a: self.srcs.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
            self.srcs.append(a.get("src", ""))
        if tag == "label" and "for" in a: self.labels_for.add(a["for"])
        # checkboxes are wrapped inside their <label> (implicit association), so only check other fields
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "checkbox", "radio") and a.get("name") != "company_website":
            self.fields.append(a.get("id"))


pages = sorted(ROOT.glob("*.html"))
all_ids = {}
for f in pages:
    t = f.read_text(encoding="utf-8")
    p = P(); p.feed(t)
    all_ids[f.name] = set(p.ids)
for f in pages:
    t = f.read_text(encoding="utf-8")
    p = P(); p.feed(t)
    if p.h1 != 1: errors.append(f"{f.name}: expected 1 h1, found {p.h1}")
    if len(p.ids) != len(set(p.ids)): errors.append(f"{f.name}: duplicate ids")
    for img in p.imgs:
        if not img.get("alt"): errors.append(f"{f.name}: img missing alt")
    for fid in p.fields:
        if fid not in p.labels_for: errors.append(f"{f.name}: field {fid} has no label[for]")
    for h in p.links + p.srcs:
        if h.startswith(("http", "mailto:", "tel:")): continue
        base, _, frag = h.partition("#")
        target = base or f.name
        if not (ROOT / target).exists(): errors.append(f"{f.name}: broken link/asset {h}")
        elif frag and frag not in all_ids.get(target, set()): errors.append(f"{f.name}: missing anchor {h}")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(m.group(1))
        except Exception as e: errors.append(f"{f.name}: invalid JSON-LD ({e})")
    style = re.search(r"<style>(.*?)</style>", t, re.S).group(1)
    script = re.search(r"<script>(.*?)</script>", t, re.S).group(1)
    for body in (style, script):
        h = "sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
        if h not in t.split("Content-Security-Policy")[1].split(">")[0]: errors.append(f"{f.name}: CSP hash mismatch")
    can = re.search(r'rel="canonical" href="([^"]+)"', t).group(1)
    if not can.startswith("https://"): errors.append(f"{f.name}: canonical not absolute")
    title = re.search(r"<title>(.*?)</title>", t).group(1)
    desc = re.search(r'name="description" content="([^"]*)"', t).group(1)
    notes.append(f"{f.name}: title {len(title)} chars, description {len(desc)} chars, canonical {can}")
    # JS syntax
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(script)
    r = subprocess.run(["node", "--check", tf.name], capture_output=True, text=True)
    if r.returncode: errors.append(f"{f.name}: JS syntax error {r.stderr[:200]}")

titles = [re.search(r"<title>(.*?)</title>", f.read_text()).group(1) for f in pages]
if len(set(titles)) != len(titles): errors.append("duplicate titles")

try:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    notes.append(f"sitemap.xml: valid XML, {len(root)} URLs")
except Exception as e:
    errors.append(f"sitemap.xml invalid: {e}")
for n in ["favicon.ico", "favicon.svg", "favicon-16x16.png", "favicon-32x32.png", "apple-touch-icon.png",
          "android-chrome-192x192.png", "android-chrome-512x512.png", "og-image.png", "site.webmanifest", "robots.txt"]:
    if not (ROOT / n).exists(): errors.append(f"missing {n}")
if "YOUR-DOMAIN.example" in (ROOT / "sitemap.xml").read_text():
    notes.append("WARNING: SITE_URL is still the placeholder; rebuild with SITE_URL before deploying")

print("\n".join(notes))
print("\nERRORS:" if errors else "\nNo errors found.")
print("\n".join(errors))
sys.exit(1 if errors else 0)
