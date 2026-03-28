# Executive Cockpit

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Getting started](getting-started.md)

---

## KPI explanations

| KPI | What it measures |
|-----|------------------|
| **Pipeline coverage** | Open opportunity value vs target |
| **Weighted forecast** | Stage-weighted INR projection |
| **At-risk ARR** | Sum of deals above risk threshold |
| **Win rate** | Closed won / (won + lost) in window |
| **Cycle time** | Median days opportunity → close |

Exact definitions follow your CRM mapping and scoring configuration.

## Chart interactions

- **Hover** tooltips show INR-formatted values and IST dates.  
- **Click** series or bars to drill into underlying deals where drill-through is wired.  
- **Legend toggles** show/hide series for cleaner comparisons.

## Time window controls

- Select **MTD**, **QTD**, **YTD**, or **custom range**.  
- Financial year aware views use **Apr–Mar** when configured for Indian reporting.  
- Data freshness indicators reflect last successful connector sync per tier.

## Export functionality

When `enable_export_functionality` is on (`FeatureFlags`):

- Export **PNG/PDF** snapshots of charts (via browser print or canvas capture).  
- Export **CSV** of tabular data from data grids.  
- Respect **data classification** — do not export restricted fields outside approved channels.

---

[← Documentation index](../README.md)
