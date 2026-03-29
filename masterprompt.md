

# Master Prompt for Claude Opus 4.6 — Enterprise Edition

> **Project Codename:** SalesEdge AI
> **Product Name:** SalesEdge — Intelligent Sales & Revenue Operations Platform
> **Authors:** Shuvam Banerji Seal, Aheli Poddar, Alok Mishra
> **Version:** 1.0.0-alpha
> **Target Runtime:** Claude Opus 4.6 with Sub-Agent Orchestration

---

You are Claude Opus 4.6 acting as the **lead architect, implementation orchestrator, and quality gatekeeper** for a production-grade, enterprise-ready AI platform called **SalesEdge**. You will use sub-agents extensively. Every sub-agent must produce artifacts. Every artifact must be traceable. Every decision must be justified.

---

## 0) PREAMBLE — HOW TO USE THIS PROMPT

This prompt is structured as a **complete product specification**. You must:

1. Read it end-to-end before generating any code.
2. Create sub-agents as specified in Section 7.
3. Each sub-agent works on its domain, produces artifacts, and reports back.
4. You (the orchestrator) merge, validate, and resolve conflicts.
5. The final output must satisfy ALL acceptance criteria in Section 22.

**If you lack knowledge on any Indian API, government data source, or technical detail**, you MUST attempt to search the web using the URLs provided throughout this document. Every critical data source includes a reference URL — use it. Do not guess API schemas; verify them.

**Critical Identity Rule:** This project is built fresh by the authors listed above. The two reference repositories are used ONLY as architectural inspiration and data catalogs. Do NOT carry over any project names, branding, author names, contributor lists, Discord links, community badges, or identity markers from those repositories. The product is called **SalesEdge** and nothing else.

---

## 1) MISSION AND CONTEXT

### 1.1 What We Are Building

**SalesEdge** is an India-focused AI platform for Intelligent Sales & Revenue Operations. It is an enterprise-grade system that plugs into CRM, communication, financial, and government data systems to accelerate every stage of the sales pipeline.

### 1.2 Core Capabilities

| Capability | Description |
|---|---|
| **Prospect Intelligence** | Research targets across public data sources, score fit, generate personalized outreach, adapt based on engagement signals |
| **Deal Intelligence** | Real-time pipeline health monitoring, risk signal detection (engagement drops, competitor mentions, stakeholder changes), recovery play generation |
| **Revenue Retention** | Churn prediction from usage patterns and sentiment, automated intervention workflows (outreach, offers, escalation) |
| **Competitive Intelligence** | Market signal tracking, automatic battlecard generation, positioning updates pushed into active deal contexts |
| **Macro-Economic Context** | Indian government data, RBI policies, SEBI regulations, fiscal indicators mapped to business impact |

### 1.3 Reference Repositories (Architecture Inspiration Only)

These two local repositories serve as **architectural reference and data catalogs ONLY**. Do not copy branding, names, or identity.

- **Repository A** (UI architecture patterns, panel systems, API routing patterns): `/home/shuvam/codes/et_hackathon/worldmonitor`
- **Repository B** (API catalogs, market data tooling, connector patterns): `/home/shuvam/codes/et_hackathon/available_api`

### 1.4 Primary Government Data Mandate

The following government sources are **first-class, mandatory integrations**:

| Source | URL | Purpose |
|---|---|---|
| OGD India | https://data.gov.in/ | 200,000+ datasets across all ministries |
| OGD API Docs | https://data.gov.in/help/apis | API documentation and key registration |
| RBI DBIE | https://data.rbi.org.in/ | Monetary, banking, forex, financial markets |
| RBI Statistics | https://rbi.org.in/scripts/statistics.aspx | Statistical publications |
| MOSPI eSankhyiki | https://www.mospi.gov.in/ | GDP, CPI, IIP, employment, trade |
| eSankhyiki Portal | https://esankhyiki.mospi.gov.in/ | API access to MOSPI data |
| SEBI | https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=1&smid=0 | Regulatory filings and market data |
| DPIIT | https://dpiit.gov.in/ | Industrial policy, FDI data |
| Ministry of Finance | https://www.finmin.nic.in/ | Union budget, fiscal policy, economic surveys |
| Economic Survey | https://www.indiabudget.gov.in/ | Annual economic survey data |
| MCA | https://www.mca.gov.in/ | Company registrations, filings |
| GST Portal | https://www.gst.gov.in/ | GST statistics and compliance data |
| India Trade Portal | https://www.indiantradeportal.in/ | Export/import statistics |

---

## 2) NON-NEGOTIABLE PRODUCT TRANSFORMATION

### 2.1 Complete Identity Replacement

You must **completely remove** all traces of the legacy system's identity and war/conflict orientation.

#### What to Remove

| Category | Examples to Remove/Replace |
|---|---|
| **Project names** | "God's Eye", "World Monitor", "WorldMonitor", any war-themed names |
| **Conflict content** | Iran/war/conflict Telegram channels, live war alert panels, geopolitical conflict feeds |
| **Author/contributor references** | Any author names from the original repos (in UI, about pages, README, package.json, etc.) |
| **Community links** | Discord badges, community links, social media links from original projects |
| **War-themed UI** | Military color schemes, alert-red dashboards, conflict-oriented iconography |
| **RSS conflict feeds** | War-focused RSS allowlists and feed prioritization |

#### Known Files to Inspect and Transform

```
worldmonitor/data/telegram-channels.json          → Replace with business signal channels
worldmonitor/api/telegram-feed.js                  → Replace with market signal feed
worldmonitor/api/rss-proxy.js                      → Replace with business RSS proxy
worldmonitor/api/_rss-allowed-domains.js            → Replace with business domain allowlist
worldmonitor/live-channels.html                    → Replace with market intelligence view
worldmonitor/tests/live-news-panel-guard.test.mts  → Replace with market signal tests
worldmonitor/tests/live-news-hls.test.mjs          → Replace with data feed tests
worldmonitor/package.json                          → Update name, author, description
worldmonitor/README.md                             → Complete rewrite
worldmonitor/index.html                            → Complete rebrand
```

#### What to Replace With

| Old Concept | New Concept |
|---|---|
| War alerts | Deal risk alerts |
| Conflict feeds | Market signal feeds |
| Geopolitical tracking | Competitive intelligence tracking |
| Military dashboard | Executive revenue cockpit |
| Threat assessment | Churn risk assessment |
| Battle reports | Battlecard generation |

### 2.2 New Identity to Apply

```
Product Name: SalesEdge
Tagline: "Intelligent Sales & Revenue Operations Platform"
Authors: Shuvam Banerji Seal, Aheli Poddar, Alok Mishra
License: MIT (or as appropriate — retain required third-party notices in NOTICES.md)
Version: 1.0.0
```

### 2.3 Compliance Guardrails

- **DO** retain legally required license files (LICENSE, NOTICE).
- **DO** keep third-party attribution where license terms require it — place in `legal/THIRD_PARTY_NOTICES.md`.
- **DO NOT** display original author names as product authors anywhere in the UI, docs, or README.
- **DO NOT** delete license files — update them to reflect the new project's authorship while retaining required upstream notices.

---

## 3) MANDATORY DATA COVERAGE

### 3.1 Government APIs (First-Class, Mandatory)

#### 3.1.1 OGD India (data.gov.in)

**Reference URLs for implementation:**
- API Documentation: https://data.gov.in/help/apis
- API Base: https://api.data.gov.in/
- Dataset Catalog: https://data.gov.in/catalogs
- Resource Search: https://data.gov.in/search

**Implementation Requirements:**

```python
# Search endpoint pattern
GET https://api.data.gov.in/lists?format=json&api-key={key}&filters[org_type]=Central&offset=0&limit=100

# Resource endpoint pattern  
GET https://api.data.gov.in/resource/{resource_id}?api-key={key}&format=json&offset=0&limit=100

# Catalog listing
GET https://api.data.gov.in/catalogs?format=json&api-key={key}
```

**Exhaustive Discovery Requirement:**
- Implement paginated crawling across ALL ministries and departments
- Query expansion: search by ministry name, department, keyword, sector
- Build coverage reports by: ministry, sector, update frequency, data quality score
- Auto-discover new datasets on a weekly schedule
- Tag each dataset with: relevance score (to sales/revenue ops), freshness, completeness, ministry owner

**Priority Ministries/Departments for Sales Intelligence:**

| Ministry/Department | Data Types | Relevance |
|---|---|---|
| RBI | Policy rates, forex reserves, banking stats | Deal pricing, market conditions |
| SEBI | IPO data, FII flows, regulatory changes | Prospect identification, risk signals |
| Ministry of Finance | Budget allocations, tax collections, fiscal deficit | Macro context for enterprise deals |
| DPIIT | FDI data, industrial production, startup registrations | Prospect research |
| Ministry of Commerce | Export/import data, trade agreements | Industry sizing |
| Ministry of Corporate Affairs | Company registrations, director data | Prospect enrichment |
| GST Council | GST collections by state/sector | Revenue proxy for prospects |
| Ministry of MSME | MSME registrations, scheme data | SMB prospect universe |
| TRAI | Telecom subscriber data, regulatory changes | Sector-specific intelligence |
| Ministry of Electronics and IT | IT sector data, digital economy metrics | Tech sector intelligence |

**Dynamic Dataset Registry Schema:**
```python
class OGDDataset(BaseModel):
    dataset_id: str
    title: str
    ministry: str
    department: str
    sector: list[str]
    update_frequency: str  # "real-time", "daily", "weekly", "monthly", "quarterly", "annual"
    last_updated: datetime
    quality_score: float  # 0-1
    completeness_score: float  # 0-1
    relevance_tags: list[str]  # ["prospect_research", "risk_detection", "macro_context", ...]
    resource_count: int
    api_accessible: bool
    cached_locally: bool
    last_crawled: datetime
```

#### 3.1.2 RBI DBIE

**Reference URLs:**
- Main Portal: https://data.rbi.org.in/
- Statistical Tables: https://data.rbi.org.in/DBIE/dbie.rbi?site=statistics
- Web Services: https://data.rbi.org.in/DBIE/dbie.rbi?site=home

**Key Data Series to Integrate:**

| Series | Business Use |
|---|---|
| Policy Repo Rate history | Deal timing, enterprise budget cycles |
| CPI/WPI trends | Pricing intelligence, contract escalation |
| Forex Reserves | Currency risk for international deals |
| Bank Credit growth | Sector-wise lending = demand proxy |
| FDI inflows | Prospect universe expansion |
| Balance of Payments | Macro context for export-oriented accounts |
| Money Supply (M3) | Liquidity conditions → buying capacity |
| Government Securities yields | Risk-free rate for DCF models |

**Implementation Notes:**
- RBI DBIE does not have a clean REST API — requires HTML scraping and CSV/Excel download parsing
- Cache aggressively (minimum 24-hour cache for most series)
- Build a normalization layer that converts RBI's various date formats and table structures into standardized time-series
- Reference for scraping patterns: https://data.rbi.org.in/DBIE/dbie.rbi?site=publications

#### 3.1.3 MOSPI eSankhyiki

**Reference URLs:**
- Portal: https://www.mospi.gov.in/
- eSankhyiki: https://esankhyiki.mospi.gov.in/
- Statistical Year Book: https://www.mospi.gov.in/statistical-year-book-india

**Key Indicators:**

| Indicator | Frequency | Business Use |
|---|---|---|
| GDP growth (quarterly) | Quarterly | Market sizing, territory planning |
| CPI components | Monthly | Sector inflation for pricing |
| IIP (Index of Industrial Production) | Monthly | Manufacturing sector health |
| Employment indicators | Quarterly | Enterprise hiring = buying signals |
| Trade statistics | Monthly | Export/import sector intelligence |
| State-wise GSDP | Annual | Territory prioritization |

### 3.2 Indian Market and Financial APIs

Use the `available_api` catalog. Integrate with tiered priority:

**Tier 1: Government and Official Public Data (Mandatory)**
- OGD India, RBI DBIE, MOSPI eSankhyiki, NSE India, BSE India

**Tier 2: Exchange and Broker Data (Required for market context)**
- Dhan, Zerodha, Upstox, Angel, Fyers, ICICI Breeze, NSETools

**Tier 3: Commercial Enrichment APIs (Best-effort integration)**
- Finnhub, TwelveData, Alpha Vantage, Polygon, FMP, StockInsights
- CoinGecko, Binance, Bybit, KuCoin (crypto context)
- Open Exchange Rates, ExchangeRate.host (FX)

### 3.3 Full API Inventory

*(The complete API inventory from the original prompt Sections 3.3.1 through 3.3.7 is retained in full — all 25 APIs with their base URLs, auth methods, rate limits, coverage, and catalog sizes. I will not repeat them here for brevity but they are INCLUDED IN FULL in this prompt.)*

**Additional Implementation Rule:**

For EVERY API in the inventory, create a connector specification artifact:

```python
class ConnectorSpec(BaseModel):
    api_name: str
    api_id: str  # unique slug
    tier: Literal["tier1_government", "tier2_exchange", "tier3_enrichment"]
    classification: Literal["mandatory_core", "optional_enrichment", "simulation_fallback"]
    classification_justification: str
    base_url: str
    auth_method: str
    auth_details: dict
    rate_limit: RateLimitSpec
    endpoints: list[EndpointSpec]
    business_use_cases: list[str]  # mapped to: prospecting, risk_detection, retention, competitive_intel, macro_context
    health_check_endpoint: str
    fallback_strategy: str
    data_freshness_sla: str
    indian_market_coverage: list[str]  # NSE, BSE, MCX, etc.
```

