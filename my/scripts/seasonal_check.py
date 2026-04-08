
import sys
from bdos import connect
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ctx = connect('novdom.pl-aktualne')

seasonal_keywords = ['black friday', 'walentynki', 'święta', 'wielkanoc', 'dzień matki', 'lato', 'zima', 'promocja', 'rabat', 'wyprzedaż']

# 1. Sprawdzenie rozszerzeń
print("--- ANALIZA TREŚCI ROZSZERZEŃ ---")
rows = ctx.client.query("""
SELECT
    campaign.name,
    asset.type,
    asset.sitelink_asset.link_text,
    asset.callout_asset.callout_text,
    asset.promotion_asset.promotion_target,
    asset.promotion_asset.redemption_end_date
FROM campaign_asset
WHERE campaign.status = 'ENABLED'
    AND campaign_asset.status = 'ENABLED'
""", ctx.customer_id)

found_seasonal = []
for r in rows:
    text = r.get('sitelink_asset_link_text') or r.get('callout_asset_callout_text') or r.get('promotion_asset_promotion_target') or ''
    if any(kw in text.lower() for kw in seasonal_keywords):
        found_seasonal.append(f"[{r.get('campaign_name')}] {text}")

if found_seasonal:
    for s in set(found_seasonal): print(f"- {s}")
else:
    print("Brak sezonowych haseł w rozszerzeniach.")

# 2. Sprawdzenie reklam RSA
print("\n--- ANALIZA TREŚCI REKLAM (RSA) ---")
rsa_rows = ctx.client.query("""
SELECT
    campaign.name,
    ad_group_ad.ad.responsive_search_ad.headlines,
    ad_group_ad.ad.responsive_search_ad.descriptions
FROM ad_group_ad
WHERE campaign.status = 'ENABLED'
    AND ad_group_ad.status = 'ENABLED'
    AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
""", ctx.customer_id)

found_ads = []
for r in rsa_rows:
    cname = r.get('campaign_name')
    headlines = r.get('ad_group_ad_ad_responsive_search_ad_headlines', [])
    descriptions = r.get('ad_group_ad_ad_responsive_search_ad_descriptions', [])
    
    all_texts = []
    for h in headlines: all_texts.append(h.get('text', ''))
    for d in descriptions: all_texts.append(d.get('text', ''))
    
    for txt in all_texts:
        if any(kw in txt.lower() for kw in seasonal_keywords):
            found_ads.append(f"[{cname}] {txt}")

if found_ads:
    for a in set(found_ads)[:20]: print(f"- {a}")
else:
    print("Brak sezonowych haseł w reklamach.")
