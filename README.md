# 🏭 Explainable Predictive Maintenance System  
## Decision‑Trace–First Architecture with Maintenance Agent

---

## 📌 Project Overview

Industrial machines generate massive sensor data, yet maintenance decisions are still
- distrusted,
- delayed,
- and poorly explained.

Most predictive maintenance systems fail **not because predictions are wrong**, but because:
- engineers cannot see *how* decisions were made,
- system logic cannot be audited,
- alerts do not translate into clear actions.

This project solves that problem by building a **trace‑first predictive maintenance system**
where **every decision is recorded, explained, and acted upon**.

> **Core philosophy:**  
> *If a system cannot show how it reasoned, it should not be trusted.*

---

## 🎯 Problem Statement

Existing predictive maintenance solutions suffer from:

- ❌ Black‑box AI alerts
- ❌ Logical mismatch between expected and real outcomes
- ❌ Alert fatigue due to poor explanations
- ❌ No direct path from alert → maintenance action

Our solution focuses on:
- **decision transparency**
- **logical correctness**
- **human trust**
- **workflow integration**

---

## 🧠 Core Idea: Decision Trace First

Explainability is **not added later** in this system.  
The architecture is built around a **Decision Trace Engine** that records *how* every decision is made.

For every alert, the system explicitly records:
- what was evaluated,
- which rules were checked and triggered,
- how risk evolved step by step,
- why the final decision occurred.

All other components — explanations, maintenance actions, and learning — are built **on top of this decision trace**.

---

### 🔍 Why Decision Trace (and Why Not Traditional XAI)

Most explainable AI (XAI) techniques attempt to explain a decision **after it has already happened**.  
While useful for understanding model behavior, they are not sufficient for **industrial decision systems** where trust, auditability, and actionability are critical.

This project uses a **Decision Trace–first approach** for the following reasons.

---

### ✅ Why Decision Trace

- **Execution‑based explainability**  
  The Decision Trace records the *actual reasoning path* taken by the system, step by step, instead of approximating it after the fact.

- **Deterministic and replayable**  
  Given the same inputs, the system produces the same trace.  
  This allows decisions to be:
  - replayed,
  - audited,
  - debugged.

- **Captures logic, not just correlations**  
  Industrial systems rely on rules, thresholds, and workflows.  
  Decision traces explicitly capture:
  - which rules were evaluated,
  - which rules fired,
  - how confidence and risk evolved.

- **Directly exposes logical errors**  
  When the system’s expected outcome does not match real‑world behavior, the trace shows *where the reasoning diverged*, instead of hiding the mistake.

- **Single source of truth**  
  Explanations, maintenance actions, and feedback all reference the same trace, ensuring consistency across the system.

---

### ❌ Why Not Traditional XAI (Alone)

- **Post‑hoc, not causal**  
  Traditional XAI explains *what influenced* a decision, not *how the decision was actually made*.

- **Approximate by nature**  
  Feature attribution methods estimate influence; they do not record execution steps.

- **Limited auditability**  
  XAI does not naturally capture:
  - rule sequences,
  - intermediate reasoning states,
  - workflow logic.

- **Weak actionability**  
  Knowing which feature mattered most does not explain:
  - why a maintenance action was chosen,
  - or why it was triggered at that specific time.

---

### 🧩 Final Design Choice

> **Decision Traces serve as the ground truth for system reasoning.  
Explainability models are used only to translate these traces into human‑understandable language.**

This makes the system:
- transparent,
- auditable,
- trustworthy,
- and suitable for real industrial deployment.

---

## 🏗️ Full Architecture Overview

### Top‑Level Flow

```mermaid
flowchart TD

%% Sensor & Data Reality Layer
subgraph L1["Sensor & Data Reality Layer"]
    S1["Sensor 1: Vibration"]
    S2["Sensor 2: Temperature"]
    S3["Sensor 3: Load"]
    SD["Sensor Data Stream"]
    S1 --> SD
    S2 --> SD
    S3 --> SD
end

%% Reasoning Engine
subgraph L2["Reasoning Engine"]
    FE["Feature Extraction"]
    RE["Deterministic Reasoning"]
    FE --> RE
end

%% Decision Trace Engine
subgraph L3["Decision Trace Engine"]
    DT["Decision Trace Builder"]
    FD["Final Decision and Confidence"]
    JS["Decision Trace Stored as JSON"]
    DT --> FD
    DT --> JS
end


%% Maintenance & Workflow Layer
subgraph L5["Maintenance Agent and Workflow"]
    MA["Maintenance Decision Agent"]
    WO["Work Order Generator"]
end

%% Explainability Layer
subgraph L4["Explainability Agent Layer"]
    TI["Trace Ingestion"]
    LLM["Explainability LLM"]
    EX["Human Readable Explanation"]
    TI --> LLM
    LLM --> EX
    FB["Engineer Feedback"]
end

%% Cross Layer Flow
SD --> FE
RE --> DT
FD --> MA
EX --> FB
MA --> WO
WO --> TI
FB --> DT