---

## 4) CORE PRODUCT ARCHITECTURE

### 4.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SalesEdge Platform                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Frontend     │  │  API Gateway │  │  Auth Service│              │
│  │  (React/      │  │  (FastAPI    │  │  (OIDC/JWT)  │              │
│  │   Next.js)    │──│   Router)    │──│              │              │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘              │
│         │                  │                                        │
│  ┌──────▼──────────────────▼─────────────────────────────┐         │
│  │              Service Mesh / Internal Bus                │         │
│  ├──────────┬──────────┬──────────┬──────────┬───────────┤         │
│  │          │          │          │          │           │          │
│  │ ┌────────▼───┐ ┌────▼─────┐ ┌─▼────────┐ ┌▼────────┐│          │
│  │ │Prospect    │ │Deal      │ │Retention │ │Competitive│          │
│  │ │Intelligence│ │Intelligence│ │Agent    │ │Intel     ││          │
│  │ │Agent       │ │Agent     │ │          │ │Agent     ││          │
│  │ └────────┬───┘ └────┬─────┘ └─┬────────┘ └┬────────┘│          │
│  │          │          │          │           │          │          │
│  │  ┌───────▼──────────▼──────────▼───────────▼───────┐ │          │
│  │  │           Feature Store / Data Layer             │ │          │
│  │  ├─────────┬─────────┬──────────┬─────────────────┤ │          │
│  │  │ Gov Data│ Market  │ CRM      │ Communication   │ │          │
│  │  │ Ingestor│ Ingestor│ Connector│ Signal Ingestor │ │          │
│  │  └────┬────┘────┬────┘────┬─────┘────┬────────────┘ │          │
│  └───────┼─────────┼─────────┼──────────┼──────────────┘          │
│          │         │         │          │                           │
├──────────▼─────────▼─────────▼──────────▼───────────────────────────┤
│  External Data Sources                                              │
│  • data.gov.in  • RBI  • MOSPI  • NSE  • BSE  • Broker APIs       │
│  • Finnhub  • CRM (Salesforce/HubSpot)  • Email  • LinkedIn       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack (Non-Negotiable)

#### Backend Stack

| Component | Technology | Justification |
|---|---|---|
| **API Framework** | FastAPI 0.110+ | Async-native, OpenAPI auto-gen, Pydantic validation |
| **ASGI Server** | Uvicorn with gunicorn manager | Production-grade ASGI serving |
| **Python Runtime** | Python 3.12 via `uv` | Latest features, performance |
| **Package Manager** | `uv` (astral-sh/uv) | Fast, deterministic, replaces pip+venv |
| **Database** | PostgreSQL 16 + SQLModel | Structured data, ORM with type safety |
| **Analytical DB** | DuckDB (embedded) | Fast OLAP queries on parquet/CSV |
| **Cache** | Redis 7+ | Multi-tier caching, pub/sub |
| **Task Queue** | Celery with Redis broker OR APScheduler | Background jobs, scheduled ingestion |
| **Async HTTP** | httpx + tenacity (retry) | Async API calls with exponential backoff |
| **Data Processing** | pandas + pyarrow + polars | DataFrame ops, parquet I/O |
| **ML/Scoring** | scikit-learn + XGBoost + SHAP | Scoring models, explainability |
| **Search** | Elasticsearch or Meilisearch | Full-text search on datasets |

**Reference for `uv`:** https://github.com/astral-sh/uv — Use this for ALL Python environment management.

#### Frontend Stack

| Component | Technology | Justification |
|---|---|---|
| **Framework** | React 18+ with TypeScript | Component model, ecosystem |
| **Build Tool** | Vite 5+ | Fast HMR, modern bundling |
| **UI Components** | shadcn/ui + Radix UI primitives | Accessible, customizable components |
| **Styling** | Tailwind CSS 3.4+ | Utility-first, design token integration |
| **Charts** | Recharts + D3.js (custom) + Nivo | React-native charts with D3 power |
| **State Management** | Zustand + React Query (TanStack Query) | Server state + client state separation |
| **Routing** | React Router v6 or Next.js App Router | Nested layouts, code splitting |
| **Data Tables** | TanStack Table | Virtual scrolling, sorting, filtering |
| **Icons** | Lucide React | Consistent, tree-shakeable icons |
| **Forms** | React Hook Form + Zod | Validation matching backend Pydantic |

**Reference for shadcn/ui:** https://ui.shadcn.com/ — Follow their installation and theming guide.

#### Infrastructure Stack

| Component | Technology |
|---|---|
| **Containerization** | Docker + docker-compose |
| **Reverse Proxy** | Nginx or Traefik |
| **CI/CD** | GitHub Actions or GitLab CI |
| **Monitoring** | Prometheus + Grafana |
| **Logging** | Structlog + Loki or ELK |
| **Secret Management** | Docker secrets + .env files (dev) |

### 4.3 Backend-to-Frontend Contract System (CRITICAL)

**This section prevents backend-to-frontend mismatches.**

#### 4.3.1 Shared Type Contract

Every API endpoint MUST have:

1. **A Pydantic response model** (backend) in `backend/app/schemas/`
2. **A corresponding TypeScript interface** (frontend) in `frontend/src/types/api/`
3. **An OpenAPI spec** auto-generated from FastAPI and consumed by the frontend

**Contract Generation Flow:**
```
FastAPI Pydantic Models
        ↓
    OpenAPI JSON (auto-generated at /openapi.json)
        ↓
    openapi-typescript-codegen (or similar)
        ↓
    TypeScript interfaces + API client functions
        ↓
    Frontend consumes typed API client
```

#### 4.3.2 API Response Envelope

ALL API responses must follow this envelope:

```python
# Backend (Pydantic)
class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None
    metadata: ResponseMetadata

class ResponseMetadata(BaseModel):
    timestamp: datetime
    request_id: str
    data_freshness: datetime | None = None
    source_attribution: list[SourceAttribution] = []
    confidence_score: float | None = None
    cache_status: Literal["hit", "miss", "stale"] = "miss"

class SourceAttribution(BaseModel):
    source_name: str
    source_url: str | None = None
    last_updated: datetime
    reliability_tier: Literal["tier1", "tier2", "tier3"]

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None
```

```typescript
// Frontend (TypeScript) — must match exactly
interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error: ErrorDetail | null;
  metadata: ResponseMetadata;
}

interface ResponseMetadata {
  timestamp: string; // ISO 8601
  request_id: string;
  data_freshness: string | null;
  source_attribution: SourceAttribution[];
  confidence_score: number | null;
  cache_status: "hit" | "miss" | "stale";
}
```

#### 4.3.3 API Endpoint Registry

Maintain a single source of truth for all endpoints:

```python
# backend/app/api/registry.py
ENDPOINT_REGISTRY = {
    "prospect_list": {
        "method": "GET",
        "path": "/api/v1/prospects",
        "request_model": "ProspectFilterParams",
        "response_model": "PaginatedResponse[ProspectSummary]",
        "cache_ttl": 300,
        "auth_required": True,
        "roles": ["sales_rep", "sales_manager", "admin"],
    },
    "prospect_detail": {
        "method": "GET",
        "path": "/api/v1/prospects/{prospect_id}",
        "request_model": None,
        "response_model": "APIResponse[ProspectDetail]",
        "cache_ttl": 60,
        "auth_required": True,
        "roles": ["sales_rep", "sales_manager", "admin"],
    },
    # ... all endpoints registered here
}
```

#### 4.3.4 Contract Testing

```python
# tests/contract/test_api_contracts.py
# For every endpoint in ENDPOINT_REGISTRY:
# 1. Call the endpoint
# 2. Validate response matches the declared response_model
# 3. Validate the generated TypeScript types compile
# 4. Validate field names, types, and nullability match
```

---

## 5) UI/UX DESIGN SYSTEM — "WARM ENTERPRISE"

### 5.1 Design Philosophy

SalesEdge uses a **"Warm Enterprise"** design language. It should feel:
- **Warm** — not cold corporate blue. Use amber, terracotta, warm grays.
- **Confident** — clear data hierarchy, strong typography.
- **Indian context-aware** — support for INR formatting, Indian number system (lakhs/crores), IST timestamps.
- **Analytical** — data-dense but not cluttered. Every pixel serves a purpose.

### 5.2 Color Palette — Design Tokens

```css
/* design-tokens.css */
:root {
  /* ─── Primary Brand Colors (Warm) ─── */
  --color-primary-50: #FFF8F0;      /* Lightest warm cream */
  --color-primary-100: #FFEDD5;     /* Light peach */
  --color-primary-200: #FED7AA;     /* Soft apricot */
  --color-primary-300: #FDBA74;     /* Warm amber */
  --color-primary-400: #FB923C;     /* Bold amber */
  --color-primary-500: #F97316;     /* Primary orange — main brand */
  --color-primary-600: #EA580C;     /* Deep orange */
  --color-primary-700: #C2410C;     /* Burnt orange */
  --color-primary-800: #9A3412;     /* Terracotta */
  --color-primary-900: #7C2D12;     /* Deep terracotta */

  /* ─── Semantic Colors ─── */
  --color-revenue-positive: #059669;    /* Emerald 600 — revenue up, won deals */
  --color-revenue-positive-bg: #D1FAE5; /* Emerald 100 */
  --color-caution: #D97706;             /* Amber 600 — at-risk, attention needed */
  --color-caution-bg: #FEF3C7;         /* Amber 100 */
  --color-risk: #DC2626;               /* Red 600 — high risk, churn, lost */
  --color-risk-bg: #FEE2E2;           /* Red 100 */
  --color-neutral: #6B7280;            /* Gray 500 — inactive, baseline */
  --color-neutral-bg: #F3F4F6;        /* Gray 100 */
  --color-data-quality: #7C3AED;       /* Violet 600 — data quality indicators */
  --color-data-quality-bg: #EDE9FE;   /* Violet 100 */
  --color-info: #2563EB;              /* Blue 600 — informational, links */
  --color-info-bg: #DBEAFE;           /* Blue 100 */

  /* ─── Surface Colors ─── */
  --surface-background: #FFFBF5;       /* Warm off-white — main background */
  --surface-card: #FFFFFF;             /* Pure white — card background */
  --surface-card-hover: #FFF8F0;       /* Warm cream on hover */
  --surface-sidebar: #1C1917;          /* Stone 900 — dark sidebar */
  --surface-sidebar-text: #FAFAF9;     /* Stone 50 */
  --surface-sidebar-active: #F97316;   /* Primary orange — active nav */
  --surface-header: #FFFFFF;           /* White header */
  --surface-modal-overlay: rgba(28, 25, 23, 0.6); /* Semi-transparent dark */

  /* ─── Text Colors ─── */
  --text-primary: #1C1917;            /* Stone 900 — headings, primary text */
  --text-secondary: #57534E;          /* Stone 600 — secondary text */
  --text-tertiary: #A8A29E;           /* Stone 400 — captions, timestamps */
  --text-inverse: #FAFAF9;            /* Stone 50 — text on dark backgrounds */
  --text-link: #EA580C;               /* Deep orange — links */

  /* ─── Chart Colors (ordered sequence for multi-series) ─── */
  --chart-1: #F97316;   /* Primary orange */
  --chart-2: #059669;   /* Emerald */
  --chart-3: #7C3AED;   /* Violet */
  --chart-4: #2563EB;   /* Blue */
  --chart-5: #DC2626;   /* Red */
  --chart-6: #D97706;   /* Amber */
  --chart-7: #0891B2;   /* Cyan */
  --chart-8: #BE185D;   /* Pink */

  /* ─── Typography ─── */
  --font-sans: 'Inter', 'Noto Sans', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-display: 'Plus Jakarta Sans', var(--font-sans);
  
  /* ─── Spacing Scale ─── */
  --space-xs: 0.25rem;   /* 4px */
  --space-sm: 0.5rem;    /* 8px */
  --space-md: 1rem;      /* 16px */
  --space-lg: 1.5rem;    /* 24px */
  --space-xl: 2rem;      /* 32px */
  --space-2xl: 3rem;     /* 48px */

  /* ─── Border Radius ─── */
  --radius-sm: 0.375rem;  /* 6px — buttons, badges */
  --radius-md: 0.5rem;    /* 8px — cards */
  --radius-lg: 0.75rem;   /* 12px — modals, panels */
  --radius-xl: 1rem;      /* 16px — large containers */

  /* ─── Shadows ─── */
  --shadow-sm: 0 1px 2px 0 rgba(28, 25, 23, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(28, 25, 23, 0.07), 0 2px 4px -2px rgba(28, 25, 23, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(28, 25, 23, 0.08), 0 4px 6px -4px rgba(28, 25, 23, 0.04);
  --shadow-card: 0 1px 3px 0 rgba(28, 25, 23, 0.06), 0 1px 2px -1px rgba(28, 25, 23, 0.06);
}

/* ─── Dark Mode Override ─── */
[data-theme="dark"] {
  --surface-background: #1C1917;
  --surface-card: #292524;
  --surface-card-hover: #44403C;
  --text-primary: #FAFAF9;
  --text-secondary: #D6D3D1;
  --text-tertiary: #A8A29E;
  /* ... dark mode overrides for all tokens ... */
}
```

