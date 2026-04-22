# BDOS Addons

Zestaw dodatkowych skilli i skryptów rozszerzających projekt BDOS AI.

## Zawartość repo

Pliki źródłowe (edytowane ręcznie):

```text
my/
  scripts/
    sync_agents.py              # synchronizuje skille i komendy do Gemini CLI i Codex
    exclude_content_labels.py
    diag_script.py
    seasonal_check.py
  skills/
    codex-setup/SKILL.md
    gemini-setup/SKILL.md
  GEMINI.md                  # prywatne instrukcje użytkownika dla Gemini CLI
  AGENTS.md                  # prywatne instrukcje użytkownika dla Codexa
```

Pliki generowane przez `sync_agents.py` w **katalogu głównym projektu BDOS AI** (nie edytuj ręcznie):

```text
BDOS-AI/                     ← katalog główny projektu BDOS AI
  GEMINI.md                  # CLAUDE.md + skille + my/GEMINI.md
  AGENTS.md                  # CLAUDE.md + skille + my/AGENTS.md
  .gemini/
    skills/<name>/SKILL.md
    commands/<name>.md
  .agents/
    skills/<name>/SKILL.md
    commands/<name>.md
```

Skrypt lokalizuje katalog główny projektu na podstawie własnej ścieżki (`my/scripts/sync_agents.py` → trzy poziomy wyżej = katalog projektu).

---

## Konfiguracja Gemini i Codex

Skrypt `my/scripts/sync_agents.py` synchronizuje skille i komendy BDOS do Gemini CLI i Codex oraz generuje pliki konfiguracyjne dla obu klientów.

### Co robi skrypt

Wszystkie ścieżki poniżej są względem **katalogu głównego projektu BDOS AI** (tam gdzie jest `CLAUDE.md`):

1. Zbiera skille z `bdos/data/claude/skills/` i `my/skills/`
2. Zbiera komendy z `bdos/data/claude/commands/` i `my/commands/`
3. Synchronizuje skille i komendy do `.gemini/skills/`, `.gemini/commands/`, `.agents/skills/`, `.agents/commands/`
4. Generuje `GEMINI.md` = `CLAUDE.md` + lista skilli + zawartość `my/GEMINI.md`
5. Generuje `AGENTS.md` = `CLAUDE.md` + lista skilli + zawartość `my/AGENTS.md`

### Użycie

```bash
# Synchronizuj (tylko zmienione pliki)
.venv/Scripts/python.exe my/scripts/sync_agents.py

# Sprawdź stan bez zmian
.venv/Scripts/python.exe my/scripts/sync_agents.py --check

# Wymuś kopię wszystkich plików (ignoruj mtime)
.venv/Scripts/python.exe my/scripts/sync_agents.py --force
```

### Kiedy uruchamiać

- po `bdos update` (nowe skille core)
- po dodaniu `my/skills/<name>/SKILL.md`
- po dodaniu `my/commands/<name>.md`
- po edycji `my/GEMINI.md` lub `my/AGENTS.md`

### Prywatne instrukcje użytkownika

Plik `my/GEMINI.md` i `my/AGENTS.md` to miejsce na własne preferencje i instrukcje — są dołączane na końcu wygenerowanego `GEMINI.md` / `AGENTS.md`. Skrypt tworzy je automatycznie przy pierwszym uruchomieniu.

`GEMINI.md` i `AGENTS.md` w katalogu głównym są generowane automatycznie — nie edytuj ich ręcznie, zmiany zostaną nadpisane przy kolejnym uruchomieniu skryptu.

---

## Skille (`my/skills/`)

Gotowe pliki `SKILL.md`, które kopiujesz do katalogu `my/skills/` w swoim projekcie BDOS AI.

Oba skille konfiguracyjne działają na tej samej zasadzie: zamiast wykonywać wiele kroków inline, uruchamiają `my/scripts/sync_agents.py` przez subprocess. Skrypt obsługuje Gemini CLI i Codex jednocześnie w jednym przebiegu.

### `gemini-setup/SKILL.md`

Skill dla Gemini CLI. Po aktywacji uruchamia `sync_agents.py` przez subprocess:

```python
import sys, subprocess
result = subprocess.run(
    [sys.executable, "my/scripts/sync_agents.py"],
    capture_output=True, text=True, encoding="utf-8"
)
print(result.stdout)
```

Skrypt synchronizuje skille do `.gemini/skills/`, komendy do `.gemini/commands/`, generuje `GEMINI.md` i tworzy `my/GEMINI.md` (jeśli nie istnieje).

Uruchom ponownie, gdy:

- dodasz nowy skill do `my/skills/`
- zaktualizujesz BDOS (`bdos/data/claude/skills/` się zmienia)
- zmienisz `my/GEMINI.md`

### `codex-setup/SKILL.md`

Skill dla Codexa. Po aktywacji uruchamia `sync_agents.py` przez subprocess (identyczny blok jak wyżej).

Skrypt synchronizuje skille do `.agents/skills/`, komendy do `.agents/commands/`, generuje `AGENTS.md` i tworzy `my/AGENTS.md` (jeśli nie istnieje).

Uruchom ponownie, gdy:

- dodasz nowy skill do `my/skills/`
- zaktualizujesz BDOS (`bdos/data/claude/skills/` się zmienia)
- zmienisz `my/AGENTS.md`

---

## Skrypty (`my/scripts/`)

Skrypty Pythona w katalogu `my/scripts/`, uruchamiane bezpośrednio. Nie są skillami `SKILL.md`.

