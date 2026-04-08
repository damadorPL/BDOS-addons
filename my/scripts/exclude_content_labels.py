"""
Wyklucz śmieciowe content labels na poziomie konta (wszystkie konta).

Wykluczone kategorie:
  JUVENILE (6)                        - treści dla dzieci/młodzieży
  BRAND_SUITABILITY_GAMES_FIGHTING (19) - gry walki
  BRAND_SUITABILITY_GAMES_MATURE (20)   - gry mature

Wykluczenia na poziomie CustomerNegativeCriterion — dotyczą całego konta
(Display, Demand Gen, YouTube).

Użycie:
  .venv/Scripts/python.exe my/exclude_content_labels.py
  .venv/Scripts/python.exe my/exclude_content_labels.py --dry-run
  .venv/Scripts/python.exe my/exclude_content_labels.py --alias moje-konto
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
from bdos.core.registry import Registry
from bdos import connect
from google.ads.googleads.v23.enums.types.content_label_type import ContentLabelTypeEnum
from google.ads.googleads.v23.resources.types.customer_negative_criterion import CustomerNegativeCriterion
from google.ads.googleads.v23.services.types.google_ads_service import MutateOperation
from google.ads.googleads.v23.services.types.customer_negative_criterion_service import CustomerNegativeCriterionOperation

ContentLabelType = ContentLabelTypeEnum.ContentLabelType

LABELS_TO_EXCLUDE = [
    ContentLabelType.JUVENILE,                          # 6  - treści dla dzieci
    ContentLabelType.BRAND_SUITABILITY_GAMES_FIGHTING,  # 19 - gry walki
    ContentLabelType.BRAND_SUITABILITY_GAMES_MATURE,    # 20 - gry mature
]

LABEL_NAMES = {
    ContentLabelType.JUVENILE: "JUVENILE (dzieci/młodzież)",
    ContentLabelType.BRAND_SUITABILITY_GAMES_FIGHTING: "GAMES_FIGHTING (gry walki)",
    ContentLabelType.BRAND_SUITABILITY_GAMES_MATURE: "GAMES_MATURE (gry mature)",
}


def run(aliases: list[str], dry_run: bool = True):
    ok, skipped, errors = [], [], []

    for alias in aliases:
        try:
            ctx = connect(alias)
            cid = ctx.customer_id

            existing = ctx.client.query(
                "SELECT customer_negative_criterion.content_label.type "
                "FROM customer_negative_criterion "
                "WHERE customer_negative_criterion.type = 'CONTENT_LABEL'",
                cid,
            )
            existing_vals = set()
            for r in existing:
                v = r.get("type")
                if v is not None:
                    existing_vals.add(int(v) if not isinstance(v, int) else v)

            to_add = [l for l in LABELS_TO_EXCLUDE if l.value not in existing_vals]

            if not to_add:
                skipped.append(alias)
                continue

            label_desc = ", ".join(LABEL_NAMES[l] for l in to_add)
            if dry_run:
                print(f"  [DRY RUN] {alias}: dodać {label_desc}")
                ok.append(alias)
                continue

            ops = []
            for label in to_add:
                criterion = CustomerNegativeCriterion()
                criterion.content_label.type_ = label.value
                ops.append(MutateOperation(
                    customer_negative_criterion_operation=CustomerNegativeCriterionOperation(
                        create=criterion
                    )
                ))

            ctx.client.mutate(ops, dry_run=False)
            print(f"  OK {alias}: dodano {label_desc}")
            ok.append(alias)
        except Exception as e:
            print(f"  BLAD {alias}: {e}")
            errors.append((alias, str(e)))

    print()
    print(f"{'[DRY RUN] ' if dry_run else ''}Wykonano: {len(ok)}/{len(aliases)}")
    print(f"Pominięto (już miały): {len(skipped)}")
    print(f"Błędy: {len(errors)}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wyklucz śmieciowe content labels")
    parser.add_argument("--dry-run", action="store_true", help="Tylko podgląd, bez zmian")
    parser.add_argument("--alias", help="Jedno konto (domyślnie: wszystkie)")
    args = parser.parse_args()

    reg = Registry()
    aliases = [args.alias] if args.alias else reg.aliases()

    print(f"Konta: {len(aliases)} | dry_run={args.dry_run}")
    print(f"Wykluczenia: {', '.join(LABEL_NAMES.values())}")
    print()

    run(aliases, dry_run=args.dry_run)
