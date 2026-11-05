# WordLand – zasady
- Jeden plik `index.html`; testy `tests/*_test.py` (Playwright, mock Supabase) przed każdym pushem.
- Hosting: GitHub Pages (push na `main`). Odpowiedzi i interfejs po polsku.
- Ikony: cały nowy interfejs używa SVG ze sprite'a `ic('nazwa','klasa')` (kreskowe, 24px); kolory `.ok/.bad/.wait/.warn/.pt`. Emoji tylko jako treść (kategorie, medale, odznaki, grafika gier, tekst udostępniania).
- Gry używają ramki `.gstage/.gs-hud/.gs-body/.gs-foot/.gbar/.gtips` (wzór: renderConn).
