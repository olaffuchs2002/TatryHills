#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nakłada na index.html poprawki, których NIE MA w paczkach eksportowanych
z narzędzia projektowego. Uruchamiaj po każdym wgraniu nowej paczki.

    python3 narzedzia/poprawki-po-paczce.py

Skrypt jest idempotentny — można go puścić wielokrotnie, nic nie zdubluje.
Kończy się kodem 0 gdy plik jest już kompletny albo został poprawiony,
kodem 1 gdy czegoś nie rozpoznał i wymaga ręcznej decyzji.
"""

import io
import os
import re
import sys

GTM_ID = "GTM-TVT2BF5X"

GTM_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','%s');</script>
<!-- End Google Tag Manager -->
""" % GTM_ID

GTM_BODY = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
""" % GTM_ID

# Etykieta "Wykonawca" + logo Capital Towers.
#
# align-items:flex-end, nie center — to nie jest przypadek. Plik
# assets/ct-logo-v3.png (1600x422) to układ pionowy: wieża u góry, napis
# "CAPITAL TOWERS" w dolnych 26% obrazka. Środek napisu leży 131,5 px
# poniżej środka pliku, więc align-items:center centruje całe pudełko razem
# z wieżą i spycha napis o ~16 px niżej niż tekst obok. Przy flex-end
# odchyłka linii pisma to 1 px (zmierzone na zrzucie ekranu).
BLOK_WYKONAWCA = (
    '<div style="display:flex;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-top:4px">'
    '<span style="font-size:10px;font-weight:600;letter-spacing:.28em;'
    'text-transform:uppercase;color:#7A7264;line-height:1">Wykonawca</span>'
    '<span style="width:1px;height:24px;background:#E4DDCF;align-self:center"></span>'
    '<a href="https://capitaltowers.pl" target="_blank" rel="noopener" '
    'style="display:block;transition:opacity .3s ease" style-hover="opacity:.72">'
    '<img src="assets/ct-logo-v3.png" alt="Capital Towers" '
    'style="display:block;width:170px;height:auto"></a></div>'
)

# Akapit z paczki, który zastępujemy blokiem powyżej. Dopasowanie luźne
# (dowolne atrybuty <p>), żeby przetrwało zmiany stylowania w eksporcie.
WZOR_AKAPITU = re.compile(
    r"<p[^>]*>\s*Pozwolenie na budowę jest uzyskane.*?</p>",
    re.S,
)


def popraw(html):
    """Zwraca (nowy_html, lista_opisow_zmian, lista_problemow)."""
    zmiany = []
    problemy = []

    # --- 1. GTM w <head> ---
    if GTM_ID in html and "gtm.js?id=" in html:
        zmiany.append("GTM w <head>: już był, pomijam")
    elif "</head>" in html:
        html = html.replace("</head>", GTM_HEAD + "</head>", 1)
        zmiany.append("GTM dodany do <head>")
    else:
        problemy.append("nie znalazłem </head> — GTM nie dodany")

    # --- 2. GTM noscript po <body> ---
    if "googletagmanager.com/ns.html" in html:
        zmiany.append("GTM noscript: już był, pomijam")
    elif "<body>" in html:
        # rstrip, bo po <body> w pliku i tak stoi juz znak nowej linii
        html = html.replace("<body>", "<body>\n" + GTM_BODY.rstrip("\n"), 1)
        zmiany.append("GTM noscript dodany po <body>")
    else:
        problemy.append("nie znalazłem <body> — noscript nie dodany")

    # --- 3. Akapit -> etykieta Wykonawca + logo ---
    if 'letter-spacing:.28em;text-transform:uppercase;color:#7A7264' in html:
        zmiany.append("blok Wykonawca: już był, pomijam")
    else:
        nowy, ile = WZOR_AKAPITU.subn(BLOK_WYKONAWCA, html, count=1)
        if ile == 1:
            html = nowy
            zmiany.append("akapit o pozwoleniu zamieniony na blok Wykonawca + logo")
        else:
            problemy.append(
                "nie znalazłem akapitu 'Pozwolenie na budowę jest uzyskane' "
                "ani gotowego bloku Wykonawca — sprawdź ręcznie, czy paczka "
                "nie zmieniła tego fragmentu"
            )

    return html, zmiany, problemy


def main():
    tu = os.path.dirname(os.path.abspath(__file__))
    plik = os.path.join(os.path.dirname(tu), "index.html")
    if len(sys.argv) > 1:
        plik = sys.argv[1]

    if not os.path.isfile(plik):
        print("BLAD: nie ma pliku %s" % plik)
        return 1

    przed = io.open(plik, encoding="utf-8").read()
    po, zmiany, problemy = popraw(przed)

    print("Plik: %s" % plik)
    for z in zmiany:
        print("  + %s" % z)
    for p in problemy:
        print("  ! %s" % p)

    if po != przed:
        io.open(plik, "w", encoding="utf-8").write(po)
        print("Zapisano zmiany (%d -> %d znakow)." % (len(przed), len(po)))
    else:
        print("Bez zmian — plik byl juz kompletny.")

    if problemy:
        print("\nUWAGA: sa nierozpoznane fragmenty, popraw je recznie.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
