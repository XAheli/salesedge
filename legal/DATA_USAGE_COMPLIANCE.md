# Data Usage Compliance

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md)

---

This document summarizes **high-level** compliance considerations for Indian public data integrations. It is **not legal advice**. Confirm all obligations with your counsel and the latest publisher terms.

## data.gov.in (OGD) API terms

- Use only within the scope of your registered API key and applicable **National Data Sharing and Accessibility Policy (NDSAP)** / portal terms.  
- **Attribution:** Preserve ministry/department attribution and dataset metadata in internal provenance records and user-facing citations where required.  
- **Rate limits:** Adhere to published quotas; implement caching and backoff (SalesEdge defaults favor this).  
- **Redistribution:** Restrictions may apply to republishing raw datasets; prefer derived metrics and aggregated views for external sharing.

## RBI data usage

- Data from **Reserve Bank of India** portals (including DBIE) is subject to RBI copyright and terms of use.  
- **Scraping:** Use official download links where available; respect `robots.txt`, acceptable use, and frequency limits.  
- **Derivatives:** Clearly label derived analytics as not official RBI communications.

## MOSPI data terms

- **Ministry of Statistics and Programme Implementation** releases are government works; still verify current guidelines for commercial use and attribution.  
- Align statistical releases with official revision schedules; do not present draft or superseded figures as current without disclosure.

## General practices in SalesEdge

- Store **dataset identifiers** and **retrieval timestamps** for audit (`data provenance` APIs).  
- Separate **PII** from open-government datasets; enforce access controls on merged tables.  
- Document **retention** and **deletion** policies for cached government payloads.

---

[← Documentation index](../README.md)
