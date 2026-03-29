# Data Usage Compliance Notes

Per-source terms of use, attribution requirements, and restrictions applicable to
SalesEdge's data connectors.

## Government Data (Open Government Data Platform — OGD)

| Source          | License              | Attribution Required | Commercial Use |
|-----------------|----------------------|----------------------|----------------|
| data.gov.in     | GODL v2.0            | Yes                  | Yes            |
| RBI DBIE        | Public domain        | Recommended          | Yes            |
| MOSPI           | Public domain        | Recommended          | Yes            |
| SEBI EDIFAR     | Public domain        | Required             | Yes            |
| MCA             | Public domain        | Required             | Yes            |

**GODL v2.0 key terms:**

- Data is free to copy, publish, distribute, and transmit.
- Must acknowledge the source by citing "data.gov.in" and the contributing ministry.
- Must not imply endorsement by the Government of India.
- SalesEdge embeds source attribution in the Data Provenance page (`/data`).

## Stock Exchanges

| Source | Terms Link                                             | Redistribution     | Real-Time Allowed |
|--------|-------------------------------------------------------|--------------------|-------------------|
| NSE    | [nseindia.com/regulations](https://www.nseindia.com)  | Prohibited         | Personal only     |
| BSE    | [bseindia.com/static/about](https://www.bseindia.com)| Prohibited         | Personal only     |

**Restrictions:**

- NSE and BSE data must not be redistributed to third parties.
- Delayed data (15 min+) can be displayed; real-time requires exchange vendor license.
- SalesEdge displays exchange data for internal enterprise use only. External
  redistribution requires a separate data vendor agreement with the exchanges.

## Broker APIs

| Broker       | Terms                        | Key Restriction                           |
|--------------|------------------------------|-------------------------------------------|
| Zerodha      | Kite Connect TOS             | No sub-licensing; per-user authentication |
| Dhan         | DhanHQ Developer TOS         | Rate limits enforced per token            |
| Upstox       | Upstox API TOS               | No scraping; API access only              |
| Angel One    | SmartAPI Agreement           | TOTP auth mandatory; no token sharing     |
| Fyers        | Fyers API TOS                | OAuth consent per user session             |
| ICICI Breeze | Breeze API Agreement         | Session-based; daily re-authentication    |

## Enrichment APIs

| Provider        | Plan Used   | Key Terms                                            |
|-----------------|-------------|------------------------------------------------------|
| Finnhub         | Free        | Attribution required; no resale of raw data          |
| Alpha Vantage   | Free/Premium| "Powered by Alpha Vantage" attribution recommended   |
| FMP             | Free        | 250 req/day limit; upgrade for production use        |
| CoinGecko       | Free        | Attribution required; "Powered by CoinGecko"         |
| ExchangeRate    | Free        | 100 req/month on free tier                           |
| OpenExchange    | Free        | Attribution required; 1000 req/month                 |

## SalesEdge Compliance Measures

1. **Attribution:** The Data Provenance page (`/data`) shows source names, freshness
   timestamps, and license links for every data source.
2. **Caching:** Aggressive multi-tier caching reduces API call volume well below
   free-tier limits during normal operation.
3. **No redistribution:** Raw third-party data is never exposed through SalesEdge's
   own API. Only derived scores, aggregations, and AI-generated insights are served.
4. **Audit trail:** Every ingested record stores `source_id`, `fetched_at`, and
   `quality_score` for provenance tracking.
5. **Key rotation:** API keys are stored in environment variables, never committed
   to source control. See `scripts/rotate-keys.sh` for rotation procedures.
