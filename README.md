# PitCrew AI 🚨🏎️

### Autonomous SRE System Built with MCP-Orchestrated Agents

PitCrew AI is an autonomous Site Reliability Engineering (SRE) platform designed to detect, diagnose, and remediate production incidents safely using AI agents.

This project is being built as part of an advanced systems-focused hackathon with the goal of demonstrating **real-world AI infrastructure orchestration**, not just chatbot capabilities.

The architecture emphasizes:

* Control-plane vs Data-plane separation
* Safe automation
* Observability-driven decisions
* Governed remediation
* Production-style failure simulation

---

# 🎯 Project Vision

Modern infrastructure demands intelligent automation — but unsafe autonomy can be catastrophic.

PitCrew AI aims to answer a critical question:

> **Can AI operate production systems safely?**

Instead of building a simple AI assistant, this project focuses on creating a **structured operational system** where agents:

1. Detect system failures
2. Investigate root causes
3. Consult operational knowledge
4. Validate actions against policy
5. Execute remediation
6. Generate incident reports

The long-term goal is to simulate a production-grade autonomous SRE.

---

# 🧠 Core Architectural Principle

## Control Plane vs Data Plane

This project intentionally separates system responsibilities:

### ✅ Data Plane (Workload)

The production system being monitored.

Currently includes:

* A dockerized Flask API
* Health monitoring endpoint
* Controlled failure triggers

### ✅ Control Plane (Operator)

The intelligence layer that observes and controls the system.

Currently includes:

* Chaos simulation script
* Docker command execution from host
* External system control

This mirrors real-world infrastructure patterns used by Kubernetes and cloud platforms.

---

# 🏗️ What Was Built — Day 1 Foundation

Day 1 focused entirely on building a **realistic, controllable production environment**.

Before creating AI agents, it is critical to have a system that can:

✅ fail predictably
✅ recover reliably
✅ expose health signals

Without this foundation, observability and remediation cannot be demonstrated convincingly.

---

# 🐳 Dockerized Production Service

A lightweight Flask API was containerized to act as the "production workload."

## Why Docker?

Docker ensures the service runs in a consistent environment across machines by packaging:

* Application code
* Dependencies
* Runtime
* OS layer

This eliminates the classic deployment issue:

> "It works on my machine."

---

## Container Behavior

### Healthy State

```
/health → HTTP 200 OK
```

### Failed State

```
/health → HTTP 500 SERVICE UNHEALTHY
```

Failure is triggered via a filesystem flag:

```
broken.flag
```

This allows deterministic outage simulation.

---

# 💥 Chaos Engineering Setup

To simulate realistic production incidents, a control script was created:

## chaos.py

Runs on the **host machine**, not inside the container.

This is intentional.

### Why?

Production systems should never self-destruct.

Failures must be triggered externally — just like real infrastructure where operators or unexpected events impact services.

This enforces proper architectural separation:

### Control Plane → manages

### Data Plane → executes

---

## Chaos Capabilities

### Break the Service

Creates `broken.flag` inside the container, forcing the health endpoint to return 500.

### Restore the Service

Removes the flag and returns the system to healthy status.

---

## Example Flow

Simulate outage:

```
python chaos.py
> break
```

Restore service:

```
python chaos.py
> fix
```

This enables **one-command failure demos**, which are critical for reliable technical presentations.

---

# 📁 Current Project Structure

```
pitcrew-ai/
│
├── victim-app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── chaos.py
└── README.md
```

### victim-app

Represents the production workload.

### chaos.py

Represents the external operator capable of controlling the system.

---

# 🧱 Key Engineering Decisions

## Deterministic Failures

Random crashes are bad for demos.

Predictable failures enable reliable testing and presentation.

---

## Minimal Infrastructure

Kubernetes was intentionally avoided to reduce resource overhead and increase development velocity.

Docker provides sufficient realism without unnecessary complexity.

---

## Externalized Control

Automation scripts remain outside the container to reflect real platform architecture patterns.

---

# 🔜 What Comes Next

With a controllable production system in place, the next phase introduces intelligent observability.

## Upcoming Component:

### 🔧 Mechanic MCP Agent

Responsibilities:

* Inspect Docker containers
* Read logs
* Detect unhealthy services
* Surface diagnostic signals

This is where the system begins evolving from a container demo into an **AI-operated infrastructure platform.**

Future agents will include:

* Strategist → Runbook-powered RAG
* Official → Policy validation
* Risk Engine → Action scoring
* Reporter → Automated postmortems

---

# 🚀 Long-Term Architecture (Target)

