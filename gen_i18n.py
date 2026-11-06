# -*- coding: utf-8 -*-
"""Generate /en/ and /pl/ static pages from the Icelandic master pages,
and update the IS masters to use a link-based language dropdown + hreflang.
Re-run after editing the IS master .html files."""
import re, os
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
# master file -> clean path (no leading slash); index -> ''
CLEAN = {
    'index.html': '',
    'bilaforgun.html': 'bilaforgun',
    'furuflis.html': 'furuflis',
    'um-furu.html': 'um-furu',
    'umhverfisstefna.html': 'umhverfisstefna',
}
NAV_PATHS = ['/bilaforgun', '/um-furu', '/furuflis', '/umhverfisstefna']
# Translated <title> and meta description per page (en, pl). IS keeps its own.
META = {
 'index.html': {
   'en': ("Fura — Metal Recycling &amp; Scrap Metal | Hafnarfjörður &amp; Akureyri",
          "Fura buys scrap metal — iron, aluminium, copper, brass, lead and more. We collect containers in the capital area, Akureyri and nearby — over 40 years' experience since 1981."),
   'pl': ("Fura — Recykling metali i skup złomu | Hafnarfjörður i Akureyri",
          "Fura skupuje złom — żelazo, aluminium, miedź, mosiądz, ołów i inne metale. Podstawiamy kontenery w regionie stołecznym, Akureyri i okolicach — ponad 40 lat doświadczenia od 1981 roku."),
 },
 'bilaforgun.html': {
   'en': ("Scrap your car — Car recycling at Fura | 40,000 ISK until the New Year",
          "Need to scrap an old car? Fura handles car scrapping in Hafnarfjörður and Akureyri. Complete the deregistration with electronic ID and get 40,000 ISK until the New Year."),
   'pl': ("Zezłomuj auto — Złomowanie aut w Furze | 40 000 ISK do Nowego Roku",
          "Chcesz zezłomować stare auto? Fura zajmuje się złomowaniem aut w Hafnarfjörður i Akureyri. Dokończ wyrejestrowanie podpisem elektronicznym i otrzymaj 40 000 ISK do Nowego Roku."),
 },
 'furuflis.html': {
   'en': ("Furuflís — Eco-friendly wood chips for stables &amp; riding arenas | Fura",
          "Furuflís is eco-friendly wood-chip bedding from Fura — recycled from Icelandic timber, ideal for stables, riding arenas and livestock housing. Made in Iceland since 2013."),
   'pl': ("Furuflís — Ekologiczne zrębki do stajni i ujeżdżalni | Fura",
          "Furuflís to ekologiczna ściółka ze zrębków drzewnych od Fury — z islandzkiego drewna z recyklingu, idealna do stajni, ujeżdżalni i pomieszczeń dla zwierząt. Produkcja na Islandii od 2013 roku."),
 },
 'um-furu.html': {
   'en': ("About Fura — Our team and history | Fura Metal Recycling",
          "Fura has operated in Iceland since 1981. Meet our team and learn the company's history in metal recycling in the capital area and Akureyri."),
   'pl': ("O Furze — Nasz zespół i historia | Fura Recykling metali",
          "Fura działa na Islandii od 1981 roku. Poznaj nasz zespół i historię firmy zajmującej się recyklingiem metali w regionie stołecznym i Akureyri."),
 },
 'umhverfisstefna.html': {
   'en': ("Environmental Policy — Sustainable metal recycling | Fura",
          "Fura's environmental policy — carbon footprint, sustainable practices and eco-friendly solutions in Icelandic metal recycling since 1981."),
   'pl': ("Polityka środowiskowa — Zrównoważony recykling metali | Fura",
          "Polityka środowiskowa Fury — ślad węglowy, zrównoważone praktyki i ekologiczne rozwiązania w islandzkim recyklingu metali od 1981 roku."),
 },
}
LANG_NAMES = {'is': 'Íslenska', 'en': 'English', 'pl': 'Polski'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
DEN = re.compile(r"""data-en=(['"])(.*?)\1""", re.S)
DPL = re.compile(r"""data-pl=(['"])(.*?)\1""", re.S)

def url_for(lang, clean):
    base = 'https://fura.is/'
    pref = '' if lang == 'is' else lang + '/'
    return base + pref + clean  # clean '' -> homepage

def path_for(lang, clean):
    pref = '/' if lang == 'is' else '/' + lang + '/'
    return pref + clean  # e.g. /en/bilaforgun ; index -> /en/

class SpanFinder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []; self.spans = []
    def setup(self, html):
        self.html = html; self.loff = [0]
        for i, c in enumerate(html):
            if c == '\n': self.loff.append(i+1)
    def pos(self):
        l, c = self.getpos(); return self.loff[l-1] + c
    def handle_starttag(self, tag, attrs):
        p = self.pos(); raw = self.get_starttag_text() or ''; cs = p + len(raw)
        if tag in VOID: return
        en = pl = None
        m = DEN.search(raw)
        if m:
            en = m.group(2); mp = DPL.search(raw); pl = mp.group(2) if mp else None
        self.stack.append({'tag': tag, 'cs': cs, 'en': en, 'pl': pl})
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        e = self.pos()
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                ent = self.stack[i]; del self.stack[i:]
                if ent['en'] is not None:
                    self.spans.append((ent['cs'], e, ent['en'], ent['pl']))
                break

def bake(html, lang):
    f = SpanFinder(); f.setup(html); f.feed(html); f.close()
    out = html
    for cs, ce, en, pl in sorted(f.spans, key=lambda s: -s[0]):
        val = en if lang == 'en' else (pl if pl is not None else en)
        out = out[:cs] + val + out[ce:]
    return out

def dropdown_html(lang, clean):
    rows = []
    for L in ('is', 'en', 'pl'):
        active = ' active' if L == lang else ''
        rows.append(f'        <li><a class="lang-opt{active}" href="{path_for(L, clean)}" hreflang="{L}" lang="{L}">{LANG_NAMES[L]}</a></li>')
    rows = '\n'.join(rows)
    return ('    <div class="lang-dd" aria-label="Tungumál / Language">\n'
            '      <button type="button" class="lang-dd-btn" aria-haspopup="true" aria-expanded="false">\n'
            f'        <span class="lang-dd-cur">{LANG_NAMES[lang]}</span>\n'
            '        <svg class="lang-dd-caret" width="11" height="7" viewBox="0 0 11 7" fill="none" aria-hidden="true"><path d="M1 1l4.5 4.5L10 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
            '      </button>\n'
            '      <ul class="lang-dd-menu" role="menu">\n'
            f'{rows}\n'
            '      </ul>\n'
            '    </div>')

OPENCLOSE_JS = """(function () {
    const dd = document.querySelector('.lang-dd');
    if (!dd) return;
    const btn = dd.querySelector('.lang-dd-btn');
    function closeMenu() { dd.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', (e) => { e.stopPropagation(); const open = dd.classList.toggle('open'); btn.setAttribute('aria-expanded', open ? 'true' : 'false'); });
    document.addEventListener('click', (e) => { if (!dd.contains(e.target)) closeMenu(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
  })()"""

DD_BLOCK = re.compile(r'<div class="lang-dd"[\s\S]*?</ul>\s*</div>')
TOGGLE_IIFE = re.compile(r"\(function \(\) \{\s*const KEY = 'fura-lang';[\s\S]*?apply\(saved\);\s*\}\)\(\)")

def hreflang_block(clean):
    return (f'  <link rel="alternate" hreflang="is" href="{url_for("is", clean)}" />\n'
            f'  <link rel="alternate" hreflang="en" href="{url_for("en", clean)}" />\n'
            f'  <link rel="alternate" hreflang="pl" href="{url_for("pl", clean)}" />\n'
            f'  <link rel="alternate" hreflang="x-default" href="{url_for("is", clean)}" />\n')

def prefix_nav(html, pref):  # pref '/en' or '/pl'
    html = html.replace('href="/"', f'href="{pref}/"')
    for p in NAV_PATHS:
        html = html.replace(f'href="{p}"', f'href="{pref}{p}"')
    html = html.replace('href="/#', f'href="{pref}/#')
    return html

def root_assets(html):
    def ra(m):
        attr, val = m.group(1), m.group(3)
        if re.match(r'(https?:|//|/|#|mailto:|tel:|data:)', val):
            return m.group(0)
        return f'{attr}="/{val}"'
    html = re.sub(r'\b(src|href)=(")([^"]*)"', ra, html)
    def ur(m):
        q = m.group(1) or ''; val = m.group(2)
        if re.match(r'(https?:|//|/|#|data:)', val):
            return m.group(0)
        return f'url({q}/{val}{q})'
    html = re.sub(r"url\((['\"]?)([^'\")]+)\1\)", ur, html)
    return html

def apply_meta(html, meta):
    title, desc = meta
    html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1, flags=re.S)
    html = re.sub(r'(name="description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), html, count=1)
    html = re.sub(r'(property="og:title" content=")[^"]*(")', lambda m: m.group(1)+title+m.group(2), html, count=1)
    html = re.sub(r'(property="og:description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), html, count=1)
    html = re.sub(r'(name="twitter:title" content=")[^"]*(")', lambda m: m.group(1)+title+m.group(2), html, count=1)
    html = re.sub(r'(name="twitter:description" content=")[^"]*(")', lambda m: m.group(1)+desc+m.group(2), html, count=1)
    return html

def common_patches(html, lang, clean, meta=None):
    if meta:
        html = apply_meta(html, meta)
    # dropdown -> links
    html = DD_BLOCK.sub(lambda _: dropdown_html(lang, clean), html, count=1)
    # toggle IIFE -> open/close only (no-op if already converted on a re-run)
    html = TOGGLE_IIFE.sub(lambda _: OPENCLOSE_JS, html, count=1)
    # link styling for anchor lang-opt (idempotent)
    if 'a.lang-opt { text-decoration' not in html:
        html = html.replace('</style>',
            '    .lang-dd-menu a.lang-opt { text-decoration: none; }\n  </style>', 1)
    # hreflang before </head> (strip any existing first, so re-runs don't duplicate)
    html = re.sub(r'[ \t]*<link rel="alternate" hreflang="[^"]*"[^>]*>\s*\n', '', html)
    html = html.replace('</head>', hreflang_block(clean) + '</head>', 1)
    # canonical + og:url to this lang's URL
    html = re.sub(r'(rel="canonical" href=")https://fura\.is/[^"]*(")',
                  lambda m: m.group(1) + url_for(lang, clean) + m.group(2), html)
    html = re.sub(r'(property="og:url" content=")https://fura\.is/[^"]*(")',
                  lambda m: m.group(1) + url_for(lang, clean) + m.group(2), html)
    # <html lang="..">
    html = re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', html, count=1)
    return html

def main():
    for fn, clean in CLEAN.items():
        master = open(ROOT + fn, encoding='utf-8').read()
        # --- IS master: in-place patches (dropdown links + hreflang + open/close JS) ---
        is_out = common_patches(master, 'is', clean)
        open(ROOT + fn, 'w', encoding='utf-8').write(is_out)
        # --- EN / PL generated ---
        for lang in ('en', 'pl'):
            h = bake(master, lang)
            h = prefix_nav(h, '/' + lang)        # prefix nav BEFORE inserting the link dropdown
            h = root_assets(h)
            h = common_patches(h, lang, clean, meta=META[fn][lang])  # dropdown + meta last
            d = ROOT + lang
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, fn), 'w', encoding='utf-8').write(h)
        print(fn, 'OK')

if __name__ == '__main__':
    main()