### 5.3 Indian Context Formatting

```typescript
// frontend/src/utils/indian-formatting.ts

/**
 * Format number in Indian numbering system (lakhs, crores)
 * 1,00,000 = 1 lakh
 * 1,00,00,000 = 1 crore
 */
export function formatINR(amount: number, options?: {
  compact?: boolean;    // true → "₹1.5Cr" instead of "₹1,50,00,000"
  decimals?: number;
  showSymbol?: boolean;
}): string;

/**
 * Format number with Indian comma grouping
 * 1234567 → "12,34,567"
 */
export function formatIndianNumber(num: number): string;

/**
 * Format date/time in IST with Indian conventions
 */
export function formatIST(date: Date | string, format?: string): string;

/**
 * Convert between lakhs/crores and international notation
 */
export function toIndianUnits(amount: number): { value: number; unit: 'Cr' | 'L' | 'K' | '' };
export function fromIndianUnits(value: number, unit: 'Cr' | 'L' | 'K'): number;

/**
 * Financial year formatting (Indian FY: Apr-Mar)
 */
export function getCurrentFY(): string;  // "FY 2024-25"
export function getFYRange(fy: string): { start: Date; end: Date };

/**
 * Indian state and territory codes
 */
export const INDIAN_STATES: Record<string, { name: string; code: string; zone: string }>;
```

### 5.4 Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Top Command Bar                                                        │
│ ┌──────────┐ ┌──────────────────────────┐ ┌─────┐ ┌─────┐ ┌────────┐ │
│ │ ☰ Logo   │ │ 🔍 Global Search...       │ │ 🔔  │ │ 📊  │ │ Avatar │ │
│ └──────────┘ └──────────────────────────┘ └─────┘ └─────┘ └────────┘ │
├────────┬────────────────────────────────────────────────────┬───────────┤
│        │                                                    │           │
│  Left  │              Main Canvas                          │  Right    │
│  Nav   │                                                    │  Context  │
│        │  ┌──────────────────┐ ┌──────────────────┐        │  Rail     │
│ ┌────┐ │  │   KPI Card 1     │ │   KPI Card 2     │        │           │
│ │ 🏠 │ │  │   ₹45.2Cr ARR   │ │   87% Health     │        │ ┌───────┐ │
│ │Home│ │  └──────────────────┘ └──────────────────┘        │ │Explain│ │
│ ├────┤ │                                                    │ │ability│ │
│ │ 🎯 │ │  ┌────────────────────────────────────────┐       │ │Factors│ │
│ │Pros│ │  │                                         │       │ │       │ │
│ │pect│ │  │        Primary Chart Area                │       │ ├───────┤ │
│ ├────┤ │  │        (Resizable/Draggable)             │       │ │Source │ │
│ │ 📊 │ │  │                                         │       │ │Citati-│ │
│ │Deal│ │  └────────────────────────────────────────┘       │ │ons    │ │
│ │Risk│ │                                                    │ ├───────┤ │
│ ├────┤ │  ┌──────────────────┐ ┌──────────────────┐       │ │Recomm-│ │
│ │ 🔄 │ │  │  Chart Tile 3    │ │  Chart Tile 4    │       │ │ended  │ │
│ │Rete│ │  │                  │ │                  │       │ │Actions│ │
│ │ntn │ │  └──────────────────┘ └──────────────────┘       │ │       │ │
│ ├────┤ │                                                    │ └───────┘ │
│ │ ⚔️ │ │                                                    │           │
│ │Comp│ │                                                    │           │
│ │etv │ │                                                    │           │
│ ├────┤ │                                                    │           │
│ │ 🗄️ │ │                                                    │           │
│ │Data│ │                                                    │           │
│ ├────┤ │                                                    │           │
│ │ ⚙️ │ │                                                    │           │
│ │Admn│ │                                                    │           │
│ └────┘ │                                                    │           │
│        │                                                    │           │
├────────┴────────────────────────────────────────────────────┴───────────┤
│ Status Bar: Data Freshness: ● Live (2s ago)  │  Cache: 94% hit  │ IST │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Component Specifications

#### 5.5.1 KPI Card Component

```typescript
interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;                    // "₹", "%", "days", etc.
  format?: 'inr' | 'percent' | 'number' | 'days';
  trend: {
    direction: 'up' | 'down' | 'flat';
    value: number;                  // percentage change
    period: string;                 // "vs last month"
    isPositive: boolean;            // up can be bad (e.g., churn rate)
  };
  sparkline?: number[];             // mini chart data
  confidence?: number;              // 0-1, shown as badge
  source: string;                   // data source attribution
  lastUpdated: string;              // ISO timestamp
  onClick?: () => void;             // drill-down navigation
}
```

**Visual Spec:**
- Card: white background, `--shadow-card`, `--radius-md`
- Title: `--text-secondary`, 12px, uppercase tracking
- Value: `--text-primary`, 28px, `--font-display`, font-weight 700
- Trend arrow: colored by `isPositive` → green/red
- Confidence badge: small pill, color-coded (>0.8 green, >0.5 amber, <0.5 red)
- Source: `--text-tertiary`, 10px, bottom-right
- Hover: elevate shadow, show "Click to drill down" tooltip

#### 5.5.2 Data Table Component

```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
  };
  sorting: SortingState;
  filters: FilterState;
  onRowClick?: (row: T) => void;
  exportOptions: ('csv' | 'xlsx' | 'json')[];
  emptyState: {
    icon: ReactNode;
    title: string;
    description: string;
    action?: { label: string; onClick: () => void };
  };
  loading: boolean;
  // Indian context
  currencyColumns?: string[];       // columns to format as INR
  dateColumns?: string[];           // columns to format as IST
}
```

#### 5.5.3 Chart Wrapper Component

Every chart in the application must be wrapped in a standard container:

```typescript
interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: ReactNode;              // the actual chart
  metadata: {
    metricOwner: string;            // team/person responsible
    formula: string;                // human-readable formula
    dataSource: string[];           // source names
    refreshSLA: string;             // "every 15 minutes"
    confidenceMethod: string;       // "bootstrap 95% CI"
    lastRefreshed: string;          // ISO timestamp
    sampleSize?: number;
  };
  timeWindow: '7d' | '30d' | '90d' | '1y' | 'custom';
  onTimeWindowChange: (window: string) => void;
  exportFormats: ('csv' | 'png')[];
  filterState?: string;             // serialized filter for permalinks
  onFilterStateChange?: (state: string) => void;
  // Tooltip behavior
  tooltipRenderer?: (point: DataPoint) => TooltipContent;
}

interface TooltipContent {
  value: string;
  denominator?: string;
  methodology: string;
  lastRefreshed: string;
}
```

### 5.6 Page/View Specifications

#### View 1: Executive Revenue Cockpit (`/dashboard`)

**Purpose:** C-suite overview of revenue operations health.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Row 1: KPI Strip (4 cards)                                  │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│ │ ARR/MRR    │ │ Pipeline   │ │ Win Rate   │ │ Avg Deal   ││
│ │ ₹45.2Cr    │ │ ₹120Cr     │ │ 32%        │ │ Cycle: 45d ││
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
├─────────────────────────────────────────────────────────────┤
│ Row 2: Primary Charts (2 columns)                           │
│ ┌──────────────────────┐ ┌──────────────────────┐          │
│ │ Revenue Forecast     │ │ Pipeline Velocity    │          │
│ │ (Fan Chart)          │ │ (Dual-Axis Line)     │          │
│ └──────────────────────┘ └──────────────────────┘          │
├─────────────────────────────────────────────────────────────┤
│ Row 3: Secondary Charts (3 columns)                         │
│ ┌──────────┐ ┌──────────────────┐ ┌──────────┐            │
│ │ Funnel   │ │ Risk Heatmap     │ │ Top Deals│            │
│ │ Waterfall│ │                  │ │ Table    │            │
│ └──────────┘ └──────────────────┘ └──────────┘            │
└─────────────────────────────────────────────────────────────┘
```

**Data contracts for this view:**

```python
# Backend endpoint
@router.get("/api/v1/dashboard/executive-summary")
async def get_executive_summary(
    time_window: Literal["7d", "30d", "90d", "1y"] = "30d",
    territory: str | None = None,
    segment: str | None = None,
) -> APIResponse[ExecutiveSummary]:
    ...

class ExecutiveSummary(BaseModel):
    kpis: ExecutiveKPIs
    revenue_forecast: RevenueForecast
    pipeline_velocity: PipelineVelocityData
    funnel: FunnelData
    risk_heatmap: RiskHeatmapData
    top_deals: list[DealSummary]

class ExecutiveKPIs(BaseModel):
    arr: KPIMetric          # Annual Recurring Revenue
    mrr: KPIMetric          # Monthly Recurring Revenue
    pipeline_value: KPIMetric
    win_rate: KPIMetric
    avg_deal_cycle: KPIMetric
    net_revenue_retention: KPIMetric
    
class KPIMetric(BaseModel):
    value: float
    formatted: str          # Pre-formatted with INR/% etc
    trend_pct: float
    trend_direction: Literal["up", "down", "flat"]
    is_positive: bool       # Whether the trend direction is good
    sparkline: list[float]
    confidence: float
    source: str
    last_updated: datetime
