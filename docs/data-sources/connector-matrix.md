# Connector × Use-Case Matrix

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Catalog](catalog.md)

---

**Legend:** ● primary · ◐ secondary · ○ minimal / indirect  

**Columns:** prospecting · risk_detection · retention · competitive_intel · macro_context  

| API / endpoint family | prospecting | risk_detection | retention | competitive_intel | macro_context |
|----------------------|-------------|----------------|-----------|-------------------|---------------|
| OGD `/resource` (sector stats) | ● | ◐ | ○ | ○ | ● |
| OGD search / catalog | ● | ○ | ○ | ◐ | ● |
| RBI DBIE (rates, credit) | ◐ | ● | ● | ○ | ● |
| MOSPI (GDP/CPI/IIP) | ◐ | ● | ● | ○ | ● |
| MCA (company master) | ● | ● | ○ | ◐ | ○ |
| SEBI disclosures | ◐ | ● | ○ | ● | ◐ |
| NSE / BSE (listings, indices) | ● | ● | ◐ | ● | ● |
| Broker quotes (Zerodha, Upstox, …) | ◐ | ● | ○ | ◐ | ● |
| Finnhub (profile, news) | ● | ◐ | ◐ | ● | ◐ |
| Alpha Vantage (fundamentals) | ● | ● | ◐ | ◐ | ○ |
| FMP (financial statements) | ● | ● | ● | ◐ | ○ |
| Polygon / Twelve Data (stub) | ◐ | ◐ | ○ | ◐ | ● |
| CoinGecko | ● | ◐ | ○ | ◐ | ○ |
| Open Exchange / ExchangeRate.host | ○ | ◐ | ◐ | ○ | ● |
| RSS business feeds | ◐ | ◐ | ◐ | ● | ○ |
| HubSpot / Salesforce (stub) | ● | ● | ● | ○ | ○ |

### How to read this matrix

- **Prospecting** — ICP fit, industry/geo/revenue signals.  
- **Risk_detection** — Deal health, financial stress, regulatory red flags.  
- **Retention** — Usage/payment/support proxies combined with macro stress.  
- **Competitive_intel** — News, mentions, battlecards.  
- **Macro_context** — FX, rates, indices for normalization and headwinds.

For automation, run `make connector-matrix` when `backend/scripts/build-connector-matrix.py` is present to regenerate an artifact from connector `get_business_use_cases()` metadata.

---

[← Documentation index](../README.md)
