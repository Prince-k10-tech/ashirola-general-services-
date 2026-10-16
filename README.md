# Ashiri-Ola General Services Ltd — website

Static multi-page site (HTML, CSS and JS embedded in each page; no framework, no external requests).
Pages: `index.html`, `about.html`, `services.html`, `contact.html`, `privacy.html`, `404.html`.

> **Why this is not the Lovable codebase.** The original Lovable project's source was not accessible
> (no GitHub repo connected), so this site was rebuilt from the live site's content and structure.
> Wording was preserved where it could be verified; unverifiable claims were softened (see "Owner to confirm").

## Rebuild after editing content

Content lives in `build/build.py`. Then:

```
python3 build/make_assets.py                 # only if you change the brand mark (needs Pillow)
SITE_URL=https://www.YOUR-REAL-DOMAIN FORM_ENDPOINT=https://... python3 build/build.py
python3 build/validate.py                    # offline checks
```

`SITE_URL` drives canonical URLs, Open Graph, JSON-LD, `sitemap.xml` and `robots.txt`.
The default is now `https://ashiriolageneralservices.com.ng` (no `www`), so a plain `python3 build/build.py` uses it. If you later prefer the `www` version, set `SITE_URL` and rebuild. Whichever you choose, redirect the other one to it at your host.
No secrets belong in either variable.

## Optional photos

Drop these into `assets/` and rebuild; they appear automatically (with width/height, lazy loading, hero eager,
and a slow zoom on the hero):
`hero-port.jpg` (home hero, landscape about 1600 px wide), `haulage.jpg`, `real-estate.jpg`.
The three photos currently in `assets/` were supplied by the owner (they look AI-generated, with garbled lettering on the containers, ship and number plates; replace them with real photographs when available). Without them the home hero shows an animated port illustration and the other spots show text panels.
The original three images are on the Lovable site (`/assets/hero-port-*.jpg`, `haulage-*.jpg`, `real-estate-*.jpg`).
Save them from the browser, rename, and compress to roughly 200 KB or less each. Only use photos you have the right to use.

## Fonts

Cormorant Garamond and Jost (SIL Open Font License, licences in `fonts/`) are self-hosted, so no visitor data goes to Google.

## Enquiry form

- **Without `FORM_ENDPOINT`:** the form validates, then opens the visitor's email app with the enquiry filled in,
  and tells them it has NOT been sent until they press Send. It never claims delivery.
- **With `FORM_ENDPOINT`:** it POSTs JSON and shows success only when the endpoint returns an OK status.
  Works with Formspree, Getform, or your own Supabase Edge Function / serverless function that emails the company.
  Keep API keys and SMTP credentials server-side only. A bot honeypot field is included.
- **The form adapts to the enquiry type.** The visitor chooses Import & Export, Real Estate, General Services or
  Something else, and only the matching questions appear (and are validated or sent).
- JSON fields always sent: `enquiry_type, name, phone, email, details`. Plus, by type:
  Import & Export: `direction, origin, destination, goods, cargo_size, services[]`;
  Real estate: `re_interest, re_property_type, re_timeline, re_location, re_budget`;
  General services: `gs_service, gs_scope, gs_location, gs_timeline`.
- Clearing & forwarding is part of Import & Export everywhere (a checkbox under that type, not a separate type).

## Navigation

A "Menu" button is shown on every screen size and opens a full-screen menu. Each link goes to its own page
(`index.html`, `about.html`, `services.html`, `contact.html`); nothing is a single scrolling page.

## Brand assets

`favicon.ico` (16/32/48), `favicon.svg`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png` (180),
`android-chrome-192x192.png`, `android-chrome-512x512.png`, `site.webmanifest`, `og-image.png` (1200×630).
The mark is a simplified "A" monogram in navy and gold. **The official logo file was not available.**
If the company has one, send it so the favicon and header mark can be matched exactly.

## Owner to confirm

1. Production domain (and whether `www` or the bare domain is preferred).
2. Official logo file and exact brand colours (navy `#0B2A4A` and gold `#C8963E` were chosen as a placeholder palette).
3. Full street address in Ikeja, if you want it shown, added to structured data, or a Google Map embedded.
4. Which shipping capabilities are genuinely offered (sea/air freight, haulage, warehousing). The site names only what the original site said: sourcing, documentation, port clearing, customs processing, haulage.
5. Wording changed from the original because it could not be verified: "Nationwide delivery", "Trusted trade routes and partners across global markets", "Clear timelines... delivery as promised".
6. CAC registration (RC) number and any customs/clearing licences. Add them only if you want them displayed.
7. Business opening hours, social profiles, and any real client names, testimonials or years in business (none are shown now).
8. Privacy notice: retention wording and the contact for data requests should be reviewed by the owner or a lawyer.
9. Where enquiries should go (form endpoint) and whether email or WhatsApp should be the primary channel. No WhatsApp number was added because none was verified.

## Production deployment checklist

- [ ] Choose host (Netlify, Cloudflare Pages, Vercel static, cPanel, GitHub Pages) and upload the folder contents (not `build/`).
- [ ] Rebuild with the real `SITE_URL` (and `FORM_ENDPOINT`), then run `python3 build/validate.py`.
- [ ] Connect the custom domain and enable HTTPS; redirect `http` to `https` and one of `www`/non-`www` to the other.
- [ ] Confirm `/404.html` is served for unknown URLs with a 404 status (host setting).
- [ ] `_headers` works on Netlify/Cloudflare Pages. On other hosts, set the same headers in server config.
- [ ] Open `https://DOMAIN/favicon.ico`, `/og-image.png`, `/robots.txt`, `/sitemap.xml` and confirm each loads.
- [ ] Test the form from a phone and confirm the message actually arrives.
- [ ] Preview social sharing (WhatsApp, Facebook Sharing Debugger, LinkedIn Post Inspector).
- [ ] Run PageSpeed Insights on mobile and fix anything reported.
- [ ] If the Lovable URL stays live, add a redirect to the new domain so it does not compete in search.

## Google Search Console

1. Deploy to the production domain over HTTPS.
2. In [Search Console](https://search.google.com/search-console), choose **Add property → Domain** and enter the domain.
3. Verify using the DNS TXT record Google gives you, added at your domain registrar. (Do not paste tokens into this repo.)
4. Open **Sitemaps** and submit `https://YOUR-DOMAIN/sitemap.xml`.
5. Use **URL Inspection** on the homepage and each main page, then **Request indexing**.
6. Monitor **Pages** (indexing) and **Page experience / Core Web Vitals** over the following weeks, and fix reported issues.
7. Create or claim a Google Business Profile separately; keep name, address and phone identical to the website.

Nothing here has been verified, submitted or indexed. Those steps need your Google account and domain access.

## What has been tested

Offline only (`build/validate.py` plus a jsdom form test): one H1 per page, unique titles, alt text, labels, internal
links and anchors, JSON-LD parses, sitemap is valid XML, CSP hashes match, JS syntax, the adaptive form (panel
switching, per-type validation, mailto / endpoint success / endpoint failure / honeypot) and the menu open/close.
**Not tested:** how the animations and layout actually look on devices (only the Claude preview, viewed by the owner),
Lighthouse/Core Web Vitals, deployed HTTPS behaviour, Rich Results validation, real email delivery.
