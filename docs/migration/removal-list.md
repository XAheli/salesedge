# Removed Modules — War/Conflict Content

## Removal Policy

SalesEdge is a **sales and revenue operations platform**. All modules from the
WorldMonitor reference repository related to armed conflict, war, military
operations, humanitarian crises, or geopolitical risk scoring have been
**completely removed** and are not present in any form in the SalesEdge codebase.

## Removed Module Categories

### 1. Conflict Tracking

| Module                       | Original Purpose                        | Removal Reason           |
|------------------------------|-----------------------------------------|--------------------------|
| `connectors/acled.py`        | Armed Conflict Location & Event Data    | Conflict data source     |
| `connectors/gdelt.py`        | Global Database of Events               | Conflict event tracking  |
| `connectors/crisis_feeds.py` | Humanitarian crisis RSS feeds           | Crisis content           |
| `services/conflict_scorer.py`| Conflict intensity scoring              | War/conflict domain      |
| `services/crisis_detector.py`| Automated crisis detection              | Crisis domain            |

### 2. Military / Geopolitical Analysis

| Module                           | Original Purpose                    | Removal Reason          |
|----------------------------------|-------------------------------------|-------------------------|
| `agents/geopolitical_agent.py`   | Geopolitical risk analysis          | Military/conflict       |
| `agents/crisis_agent.py`        | Crisis response recommendations     | Crisis domain           |
| `services/military_tracker.py`  | Military movement tracking          | Military content        |
| `services/sanctions_checker.py` | Sanctions list screening            | Geopolitical domain     |

### 3. Risk Models

| Module                          | Original Purpose                     | Removal Reason          |
|---------------------------------|--------------------------------------|-------------------------|
| `scoring/country_risk.py`       | Country-level geopolitical risk      | War/conflict factors    |
| `scoring/conflict_probability.py`| Conflict escalation prediction      | War prediction          |
| `scoring/humanitarian_index.py` | Humanitarian crisis severity         | Crisis domain           |

### 4. Frontend Components

| Component                       | Original Purpose                     | Removal Reason          |
|---------------------------------|--------------------------------------|-------------------------|
| `MapView.tsx`                   | Conflict zone visualization          | War content             |
| `CrisisTimeline.tsx`           | Crisis event timeline                | Crisis domain           |
| `ThreatHeatmap.tsx`            | Geopolitical threat map              | Military content        |
| `ConflictDashboard.tsx`        | Conflict monitoring dashboard        | War/conflict            |

### 5. Data Schemas

| Schema                          | Original Purpose                     | Removal Reason          |
|---------------------------------|--------------------------------------|-------------------------|
| `conflict_event.py`            | Conflict event data model            | War content             |
| `crisis_alert.py`              | Crisis alert data model              | Crisis domain           |
| `threat_level.py`              | Threat level enumeration             | Military content        |

## Verification

- No references to `conflict`, `war`, `military`, `crisis`, `geopolitical`,
  `sanctions`, `armed`, or `humanitarian` exist in the SalesEdge codebase
  (excluding this removal documentation).
- All database migrations referencing removed models have been excluded.
- No seed data contains conflict-related content.

## Replacement Mapping

| Removed Concept          | SalesEdge Replacement                 |
|--------------------------|---------------------------------------|
| Country risk score       | Prospect fit score                    |
| Conflict probability     | Deal risk score                       |
| Crisis detection         | Churn prediction                      |
| Geopolitical agent       | Competitive intelligence agent        |
| Crisis agent             | Retention agent                       |
| Threat heatmap           | Deal risk heatmap                     |
