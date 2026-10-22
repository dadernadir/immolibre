#!/usr/bin/env python3
"""Génère les pages statiques /annonce/ID d'ImmoLibre dans un dossier de version.

Usage :
  python3 -I gen_annonces.py --site DOSSIER_VERSION --data annonces.json --version v128
  python3 -I gen_annonces.py --site DOSSIER_VERSION --fetch --version v128   (lit Supabase directement)

Ce que fait le script (dans DOSSIER_VERSION, modifié sur place) :
  1. annonce/<id>.html pour chaque annonce disponible ou en option ;
  2. sitemap-annonces.xml statique (adresses /annonce/<id>) et retrait du proxy Supabase dans netlify.toml ;
  3. retrait des adresses ?route= du sitemap.xml (leur canonical pointe vers l'accueil) ;
  4. index.html : liste des annonces qui ont une page, et canonical /annonce/<id> pour elles ;
  5. sw.js : CACHE_NAME = immolibre-<version>.
Aucune donnée privée n'est utilisée (ni téléphone, ni e-mail, ni propriétaire).
"""
import argparse, datetime, html, json, os, re, sys, urllib.request

SITE = "https://immolibre.be"
SUPABASE = "https://svjkpexgckghrtrfowtq.supabase.co"
FIELDS = ("id,type,kind,price,city,zip,rooms,surface,terrain,charges,charges_incluses,peb,"
          "coloc,animaux,meuble,dispo_date,status,pays,created_at,description,photos")
MAX_PHOTOS = 6


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def fmt_num(n):
    if n is None:
        return ""
    n = float(n)
    s = f"{n:,.0f}" if n == int(n) else f"{n:,.2f}"
    return s.replace(",", " ").replace(".", ",")


def fmt_price(a):
    p = a.get("price")
    if not p:
        return "Prix sur demande"
    return fmt_num(p) + (" €/mois" if a.get("type") == "location" else " €")


def action(a):
    return "à louer" if a.get("type") == "location" else "à vendre"


def clean_text(s):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s


def meta_desc(a):
    parts = [f"{a.get('kind') or 'Bien'} {action(a)} à {a.get('city') or 'Belgique'}"
             + (f" ({a['zip']})" if a.get("zip") else ""), fmt_price(a)]
    if a.get("surface"):
        parts.append(f"{fmt_num(a['surface'])} m²")
    if a.get("rooms"):
        parts.append(f"{a['rooms']} chambre" + ("s" if a["rooms"] > 1 else ""))
    head = " · ".join(parts) + ". "
    body = clean_text(a.get("description"))
    room = 158 - len(head)
    if room > 20 and body:
        body = body[:room].rsplit(" ", 1)[0] + "…" if len(body) > room else body
        return head + body
    return head + "Sans commission sur ImmoLibre."


def title(a):
    city = a.get("city") or "Belgique"
    return f"{a.get('kind') or 'Bien'} {action(a)} à {city} — {fmt_price(a)} | ImmoLibre"


def specs(a):
    rows = []
    rows.append(("Prix", fmt_price(a)))
    if a.get("type") == "location" and a.get("charges"):
        rows.append(("Charges", fmt_num(a["charges"]) + " €/mois" + (" (comprises)" if a.get("charges_incluses") else "")))
    if a.get("surface"):
        rows.append(("Surface habitable", f"{fmt_num(a['surface'])} m²"))
    if a.get("terrain"):
        rows.append(("Terrain", f"{fmt_num(a['terrain'])} m²"))
    if a.get("rooms"):
        rows.append(("Chambres", str(a["rooms"])))
    if a.get("peb"):
        rows.append(("PEB", str(a["peb"])))
    if a.get("dispo_date"):
        try:
            d = datetime.date.fromisoformat(str(a["dispo_date"])[:10])
            rows.append(("Disponible le", d.strftime("%d/%m/%Y")))
        except ValueError:
            pass
    extras = [lbl for key, lbl in (("meuble", "Meublé"), ("animaux", "Animaux acceptés"), ("coloc", "Colocation possible")) if a.get(key)]
    if extras:
        rows.append(("Atouts", ", ".join(extras)))
    if a.get("status") == "option":
        rows.append(("Statut", "Sous option"))
    loc = (a.get("zip") + " " if a.get("zip") else "") + (a.get("city") or "")
    if loc.strip():
        rows.append(("Localité", loc.strip()))
    return rows


def photos(a):
    out = []
    for p in (a.get("photos") or [])[:MAX_PHOTOS]:
        if isinstance(p, str) and p.startswith("https://"):
            out.append(p)
    return out


