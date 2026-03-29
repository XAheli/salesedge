# Enrichment APIs

External financial data sources that augment Indian market data with global context,
alternative data, and cross-asset signals.

## Finnhub

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://finnhub.io/api/v1`                        |
| Auth            | Query param `token={api_key}`                      |
| Free Tier       | 60 calls/minute, real-time US quotes               |
| Connector       | `app.connectors.enrichment.finnhub`                |

**Endpoints used:**

- `/stock/profile2?symbol={symbol}` — Company profile (industry, market cap, IPO date)
- `/company-news?symbol={symbol}&from=&to=` — Recent news articles
- `/stock/recommendation?symbol={symbol}` — Analyst consensus (buy/hold/sell)
- `/stock/peers?symbol={symbol}` — Related companies for competitive mapping

## Alpha Vantage

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://www.alphavantage.co/query`                |
| Auth            | Query param `apikey={key}`                         |
| Free Tier       | 25 calls/day (premium: 75-1200/min)               |
| Connector       | `app.connectors.enrichment.alpha_vantage`          |

**Endpoints used:**

- `function=GLOBAL_QUOTE&symbol={symbol}` — Latest quote
- `function=TIME_SERIES_DAILY&symbol={symbol}.BSE` — Indian stocks via BSE suffix
- `function=SECTOR` — US sector performance (macro signal)
- `function=NEWS_SENTIMENT&tickers={symbol}` — Sentiment analysis per ticker

## Financial Modeling Prep (FMP)

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://financialmodelingprep.com/api/v3`         |
| Auth            | Query param `apikey={key}`                         |
| Free Tier       | 250 calls/day                                      |
| Connector       | `app.connectors.enrichment.fmp`                    |

**Endpoints used:**

- `/profile/{symbol}` — Company fundamentals (P/E, EPS, market cap)
- `/income-statement/{symbol}?period=annual` — Revenue, margins, profit
- `/ratios/{symbol}` — Valuation ratios for scoring models
- `/stock-screener` — Bulk filtering for prospect discovery

## CoinGecko

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://api.coingecko.com/api/v3`                 |
| Auth            | None (free) or header `x-cg-demo-key` (demo)      |
| Free Tier       | 10-30 calls/min                                    |
| Connector       | `app.connectors.enrichment.coingecko`              |

**Endpoints used:**

- `/coins/{id}` — Token details for crypto-native prospects
- `/coins/{id}/market_chart?vs_currency=inr` — Price history in INR
- `/search/trending` — Trending tokens (signals for fintech prospects)

## FX Rate APIs

### ExchangeRate.host

- **URL:** `https://api.exchangerate.host/live`
- **Auth:** Query param `access_key`
- **Connector:** `app.connectors.enrichment.fx.exchangerate_host`
- **Used for:** USD/INR, EUR/INR for revenue normalization

### Open Exchange Rates

- **URL:** `https://openexchangerates.org/api/latest.json`
- **Auth:** Query param `app_id`
- **Connector:** `app.connectors.enrichment.fx.open_exchange`
- **Used for:** Fallback FX source, 170+ currencies

## Rate Limit Strategy

All enrichment connectors use `tenacity` retry with exponential backoff. The
`app.cache.manager` provides three-tier caching (in-memory → Redis → DB) to
minimize API calls. Cache TTLs are tuned per source based on data volatility.

| Source        | Cache TTL | Retry Policy                  |
|---------------|-----------|-------------------------------|
| Finnhub       | 5 min     | 3 retries, 2s exponential     |
| Alpha Vantage | 15 min    | 2 retries, 5s exponential     |
| FMP           | 30 min    | 3 retries, 2s exponential     |
| CoinGecko     | 5 min     | 3 retries, 3s exponential     |
| FX rates      | 1 hour    | 2 retries, 2s exponential     |