```
Incident Trigger
      ↓
Observability Agent
      ↓
Diagnosis
      ↓
Runbook Retrieval
      ↓
Policy Validation
      ↓
Risk Assessment
      ↓
Autonomous Remediation
      ↓
Incident Report
```

The objective is not to create a chatbot, but a **governed autonomous operator.**

---

# 💡 Why This Project Matters

AI is rapidly gaining operational authority inside production environments.

The challenge is no longer intelligence.

It is **trust.**

PitCrew AI explores how structured orchestration, policy enforcement, and risk-aware automation can make AI safe enough to operate critical systems.

---

# ✅ Day 1 Status

✔ Dockerized production service
✔ Health monitoring endpoint
✔ Deterministic failure mechanism
✔ Chaos simulation
✔ Control/Data plane separation

## Day 2 — Autonomous Recovery Engine

Day 2 upgraded **PitCrew AI** from a failure simulator into an **autonomous self-healing system**.

It now runs a closed-loop workflow:

**Failure → Diagnose → Decide → Remediate → Verify**

aligned with real-world **SRE automation**.

---

### Architecture

PitCrew introduces a **data plane / control plane** split:

- **Data Plane:** Dockerized Flask workload with deterministic failure + health telemetry  
- **Control Plane:** Mechanic MCP (FastAPI) + AI Driver for observability and execution  

This keeps decisions external to workloads, like production infrastructure.

---

### Core Components

**Mechanic MCP (Ops Layer)**  
- Logs, inspect, restart, targeted recovery  
- Executes actions, never decides  

**AI Driver (Brain)**  
- Collects telemetry  
- Diagnoses via LLM  
- Normalizes outputs into deterministic actions  
- Executes remediation  
- Verifies recovery  

---

### Key Engineering Wins

- **Context engineering:** Only critical log signals go to the model  
- **Deterministic actions:** Free text → stable commands  
- **Root-cause recovery:** Remove failure trigger + restart, not blind reboot  

---

### Result

PitCrew AI now performs **fully autonomous self-healing**:

Chaos → Observe → Reason → Fix → Verify  

with no human intervention, modeling real SRE behavior instead of a demo bot.

Foundation complete.

The system is now ready for intelligent observability.

---


## Day 3 — Governance Layer & Reliability Hardening

Day 3 focused on transforming PitCrew from an autonomous recovery script into a governed infrastructure system by introducing policy enforcement, execution safety, and state-aware incident validation.

### Key Architectural Upgrade
Implemented a Policy Engine ("Official") to validate all remediation actions before execution.  
This establishes a controlled workflow:

Health → Diagnosis → Policy Evaluation → Approved Action → Recovery → Verification

The system now demonstrates governed autonomy rather than unrestricted AI-driven execution.

---

### Policy Engine Integration
- Built a dedicated FastAPI policy service.
- Enforced approval checks before container remediation.
- Introduced human-in-the-loop override for high-severity incidents.
- Prevented direct LLM-to-infrastructure execution.

This aligns the platform with real-world operational risk controls.

---

### Severity Normalization
Detected a governance bypass caused by vocabulary drift (`CRITICAL` vs `HIGH`).  
Implemented severity normalization to enforce a strict contract between the Driver and Policy Engine.

Result:
- Eliminated unintended auto-approvals.
- Strengthened decision determinism.

---

### Deterministic Parsing
Replaced fuzzy keyword detection with structured field extraction from LLM output.

Benefits:
- Reduced ambiguity in action selection.
- Improved automation reliability.
- Prevented prompt bleed from affecting execution.

---

### False Incident Prevention (Major Reliability Upgrade)
Observed that historical Docker logs triggered recovery on healthy services.

Added a **health pre-check gate** before running AI diagnosis:

Live Service State → Validate → Diagnose (only if degraded)

This shifted the system from log-driven behavior to state-aware incident response — a critical reliability pattern.

---

### Execution Safety Improvements
- Added guarded recovery flow to prevent duplicate remediation.
- Introduced safe request wrappers to handle service outages gracefully.
- Hardened driver against dependency failures.

The control plane now fails safely rather than unpredictably.

---

### Operational Traceability
Added incident IDs to each response cycle, improving observability and aligning the system with real incident-management workflows.

---

### Outcome
PitCrew now operates as a governed recovery platform with:

- Policy-based execution control  
- Human override for high-risk actions  
- Deterministic AI behavior  
- State-aware incident detection  
- Hardened orchestration layer  

This marks the transition from a prototype automation script to a reliability-oriented control plane.

feat(governance): add risk scoring, rule attribution, and audit trail
