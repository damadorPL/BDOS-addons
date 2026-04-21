# BDOS Addons

Zestaw dodatkowych skilli i skryptów rozszerzających projekt BDOS AI.

## Zawartość repo

```text
my/
  scripts/
    exclude_content_labels.py          # skrypt do wykluczeń content labels w Google Ads
    diag_script.py                     # diagnostyka konta: kampanie, reguły, rozszerzenia
    seasonal_check.py                  # sprawdzanie sezonowych haseł w reklamach i rozszerzeniach
  skills/
    codex-setup/
      SKILL.md
    gemini-setup/
      SKILL.md
```

---

## Konfiguracja Gemini i Codex (import instrukcji)

Pliki `.gemini/GEMINI.md` i `.agents/AGENTS.md` w tym repo zawierają tylko jeden wpis:

```
@./CLAUDE.md
```

Oznacza to, że Gemini CLI i Codex wczytują instrukcje projektowe bezpośrednio z `CLAUDE.md` przez mechanizm importu (`@`-imports). Nie ma potrzeby utrzymywania osobnych plików instrukcji — wystarczy edytować `CLAUDE.md`, a zmiany obowiązują we wszystkich trzech klientach: Claude Code, Gemini CLI i Codex.

---

## Skille (`my/skills/`)

Gotowe pliki `SKILL.md`, które kopiujesz do katalogu `my/skills/` w swoim projekcie BDOS AI.

### `gemini-setup`

Skill dla Gemini CLI. Jego celem jest:

- wygenerowanie lub odświeżenie `GEMINI.md` (odpowiednik `CLAUDE.md` dla Gemini)
- utworzenie i synchronizacja `.gemini/skills/` (natywne skille Gemini)
- przygotowanie `my/GEMINI.md` na prywatne instrukcje użytkownika

Używaj go, gdy chcesz, żeby Gemini CLI widział skille BDOS natywnie przez `/skills`.

Po uruchomieniu:

- skille z `bdos/data/claude/skills/` oraz `my/skills/` są synchronizowane do `.gemini/skills/<name>/SKILL.md`
- Gemini CLI wykrywa te skille natywnie, co pozwala na ich automatyczną aktywację na podstawie opisu (intent matching)
- `GEMINI.md` staje się głównym plikiem instrukcji, a Twoje prywatne preferencje są ładowane z `my/GEMINI.md`

Uruchom `gemini-setup` ponownie, gdy:

- dodasz nowy skill do `my/skills/`
- zaktualizujesz BDOS i zmienia się `bdos/data/claude/skills/`
- zmienisz `my/GEMINI.md`
- chcesz odświeżyć `GEMINI.md` po zmianach w `CLAUDE.md`

### `codex-setup`

Skill dla Codexa. Jego celem jest:

- skopiowanie lub odświeżenie skilli BDOS w `.agents/skills/`
- wygenerowanie lub odświeżenie `AGENTS.md`
- utworzenie `my/AGENTS.md`

Używaj go, gdy chcesz skonfigurować projekt BDOS pod Codexa.

Po uruchomieniu:

- skille z `bdos/data/claude/skills/` oraz `my/skills/` są synchronizowane do `.agents/skills/<name>/SKILL.md`
- Codex może wykrywać te skille natywnie z katalogu projektu, analogicznie do `.gemini/skills/`
- `AGENTS.md` pozostaje plikiem instrukcji projektowych, ale nie musi już zawierać ręcznie utrzymywanej listy skilli

Uruchom `codex-setup` ponownie, gdy:

- dodasz nowy skill do `my/skills/`
- zaktualizujesz BDOS i zmienia się `bdos/data/claude/skills/`
- zmienisz `my/AGENTS.md`
- chcesz odświeżyć `AGENTS.md` po zmianach w `CLAUDE.md`

---

## Skrypty (`my/scripts/`)

Skrypty Pythona w katalogu `my/scripts/`, uruchamiane bezpośrednio przez BDOS. Nie są skillami `SKILL.md`.

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

Po skopiowaniu przejdź do repo BDOS AI i odśwież konfigurację:

```bash
bdos update --regenerate
```

### Opcja 2 - sklonuj to repo obok BDOS AI i kopiuj z niego

Jeśli chcesz trzymać skille w osobnym repo i aktualizować je niezależnie:

```bash
git clone https://github.com/TWOJ-LOGIN/BDOS-addons.git
```

Kopię BDOS AI można nabyć na https://bdos.ai/

Następnie kopiuj wybrane skille z `BDOS-addons/my/skills/` do `BDOS-AI/my/skills/` i uruchamiaj:

```bash
cd BDOS-AI
bdos update --regenerate
```

## Aktywacja po instalacji

Samo skopiowanie plików nie wystarczy. Po dodaniu skilli do BDOS uruchom w repo projektu:

```bash
bdos update --regenerate
```

Potem użyj odpowiedniego skilla:

- dla Gemini CLI: uruchom `gemini-setup`
- dla Codexa: uruchom `codex-setup`

## Jak używać skilli

Po instalacji możesz poprosić agenta o konfigurację odpowiedniego środowiska.

Przykłady:

```text
Uruchom gemini-setup
```

```text
Uruchom codex-setup
```

Jeśli agent obsługuje jawne wywołanie przez ścieżkę, możesz wskazać plik bezpośrednio:

```text
@my/skills/gemini-setup/SKILL.md
```

```text
@my/skills/codex-setup/SKILL.md
```

## Aktualizacja

Gdy zmienisz zawartość któregoś skilla:

1. Podmień pliki w `BDOS-AI/my/skills/`
2. Uruchom `bdos update --regenerate`
3. Ponownie uruchom `gemini-setup` albo `codex-setup`, zależnie od klienta

## Uwagi

- Repo nie zawiera całego BDOS AI, tylko dodatkowe skille i skrypty
- Skille są przeznaczone do wgrania do `my/skills/` w istniejącej instancji BDOS
- `gemini-setup` i `codex-setup` są skillami konfiguracyjnymi, a nie skillami do analizy kampanii
- Skrypty w `my/` są zahardkodowane na konkretne konta — dostosuj je do swoich potrzeb przed użyciem
