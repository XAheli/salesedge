# Market Data APIs

## Indian Stock Exchanges

### NSE (National Stock Exchange)

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://www.nseindia.com/api`                     |
| Auth            | No API key; session cookies required               |
| Rate Limit      | ~3 requests/second (unofficial)                    |
| Connector       | `app.connectors.market.nse`                        |

**Endpoints used:**

- `/equity-stockIndices?index=NIFTY%2050` — NIFTY 50 constituents with live prices
- `/quote-equity?symbol={symbol}` — Individual stock quote (OHLC, volume, 52-week range)
- `/historical/cm/equity?symbol={symbol}` — Historical price data (requires date range)
- `/corporates/announcements` — Board meetings, AGMs, corporate actions

**Notes:** NSE blocks requests without browser-like headers. The connector uses
a session-based approach with `httpx` to maintain cookies from an initial
`/option-chain` warm-up request.

### BSE (Bombay Stock Exchange)

| Attribute       | Details                                            |
|-----------------|----------------------------------------------------|
| Base URL        | `https://api.bseindia.com/BseIndiaAPI/api`         |
| Auth            | None                                               |
| Rate Limit      | ~5 requests/second                                 |
| Connector       | `app.connectors.market.bse`                        |

**Endpoints used:**

- `/Sensex/getSensexData` — SENSEX index data
- `/StockReachGraph/GetStockReachGraphData/{scripcode}` — Price chart data
- `/ComHeader/GetQuoteData/&scripcode={code}` — Quote details

## Broker APIs

### Zerodha (Kite Connect)

- **Docs:** [kite.trade/docs/connect](https://kite.trade/docs/connect/)
- **Auth:** OAuth2 token-based; requires `api_key` and `access_token`
- **Connector:** `app.connectors.broker.zerodha`
- **Used for:** Real-time quotes, historical candles, order book data

### Dhan

- **Docs:** [dhanhq.co/docs](https://dhanhq.co/docs/)
- **Auth:** Bearer token (`access_token` in header)
- **Connector:** `app.connectors.broker.dhan`
- **Used for:** Market depth, intraday candles, portfolio holdings

### Upstox

- **Docs:** [upstox.com/developer/api](https://upstox.com/developer/api-documentation)
- **Auth:** OAuth2 (authorization code grant)
- **Connector:** `app.connectors.broker.upstox`
- **Used for:** Historical data, market quotes, instrument master

### Angel One (SmartAPI)

- **Docs:** [smartapi.angelone.in](https://smartapi.angelone.in/docs)
- **Auth:** JWT token with TOTP-based 2FA
- **Connector:** `app.connectors.broker.angelone`
- **Used for:** Live feeds, candle data, order analytics

### Fyers

- **Docs:** [myapi.fyers.in/docs](https://myapi.fyers.in/docs)
- **Auth:** OAuth2 with app_id and app_secret
- **Connector:** `app.connectors.broker.fyers`
- **Used for:** Market depth, symbol master, historical data

### ICICI Breeze

- **Docs:** [breezeconnect.com](https://api.icicidirect.com/breezeapi/)
- **Auth:** Session token via TOTP
- **Connector:** `app.connectors.broker.icici_breeze`
- **Used for:** Historical data, live feeds, derivatives chain

## Data Refresh Cadence

| Source   | Frequency       | Cache TTL | Priority |
|----------|-----------------|-----------|----------|
| NSE      | Every 5 min     | 60s       | High     |
| BSE      | Every 5 min     | 60s       | High     |
| Brokers  | On-demand       | 30s       | Medium   |
