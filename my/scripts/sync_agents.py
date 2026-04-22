"""
Synchronizuje skille i komendy BDOS do Gemini CLI i Codex.

Źródła (READ ONLY):
  bdos/data/claude/skills/   — skille systemowe (core)
  my/skills/                 — skille użytkownika
  bdos/data/claude/commands/ — komendy systemowe
  my/commands/               — komendy użytkownika

Cel:
  .gemini/skills/            — Gemini CLI
  .gemini/commands/          — Gemini CLI
  .agents/skills/            — Codex
  .agents/commands/          — Codex

Generuje też:
  GEMINI.md                  — kontekst systemowy Gemini (na bazie CLAUDE.md)
  AGENTS.md                  — kontekst systemowy Codex (na bazie CLAUDE.md)

Użycie:
  .venv/Scripts/python.exe my/sync_agents.py           # synchronizuj
  .venv/Scripts/python.exe my/sync_agents.py --check   # tylko sprawdź stan
  .venv/Scripts/python.exe my/sync_agents.py --force   # kopiuj wszystko (zignoruj mtime)

Kiedy uruchamiać:
  - po bdos update (nowe skille core)
  - po dodaniu my/skills/<name>/SKILL.md
  - po dodaniu my/commands/<name>.md
  - po edycji my/GEMINI.md lub my/AGENTS.md
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

SKILL_SOURCES = [
    ROOT / "bdos" / "data" / "claude" / "skills",
    ROOT / "my" / "skills",
]
COMMAND_SOURCES = [
    ROOT / "bdos" / "data" / "claude" / "commands",
    ROOT / "my" / "commands",
]

TARGETS = {
    "gemini": {
        "skills": ROOT / ".gemini" / "skills",
        "commands": ROOT / ".gemini" / "commands",
        "config": ROOT / "GEMINI.md",
        "user_extra": ROOT / "my" / "GEMINI.md",
        "label": "Gemini CLI",
    },
    "codex": {
        "skills": ROOT / ".agents" / "skills",
        "commands": ROOT / ".agents" / "commands",
        "config": ROOT / "AGENTS.md",
        "user_extra": ROOT / "my" / "AGENTS.md",
        "label": "Codex",
    },
}

USER_GEMINI_TEMPLATE = """\
# Moje instrukcje dla Gemini CLI

<!-- Edytuj ten plik, potem uruchom:
     .venv/Scripts/python.exe my/sync_agents.py -->

## Moje preferencje

"""

USER_AGENTS_TEMPLATE = """\
# Moje instrukcje dla Codexa

<!-- Edytuj ten plik, potem uruchom:
     .venv/Scripts/python.exe my/sync_agents.py -->

## Moje preferencje

"""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def _frontmatter_field(content: str, field: str) -> str:
    if not content.startswith("---"):
        return ""
    in_front = False
    for i, line in enumerate(content.split("\n")):
        if i == 0 and line == "---":
            in_front = True
            continue
        if in_front and line == "---":
            break
        if in_front and line.startswith(f"{field}:"):
            return line[len(f"{field}:"):].strip()
    return ""


def discover_skills() -> list[dict]:
    seen: set[str] = set()
    skills = []
    for base in SKILL_SOURCES:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name in seen:
                continue
            skill_file = d / "SKILL.md"
            if not skill_file.exists():
                continue
            content = skill_file.read_text(encoding="utf-8")
            desc = _frontmatter_field(content, "description")
            skills.append({"name": d.name, "desc": desc, "src": d})
            seen.add(d.name)
    return skills


def discover_commands() -> list[dict]:
    seen: set[str] = set()
    commands = []
    for base in COMMAND_SOURCES:
        if not base.exists():
            continue
        for f in sorted(base.iterdir()):
            if not f.is_file() or f.suffix != ".md":
                continue
            if f.name.lower() == "readme.md" or f.stem in seen:
                continue
            content = f.read_text(encoding="utf-8")
            desc = _frontmatter_field(content, "description") or f.stem
            commands.append({"name": f.stem, "desc": desc, "src": f})
            seen.add(f.stem)
    return commands


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

def _needs_update(src: Path, dst: Path, force: bool) -> bool:
    if force or not dst.exists():
        return True
    return src.stat().st_mtime > dst.stat().st_mtime


def sync_skills(skills: list[dict], target_dir: Path, force: bool) -> tuple[list, list]:
    target_dir.mkdir(parents=True, exist_ok=True)
    copied, skipped = [], []
    for skill in skills:
        src_dir: Path = skill["src"]
        dst_dir = target_dir / skill["name"]
        dst_skill = dst_dir / "SKILL.md"
        src_skill = src_dir / "SKILL.md"

        if not _needs_update(src_skill, dst_skill, force):
            skipped.append(skill["name"])
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)
        for item in src_dir.iterdir():
            dst_path = dst_dir / item.name
            if item.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(item, dst_path)
            else:
                shutil.copy2(item, dst_path)

        copied.append(skill["name"])
    return copied, skipped


def sync_commands(commands: list[dict], target_dir: Path, force: bool) -> tuple[list, list]:
    if not commands:
        return [], []
    target_dir.mkdir(parents=True, exist_ok=True)
    copied, skipped = [], []
    for cmd in commands:
        src: Path = cmd["src"]
        dst = target_dir / src.name
        if not _needs_update(src, dst, force):
            skipped.append(cmd["name"])
            continue
        shutil.copy2(src, dst)
        copied.append(cmd["name"])
    return copied, skipped


# ---------------------------------------------------------------------------
# Config generation
# ---------------------------------------------------------------------------

def _skills_table(skills: list[dict]) -> str:
    rows = ["| Skill | Opis |", "|-------|------|"]
    for s in skills:
        rows.append(f"| `{s['name']}` | {s['desc']} |")
    return "\n".join(rows)


def _commands_table(commands: list[dict]) -> str:
    if not commands:
        return "_Brak zdefiniowanych komend._"
    rows = ["| Komenda | Opis |", "|---------|------|"]
    for c in commands:
        rows.append(f"| `/{c['name']}` | {c['desc']} |")
    return "\n".join(rows)


def _generate_gemini_md(skills: list[dict], commands: list[dict], user_extra: str) -> str:
    base = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    skills_block = f"""\n\n---\n
