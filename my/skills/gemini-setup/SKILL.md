---
description: Set up Gemini CLI for BDOS by syncing skills and generating GEMINI.md — runs my/scripts/sync_agents.py
---

# Setup Gemini CLI dla BDOS

Uruchamia `my/scripts/sync_agents.py`, który:
- kopiuje skille BDOS do `.gemini/skills/`
- kopiuje komendy do `.gemini/commands/`
- generuje `GEMINI.md` na bazie `CLAUDE.md`
- tworzy `my/GEMINI.md` (jeśli nie istnieje)

## Uruchom synchronizację

```python
import sys, subprocess
result = subprocess.run(
    [sys.executable, "my/scripts/sync_agents.py"],
    capture_output=True, text=True, encoding="utf-8"
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
```

## Opcje

| Flaga | Działanie |
|-------|-----------|
| _(brak)_ | synchronizuj — kopiuj tylko zmienione (wg mtime) |
| `--check` | tylko sprawdź stan, bez zmian |
| `--force` | kopiuj wszystko (ignoruj mtime) |

Żeby uruchomić z flagą, zmień wywołanie na np.:
```python
subprocess.run([sys.executable, "my/scripts/sync_agents.py", "--check"], ...)
```

## Kiedy uruchamiać

- po `bdos update` (nowe skille core)
- po dodaniu `my/skills/<name>/SKILL.md`
- po edycji `my/GEMINI.md`

## Podsumuj

Po wykonaniu powiedz użytkownikowi:

> **Gemini CLI skonfigurowany.**
>
> Skille BDOS są w `.gemini/skills/` i aktywują się automatycznie.
> Kontekst systemowy: `GEMINI.md` | Twoje instrukcje: `my/GEMINI.md`
>
> Gdy dodasz nowy skill lub zrobisz `bdos update`, uruchom ponownie `gemini-setup`.