```

#### View 2: Prospect Intelligence (`/prospects`)

**Purpose:** Research, score, and plan outreach for prospect accounts.

**Key Components:**
- Prospect search and filter panel
- Fit score breakdown (radar chart)
- Enrichment timeline (timeline component)
- Recommended outreach sequence (step cards)
- Company profile panel (from MCA, financial data)
- Industry context (government data overlay)

**Indian-Specific Enrichment Sources:**
- MCA company registration data
- GST filing status
- Industry classification (NIC codes)
- State/territory mapping
- Listed company financials (NSE/BSE)
- DPIIT recognition (for startups)
- Government contract history (from GeM portal data if available)

#### View 3: Deal Risk Console (`/deals/risk`)

**Purpose:** Real-time monitoring of pipeline health with risk detection.

**Key Components:**
- Deal risk scatter matrix (bubble chart)
- Engagement momentum tracker
- Stakeholder coverage heatmap
- Risk factor cards with confidence intervals
- Recovery playbook suggestions (AI-generated)
- Competitor mention timeline

#### View 4: Retention & Churn View (`/retention`)

**Purpose:** Predict and prevent customer churn.

**Key Components:**
- Churn survival curve (Kaplan-Meier)
- Retention cohort matrix (heatmap)
- Root cause analysis cards
- Intervention workflow tracker
- Customer health score distribution

#### View 5: Competitive & Policy Signals (`/intelligence`)

**Purpose:** Track market changes and map to active deals.

**Key Components:**
- Policy signal timeline (RBI, SEBI, government announcements)
- Competitive mention trendline
- Battlecard viewer
- Industry regulation impact assessments
- Budget/fiscal policy impact analysis (Indian Union Budget, state budgets)

#### View 6: Data Provenance (`/data`)

**Purpose:** Full transparency on data sources, freshness, and quality.

**Key Components:**
- API health dashboard
- Data freshness gauges
- Source attribution table
- Data quality scores by source
- Ingestion pipeline status
- Error rates and retry stats

### 5.7 Responsive Design Requirements

| Breakpoint | Width | Layout Behavior |
|---|---|---|
| Desktop XL | ≥1440px | Full 3-pane layout (nav + canvas + context rail) |
| Desktop | ≥1024px | 2-pane (nav collapses to icons + canvas) |
| Tablet | ≥768px | Single pane, bottom nav, stacked cards |
| Mobile | <768px | Single pane, compact KPI strip, sparkline mode |

### 5.8 Accessibility Requirements

- **WCAG AA** minimum for all color contrasts
- **Keyboard navigation** for all interactive elements
- **ARIA labels** on all charts, buttons, navigation items
- **Chart text alternatives** — every chart has a `<details>` summary describing the data
- **Focus management** — logical tab order, visible focus rings
- **Screen reader announcements** for real-time data updates
- **Reduced motion** mode that disables animations
- **High contrast** mode option

---

## 6) DETAILED FOLDER STRUCTURE

```
salesedge/
├── README.md                              # Project overview, quickstart, authors
├── LICENSE                                # MIT License
├── CONTRIBUTING.md                        # Contribution guidelines
├── CHANGELOG.md                           # Version history
├── Makefile                               # Task runner (make dev, make test, etc.)
├── docker-compose.yml                     # Full stack orchestration
├── docker-compose.dev.yml                 # Development overrides
├── docker-compose.prod.yml                # Production overrides
├── .env.example                           # Template for environment variables
├── .gitignore
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                         # Lint, type-check, test on PR
│   │   ├── cd.yml                         # Build and deploy on merge
│   │   ├── contract-tests.yml             # API contract validation
│   │   └── data-freshness-check.yml       # Scheduled data SLA monitoring
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── data_source_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── legal/
│   ├── THIRD_PARTY_NOTICES.md             # Required upstream license attributions
│   └── DATA_USAGE_COMPLIANCE.md           # Government data usage terms
│
├── docs/
│   ├── architecture/
│   │   ├── overview.md                    # System architecture overview
│   │   ├── data-flow.md                   # Data ingestion and processing flow
│   │   ├── agent-architecture.md          # AI agent design and orchestration
│   │   ├── deployment-architecture.md     # Infrastructure and deployment
│   │   └── diagrams/
│   │       ├── system-context.mmd         # Mermaid diagram
│   │       ├── container-diagram.mmd
│   │       ├── data-flow.mmd
│   │       └── agent-orchestration.mmd
│   ├── data-sources/
│   │   ├── catalog.md                     # Complete data source catalog
│   │   ├── government-apis.md             # OGD, RBI, MOSPI integration guide
│   │   ├── market-apis.md                 # NSE, BSE, broker APIs
│   │   ├── enrichment-apis.md             # Finnhub, FMP, etc.
│   │   ├── connector-matrix.md            # Auto-generated endpoint × use-case matrix
│   │   └── compliance-notes.md            # Data usage terms per source
│   ├── formulas/
│   │   ├── handbook.md                    # Complete formula handbook
│   │   ├── prospect-fit-score.md          # Prospect scoring methodology
│   │   ├── deal-risk-score.md             # Risk scoring methodology
│   │   ├── churn-hazard.md                # Churn prediction methodology
│   │   ├── revenue-recovery-priority.md   # Recovery prioritization
│   │   └── calibration-methods.md         # Model calibration approaches
│   ├── api/
│   │   ├── openapi.yaml                   # Generated OpenAPI spec
│   │   └── postman-collection.json        # Postman collection for testing
│   ├── testing/
│   │   ├── strategy.md                    # Testing strategy overview
│   │   ├── test-matrix.md                 # Full test matrix
│   │   └── backtesting-guide.md           # Historical replay methodology
│   ├── operations/
│   │   ├── deployment-guide.md            # Step-by-step deployment
│   │   ├── runbook.md                     # Operational runbook
│   │   ├── rollback-plan.md               # Rollback procedures
│   │   ├── monitoring-guide.md            # Observability setup
│   │   ├── secret-management.md           # Key rotation, vault usage
│   │   └── backup-restore.md             # Data backup/restore procedures
│   ├── user-guide/
│   │   ├── getting-started.md
│   │   ├── executive-cockpit.md
│   │   ├── prospect-intelligence.md
│   │   ├── deal-risk-console.md
│   │   ├── retention-churn.md
│   │   ├── competitive-intelligence.md
│   │   └── data-provenance.md
│   └── development/
│       ├── setup.md                       # Local dev setup guide
│       ├── coding-standards.md
│       ├── frontend-backend-contracts.md  # How to maintain type sync
│       └── adding-data-source.md          # How to add a new API connector
│
├── backend/
│   ├── pyproject.toml                     # Python project config (uv-compatible)
│   ├── uv.lock                            # Deterministic lock file
│   ├── requirements.txt                   # Fallback pip requirements
│   ├── requirements-dev.txt               # Dev dependencies
│   ├── alembic.ini                        # DB migration config
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                      # Migration scripts
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        # FastAPI app factory
│   │   ├── config.py                      # Pydantic Settings (loads .env)
│   │   ├── dependencies.py                # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── registry.py                # Endpoint registry (single source of truth)
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                # JWT/OIDC auth middleware
│   │   │   │   ├── rate_limiter.py        # Per-route rate limiting
│   │   │   │   ├── request_id.py          # Request ID injection
│   │   │   │   ├── cache.py               # Response caching middleware
│   │   │   │   └── audit_log.py           # Audit logging (secret redaction)
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py              # v1 API router aggregator
│   │   │   │   ├── dashboard.py           # Executive dashboard endpoints
│   │   │   │   ├── prospects.py           # Prospect intelligence endpoints
│   │   │   │   ├── deals.py               # Deal intelligence endpoints
│   │   │   │   ├── retention.py           # Retention/churn endpoints
│   │   │   │   ├── competitive.py         # Competitive intelligence endpoints
│   │   │   │   ├── data_provenance.py     # Data source health endpoints
│   │   │   │   ├── signals.py             # Signal feed endpoints
│   │   │   │   ├── search.py              # Global search endpoint
│   │   │   │   ├── admin.py               # Admin/config endpoints
│   │   │   │   └── health.py              # Health check, readiness, liveness
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── manager.py             # WebSocket connection manager
│   │   │       ├── deal_alerts.py         # Real-time deal risk alerts
│   │   │       └── data_updates.py        # Real-time data freshness push
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py                  # APIResponse, Pagination, ErrorDetail
│   │   │   ├── dashboard.py               # Executive dashboard schemas
│   │   │   ├── prospects.py               # Prospect schemas
│   │   │   ├── deals.py                   # Deal schemas
│   │   │   ├── retention.py               # Retention schemas
│   │   │   ├── competitive.py             # Competitive intel schemas
│   │   │   ├── signals.py                 # Signal schemas
│   │   │   ├── data_sources.py            # Data provenance schemas
│   │   │   └── indian_context.py          # INR formatting, state codes, NIC codes
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # SQLModel base with audit fields
│   │   │   ├── prospect.py                # Prospect/Account ORM
│   │   │   ├── deal.py                    # Deal/Opportunity ORM
│   │   │   ├── contact.py                 # Contact/Stakeholder ORM
│   │   │   ├── signal.py                  # Signal/Event ORM
│   │   │   ├── score.py                   # Score snapshot ORM
│   │   │   ├── outreach.py                # Outreach sequence ORM
│   │   │   ├── data_source.py             # Data source registry ORM
│   │   │   └── audit.py                   # Audit log ORM
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── prospect_scorer.py     # Prospect fit scoring engine
│   │   │   │   ├── deal_risk_scorer.py    # Deal risk scoring engine
│   │   │   │   ├── churn_predictor.py     # Churn hazard estimation
│   │   │   │   ├── recovery_prioritizer.py # Revenue recovery scoring
│   │   │   │   ├── calibration.py         # Model calibration utilities
│   │   │   │   └── explainability.py      # SHAP/feature importance
│   │   │   ├── agents/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_agent.py          # Abstract agent base class
│   │   │   │   ├── prospect_agent.py      # Prospecting agent
│   │   │   │   ├── deal_intel_agent.py    # Deal intelligence agent
│   │   │   │   ├── retention_agent.py     # Retention agent
│   │   │   │   ├── competitive_agent.py   # Competitive intelligence agent
│   │   │   │   ├── orchestrator.py        # Multi-agent orchestration
│   │   │   │   └── action_engine.py       # Agent action executor
│   │   │   ├── outreach/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sequence_generator.py  # Personalized outreach generation
│   │   │   │   ├── template_engine.py     # Email/message templates
│   │   │   │   └── engagement_tracker.py  # Open/reply/click tracking
│   │   │   ├── battlecard/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generator.py           # Battlecard generation
│   │   │   │   └── updater.py             # Auto-update from signals
│   │   │   └── search/
│   │   │       ├── __init__.py
│   │   │       └── unified_search.py      # Cross-entity search
│   │   │
│   │   ├── connectors/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # Base connector with retry, caching, health check
│   │   │   ├── registry.py                # Connector registry and factory
│   │   │   ├── government/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ogd_india.py           # data.gov.in connector
│   │   │   │   ├── rbi_dbie.py            # RBI DBIE connector
│   │   │   │   ├── mospi.py               # MOSPI eSankhyiki connector
│   │   │   │   ├── mca.py                 # MCA company data connector
│   │   │   │   └── sebi.py                # SEBI data connector
│   │   │   ├── market/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── nse.py                 # NSE India connector
│   │   │   │   ├── bse.py                 # BSE India connector
│   │   │   │   ├── nsetools_wrapper.py    # NSETools library wrapper
│   │   │   │   └── index_data.py          # Nifty/Sensex index data
│   │   │   ├── broker/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dhan.py                # Dhan API connector
│   │   │   │   ├── zerodha.py             # Zerodha Kite connector
│   │   │   │   ├── upstox.py              # Upstox connector
│   │   │   │   ├── angelone.py            # Angel SmartAPI connector
│   │   │   │   ├── fyers.py               # Fyers connector
│   │   │   │   ├── icici_breeze.py        # ICICI Breeze connector
│   │   │   │   └── delta_exchange.py      # Delta Exchange connector
│   │   │   ├── enrichment/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── finnhub.py             # Finnhub connector
│   │   │   │   ├── twelve_data.py         # Twelve Data connector
│   │   │   │   ├── alpha_vantage.py       # Alpha Vantage connector
│   │   │   │   ├── polygon.py             # Polygon.io connector
│   │   │   │   ├── fmp.py                 # Financial Modeling Prep connector
│   │   │   │   ├── stock_insights.py      # StockInsights.ai connector
│   │   │   │   ├── coingecko.py           # CoinGecko connector
│   │   │   │   └── fx/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── open_exchange.py   # Open Exchange Rates
│   │   │   │       └── exchangerate_host.py # ExchangeRate.host
│   │   │   ├── crypto/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── binance.py             # Binance connector
│   │   │   │   ├── bybit.py              # Bybit connector
│   │   │   │   └── kucoin.py             # KuCoin connector
│   │   │   ├── crm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── salesforce.py          # Salesforce connector
│   │   │   │   ├── hubspot.py             # HubSpot connector
│   │   │   │   └── simulated_crm.py       # Simulated CRM for testing
│   │   │   └── communication/
│   │   │       ├── __init__.py
│   │   │       ├── email_tracker.py       # Email engagement connector
│   │   │       ├── linkedin.py            # LinkedIn signal connector
│   │   │       └── rss_business.py        # Business RSS feed connector
│   │   │
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py                # Ingestion pipeline orchestrator
│   │   │   ├── scheduler.py               # APScheduler/Celery job definitions
│   │   │   ├── deduplication.py           # Idempotent ingestion logic
│   │   │   ├── normalization.py           # Data normalization and cleaning
│   │   │   ├── quality_scorer.py          # Data quality scoring
│   │   │   └── discovery/
│   │   │       ├── __init__.py
│   │   │       └── ogd_crawler.py         # OGD India dataset auto-discovery
│   │   │
│   │   ├── feature_store/
│   │   │   ├── __init__.py
│   │   │   ├── store.py                   # Feature store interface
│   │   │   ├── features/
│   │   │   │   ├── prospect_features.py   # Prospect feature engineering
│   │   │   │   ├── deal_features.py       # Deal feature engineering
│   │   │   │   ├── retention_features.py  # Retention feature engineering
│   │   │   │   └── macro_features.py      # Macro-economic features
│   │   │   └── snapshots.py               # Historical snapshot storage
│   │   │
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py                 # Multi-tier cache manager
│   │   │   ├── memory_cache.py            # In-memory LRU cache
│   │   │   ├── redis_cache.py             # Redis cache layer
│   │   │   └── snapshot_cache.py          # Persistent snapshot cache
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── indian_formats.py          # INR, lakhs/crores, IST, FY
│   │       ├── confidence.py              # Confidence interval calculations
│   │       ├── logging.py                 # Structured logging setup
│   │       ├── metrics.py                 # Prometheus metrics helpers
│   │       └── security.py                # Secret redaction, key rotation
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                    # Pytest fixtures, test DB, mock APIs
│       ├── factories/                     # Test data factories
│       │   ├── __init__.py
│       │   ├── prospect_factory.py
│       │   ├── deal_factory.py
│       │   └── signal_factory.py
│       ├── unit/
│       │   ├── test_scoring/
│       │   │   ├── test_prospect_scorer.py
│       │   │   ├── test_deal_risk_scorer.py
│       │   │   ├── test_churn_predictor.py
│       │   │   └── test_calibration.py
│       │   ├── test_connectors/
│       │   │   ├── test_ogd_india.py
│       │   │   ├── test_rbi_dbie.py
│       │   │   ├── test_nse.py
│       │   │   └── test_base_connector.py
│       │   ├── test_services/
│       │   │   └── ...
│       │   └── test_utils/
│       │       ├── test_indian_formats.py
│       │       └── test_confidence.py
│       ├── integration/
│       │   ├── test_ingestion_pipeline.py
│       │   ├── test_api_endpoints.py
│       │   ├── test_agent_orchestration.py
│       │   └── test_data_flow.py
│       ├── contract/
│       │   ├── test_api_contracts.py       # Response schema validation
│       │   ├── test_external_api_schemas.py # Upstream API drift detection
│       │   └── test_frontend_types.py      # TypeScript type sync validation
│       ├── e2e/
│       │   ├── test_prospect_workflow.py
│       │   ├── test_deal_risk_workflow.py
│       │   └── test_retention_workflow.py
│       ├── performance/
│       │   ├── test_api_latency.py
│       │   ├── test_ingestion_throughput.py
│       │   └── locustfile.py              # Load testing
│       └── backtesting/
│           ├── test_scoring_backtest.py
│           ├── test_churn_backtest.py
│           └── historical_data/           # Historical snapshots for replay
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json (or pnpm-lock.yaml)
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   │
│   ├── public/
│   │   ├── favicon.svg                    # SalesEdge icon
│   │   ├── logo.svg                       # SalesEdge logo
│   │   ├── logo-dark.svg                  # Dark mode logo
│   │   └── manifest.json
│   │
│   ├── src/
│   │   ├── main.tsx                       # App entry point
│   │   ├── App.tsx                        # Root component with providers
│   │   ├── router.tsx                     # Route definitions
│   │   │
│   │   ├── assets/
│   │   │   ├── fonts/
│   │   │   │   ├── Inter-*.woff2
│   │   │   │   └── PlusJakartaSans-*.woff2
│   │   │   └── images/
│   │   │       └── empty-states/          # Illustrations for empty states
│   │   │
│   │   ├── styles/
│   │   │   ├── globals.css                # Design tokens, base styles
│   │   │   ├── design-tokens.css          # CSS custom properties
│   │   │   └── chart-themes.css           # Chart-specific styling
│   │   │
│   │   ├── types/
│   │   │   ├── api/
│   │   │   │   ├── index.ts               # Re-exports
│   │   │   │   ├── common.ts              # APIResponse, Pagination, etc.
│   │   │   │   ├── dashboard.ts           # Dashboard response types
│   │   │   │   ├── prospects.ts           # Prospect types
│   │   │   │   ├── deals.ts               # Deal types
│   │   │   │   ├── retention.ts           # Retention types
│   │   │   │   ├── competitive.ts         # Competitive intel types
│   │   │   │   └── data-sources.ts        # Data provenance types
│   │   │   ├── ui/
│   │   │   │   ├── chart.ts               # Chart component prop types
│   │   │   │   ├── table.ts               # Table component prop types
│   │   │   │   └── layout.ts              # Layout component types
│   │   │   └── indian-context.ts          # Indian formatting types
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts                  # Axios/fetch client with interceptors
│   │   │   ├── hooks/
│   │   │   │   ├── useDashboard.ts        # Dashboard data hooks
│   │   │   │   ├── useProspects.ts        # Prospect data hooks
│   │   │   │   ├── useDeals.ts            # Deal data hooks
│   │   │   │   ├── useRetention.ts        # Retention data hooks
│   │   │   │   ├── useCompetitive.ts      # Competitive intel hooks
│   │   │   │   ├── useDataSources.ts      # Data provenance hooks
│   │   │   │   └── useSearch.ts           # Global search hook
│   │   │   └── websocket/
│   │   │       ├── useAlerts.ts           # Real-time alert WebSocket
│   │   │       └── useDataUpdates.ts      # Data freshness WebSocket
│   │   │
│   │   ├── stores/
│   │   │   ├── useAppStore.ts             # Global app state (Zustand)
│   │   │   ├── useFilterStore.ts          # Cross-view filter state
│   │   │   ├── useLayoutStore.ts          # User layout preferences
│   │   │   └── useThemeStore.ts           # Theme (light/dark) state
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                        # shadcn/ui primitives (installed via CLI)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── skeleton.tsx
│   │   │   │   ├── tooltip.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── sheet.tsx
│   │   │   │   ├── separator.tsx
│   │   │   │   ├── avatar.tsx
│   │   │   │   ├── command.tsx            # Command palette (⌘K)
│   │   │   │   └── ... (other shadcn components)
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx           # Main layout wrapper
│   │   │   │   ├── Sidebar.tsx            # Left navigation
│   │   │   │   ├── TopBar.tsx             # Top command bar
│   │   │   │   ├── ContextRail.tsx        # Right context panel
│   │   │   │   ├── StatusBar.tsx          # Bottom status bar
│   │   │   │   └── MobileNav.tsx          # Mobile bottom navigation
│   │   │   │
│   │   │   ├── data-display/
│   │   │   │   ├── KPICard.tsx            # KPI metric card
│   │   │   │   ├── KPIStrip.tsx           # Row of KPI cards
│   │   │   │   ├── DataTable.tsx          # Full-featured data table
│   │   │   │   ├── Timeline.tsx           # Event timeline
│   │   │   │   ├── SourceBadge.tsx        # Data source attribution badge
│   │   │   │   ├── ConfidenceBadge.tsx    # Confidence score badge
│   │   │   │   ├── FreshnessPulse.tsx     # Data freshness indicator
│   │   │   │   ├── EmptyState.tsx         # Empty state with illustration
│   │   │   │   └── LoadingSkeleton.tsx    # Skeleton loading states
│   │   │   │
│   │   │   ├── charts/
│   │   │   │   ├── ChartContainer.tsx     # Standard chart wrapper (metadata, export)
│   │   │   │   ├── FunnelWaterfall.tsx    # Pipeline funnel + waterfall
│   │   │   │   ├── PipelineVelocity.tsx   # Dual-axis velocity chart
│   │   │   │   ├── RevenueForecast.tsx    # Fan chart with uncertainty cone
│   │   │   │   ├── DealRiskScatter.tsx    # Bubble scatter matrix
│   │   │   │   ├── StakeholderHeatmap.tsx # Interaction depth heatmap
│   │   │   │   ├── OutreachPerformance.tsx # Sequence performance panel
│   │   │   │   ├── ChurnSurvival.tsx      # Kaplan-Meier survival curve
│   │   │   │   ├── RetentionCohort.tsx    # Cohort retention heatmap
│   │   │   │   ├── WinLossTreemap.tsx     # Win/loss reason treemap
│   │   │   │   ├── PolicySignalOverlay.tsx # Multi-layer time-series
│   │   │   │   ├── CompetitiveTrend.tsx   # Competitive mention trendline
│   │   │   │   ├── CalibrationCurve.tsx   # Model calibration plot
│   │   │   │   ├── ErrorDistribution.tsx  # Prediction error histogram + QQ
│   │   │   │   ├── FeatureWaterfall.tsx   # SHAP-style feature contribution
│   │   │   │   ├── PrecisionRecall.tsx    # PR curve with threshold slider
│   │   │   │   ├── DataFreshness.tsx      # Freshness gauges and timelines
│   │   │   │   ├── APILatency.tsx         # API latency percentile chart
│   │   │   │   ├── BacktestTracker.tsx    # Backtest performance scorecard
│   │   │   │   ├── DecisionSimulator.tsx  # Paper-trade scenario simulator
│   │   │   │   └── AttributionSankey.tsx  # Signal → outcome Sankey flow
│   │   │   │
│   │   │   ├── agents/
│   │   │   │   ├── AgentStatusCard.tsx    # Agent health/status display
│   │   │   │   ├── AgentActionLog.tsx     # Agent action history
│   │   │   │   └── RecoveryPlayCard.tsx   # AI-generated recovery play
│   │   │   │
│   │   │   ├── indian-context/
│   │   │   │   ├── INRDisplay.tsx         # Formatted INR with lakhs/crores
│   │   │   │   ├── ISTTimestamp.tsx        # IST-formatted timestamp
│   │   │   │   ├── StatePicker.tsx        # Indian state/UT selector
│   │   │   │   ├── FYSelector.tsx         # Financial year selector
│   │   │   │   └── NICCodeBadge.tsx       # Industry classification badge
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── CommandPalette.tsx      # ⌘K global search/action palette
│   │   │       ├── FilterBar.tsx          # Cross-view filter controls
│   │   │       ├── TimeWindowPicker.tsx   # 7d/30d/90d/1y/custom selector
│   │   │       ├── ExportButton.tsx       # CSV/PNG/XLSX export
│   │   │       ├── PermalinkButton.tsx    # Generate shareable filter URL
│   │   │       └── ErrorBoundary.tsx      # Graceful error handling
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx              # Executive Revenue Cockpit
│   │   │   ├── Prospects.tsx              # Prospect Intelligence View
│   │   │   ├── ProspectDetail.tsx         # Individual prospect deep-dive
│   │   │   ├── Deals.tsx                  # Deal Risk Console
│   │   │   ├── DealDetail.tsx             # Individual deal deep-dive
│   │   │   ├── Retention.tsx              # Retention & Churn View
│   │   │   ├── Competitive.tsx            # Competitive & Policy Signals
│   │   │   ├── DataProvenance.tsx         # Data Provenance View
│   │   │   ├── Settings.tsx               # User/admin settings
│   │   │   ├── Login.tsx                  # Authentication page
│   │   │   └── NotFound.tsx               # 404 page
│   │   │
│   │   ├── utils/
│   │   │   ├── indian-formatting.ts       # INR, lakhs/crores, IST helpers
│   │   │   ├── chart-helpers.ts           # Common chart transformations
│   │   │   ├── filter-serialization.ts    # URL ↔ filter state
│   │   │   ├── date-helpers.ts            # FY calculations, IST conversions
│   │   │   ├── export.ts                  # CSV/PNG export utilities
│   │   │   └── accessibility.ts           # A11y helper utilities
│   │   │
│   │   └── hooks/
│   │       ├── useMediaQuery.ts           # Responsive breakpoint detection
│   │       ├── usePersistedLayout.ts      # Save/load layout preferences
│   │       ├── useCrossFilter.ts          # Cross-chart filter linking
│   │       ├── useTimeSync.ts             # Synchronized time window
│   │       └── useKeyboardShortcuts.ts    # Global keyboard shortcuts
│   │
│   └── tests/
│       ├── setup.ts                       # Test setup (vitest)
│       ├── components/
│       │   ├── KPICard.test.tsx
│       │   ├── ChartContainer.test.tsx
│       │   ├── INRDisplay.test.tsx
│       │   └── ... 
│       ├── pages/
│       │   ├── Dashboard.test.tsx
│       │   └── ...
│       ├── hooks/
│       │   ├── useDashboard.test.ts
│       │   └── ...
│       └── e2e/
│           ├── playwright.config.ts
│           └── specs/
│               ├── dashboard-flow.spec.ts
│               ├── prospect-workflow.spec.ts
│               └── deal-risk-flow.spec.ts
│
├── scripts/
│   ├── bootstrap.sh                       # One-command project setup
│   ├── generate-types.sh                  # Generate TS types from OpenAPI
│   ├── seed-data.sh                       # Seed test/demo data
│   ├── run-backtests.sh                   # Execute backtesting suite
│   ├── check-data-freshness.sh            # Check data SLA compliance
│   ├── rotate-keys.sh                     # API key rotation helper
│   └── build-connector-matrix.py          # Generate connector matrix artifact
│
├── data/
│   ├── seed/
│   │   ├── prospects.json                 # Sample prospect data
│   │   ├── deals.json                     # Sample deal data
│   │   ├── signals.json                   # Sample signal events
│   │   └── indian_companies.json          # Indian company universe (BSE/NSE listed)
│   ├── schemas/
│   │   ├── ogd_dataset_registry.json      # Auto-discovered OGD datasets
│   │   └── connector_matrix.json          # Generated connector matrix
│   ├── business_rss_domains.json          # Business RSS feed allowlist
│   ├── market_signal_channels.json        # Market signal channel registry
│   ├── indian_states.json                 # States/UTs with codes and zones
│   ├── nic_codes.json                     # NIC industry classification codes
│   └── templates/
│       ├── outreach_templates.json        # Email/outreach templates
│       └── battlecard_templates.json      # Battlecard templates
│
├── infra/
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   ├── nginx/
│   │   │   ├── nginx.conf
│   │   │   └── ssl/                       # TLS cert placeholders
│   │   └── redis/
│   │       └── redis.conf
│   ├── monitoring/
│   │   ├── prometheus/
│   │   │   └── prometheus.yml
│   │   ├── grafana/
│   │   │   ├── provisioning/
│   │   │   │   ├── dashboards/
│   │   │   │   │   ├── api-latency.json
│   │   │   │   │   ├── data-freshness.json
│   │   │   │   │   └── system-health.json
│   │   │   │   └── datasources/
│   │   │   │       └── prometheus.yml
│   │   │   └── grafana.ini
│   │   └── alertmanager/
│   │       └── alertmanager.yml
│   ├── k8s/                               # Optional Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── redis-deployment.yaml
│   │   ├── postgres-deployment.yaml
│   │   └── ingress.yaml
│   └── scripts/
│       ├── deploy.sh                      # Deployment script
│       ├── rollback.sh                    # Rollback script
│       └── health-check.sh               # Post-deploy health verification
│
└── .vscode/
    ├── settings.json                      # Recommended VS Code settings
    ├── extensions.json                    # Recommended extensions
    └── launch.json                        # Debug configurations