### `sync_agents.py`

Synchronizuje skille i komendy BDOS do Gemini CLI i Codex. Szczegóły w sekcji [Konfiguracja Gemini i Codex](#konfiguracja-gemini-i-codex).

### `exclude_content_labels.py`

Narzędzie do automatycznego wykluczania niechcianych kategorii treści (content labels) w Google Ads na poziomie konta.

Wykluczone kategorie:
- **JUVENILE (6)** - treści dla dzieci/młodzieży
- **BRAND_SUITABILITY_GAMES_FIGHTING (19)** - gry walki
- **BRAND_SUITABILITY_GAMES_MATURE (20)** - gry mature

Wykluczenia są stosowane na poziomie `CustomerNegativeCriterion` i dotyczą wszystkich kampanii w koncie (Display, Demand Gen, YouTube).

**Użycie:**

```bash
# Podgląd bez zmian (domyślnie dry-run)
.venv/Scripts/python.exe my/scripts/exclude_content_labels.py --dry-run

# Zastosuj wykluczenia na wszystkich kontach
.venv/Scripts/python.exe my/scripts/exclude_content_labels.py

# Zastosuj wykluczenia tylko na jednym koncie
.venv/Scripts/python.exe my/scripts/exclude_content_labels.py --alias moje-konto
```

Skrypt automatycznie pomija konta, które już mają skonfigurowane te wykluczenia.

### `diag_script.py`

Skrypt diagnostyczny konta Google Ads. Sprawdza:

- aktywne kampanie z wydatkami z ostatnich 30 dni (nazwa, koszt, kliknięcia, konwersje)
- wyniki silnika reguł (`RuleEngine`) — lista problemów z podziałem na severity
- typy rozszerzeń kampanii (sitelinki, callouts)

Skrypt jest zahardkodowany na konkretne konto (`loremipsum`). Przed użyciem zmień alias konta.

**Użycie:**

```bash
.venv/Scripts/python.exe my/scripts/diag_script.py
```

### `seasonal_check.py`

Skrypt do wykrywania sezonowych haseł w treściach reklamowych. Sprawdza:

- rozszerzenia kampanii (sitelinki, callouts, promocje) pod kątem sezonowych słów kluczowych
- nagłówki i opisy reklam RSA

Szukane hasła: `black friday`, `walentynki`, `święta`, `wielkanoc`, `dzień matki`, `lato`, `zima`, `promocja`, `rabat`, `wyprzedaż`.

Skrypt jest zahardkodowany na konkretne konto (`loremipsum`). Przed użyciem zmień alias konta.

**Użycie:**

```bash
.venv/Scripts/python.exe my/scripts/seasonal_check.py
```

---

## Instalacja skilli

### Wymagania

Potrzebujesz działającej kopii projektu BDOS AI. Odwiedź https://bdos.ai/ aby nabyć kopię.

### Opcja 1 - ręcznie skopiuj skille

Skopiuj folder `my/skills/` z tego repo do katalogu `my/skills/` w swoim projekcie BDOS.

Przykład na Windows PowerShell:

```powershell
Copy-Item -Recurse -Force `
  "C:\Users\damador\Documents\Code\BDOS-addons\my\skills\*" `
  "C:\sciezka\do\BDOS-AI\my\skills\"
```

Przykład na macOS lub Linux:

```bash
cp -R /sciezka/do/BDOS-addons/my/skills/* /sciezka/do/BDOS-AI/my/skills/
```

Po skopiowaniu przejdź do repo BDOS AI i uruchom synchronizację:

```bash
.venv/Scripts/python.exe my/scripts/sync_agents.py
```

### Opcja 2 - sklonuj to repo obok BDOS AI i kopiuj z niego

Jeśli chcesz trzymać skille w osobnym repo i aktualizować je niezależnie:

```bash
git clone https://github.com/TWOJ-LOGIN/BDOS-addons.git
```

Kopię BDOS AI można nabyć na https://bdos.ai/

Następnie kopiuj wybrane skille z `BDOS-addons/my/skills/` do `BDOS-AI/my/skills/` i uruchamiaj:

```bash
.venv/Scripts/python.exe my/scripts/sync_agents.py
```

## Aktywacja po instalacji

Po skopiowaniu skilli uruchom skrypt synchronizacji w repo projektu:

```bash
.venv/Scripts/python.exe my/scripts/sync_agents.py
```

Skrypt zsynchronizuje skille do `.gemini/skills/` i `.agents/skills/` oraz wygeneruje `GEMINI.md` i `AGENTS.md`.

Alternatywnie możesz poprosić agenta Claude Code:

```text
Uruchom gemini-setup
```

```text
Uruchom codex-setup
```

## Aktualizacja

Gdy zmienisz zawartość któregoś skilla lub zaktualizujesz BDOS:

1. Podmień pliki w `BDOS-AI/my/skills/`
2. Uruchom skrypt synchronizacji:

```bash
.venv/Scripts/python.exe my/scripts/sync_agents.py
```

## Uwagi

- Repo nie zawiera całego BDOS AI, tylko dodatkowe skille i skrypty
- Skille są przeznaczone do wgrania do `my/skills/` w istniejącej instancji BDOS
- `gemini-setup` i `codex-setup` są skillami konfiguracyjnymi, a nie skillami do analizy kampanii
- Skrypty w `my/` są zahardkodowane na konkretne konta — dostosuj je do swoich potrzeb przed użyciem