## Skille BDOS w Gemini CLI

Skille zainstalowane w `.gemini/skills/` — aktywują się automatycznie po rozpoznaniu intencji.
Lista: `/skills` lub `/skills list`

{_skills_table(skills)}

**Przykłady** (pisz naturalnie, Gemini dobiera skill):
- *„sprawdź konto X"* → `bdos-check`
- *„utwórz kampanię Search"* → `bdos-create`
- *„keyword research dla frazy Y"* → `bdos-keyword-research`

Ręczna aktywacja fallback: `@.gemini/skills/bdos-check/SKILL.md sprawdź konto X`
"""

    if commands:
        skills_block += f"""\n## Komendy BDOS\n\nDostępne w `.gemini/commands/`.\n\n{_commands_table(commands)}\n"""

    extra = user_extra.strip()
    if extra and extra not in ("# Moje instrukcje dla Gemini CLI", ""):
        skills_block += f"\n---\n\n## Dodatkowe instrukcje\n\n{extra}\n"

    return base.rstrip() + skills_block


def _generate_agents_md(skills: list[dict], commands: list[dict], user_extra: str) -> str:
    base = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    skills_block = f"""\n\n---\n
## Skills (Codex)

Skille zainstalowane w `.agents/skills/` — Codex wykrywa je natywnie.

{_skills_table(skills)}

**Trigger rules**: skill uruchamia się po dopasowaniu `description` lub przez `$skill-name`.
Po dodaniu nowego skilla lub `bdos update` uruchom: `.venv/Scripts/python.exe my/sync_agents.py`
"""

    if commands:
        skills_block += f"""\n## Komendy\n\n{_commands_table(commands)}\n"""

    extra = user_extra.strip()
    if extra and extra not in ("# Moje instrukcje dla Codexa", ""):
        skills_block += f"\n---\n\n## Dodatkowe instrukcje\n\n{extra}\n"

    return base.rstrip() + skills_block


def ensure_user_files() -> list[str]:
    created = []
    gemini_user = ROOT / "my" / "GEMINI.md"
    if not gemini_user.exists():
        gemini_user.write_text(USER_GEMINI_TEMPLATE, encoding="utf-8")
        created.append("my/GEMINI.md")

    agents_user = ROOT / "my" / "AGENTS.md"
    if not agents_user.exists():
        agents_user.write_text(USER_AGENTS_TEMPLATE, encoding="utf-8")
        created.append("my/AGENTS.md")

    return created


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    check_only = "--check" in args
    force = "--force" in args

    print("BDOS Sync — Gemini CLI + Codex")
    print("=" * 42)

    skills = discover_skills()
    commands = discover_commands()

    print(f"Skille znalezione:  {len(skills)}")
    print(f"Komendy znalezione: {len(commands)}")

    if check_only:
        print("\n[--check] tryb podglądu — bez zmian\n")
        print("Skille:")
        for s in skills:
            gem = (ROOT / ".gemini" / "skills" / s["name"] / "SKILL.md")
            ag  = (ROOT / ".agents" / "skills" / s["name"] / "SKILL.md")
            gem_ok = "OK" if gem.exists() else "BRAK"
            ag_ok  = "OK" if ag.exists() else "BRAK"
            print(f"  {s['name']:<35} gemini={gem_ok}  codex={ag_ok}")
        if commands:
            print("Komendy:")
            for c in commands:
                print(f"  /{c['name']}")
        return

    # Pliki użytkownika
    created = ensure_user_files()
    for f in created:
        print(f"  Utworzono: {f}")

    # Sync skilli
    for tool_key, cfg in TARGETS.items():
        s_copied, s_skipped = sync_skills(skills, cfg["skills"], force)
        c_copied, c_skipped = sync_commands(commands, cfg["commands"], force)

        label = cfg["label"]
        print(f"\n{label}:")
        if s_copied:
            print(f"  skills +{len(s_copied)}: {', '.join(s_copied)}")
        if s_skipped:
            print(f"  skills bez zmian: {len(s_skipped)}")
        if c_copied:
            print(f"  commands +{len(c_copied)}: {', '.join(c_copied)}")
        elif commands and not c_copied:
            print(f"  commands bez zmian: {len(c_skipped)}")

    # Generuj pliki konfiguracyjne
    user_gemini = (ROOT / "my" / "GEMINI.md").read_text(encoding="utf-8")
    (ROOT / "GEMINI.md").write_text(
        _generate_gemini_md(skills, commands, user_gemini),
        encoding="utf-8",
    )
    print("\nGEMINI.md  zaktualizowany")

    user_agents = (ROOT / "my" / "AGENTS.md").read_text(encoding="utf-8")
    (ROOT / "AGENTS.md").write_text(
        _generate_agents_md(skills, commands, user_agents),
        encoding="utf-8",
    )
    print("AGENTS.md  zaktualizowany")

    print("\nGotowe.")
    print("  Gemini CLI: .gemini/skills/ + GEMINI.md")
    print("  Codex:      .agents/skills/ + AGENTS.md")
    print("  Po edycji my/GEMINI.md lub my/AGENTS.md — uruchom ponownie")


if __name__ == "__main__":
    main()