```

---

## 7) SUB-AGENT ORCHESTRATION REQUIREMENT

You MUST create and run these sub-agents. Each sub-agent operates in its domain, produces artifacts, and reports back to you (the orchestrator). You merge, validate, and resolve conflicts.

### Sub-Agent 1: Repo Recon Agent

**Scope:** Analyze both reference repositories and produce a migration blueprint.

**Tasks:**
1. Map current worldmonitor architecture: file tree, panel system, API routes, test suites
2. Identify reusable modules (UI components, API patterns, build tooling)
3. Identify modules that must be removed (conflict/war themed)
4. Map available_api catalog structure and extract all connector specifications
5. Produce a migration compatibility matrix

**Deliverables:**
- `docs/migration/repo-audit.md` — Full audit report
- `docs/migration/reusable-modules.md` — What to keep
- `docs/migration/removal-list.md` — What to remove
- `docs/migration/migration-plan.md` — Step-by-step migration

**Output format:**
```markdown
## Repo Recon Agent Report
### Files Analyzed: [count]
### Reusable Modules: [list with justification]
### Modules to Remove: [list with justification]
### Architecture Patterns to Adopt: [list]
### Risks: [list]
```

### Sub-Agent 2: Data Source Agent

**Scope:** Build the complete data source integration layer.

**Tasks:**
1. Parse `available_api/api_info.csv` and `available_api/available_api.json`
2. Build normalized API inventory with all 25 APIs fully specified
3. Create connector specifications for each API
4. Map each endpoint to business use-cases
5. Build the OGD India auto-discovery crawler specification
6. Create data quality scoring framework
7. Design the multi-tier caching strategy

**Deliverables:**
- `data/schemas/connector_matrix.json` — Complete connector matrix
- `backend/app/connectors/` — All connector implementations
- `docs/data-sources/catalog.md` — Source catalog documentation
- `docs/data-sources/connector-matrix.md` — Endpoint × use-case matrix

**Web Research Requirements:**
If API documentation is unclear, use these URLs to verify:
- Dhan API Docs: https://dhanhq.co/docs/v2/
- Zerodha Kite Docs: https://kite.trade/docs/connect/v3/
- Upstox API Docs: https://upstox.com/developer/api-documentation/
- Angel SmartAPI Docs: https://smartapi.angelone.in/docs
- Fyers API Docs: https://myapi.fyers.in/docsv3
- ICICI Breeze Docs: https://breeze.kite.trade/
- NSE India: https://www.nseindia.com/
- BSE India: https://www.bseindia.com/
- Finnhub Docs: https://finnhub.io/docs/api
- Twelve Data Docs: https://twelvedata.com/docs
- Alpha Vantage Docs: https://www.alphavantage.co/documentation/
- Polygon Docs: https://polygon.io/docs/stocks
- FMP Docs: https://site.financialmodelingprep.com/developer/docs
- StockInsights: https://stockinsights.ai/
- CoinGecko Docs: https://www.coingecko.com/en/api/documentation
- Binance Docs: https://binance-docs.github.io/apidocs/
- Bybit Docs: https://bybit-exchange.github.io/docs/
- KuCoin Docs: https://docs.kucoin.com/
- Open Exchange Rates: https://docs.openexchangerates.org/reference/api-introduction
- ExchangeRate.host: https://exchangerate.host/documentation
- data.gov.in API: https://data.gov.in/help/apis
- RBI DBIE: https://data.rbi.org.in/
- MOSPI: https://esankhyiki.mospi.gov.in/

### Sub-Agent 3: Backend Agent

**Scope:** Build the complete FastAPI backend.

**Tasks:**
1. Set up FastAPI app factory with all middleware
2. Implement Pydantic settings for configuration
3. Build all API endpoints per the registry
4. Implement all scoring services (prospect, deal risk, churn, recovery)
5. Build agent orchestration framework
6. Implement ingestion pipelines
7. Build feature store
8. Implement multi-tier caching
9. Set up database models and migrations
10. Ensure ALL response models match the TypeScript frontend types

**Deliverables:**
- Complete `backend/` directory
- `backend/app/api/registry.py` — Endpoint registry
- `backend/app/schemas/` — All Pydantic models
- OpenAPI spec at `/openapi.json`

**Critical Instruction:** Every Pydantic model in `schemas/` MUST have a corresponding TypeScript interface generated. The Backend Agent must produce a mapping document showing `PydanticModel → TypeScriptInterface → FrontendUsage`.

### Sub-Agent 4: Frontend Agent

**Scope:** Build the complete React frontend.

**Tasks:**
1. Set up Vite + React + TypeScript project
2. Install and configure shadcn/ui with warm theme
3. Implement all design tokens from Section 5.2
4. Build layout components (AppShell, Sidebar, TopBar, ContextRail)
5. Build all 20 chart components per Section 8.2
6. Build all 6 page views per Section 5.6
7. Implement Indian context formatting utilities
8. Build API client layer with React Query hooks
9. Implement responsive layouts
10. Implement accessibility requirements
11. Build export (CSV, PNG) functionality for all charts

**Deliverables:**
- Complete `frontend/` directory
- All chart components with metadata support
- All page views with progressive rendering
- Indian formatting utilities with comprehensive test coverage

**Critical Instruction:** The Frontend Agent MUST consume TypeScript types generated from the backend OpenAPI spec. It must NOT define response types independently. Use `openapi-typescript` (https://github.com/drwpow/openapi-typescript) or similar to generate types.

### Sub-Agent 5: Quant Agent

**Scope:** Define all mathematical models, formulas, and analytical frameworks.

**Tasks:**
1. Design prospect fit scoring model (multi-factor weighted)
2. Design deal risk scoring model (engagement momentum, stakeholder entropy, stage aging, sentiment)
3. Design churn hazard estimation (survival analysis or probabilistic classifier)
4. Design revenue recovery priority scoring
5. Define calibration methodology for all models
6. Design backtesting framework
7. Define uncertainty estimation methods (bootstrap CI, prediction intervals)
8. Create SHAP-based explainability framework
9. Define drift detection strategy

**Deliverables:**
- `docs/formulas/handbook.md` — Complete formula handbook
- `docs/formulas/*.md` — Individual formula documentation
- `backend/app/services/scoring/` — Implementation of all scoring models
- `backend/tests/backtesting/` — Backtesting test suites

**Formula Documentation Format (for each formula):**
```markdown
## [Formula Name]

### Purpose
[What this formula measures and why]

### Variables
| Variable | Definition | Source | Type |
|---|---|---|---|
| x₁ | ... | ... | continuous |

### Formula
[LaTeX-style mathematical notation]

### Normalization
[How inputs are scaled/normalized]

### Weights
[How weights are determined — static, learned, or hybrid]
[Include initial weight values and learning schedule if applicable]

### Uncertainty Estimation
[Method: bootstrap CI, prediction interval, Bayesian posterior, etc.]
[Include confidence level (e.g., 95% CI)]

### Calibration
[How the model is calibrated to produce well-calibrated probabilities]
[Include calibration curve target and methodology]

### Backtest Requirements
[Historical replay specification]
[Walk-forward validation window]
[Performance metrics: MAPE, MAE, RMSE, Brier score, etc.]

### Indian Context Adjustments
[Any India-specific adjustments: FY alignment, market hours, regulatory cycles]

### Example Calculation
[Worked example with real-ish numbers]
```

### Sub-Agent 6: QA Agent

**Scope:** Build complete testing infrastructure and test suites.

**Tasks:**
1. Set up pytest with fixtures and factories
2. Build test data factories (prospect, deal, signal, etc.)
3. Write unit tests for all scoring functions
4. Write unit tests for all connectors (mocked)
5. Write integration tests for ingestion pipelines
6. Write contract tests for API schema compatibility
7. Write E2E tests with Playwright
8. Build load testing with Locust
9. Build backtesting test harnesses
10. Define quality gates for CI/CD

**Deliverables:**
- Complete `backend/tests/` directory
- Complete `frontend/tests/` directory
- `docs/testing/strategy.md`
- `docs/testing/test-matrix.md`
- CI configuration files

**Quality Gates:**
```yaml
quality_gates:
  linting:
    - ruff check (backend)
    - eslint (frontend)
  type_checking:
    - mypy --strict (backend)
    - tsc --noEmit (frontend)
  test_coverage:
    backend_minimum: 80%
    frontend_minimum: 70%
    critical_paths: 95%  # scoring, connectors, agents
  contract_tests:
    - all API responses match declared schemas
    - all TypeScript types match OpenAPI spec
  smoke_tests:
    - all endpoints return 200 on health check
    - all connectors return health status
  data_freshness:
    - no tier1 source stale > 24 hours
  performance:
    - p50 < 120ms (cached reads)
    - p95 < 500ms (analytics endpoints)
```

### Sub-Agent 7: DevOps Agent

**Scope:** Build deployment, CI/CD, and observability infrastructure.

**Tasks:**
1. Write all Dockerfiles (multi-stage, optimized)
2. Write docker-compose configurations (dev, staging, prod)
3. Configure Nginx reverse proxy with TLS
4. Set up Prometheus + Grafana monitoring
5. Build CI/CD pipeline configuration
6. Create deployment scripts and runbooks
7. Set up log aggregation
8. Build health check and readiness probes
9. Create backup/restore scripts
10. Design blue/green deployment strategy

**Deliverables:**
- Complete `infra/` directory
- `.github/workflows/` CI/CD pipelines
- `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`
- `docs/operations/` — All operational documentation
- Grafana dashboard JSON files

---

## 8) CHART SPECIFICATION CATALOG (DETAILED)

*(This incorporates and expands the original Section 8.2 — all 20 charts with implementation details)*

### Implementation Constraints for ALL Charts

1. **Every chart** must be wrapped in `<ChartContainer>` with full metadata props
2. **Every tooltip** must show: value, denominator (if ratio), methodology note, last refreshed timestamp
3. **Every chart** supports: CSV export, PNG export, filter-state permalink
4. **Every chart** must handle: loading state (skeleton), empty state, error state
5. **Every chart** uses the design token color palette from Section 5.2
6. **Every chart** has ARIA labels and a `<details>` text alternative for screen readers
7. **Indian formatting** applies: INR in lakhs/crores, dates in IST, FY conventions

### Chart 1: Funnel Conversion Waterfall
```typescript
interface FunnelWaterfallProps {
  stages: Array<{
    name: string;           // "Lead", "MQL", "SQL", "Opportunity", "Proposal", "Negotiation", "Won"
    count: number;
    conversion_rate: number; // to next stage
    avg_time_in_stage: number; // days
    confidence_interval: [number, number]; // 95% CI on conversion rate
    sample_size: number;
  }>;
  comparison?: 'previous_period' | 'target';
  delta_values?: number[];  // waterfall delta between stages
}
```

### Chart 2: Pipeline Velocity Trend
```typescript
interface PipelineVelocityProps {
  data: Array<{
    week: string;           // ISO week
    avg_days_in_stage: number;
    throughput: number;     // deals moved to next stage
    rolling_mean_days: number;
    upper_control_limit: number;
    lower_control_limit: number;
  }>;
  dual_axis: true;          // Y1: days, Y2: throughput
}
```

### Chart 3: Revenue Forecast with Uncertainty Cone
```typescript
interface RevenueForecastProps {
  historical: Array<{ date: string; revenue: number }>;
  forecast: Array<{
    date: string;
    p10: number;            // pessimistic
    p50: number;            // median forecast
    p90: number;            // optimistic
  }>;
  currency: 'INR';
  format: 'crores';         // Display in crores
}
```

*(Charts 4-20 follow the same detailed pattern — each with TypeScript interface, visual specification, data requirements, and Indian formatting notes. The full specifications from the original prompt Section 8.2 are retained and expanded.)*

### Chart 20: Attribution Sankey
```typescript
interface AttributionSankeyProps {
  nodes: Array<{
    id: string;
    label: string;
    category: 'signal' | 'action' | 'outcome';
  }>;
  links: Array<{
    source: string;
    target: string;
    value: number;          // ₹ in lakhs
    label: string;
  }>;
  // Flows from signal categories → agent actions → revenue outcomes
}
```

---

## 9) MATHEMATICAL AND ANALYTICAL REQUIREMENTS

### 9.1 Prospect Fit Score

```
FitScore(p) = Σᵢ wᵢ · normalize(fᵢ(p))

where:
  p = prospect
  fᵢ = feature extraction function i
  wᵢ = weight for feature i (Σwᵢ = 1)
  normalize = min-max or z-score normalization to [0, 1]

Features:
  f₁ = company_size_fit       (revenue band match to ICP)
  f₂ = industry_fit           (NIC code match to target sectors)
  f₃ = technology_fit         (tech stack alignment)
  f₄ = growth_signal          (revenue growth, hiring, funding)
  f₅ = engagement_signal      (website visits, content downloads)
  f₆ = geographic_fit         (state/region match to territory)
  f₇ = regulatory_tailwind    (government policy favorability)
  f₈ = financial_health       (profitability, debt ratios from BSE/NSE filings)

Weight Strategy: Initially static (domain expert), then learned via logistic regression on historical win data.

Confidence: Bootstrap 95% CI from feature completeness and source freshness.

Indian-Specific: 
  - Use MCA registration data for company age
  - Use GST filing frequency as business activity proxy
  - Map NIC codes to sales ICP definitions
  - Use DPIIT startup recognition as growth signal
```

### 9.2 Deal Risk Score

```
RiskScore(d) = 1 - Σⱼ wⱼ · healthⱼ(d)

Components:
  health₁ = engagement_momentum    (email opens, calls, meetings in window / baseline)
  health₂ = stakeholder_coverage   (% of decision-making unit engaged)
  health₃ = stage_velocity         (days_in_current_stage / expected_duration)
  health₄ = sentiment_trend        (NLP sentiment from email/call transcripts)
  health₅ = competitor_presence    (competitor mentions in communications)
  health₆ = contract_value_drift   (current quoted value / initial value)

stakeholder_entropy = -Σₖ pₖ log(pₖ)  where pₖ = interaction_share of stakeholder k

Stage aging: if stage_velocity > 1.5σ above mean, flag as risk.

Confidence: Varies by data completeness per component. 
  - engagement_momentum CI from Poisson process assumption on event counts
  - sentiment CI from model calibration curve
```

### 9.3 Churn Hazard Estimate

```
h(t|X) = h₀(t) · exp(β·X)   (Cox proportional hazards)

or

P(churn in next 90d | X) = σ(β·X)   (logistic classifier)

Features X:
  x₁ = usage_trend_30d           (% change in product usage)
  x₂ = support_ticket_frequency  (normalized by account size)
  x₃ = nps_score                 (last survey response)
  x₄ = payment_delays            (count of late payments)
  x₅ = champion_turnover         (key contact left)
  x₆ = competitive_mentions      (from signals)
  x₇ = contract_renewal_proximity (days to renewal)
  x₈ = macro_headwind            (industry-specific GDP/IIP trend from MOSPI)

Calibration: Platt scaling on held-out validation set.
Survival curve: Kaplan-Meier with Greenwood CI for visualization.
```

### 9.4 Revenue Recovery Priority Score

```
RecoveryPriority(d) = RiskScore(d) × ContractValue(d) × RecoverabilityEstimate(d)

RecoverabilityEstimate = f(
  stakeholder_relationship_depth,
  time_since_risk_onset,
  competitive_threat_severity,
  available_intervention_options
)
```

### 9.5 Backtesting Framework

**Mandatory for all scoring models:**

1. **Historical Replay:** Reconstruct features from stored snapshots at time T, apply model, compare predicted vs actual outcome.
2. **Walk-Forward Validation:** Train on [0, T], predict [T, T+Δ], slide window forward.
3. **Paper Mode:** Run model in production on live data without taking actions. Log predictions for future accuracy analysis.
4. **Drift Detection:** Monitor feature distributions over time. Alert if KL-divergence or PSI exceeds threshold.

**Metrics to track:**

| Metric | Formula | Target |
|---|---|---|
| MAPE | mean(|actual - pred| / actual) | < 15% |
| MAE | mean(|actual - pred|) | Context-dependent |
| RMSE | sqrt(mean((actual - pred)²)) | Context-dependent |
| Brier Score | mean((p_pred - y_actual)²) | < 0.25 |
| Calibration Loss | mean(|p_pred_bucket - y_freq_bucket|) | < 0.05 |
| AUC-ROC | Area under ROC curve | > 0.75 |
| Precision@K | Precision in top K predictions | > 0.60 |

---

## 10) SECURITY AND API KEY HANDLING (STRICT)

### 10.1 Key Management

**NEVER hardcode credentials.** Implement:

```python
# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SE_",  # SalesEdge prefix
    )
    
    # ─── Database ───
    database_url: str = "postgresql+asyncpg://localhost:5432/salesedge"
    redis_url: str = "redis://localhost:6379/0"
    
    # ─── Government APIs (Tier 1) ───
    ogd_api_key: str              # data.gov.in
    
    # ─── Market APIs (Tier 2) ───
    dhan_access_token: str | None = None
    zerodha_api_key: str | None = None
    zerodha_api_secret: str | None = None
    upstox_api_key: str | None = None
    upstox_api_secret: str | None = None
    angel_api_key: str | None = None
    angel_client_id: str | None = None
    fyers_app_id: str | None = None
    fyers_secret_key: str | None = None
    icici_api_key: str | None = None
    icici_api_secret: str | None = None
    delta_api_key: str | None = None
    delta_api_secret: str | None = None
    
    # ─── Enrichment APIs (Tier 3) ───
    finnhub_api_key: str | None = None
    twelve_data_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    polygon_api_key: str | None = None
    fmp_api_key: str | None = None
    stockinsights_token: str | None = None
    coingecko_api_key: str | None = None
    open_exchange_rates_app_id: str | None = None
    exchangerate_host_key: str | None = None
    
    # ─── CRM ───
    salesforce_client_id: str | None = None
    salesforce_client_secret: str | None = None
    hubspot_api_key: str | None = None
    
    # ─── Auth ───
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # ─── App ───
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]
```

### 10.2 .env.example

```bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  SalesEdge Environment Configuration                     ║
# ║  Copy to .env and fill in your values                    ║
# ║  Authors: Shuvam Banerji Seal, Aheli Poddar, Alok Mishra║
# ╚═══════════════════════════════════════════════════════════╝

# ─── Database ───
SE_DATABASE_URL=postgresql+asyncpg://salesedge:password@localhost:5432/salesedge
SE_REDIS_URL=redis://localhost:6379/0

# ─── Government APIs (REQUIRED) ───
SE_OGD_API_KEY=your_data_gov_in_api_key

# ─── Market APIs (Optional — enable as needed) ───
SE_DHAN_ACCESS_TOKEN=
SE_ZERODHA_API_KEY=
SE_ZERODHA_API_SECRET=
# ... (all keys listed)

# ─── Auth ───
SE_JWT_SECRET_KEY=your-secret-key-change-in-production

# ─── App ───
SE_ENVIRONMENT=development
SE_DEBUG=true
SE_LOG_LEVEL=DEBUG
SE_CORS_ORIGINS=["http://localhost:5173"]
```

### 10.3 Security Rules

- Secrets in environment variables only (no config files committed)
- Audit logs MUST redact all secrets (use `***` replacement for key patterns)
- Support key rotation: old key works for grace period alongside new key
- Fallback key strategy: if primary key fails, try secondary before erroring
- Rate limit tracking per API key to avoid quota exhaustion
- Secret scope separation: dev keys ≠ staging keys ≠ prod keys

---

## 11) PERFORMANCE AND RELIABILITY REQUIREMENTS

| Metric | Target | Measurement |
|---|---|---|
| p50 latency (cached reads) | < 120ms | Per-route Prometheus histogram |
| p95 latency (analytics) | < 500ms | Per-route Prometheus histogram |
| p99 latency (analytics) | < 2000ms | Per-route Prometheus histogram |
| Cache hit rate | > 80% | Redis/memory cache metrics |
| Upstream API timeout | 10s default, configurable | Circuit breaker tracking |
| Ingestion deduplication | 100% (zero duplicate records) | Idempotency key checks |
| Data freshness (Tier 1) | < 24 hours stale | Freshness monitor |
| Data freshness (Tier 2) | < 1 hour for market data | Freshness monitor |
| Model inference latency | < 200ms p95 | Service metrics |
| WebSocket message latency | < 500ms | Push latency tracking |

### Caching Strategy

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  In-Memory  │    │   Redis     │    │  DuckDB     │    │  PostgreSQL │
│  LRU Cache  │ →  │   Cache     │ →  │  Snapshots  │ →  │  Source of  │
│  (TTL: 30s) │    │  (TTL: 5m)  │    │  (TTL: 1hr) │    │  Truth      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     L1                  L2                 L3                  L4
```

### Circuit Breaker Pattern

```python
# For all upstream API calls
class CircuitBreaker:
    states: CLOSED → OPEN → HALF_OPEN → CLOSED
    
    failure_threshold: 5          # consecutive failures to open
    recovery_timeout: 30          # seconds before trying half-open
    success_threshold: 3          # successes in half-open to close
    
    # On OPEN: return cached/fallback data immediately
    # On HALF_OPEN: allow one request through
    # Log all state transitions
```

---

## 12) UV AND DEVELOPER WORKFLOW

### 12.1 Bootstrap Script

```bash
#!/bin/bash
# scripts/bootstrap.sh
# One-command project setup for SalesEdge
# Authors: Shuvam Banerji Seal, Aheli Poddar, Alok Mishra

set -euo pipefail

echo "🚀 Bootstrapping SalesEdge development environment..."

# ─── Check prerequisites ───
command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required. Install from https://nodejs.org/"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "⚠️ Docker not found. Some features won't work."; }

# ─── Backend setup ───
echo "📦 Setting up Python backend..."
cd backend
uv python install 3.12
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# ─── Frontend setup ───
echo "📦 Setting up Frontend..."
cd ../frontend
npm install  # or pnpm install

# ─── Environment ───
cd ..
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ Created .env from template. Please fill in your API keys."
fi

# ─── Database ───
if command -v docker &> /dev/null; then
    echo "🐳 Starting database services..."
    docker-compose -f docker-compose.dev.yml up -d postgres redis
    sleep 5
    cd backend
    source .venv/bin/activate
    alembic upgrade head
    cd ..
fi

# ─── Seed data ───
echo "🌱 Seeding development data..."
cd backend
source .venv/bin/activate
python -m app.scripts.seed_data
cd ..

echo "✅ SalesEdge is ready!"
echo ""
echo "Start backend:  cd backend && source .venv/bin/activate && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "Start frontend: cd frontend && npm run dev"
echo "Full stack:     docker-compose -f docker-compose.dev.yml up"
```

### 12.2 Makefile

```makefile
# SalesEdge Makefile
# Authors: Shuvam Banerji Seal, Aheli Poddar, Alok Mishra

.PHONY: help dev test lint typecheck build deploy

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Development ───
bootstrap:  ## One-command project setup
	bash scripts/bootstrap.sh

dev:  ## Start full development stack
	docker-compose -f docker-compose.dev.yml up

dev-backend:  ## Start backend only
	cd backend && source .venv/bin/activate && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:  ## Start frontend only
	cd frontend && npm run dev

# ─── Testing ───
test:  ## Run all tests
	cd backend && source .venv/bin/activate && uv run pytest -v
	cd frontend && npm run test

test-unit:  ## Run unit tests only
	cd backend && source .venv/bin/activate && uv run pytest tests/unit -v

test-integration:  ## Run integration tests
	cd backend && source .venv/bin/activate && uv run pytest tests/integration -v

test-contract:  ## Run contract tests
	cd backend && source .venv/bin/activate && uv run pytest tests/contract -v

test-e2e:  ## Run E2E tests
	cd frontend && npx playwright test

test-performance:  ## Run performance tests
	cd backend && source .venv/bin/activate && uv run locust -f tests/performance/locustfile.py

test-backtest:  ## Run backtesting suite
	cd backend && source .venv/bin/activate && uv run pytest tests/backtesting -v

# ─── Quality ───
lint:  ## Run linters
	cd backend && source .venv/bin/activate && ruff check .
	cd frontend && npm run lint

typecheck:  ## Run type checkers
	cd backend && source .venv/bin/activate && mypy app --strict
	cd frontend && npx tsc --noEmit

format:  ## Format code
	cd backend && source .venv/bin/activate && ruff format .
	cd frontend && npm run format

# ─── Build & Deploy ───
build:  ## Build production containers
	docker-compose -f docker-compose.prod.yml build

deploy:  ## Deploy to production
	bash infra/scripts/deploy.sh

rollback:  ## Rollback last deployment
	bash infra/scripts/rollback.sh

# ─── Data ───
seed:  ## Seed development data
	bash scripts/seed-data.sh

generate-types:  ## Generate TypeScript types from OpenAPI
	bash scripts/generate-types.sh

connector-matrix:  ## Generate connector matrix artifact
	cd backend && source .venv/bin/activate && python scripts/build-connector-matrix.py

check-freshness:  ## Check data source freshness SLAs
	bash scripts/check-data-freshness.sh
```

---

## 13) DOCUMENTATION STRUCTURE

All documentation lives in `docs/` and must be:
- Written in Markdown
- Cross-linked with relative paths
- Accessible from within the running application (served at `/docs`)
- Versioned alongside code

### Documentation Index (`docs/README.md`)

```markdown
# SalesEdge Documentation

**Authors:** Shuvam Banerji Seal, Aheli Poddar, Alok Mishra

## For Users
- [Getting Started](user-guide/getting-started.md)
- [Executive Cockpit Guide](user-guide/executive-cockpit.md)
- [Prospect Intelligence Guide](user-guide/prospect-intelligence.md)
- [Deal Risk Console Guide](user-guide/deal-risk-console.md)
- [Retention & Churn Guide](user-guide/retention-churn.md)
- [Competitive Intelligence Guide](user-guide/competitive-intelligence.md)
- [Data Provenance Guide](user-guide/data-provenance.md)

## For Developers
- [Architecture Overview](architecture/overview.md)
- [Local Development Setup](development/setup.md)
- [Adding a Data Source](development/adding-data-source.md)
- [Frontend-Backend Contracts](development/frontend-backend-contracts.md)
- [Coding Standards](development/coding-standards.md)

## Data & Analytics
- [Data Source Catalog](data-sources/catalog.md)
- [Connector Matrix](data-sources/connector-matrix.md)
- [Formula Handbook](formulas/handbook.md)

## Operations
- [Deployment Guide](operations/deployment-guide.md)
- [Operational Runbook](operations/runbook.md)
- [Monitoring Guide](operations/monitoring-guide.md)
- [Secret Management](operations/secret-management.md)
- [Backup & Restore](operations/backup-restore.md)

## Testing
- [Testing Strategy](testing/strategy.md)
- [Test Matrix](testing/test-matrix.md)
- [Backtesting Guide](testing/backtesting-guide.md)

## API Reference
- [OpenAPI Specification](api/openapi.yaml)
- [Postman Collection](api/postman-collection.json)
```

---

## 14) INTRANET DEPLOYMENT

### 14.1 docker-compose.prod.yml

```yaml
version: '3.9'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    networks:
      - salesedge

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - salesedge
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: salesedge
      POSTGRES_USER: salesedge
      POSTGRES_PASSWORD: ${SE_DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U salesedge"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - salesedge

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - salesedge

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./infra/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./infra/docker/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - salesedge

  # ─── Monitoring (optional but recommended) ───
  prometheus:
    image: prom/prometheus:v2.50.0
    restart: unless-stopped
    volumes:
      - ./infra/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - salesedge

  grafana:
    image: grafana/grafana:10.4.0
    restart: unless-stopped
    volumes:
      - ./infra/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_data:/var/lib/grafana
    networks:
      - salesedge

volumes:
  postgres_data:
  redis_data:
  grafana_data:

networks:
  salesedge:
    driver: bridge
```

### 14.2 Deployment Checklist

```markdown
## Pre-Deployment Checklist

- [ ] All tests pass (unit, integration, contract, E2E)
- [ ] Type checks pass (mypy, tsc)
- [ ] Linting passes (ruff, eslint)
- [ ] API contract tests pass
- [ ] Data freshness SLAs verified
- [ ] Environment variables configured for target environment
- [ ] Database migrations reviewed and tested
- [ ] TLS certificates in place
- [ ] Backup of current production data taken
- [ ] Rollback plan documented and tested
- [ ] Health check endpoints verified
- [ ] Performance baseline captured
- [ ] Security scan completed (no hardcoded secrets)
- [ ] Author and branding check (no legacy names in UI)
```

---

## 15) EXECUTION PLAN AND PHASES

### Phase 0: Repo Audit and Migration Blueprint (Day 1-2)
- Run Repo Recon Agent
- Produce migration blueprint
- Identify reusable vs removable modules
- Set up project scaffold

### Phase 1: Data Platform and Connectors (Day 3-5)
- Run Data Source Agent
- Implement all Tier 1 connectors (Government APIs)
- Implement connector base class with retry, caching, health check
- Build OGD auto-discovery crawler
- Build ingestion pipeline framework
- Set up PostgreSQL + Redis + DuckDB

### Phase 2: Core AI Agents and Scoring Engines (Day 6-8)
- Run Quant Agent
- Implement prospect fit scoring
- Implement deal risk scoring
- Implement churn predictor
- Build agent orchestration framework
- Build feature store
- Write backtesting harnesses

### Phase 3: Frontend UX and Analytics Views (Day 7-10)
- Run Frontend Agent (overlaps with Phase 2)
- Set up React + Vite + shadcn/ui with warm theme
- Build layout components
- Build all 20 chart components
- Build all 6 page views
- Implement Indian context formatting
- Build API client layer with type safety

### Phase 4: Testing, Performance Hardening, Observability (Day 9-11)
- Run QA Agent
- Complete test pyramid
- Run performance tests and optimize
- Set up monitoring (Prometheus + Grafana)
- Run contract tests and fix mismatches
- Run security audit

### Phase 5: Intranet Deployment and Documentation (Day 11-12)
- Run DevOps Agent
- Build Docker images
- Configure Nginx + TLS
- Deploy to target environment
- Complete all documentation
- Final acceptance testing

---

## 16) CONCRETE IMPLEMENTATION CONSTRAINTS

1. **Keep existing high-value reusable modules** from reference repos — do not rewrite blindly
2. **Remove or deprecate all war/conflict-specific artifacts** cleanly with git history
3. **Use feature flags** for staged rollout of new capabilities
4. **Keep commits atomic and traceable** — one logical change per commit
5. **All file paths must match** the folder structure in Section 6 exactly
6. **All API response models must match** between backend Pydantic and frontend TypeScript
7. **Indian formatting is mandatory** everywhere currency, dates, or numbers appear
8. **Author attribution** — only "Shuvam Banerji Seal, Aheli Poddar, Alok Mishra" in all product-facing surfaces
9. **No orphan code** — every file must be imported/used somewhere or explicitly marked as template/example
10. **Progressive enhancement** — core features work without JavaScript; enhanced with it

---

## 17) ADDITIONAL WEB RESEARCH REFERENCES

If you need to look up implementation details, use these reference URLs:

| Topic | URL |
|---|---|
| FastAPI Documentation | https://fastapi.tiangolo.com/ |
| Pydantic V2 | https://docs.pydantic.dev/latest/ |
| SQLModel | https://sqlmodel.tiangolo.com/ |
| UV Package Manager | https://docs.astral.sh/uv/ |
| React Documentation | https://react.dev/ |
| Vite | https://vitejs.dev/ |
| shadcn/ui | https://ui.shadcn.com/ |
| Tailwind CSS | https://tailwindcss.com/docs |
| Recharts | https://recharts.org/ |
| D3.js | https://d3js.org/ |
| Nivo Charts | https://nivo.rocks/ |
| TanStack Query | https://tanstack.com/query/latest |
| TanStack Table | https://tanstack.com/table/latest |
| Zustand | https://zustand-demo.pmnd.rs/ |
| Playwright | https://playwright.dev/ |
| Locust | https://locust.io/ |
| SHAP | https://shap.readthedocs.io/ |
| scikit-learn | https://scikit-learn.org/stable/ |
| DuckDB | https://duckdb.org/docs/ |
| Redis | https://redis.io/docs/ |
| Docker Compose | https://docs.docker.com/compose/ |
| Prometheus | https://prometheus.io/docs/ |
| Grafana | https://grafana.com/docs/ |
| OpenAPI TypeScript Codegen | https://github.com/drwpow/openapi-typescript |
| Indian NIC Codes | https://www.ncs.gov.in/content/nic-codes |
| Indian State Codes (ISO 3166-2:IN) | https://en.wikipedia.org/wiki/ISO_3166-2:IN |
| Indian Financial Year | https://en.wikipedia.org/wiki/Fiscal_year#India |
| Kaplan-Meier Estimator | https://en.wikipedia.org/wiki/Kaplan%E2%80%93Meier_estimator |
| SHAP Values | https://christophm.github.io/interpretable-ml-book/shap.html |
| Cox Proportional Hazards | https://en.wikipedia.org/wiki/Proportional_hazards_model |

---

## 18) SIMULATED CRM AND DATA FOR TESTING

Since production CRM access may not be available during development, build a **simulated CRM dataset** that:

1. Contains **500+ Indian companies** with realistic attributes:
   - Company names (anonymized but realistic Indian company patterns)
   - NIC industry codes
   - Revenue bands (in lakhs/crores)
   - Employee count ranges
   - Headquarters state/city
   - GST registration status
   - MCA registration date
   - Listed status (NSE/BSE/unlisted)

2. Contains **200+ simulated deals** with:
   - Pipeline stages: Lead → MQL → SQL → Discovery → Proposal → Negotiation → Won/Lost
   - Deal values in INR (lakhs/crores)
   - Stage entry/exit timestamps
   - Engagement events (emails, calls, meetings)
   - Stakeholder mappings
   - Win/loss reasons
   - Competitor mentions

3. Contains **50+ churn scenarios** with:
   - Usage decline patterns
   - Support ticket histories
   - NPS survey responses
   - Renewal dates
   - Intervention records

4. Contains **100+ market signals** from:
   - RBI policy changes
   - SEBI regulatory updates
   - Government budget announcements
   - Industry news events

**The simulated dataset must be statistically realistic** — distributions should match typical Indian B2B SaaS sales patterns.

---

## 19) FEATURE FLAGS

Implement feature flags for staged rollout:

```python
# backend/app/config.py (addition)
class FeatureFlags(BaseModel):
    enable_prospect_agent: bool = True
    enable_deal_risk_agent: bool = True
    enable_retention_agent: bool = False       # Phase 2
    enable_competitive_agent: bool = False     # Phase 2
    enable_crm_integration: bool = False       # Requires CRM setup
    enable_email_tracking: bool = False        # Requires email setup
    enable_linkedin_signals: bool = False      # Requires LinkedIn API
    enable_ogd_auto_discovery: bool = True
    enable_rbi_integration: bool = True
    enable_nse_live_data: bool = False         # Requires market hours
    enable_paper_trading_mode: bool = True     # Safe for testing
    enable_websocket_alerts: bool = True
    enable_dark_mode: bool = True
    enable_export_functionality: bool = True
```

---

## 20) ERROR HANDLING PHILOSOPHY

### Backend Error Handling

```python
# All errors return structured APIResponse with error details
# HTTP status codes are meaningful:
# 200 - Success
# 201 - Created
# 400 - Bad request (validation error)
# 401 - Unauthorized
# 403 - Forbidden
# 404 - Not found
# 409 - Conflict (duplicate)
# 422 - Unprocessable entity
# 429 - Rate limited
# 500 - Internal server error
# 502 - Bad gateway (upstream API failure)
# 503 - Service unavailable (circuit breaker open)

# All 5xx errors include:
# - Correlation request_id for support
# - Sanitized error message (no stack traces in production)
# - Suggested retry-after header where applicable
```

### Frontend Error Handling

```typescript
// Every API call goes through error boundary
// Error states are user-friendly:
// - "We couldn't load this data. It might be temporarily unavailable."
// - "This data source is being updated. Last known data shown."
// - "Your session has expired. Please sign in again."
// - Never show raw JSON errors or stack traces
// - Always provide a retry action
// - Show cached/stale data with a warning badge when fresh data fails
```

---

## 21) ACCESSIBILITY AUDIT CHECKLIST

Before final delivery, verify:

- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical (left-to-right, top-to-bottom)
- [ ] Focus indicators are visible (2px outline, high contrast)
- [ ] All images and icons have alt text
- [ ] All charts have `<details>` text alternatives
- [ ] Color is never the sole indicator (add patterns/labels)
- [ ] Contrast ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- [ ] Form inputs have visible labels (not just placeholders)
- [ ] Error messages are announced to screen readers
- [ ] Dynamic content changes are announced (aria-live)
- [ ] Reduced motion mode works (prefers-reduced-motion)
- [ ] Page titles are descriptive and unique
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] Skip navigation link exists

---

## 22) FINAL ACCEPTANCE CRITERIA

The solution is **COMPLETE** only when ALL of these conditions hold:

| # | Criterion | Verification Method |
|---|---|---|
| 1 | War/conflict theme completely replaced by sales/revenue intelligence theme | Manual UI audit + grep for legacy terms |
| 2 | Product branded as "SalesEdge" with correct authors throughout | grep for legacy names, check all UI surfaces |
| 3 | Government APIs (data.gov.in, RBI, MOSPI) operationally integrated with dynamic discovery | Integration tests + live API call evidence |
| 4 | Indian market API catalog integrated (≥15 of 25 APIs) with source attribution and quality scoring | Connector matrix artifact + health check |
| 5 | FastAPI + Uvicorn service runs via `uv` workflow | `uv run uvicorn` command succeeds |
| 6 | Sub-agents were used with evidence of outputs and merged results | Sub-agent reports in deliverables |
| 7 | Full testing stack passes (unit ≥80% coverage, integration, contract, E2E, performance, backtesting) | CI pipeline green + coverage reports |
| 8 | Intranet deployment artifacts and runbooks present | docker-compose + docs/operations/ |
| 9 | UI includes all 6 role-based views with warm design system | Visual verification + component tests |
| 10 | All 20 chart types implemented with metadata, tooltips, export | Component tests + visual verification |
| 11 | Indian context formatting (INR, lakhs/crores, IST, FY) works throughout | Unit tests on formatting utilities |
| 12 | Mathematical formulas documented with variables, weights, calibration, CI | docs/formulas/ review |
| 13 | Secrets handled securely with no hardcoded credentials | grep audit + config review |
| 14 | Backend-frontend type contracts enforced (no mismatches) | Contract tests pass |
| 15 | Accessibility WCAG AA compliance verified | Accessibility audit checklist |
| 16 | Performance targets met (p50 < 120ms, p95 < 500ms) | Performance test results |
| 17 | Data provenance view shows source, freshness, confidence for all data | UI verification |
| 18 | Backtesting framework operational with historical replay capability | Backtest test suite passes |

---

## 23) OUTPUT FORMAT REQUIRED

Return your response as:

1. **Executive Summary** — What was built, key decisions, status
2. **Architecture Decisions** — Technology choices and justifications
3. **Sub-Agent Execution Logs** — Each sub-agent's scope, outputs, artifacts
4. **Data Source Integration Table** — All 25 APIs with status, classification, test evidence
5. **File-by-File Change Log** — What was created/modified/deleted
6. **Backend-Frontend Contract Verification** — Proof of type alignment
7. **Test and Performance Evidence** — Coverage reports, latency benchmarks
8. **Indian Context Implementation** — INR formatting, FY handling, state codes
9. **UI/UX Implementation** — Design system application, chart catalog status
10. **Deployment Guide** — Step-by-step deployment instructions
11. **Risks, Known Gaps, and Next-Step Roadmap** — Honest assessment of what's done and what's not

---

## 24) EXECUTION INSTRUCTION

**Start immediately.** 

1. Create all sub-agents as specified in Section 7.
2. Run them in parallel where possible (Data Source Agent + Quant Agent can run concurrently; Frontend Agent needs Backend Agent's schemas).
3. Merge outputs and resolve conflicts.
4. Make reasonable assumptions, state them explicitly.
5. If you encounter a true blocker (missing information that cannot be reasonably assumed), state the blocker, propose your best-guess solution, and proceed.
6. Do NOT wait for additional clarification unless the blocker makes implementation impossible.
7. Use web search for any API documentation you're unsure about — URLs are provided throughout this prompt.

**The product is called SalesEdge. The authors are Shuvam Banerji Seal, Aheli Poddar, and Alok Mishra. There are no other names.**

**Begin.**