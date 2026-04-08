
import sys
from datetime import date
from collections import defaultdict
from bdos import connect
from bdos.engine.rule_engine import RuleEngine

sys.stdout.reconfigure(encoding='utf-8')
ctx = connect('novdom.pl-aktualne')

# 1. Sprawdzenie aktywności (Kampanie z wydatkami 30 dni)
print("--- AKTYWNE KAMPANIE ---")
res = ctx.engine.execute(entity='campaigns', fields=['name', 'status', 'cost', 'clicks', 'conversions'], filters=['cost > 0'], days=30)
print(f"Liczba kampanii z wydatkami: {len(res.data)}")
for r in res.data[:10]:
    print(f"- {r['name']}: Koszt {r['cost']:.2f}, Kliknięcia {r['clicks']}, Konwersje {r['conversions']}")

# 2. Silnik reguł (30 dni)
print("\n--- DIAGNOSTYKA (RuleEngine) ---")
rule_engine = RuleEngine(engine=ctx.engine)
try:
    report = rule_engine.run(ctx.account, days=30)
    print(f"Znaleziono problemów: {len(report.findings)}")
    for f in report.findings:
        print(f"[{f.severity.name}] {f.title}: {f.message}")
except Exception as e:
    print(f"Błąd RuleEngine: {e}")

# 3. Rozszerzenia (Kampanie)
print("\n--- ROZSZERZENIA ---")
try:
    rows = ctx.client.query("""
    SELECT
        campaign.name,
        asset.type,
        asset.sitelink_asset.link_text,
        asset.callout_asset.callout_text
    FROM campaign_asset
    WHERE campaign.status = 'ENABLED'
        AND campaign_asset.status = 'ENABLED'
    """, ctx.customer_id)
    print(f"Pobrano rekordów rozszerzeń: {len(rows)}")
    ext_types = defaultdict(int)
    for r in rows:
        atype_int = r.get('asset_type', 0)
        ext_types[atype_int] += 1
    print(f"Typy rozszerzeń (int): {dict(ext_types)}")
except Exception as e:
    print(f"Błąd przy rozszerzeniach: {e}")
