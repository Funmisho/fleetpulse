# Industry Case Study: Inter-City & Last-Mile SLA Compliance & Fleet Efficiency

**Industry Track:** Logistics  
**Stakeholder Audience:** Supply Chain & Fleet Operations Leadership

---

## 1. Executive Context & Problem Statement

Our B2B and e-commerce freight and last-mile delivery network guarantees strict 24-hour urban and 48-hour inter-city Service Level Agreements (SLAs). Over the past quarter, on-time SLA compliance dropped from 91% to 74%, triggering contractual penalty rebates while per-shipment fuel and fleet operating costs rose by 19%.

Dispatch leadership currently relies on manual allocation without predictive visibility into corridor bottlenecks, hub transfer delays, or external disruptions. Your team is tasked with uncovering the root causes of SLA breaches and cost overruns, and building an operational intelligence solution that improves pre-dispatch decision-making and fleet visibility.

---

## 2. Available Data Landscape

Operational telemetry and dispatch logs reside across disconnected fleet and warehouse systems:
* **Core Dispatch & Fleet Store:** Multi-table relational database tracking waybills, fleet assignments, corridors, and hub transfers (`logistics_core.db`).
* **Depot Fuel & Maintenance Sheets:** Legacy regional depot fuel expenditure and vehicle downtime exports (CSV archives).
* **Transit & Exception Event Logs:** Raw scan events, hub handoff timestamps, and roadside delay reports (`transit_events.jsonl`).
* **External Context:** Teams are expected to identify, source, and integrate relevant external public data (such as historical weather conditions, fuel price trends, or regional corridor/holiday data) to improve delay and cost modeling.

*Access links to the internal data stores will be shared with your Team Lead upon repository setup.*

---

## 3. Expected Deliverables

Your team owns the end-to-end framing, architecture, product naming, and technical execution. Your team must deliver:

1. **Public GitHub Repository:** Clean, reproducible codebase with a clear `README.md` and setup instructions.
2. **Engineering & Analytical Decision Log (`DECISION_LOG.md`):** Documentation of data reconciliation assumptions, metric definitions, trade-offs, and limitations.
3. **Accessible Working Solution:** A live, interactive product (such as a fleet SLA command dashboard, pre-dispatch risk estimator, or route/resource allocation tool) that stakeholders can use directly without running local code.
4. **Executive Walkthrough (3 to 5 Minutes):** A recorded video demonstrating the business insights uncovered, the live solution in action, and concrete recommendations for leadership.