def page(a):
    aid = int(a["id"])
    url = f"{SITE}/annonce/{aid}"
    app_url = f"/?annonce={aid}"
    t = title(a)
    d = meta_desc(a)
    ph = photos(a)
    og_img = ph[0] if ph else f"{SITE}/icon-512.png"
    h1 = f"{a.get('kind') or 'Bien'} {action(a)} à {a.get('city') or 'Belgique'}"
    desc_html = "<br>".join(esc(line) for line in (a.get("description") or "").strip().splitlines()) or "Aucune description."
    specs_html = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in specs(a))
    lazy = 'loading="lazy" '
    imgs = "".join(
        f'<img src="{esc(p)}" alt="{esc(h1)} – photo {i + 1}" {"" if i == 0 else lazy}decoding="async">'
        for i, p in enumerate(ph))
    ld = {
        "@context": "https://schema.org",
        "@type": "RealEstateListing",
        "name": h1,
        "description": clean_text(a.get("description"))[:500],
        "url": url,
        "datePosted": str(a.get("created_at") or "")[:10] or None,
        "image": ph[:3] or None,
        "offers": {"@type": "Offer", "price": a.get("price") or None, "priceCurrency": "EUR",
                   "availability": "https://schema.org/InStock"},
        "contentLocation": {"@type": "Place", "address": {"@type": "PostalAddress",
                            "addressLocality": a.get("city"), "postalCode": a.get("zip"),
                            "addressCountry": a.get("pays") or "BE"}},
    }
    ld = {k: v for k, v in ld.items() if v not in (None, "", [])}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ImmoLibre", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": h1, "item": url}]}
    # "<" encodé en \u003c : aucun texte d'annonce ne peut fermer ou perturber le bloc <script> (ex. "<!--").
    ld_json = json.dumps(ld, ensure_ascii=False).replace("<", "\\u003c")
    cr_json = json.dumps(crumbs, ensure_ascii=False).replace("<", "\\u003c")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(t)}</title>
