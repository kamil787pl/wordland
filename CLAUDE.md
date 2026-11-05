# WordLand – zasady
- Jeden plik `index.html`; testy `tests/*_test.py` (Playwright, mock Supabase) przed każdym pushem.
- Hosting: GitHub Pages (push na `main`). Odpowiedzi i interfejs po polsku.
- Ikony: cały nowy interfejs używa SVG ze sprite'a `ic('nazwa','klasa')` (kreskowe, 24px); kolory `.ok/.bad/.wait/.warn/.pt`. Emoji tylko jako treść (kategorie, medale, odznaki, grafika gier, tekst udostępniania).
- Gry używają ramki `.gstage/.gs-hud/.gs-body/.gs-foot/.gbar/.gtips` (wzór: renderConn).
- Każda nowa gra MUSI mieć (jak WordCraft, WordLinks, WordElf): punkty i rangi (progi + `rankPanel` w profilu), ranking w `wbHtml` (przełącznik gry, tydzień/ogółem/moja klasa) na stronie głównej i w profilu, tabelę wyników i RPC `<gra>_award/_my_points/_pts_board` (RLS, security definer, execute tylko dla authenticated), synchronizację punktów po zalogowaniu, panel `gpanel` w profilu, kartę z grafiką na stronie głównej, slajd w karuzeli, zakładkę w „Jak to działa”, przycisk w menu i test w `tests/`.
