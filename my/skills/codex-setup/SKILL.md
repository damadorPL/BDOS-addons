---
description: Setup Codex for BDOS by installing BDOS skills into .agents/skills and generating AGENTS.md — runs my/scripts/myskills.py
---

# Setup Codex dla BDOS

Uruchamia `my/scripts/myskills.py`, który:
- kopiuje skille BDOS do `.agents/skills/`
- kopiuje komendy do `.agents/commands/`
- generuje `AGENTS.md` na bazie `CLAUDE.md`
- tworzy `my/AGENTS.md` (jeśli nie istnieje)

## Uruchom synchronizację

```python
import sys, subprocess
result = subprocess.run(
    [sys.executable, "my/scripts/myskills.py"],
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
subprocess.run([sys.executable, "my/scripts/myskills.py", "--check"], ...)
```

## Kiedy uruchamiać

- po `bdos update` (nowe skille core)
- po dodaniu `my/skills/<name>/SKILL.md`
- po edycji `my/AGENTS.md`

## Podsumuj

Po wykonaniu powiedz użytkownikowi:

> **Codex skonfigurowany.**
>
> Skille BDOS są w `.agents/skills/` — Codex wykrywa je natywnie z `.agents/skills/**/SKILL.md`.
> Instrukcje projektu: `AGENTS.md` | Twoje ustawienia: `my/AGENTS.md`
>
> Gdy dodasz nowy skill lub zrobisz `bdos update`, uruchom ponownie `codex-setup`.