<meta name="description" content="{esc(d)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="ImmoLibre">
<meta property="og:locale" content="fr_BE">
<meta property="og:title" content="{esc(t)}">
<meta property="og:description" content="{esc(d)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{esc(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icon-192.png">
<meta name="theme-color" content="#1b5e20">
<script type="application/ld+json">{ld_json}</script>
<script type="application/ld+json">{cr_json}</script>
<style>
:root{{--g:#1b5e20;--bg:#f6f8f6;--fg:#1d2420;--mut:#5b6660;--card:#fff;--line:#e3e8e4}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--fg);line-height:1.55}}
header{{background:var(--g);color:#fff;padding:12px 16px}}
header a{{color:#fff;text-decoration:none;font-weight:800;font-size:18px}}
main{{max-width:860px;margin:0 auto;padding:16px}}
nav.crumbs{{font-size:13px;color:var(--mut);margin-bottom:8px}}
nav.crumbs a{{color:var(--g)}}
h1{{font-size:24px;margin:4px 0 6px}}
.price{{font-size:22px;font-weight:800;color:var(--g);margin:0 0 14px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(240px,100%),1fr));gap:8px;margin-bottom:16px}}
.gallery img{{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;background:#dde3de}}
.gallery img:first-child{{grid-column:1/-1;aspect-ratio:16/9}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:14px}}
dl{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(150px,100%),1fr));gap:10px;margin:0}}
dt{{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em}}
dd{{margin:0;font-weight:700}}
h2{{font-size:17px;margin:0 0 8px}}
.cta{{display:block;text-align:center;background:var(--g);color:#fff;text-decoration:none;font-weight:800;padding:14px;border-radius:12px;font-size:16px}}
.note{{font-size:13px;color:var(--mut);text-align:center;margin-top:8px}}
footer{{max-width:860px;margin:0 auto;padding:16px;font-size:13px;color:var(--mut)}}
footer a{{color:var(--g)}}
</style>
</head>
<body>
<header><a href="/">🏠 ImmoLibre</a></header>
<main>
<nav class="crumbs"><a href="/">Accueil</a> › {esc(a.get('city') or 'Belgique')} › Annonce n°{aid}</nav>
<h1>{esc(h1)}</h1>
<p class="price">{esc(fmt_price(a))}</p>
{f'<div class="gallery">{imgs}</div>' if imgs else ''}
<a class="cta" href="{app_url}">Voir l'annonce complète et contacter l'annonceur</a>
<p class="note">Annonce publiée gratuitement sur ImmoLibre, sans commission.</p>
<section class="card"><h2>Caractéristiques</h2><dl>{specs_html}</dl></section>
<section class="card"><h2>Description</h2><p>{desc_html}</p></section>
<a class="cta" href="{app_url}">Contacter l'annonceur</a>
</main>
<footer><a href="/">ImmoLibre</a> · L'immobilier belge gratuit, pour particuliers et agences · <a href="/blog/">Guides</a> · <a href="/confidentialite">Confidentialité</a></footer>
</body>
</html>
"""


def fetch_all(site_dir):
    idx = open(os.path.join(site_dir, "index.html"), encoding="utf-8").read()
    m = re.search(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", idx)
    if not m:
        sys.exit("Clé publique Supabase introuvable dans index.html")
    key = m.group(0)
    out, start = [], 0
    while True:
        url = (f"{SUPABASE}/rest/v1/annonces?select={FIELDS}&status=in.(disponible,option)"
               f"&order=id.asc&offset={start}&limit=500")
        req = urllib.request.Request(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)
        out += batch
        if len(batch) < 500:
            return out
        start += 500


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--data")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--version", required=True)
    args = ap.parse_args()
    site = args.site
    rows = fetch_all(site) if args.fetch else json.load(open(args.data, encoding="utf-8"))
    rows = [r for r in rows if r.get("status") in ("disponible", "option") and r.get("id") is not None]
    rows.sort(key=lambda r: int(r["id"]))

    # 1. pages
    adir = os.path.join(site, "annonce")
    os.makedirs(adir, exist_ok=True)
    for f in os.listdir(adir):
        if re.fullmatch(r"\d+\.html", f):
            os.remove(os.path.join(adir, f))
    for a in rows:
        with open(os.path.join(adir, f"{int(a['id'])}.html"), "w", encoding="utf-8") as fh:
            fh.write(page(a))

    # 2. sitemap-annonces.xml statique
    today = datetime.date.today().isoformat()
    items = "".join(
        f"<url><loc>{SITE}/annonce/{int(a['id'])}</loc><lastmod>{str(a.get('created_at') or today)[:10]}</lastmod></url>\n"
        for a in rows)
    with open(os.path.join(site, "sitemap-annonces.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + items + "</urlset>\n")
    toml_p = os.path.join(site, "netlify.toml")
    toml = open(toml_p, encoding="utf-8").read()
    toml2 = re.sub(r'\[\[redirects\]\]\s*\n\s*from = "/sitemap-annonces\.xml"\s*\n\s*to = "[^"]*"\s*\n\s*status = 200\s*\n(\s*force = (true|false)\s*\n)?',
                   "", toml)
    if toml2 == toml and "/sitemap-annonces.xml" in toml:
        print("ATTENTION : règle sitemap-annonces non retirée de netlify.toml", file=sys.stderr)
    open(toml_p, "w", encoding="utf-8").write(toml2)

    # 3. sitemap.xml : retirer les ?route=
    sm_p = os.path.join(site, "sitemap.xml")
    sm = open(sm_p, encoding="utf-8").read()
    sm = re.sub(r"\s*<url>\s*<loc>https://immolibre\.be/\?route=[^<]*</loc>.*?</url>", "", sm, flags=re.S)
    open(sm_p, "w", encoding="utf-8").write(sm)

    # 4. index.html : liste des pages + canonical
    idx_p = os.path.join(site, "index.html")
    idx = open(idx_p, encoding="utf-8").read()
    ids = ",".join(str(int(a["id"])) for a in rows)
    marker_re = re.compile(r"<script id=\"static-annonces\">.*?</script>\n?", re.S)
    tag = f'<script id="static-annonces">window.__STATIC_ANNONCES=new Set([{ids}]);</script>\n'
    idx = marker_re.sub("", idx)
    idx = idx.replace("</head>", tag + "</head>", 1)
    old = "const url = `https://immolibre.be/?annonce=${encodeURIComponent(l.id)}`;"
    new = ("const url = (window.__STATIC_ANNONCES && window.__STATIC_ANNONCES.has(Number(l.id)))\n"
           "    ? `https://immolibre.be/annonce/${encodeURIComponent(l.id)}`\n"
           "    : `https://immolibre.be/?annonce=${encodeURIComponent(l.id)}`;")
    if old in idx:
        idx = idx.replace(old, new, 1)
    elif "__STATIC_ANNONCES.has" not in idx:
        print("ATTENTION : canonical d'annonce non modifié dans index.html", file=sys.stderr)
    open(idx_p, "w", encoding="utf-8").write(idx)

    # 5. sw.js
    sw_p = os.path.join(site, "sw.js")
    sw = open(sw_p, encoding="utf-8").read()
    sw = re.sub(r"const CACHE_NAME = 'immolibre-v\d+';", f"const CACHE_NAME = 'immolibre-{args.version}';", sw, count=1)
    open(sw_p, "w", encoding="utf-8").write(sw)

    print(f"{len(rows)} pages générées ; sitemap-annonces.xml : {len(rows)} adresses")


if __name__ == "__main__":
    main()
