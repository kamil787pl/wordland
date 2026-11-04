# Testy WordLand

Testy sterują prawdziwą przeglądarką (Playwright) i podstawiają atrapę Supabase, więc nie dotykają prawdziwej bazy.

```
npm install            # pobiera supabase-js do node_modules
pip install playwright && playwright install chromium
python3 tests/teacher_test.py   # panel nauczyciela, kreator, reset hasła
python3 tests/stage_test.py     # etapy rundy, checkpointy, boss
python3 tests/hard_test.py      # tryb Hard
python3 tests/mobile_test.py    # telefon: pion/poziom, przyciski dotykowe
```

Każdy test drukuje wynik jako JSON; pole `errors` powinno zawierać co najwyżej błąd ładowania czcionek Google.
Nie sprawdzają połączenia z prawdziwym Supabase ani funkcji serwerowej `reset-student-password`.
