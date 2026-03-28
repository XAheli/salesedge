# Data Source Catalog (25 APIs)

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Government APIs](government-apis.md) · [Connector matrix](connector-matrix.md)

---

This catalog lists the **25** external integration surfaces SalesEdge targets: government and statistical sources, Indian market infrastructure, broker APIs, enrichment feeds, and CRM placeholders. **Status** reflects the repository as of v1.0.0: *implemented* connectors live under `backend/app/connectors/`; *stub* means configuration or contracts exist without a full connector module.

## Master table

| # | API name | Tier | Base URL (typical) | Auth | Rate limits (indicative) | Key endpoints / operations | Business use cases | Status |
|---|----------|------|-------------------|------|--------------------------|----------------------------|-------------------|--------|
| 1 | **OGD India (data.gov.in)** | 1 | `https://api.data.gov.in` | API key query `api-key` | Per key / plan on portal | `/resource`, search, catalog discovery | Macro context, sector stats, compliance datasets | **Implemented** (`ogd_india`) |
| 2 | **RBI DBIE** | 1 | RBI DBIE host (HTML/CSV) | Public read; respect robots | Throttle + cache | Series download, table scrape | Interest rates, reserves, credit growth | **Implemented** (`rbi_dbie`) |
| 3 | **MOSPI** | 1 | data.gov.in resources + MOSPI | OGD key where applicable | As per dataset | National accounts, CPI, IIP proxies | Macro context, forecasting inputs | **Implemented** (`mospi`) |
| 4 | **MCA** | 1 | MCA portals / filings | User/session varies | Strict throttling | Company master, charges, filings | Prospect firmographics, risk signals | **Implemented** (`mca`) |
| 5 | **SEBI** | 1 | SEBI disclosures host | Public | Throttle | Circulars, filings, mutual fund data | Regulatory context, listed entities | **Implemented** (`sebi`) |
| 6 | **NSE** | 2 | NSE India endpoints | As per product | Aggressive throttling required | Indices, equity metadata | Market context, listed prospect flags | **Implemented** (`nse`) |
| 7 | **BSE** | 2 | BSE endpoints | As per product | Throttle | Security lists, bhav copy patterns | Market context | **Implemented** (`bse`) |
| 8 | **Zerodha Kite Connect** | 2 | `https://api.kite.trade` | API key + secret + token | Per broker policy | Quotes, orders (if enabled) | Live prices, paper trading | **Implemented** (`zerodha`) |
| 9 | **Upstox** | 2 | Upstox API base | OAuth2 | Per broker policy | Market data, account | Brokerage-integrated context | **Implemented** (`upstox`) |
| 10 | **Angel One SmartAPI** | 2 | Angel API host | API key + client | Per broker policy | Market data | Trading-adjacent enrichment | **Implemented** (`angelone`) |
| 11 | **FYERS** | 2 | FYERS API host | App ID + secret | Per broker policy | Quotes | Market hours signals | **Implemented** (`fyers`) |
| 12 | **ICICI Breeze** | 2 | ICICI API host | API key pair | Per bank policy | Market data | Enterprise broker integration | **Implemented** (`icici_breeze`) |
| 13 | **Dhan** | 2 | Dhan API host | Access token | Per broker policy | Market data | Retail broker channel | **Implemented** (`dhan`) |
| 14 | **Finnhub** | 3 | `https://finnhub.io/api/v1` | Token header | Free tier caps | Quote, profile, news | Competitive intel, global comps | **Implemented** (`finnhub`) |
| 15 | **Alpha Vantage** | 3 | `https://www.alphavantage.co/query` | API key param | ~5 calls/min free | `TIME_SERIES`, fundamentals | Enrichment, backtests | **Implemented** (`alpha_vantage`) |
| 16 | **Polygon.io** | 3 | `https://api.polygon.io` | API key | Tiered | Aggregates, ticks | High-frequency context | **Stub** (`SE_POLYGON_API_KEY` only) |
| 17 | **Financial Modeling Prep** | 3 | `https://financialmodelingprep.com/api/v3` | API key | Tiered | Financial statements, key metrics | Prospect/deal financial health | **Implemented** (`fmp`) |
| 18 | **CoinGecko** | 3 | `https://api.coingecko.com/api/v3` | Optional Pro key | Rate limits by tier | `/simple/price`, markets | Crypto treasury / fintech prospects | **Implemented** (`coingecko`) |
| 19 | **Open Exchange Rates** | 3 | `https://openexchangerates.org/api` | App ID | Monthly quota | Latest / historical FX | INR normalization | **Implemented** (`open_exchange`) |
| 20 | **ExchangeRate.host** | 3 | `https://api.exchangerate.host` | Optional key | Fair-use | `/latest`, `/timeseries` | FX fallback | **Implemented** (`exchangerate_host`) |
| 21 | **Twelve Data** | 3 | Twelve Data REST | API key | Tiered | Time series | Enrichment alt to AV | **Stub** (`SE_TWELVE_DATA_API_KEY`) |
| 22 | **StockInsights / Delta-class crypto** | 3 | Provider-specific | Token / key | Tiered | Derivatives metrics | Crypto-heavy accounts | **Stub** (keys in `Settings`) |
| 23 | **HubSpot** | 4 | `https://api.hubapi.com` | Private app / OAuth | Per portal | Contacts, deals | CRM sync | **Stub** (`SE_HUBSPOT_API_KEY`) |
| 24 | **Salesforce** | 4 | Instance URL | OAuth JWT / web | Per org | SOQL, objects | CRM system of record | **Stub** (client id/secret settings) |
| 25 | **RSS / public business feeds** | 3 | Feed URLs | None | Be polite | Poll + parse | News, competitive chatter | **Implemented** (`rss_business`) |

> **Note:** `simulated_crm` provides deterministic CRM data for demos and tests and is not counted toward the 25 external APIs above.

---

## Government APIs (summary)

See [government-apis.md](government-apis.md) for operational detail.

| API | Role |
|-----|------|
| **OGD India** | Primary discovery and download path for ministry datasets |
| **RBI DBIE** | Official monetary and banking statistics |
| **MOSPI** | National statistics for GDP/CPI/IIP-style features |
| **MCA** | Corporate registry-style signals |
| **SEBI** | Market regulator disclosures |

## Market APIs (summary)

| API | Role |
|-----|------|
| **NSE / BSE** | Indian listing and market context |
| **Broker APIs** | User-authorized quotes; gated by `FeatureFlags` (e.g. `enable_nse_live_data`) |

## Enrichment APIs (summary)

| API | Role |
|-----|------|
| **Finnhub, Alpha Vantage, FMP** | Global equity fundamentals and news |
| **Polygon, Twelve Data** | Planned expansion / higher cadence (stub) |
| **CoinGecko, FX providers** | Crypto and currency normalization to INR |

---

[← Documentation index](../README.md)
