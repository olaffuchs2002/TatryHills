# TatryHills — instrukcja dla Claude Code

Strona inwestycji Tatry Hills (Zakopane). Publikowana przez GitHub Pages
z gałęzi `main`: https://olaffuchs2002.github.io/TatryHills/

## Czym to jest technicznie

Statyczna strona. **Nie ma etapu budowania, nie ma bazy danych, nie ma
zależności do zainstalowania.** Pliki z korzenia repo wgrane do katalogu WWW
to działająca strona.

```
index.html                 cała strona, jeden plik
support.js                 runtime mini-frameworka (nie edytować)
i18n.js                    tłumaczenia
map.html                   mapa w iframe
polityka-prywatnosci.html  polityka
assets/                    41 plików: 2 wideo, zdjęcia, logotypy
assets/rzut/               66 rzutów apartamentów (01.jpg–66.jpg)
narzedzia/                 skrypty pomocnicze (nie trafiają na stronę)
```

## NAJWAŻNIEJSZE: index.html jest plikiem generowanym

`index.html` to eksport z narzędzia projektowego (Claude Design — stąd
`<x-dc>`, `<helmet>`, `support.js` i placeholdery `{{ }}`).

Właściciel dostaje kolejne wersje jako paczki `paczka-*` i wgrywa je,
**nadpisując `index.html` w całości**. Każda ręczna poprawka w tym pliku
wtedy ginie.

Wniosek praktyczny:

- Poprawki dotyczące **zasobów** rób w `assets/` — nazwy plików bez zmian.
  To przeżywa każdy eksport.
- Poprawki w **HTML** trzeba nakładać po każdej paczce. Służy do tego
  `narzedzia/poprawki-po-paczce.py` (patrz niżej).

### Placeholdery `{{ }}` to nie błąd

`index.html` zawiera ~500 placeholderów `{{ nazwa }}`, podmienianych
w runtime przez `support.js` i inline `<script>`. To konwencja tej strony.
**Nie „naprawiać" ich przez wstawianie wartości na sztywno.**

`support.js` tylko **dopisuje** do `<head>` (`appendChild`, `prepend`) —
nigdzie nie nadpisuje `innerHTML` head ani body. Dlatego wstawki
w prawdziwym `<head>` i zaraz po `<body>` są bezpieczne.

## Procedura po otrzymaniu nowej paczki

```bash
# 1. skopiuj index.html z paczki do korzenia repo (nadpisując)
# 2. nałóż poprawki, których paczka nie zawiera:
python3 narzedzia/poprawki-po-paczce.py
# 3. sprawdź, czy skrypt nie zgłosił problemów (kod wyjścia 0)
# 4. commit i push
git add index.html && git commit -m "..." && git push origin main
```

Skrypt jest idempotentny — wielokrotne uruchomienie nic nie zdubluje.
Kod wyjścia 1 znaczy, że któregoś fragmentu nie rozpoznał i trzeba zajrzeć
ręcznie (np. paczka zmieniła treść akapitu).

### Co skrypt nakłada

1. **Google Tag Manager `GTM-TVT2BF5X`** — snippet w `<head>` i `<noscript>`
   zaraz po `<body>`.
2. **Etykieta „Wykonawca" + logo Capital Towers** w sekcji „O inwestycji",
   w miejsce akapitu o pozwoleniu na budowę i planie miejscowym.

Uwaga na logo: `assets/ct-logo-v3.png` (1600×422) to układ pionowy — wieża
u góry, napis „CAPITAL TOWERS" w dolnych 26% obrazka. Środek napisu leży
131,5 px poniżej środka pliku, więc `align-items:center` centruje pudełko
razem z wieżą i spycha napis o ~16 px niżej niż tekst obok. Dlatego blok
używa `align-items:flex-end` (odchyłka linii pisma 1 px).

## Waga strony — nie regresować

Wideo i zdjęcia zostały przekodowane (commit `fb6b109`), waga startowa
spadła z 27,18 MB do 8,96 MB. Jeśli podmieniasz te zasoby, trzymaj parametry:

| plik | parametry |
|---|---|
| `assets/hero.mp4` | 1920×1080, ~2200 kbps, **bez audio**, `+faststart` |
| `assets/apartment.mp4` | 1280×720, ~1300 kbps, **bez audio**, `+faststart` |
| zdjęcia `.jpg` | mozjpeg, q82 (rzuty q85), progressive, pełne rozdzielczości |

Oba wideo są `muted` w HTML, więc ścieżka audio to czysty balast — usuwać
przez `-an`. Narzędzia: `ffmpeg` i `mozjpeg` z Homebrew (`cjpeg` leży
w `/opt/homebrew/opt/mozjpeg/bin/`). Wbudowany w macOS `sips` **nie nadaje
się** do JPEG — produkuje pliki większe od oryginałów.

Zdjęcia mają `loading="lazy"` na 48 z 55 elementów, więc nie blokują startu.
Startową wagę robią wideo — `apartment.mp4` jest siłowo odtwarzany od
załadowania strony (`kickApt()` plus `setInterval` co 1200 ms wznawiający po
pauzie), mimo że leży daleko poniżej pierwszego ekranu. Odroczenie go do
wejścia w viewport ścięłoby start o kolejne ~3 MB, ale to poprawka w HTML,
więc do zrobienia u źródła, w narzędziu projektowym.

## Znane rzeczy, których nie naprawiono

Obie są zastane i pochodzą z eksportu, nie z ręcznych zmian:

- `{{ c.img }}` stoi w atrybucie `src`, więc przeglądarka zgłasza jeden 404
  na `/%7B%7B%20c.img%20%7D%7D` przy każdym ładowaniu, zanim skrypt podmieni
  wartość. Kosmetyczne.
- 5 linków wskazuje na `polityka-prywatnosci.dc.html`, a plik w repo nazywa
  się `polityka-prywatnosci.html` — „Polityka prywatności", „Polityka
  cookies" i „Klauzula RODO" dają 404. Naprawa to podmiana `.dc.html`
  na `.html`, ale w `index.html`, więc zniknie z następną paczką.

## Formularz kontaktowy

Wysyła AJAX-em na `https://formsubmit.co/ajax/biuro@tatry-hills.pl`.
formsubmit.co wymaga **jednorazowej aktywacji** linkiem wysłanym na ten
adres — bez tego zgłoszenia nie dochodzą. Na stronie nie ma pomiaru
konwersji; gdyby dodawać, zdarzenie trzeba odpalić po udanej odpowiedzi
`fetch`, bo wysyłka nie przeładowuje strony.
