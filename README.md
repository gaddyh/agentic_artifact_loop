# Evaluation-Driven Architecture Synthesis Lab

> A measurable artifact-refinement framework for exploring iterative AI system design.

This project studies how large language models can generate, evaluate, critique, and refine structured software architecture artifacts using deterministic governance and observable convergence metrics.

**The goal is not autonomous AGI or "magic agents."**

The goal is engineering systems that can:

- generate structured artifacts
- evaluate grounding against source requirements
- detect hallucinations and distortions
- iteratively refine outputs
- measure convergence over time

---

## Core Idea

Instead of treating LLMs as chatbots, this project treats them as **probabilistic artifact generators** inside a measurable engineering loop.

Each stage follows:

```
input
→ artifact generation
→ grounding evaluation
→ deterministic metrics
→ retry / refinement
→ convergence analysis
```

The system combines:

- LLM-based semantic evaluation
- deterministic governance rules
- structured observability
- convergence tracking
- stress-test benchmarking

---

## Current Pipeline

```
RawSpec
→ HighArchitectStage
→ High-Level Design (HLD)
→ Evaluation
→ Metrics
→ Feedback Loop
→ Convergence Tracking
```

**Example:**

> *"I want a WhatsApp assistant for solo service providers."*

becomes an HLD with:

- `users`
- `capabilities`
- `components`
- `assumptions`
- `open questions`

The generated architecture is then evaluated against the original specification.

---

## What Makes This Different

Most agent demos optimize for:

- flashy autonomy
- multi-agent theatrics
- tool calling
- prompt chaining

This project focuses on a single question:

> **Can we measure whether the system is actually improving?**

The system explicitly separates concerns:

| Layer | Responsibility |
|---|---|
| **LLM Judge** | Semantic observations |
| **Metrics Layer** | Deterministic interpretation |
| **Governance Layer** | Retry / convergence decisions |
| **Artifact Loop** | Iterative refinement |

---

## Key Concepts

### 1. Artifact-Centric Design

The important outputs are not conversations — they are **artifacts**:

- HLDs
- evaluations
- grounding reports
- metrics
- convergence traces

Each artifact is structured, inspectable, and measurable.

### 2. Grounding Evaluation

The evaluator checks whether each HLD field is:

- `explicitly_supported`
- `strongly_implied`
- `weakly_implied`
- `unsupported`
- `contradicted`

Example:

```json
{
  "field_path": "main_components[1]",
  "value": "Notification System",
  "verdict": "strongly_implied"
}
```

This enables precise observability over hallucinations and architectural speculation.

### 3. Deterministic Governance

The system does not trust a single opaque LLM score. Retry decisions are based on deterministic metrics:

- `hallucination_count`
- `preservation_score`
- `risk_score`
- `blocking_failure`
- `core_capability_coverage`

Example:

```python
if not metrics.blocking_failure and metrics.risk_score <= threshold:
    converge()
```

### 4. Convergence Tracking

The framework measures refinement quality across attempts. Example signals:

- hallucinations removed
- risk reduction
- preservation stability
- convergence score

This enables evaluation of prompts, evaluators, retry policies, models, and architectural reasoning quality.

---

## Stress-Test Suite

A growing benchmark suite of varied specification types:

| Category | Example |
|---|---|
| **Underspecified** | *"Build a family budgeting app."* |
| **Contradictory** | *"Private messaging but publicly searchable."* |
| **Operational Systems** | Warehouse refrigeration monitoring |
| **Multi-Actor Systems** | Marketplace for music teachers |
| **Intentionally Vague** | *"AI second brain for my life."* |
| **Constraint-Heavy** | Therapist scheduling with anonymity |

The purpose is to test whether:

- the evaluator stays honest
- metrics remain meaningful
- convergence correlates with semantic quality

### Latest Run

| Spec | Attempts | Converged | Risk | Blocking | Hallucinations | Preservation | Weak Assumptions | Weak Open Qs | Convergence |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `spec_01_underspecified` | 3 | ✗ | 1.00 | ✓ | 2 | 0.60 | 0 | 0 | 0.398 |
| `spec_02_contradictory` | 3 | ✗ | 0.80 | ✓ | 1 | 0.80 | 0 | 0 | 0.590 |
| `spec_03_non_crud_workflow` | 3 | ✗ | 1.00 | ✓ | 6 | 0.00 | 0 | 0 | 0.167 |
| `spec_04_operational_system` | 2 | ✓ | 0.00 | ✗ | 0 | 1.00 | 0 | 0 | 1.000 |
| `spec_05_multi_actor` | 3 | ✓ | 0.06 | ✗ | 0 | 1.00 | 0 | 2 | 0.982 |
| `spec_06_intentionally_vague` | 3 | ✗ | 1.00 | ✓ | 9 | 0.00 | 1 | 1 | 0.125 |
| `spec_07_edge_case_constraints` | 2 | ✓ | 0.10 | ✗ | 0 | 1.00 | 1 | 0 | 0.970 |

---

## Repository Structure

```
src/artifact_loop/
├── models.py
├── metrics.py
├── stages.py
├── llm.py
├── evaluators/
└── stages/

examples/
├── run_high_architect.py
└── run_hld_stress_suite.py

results/
└── hld_stress_suite/
```

---

## Example Output

```
Attempt 1:
  risk_score    = 1.00
  hallucinations = 6

Attempt 2:
  risk_score    = 0.42
  hallucinations = 1

Attempt 3:
  risk_score    = 0.09
  hallucinations = 0
  converged     = true
```

---

## Installation

```bash
pip install -e .
```

## Running the Examples

```bash
python examples/run_high_architect.py
python examples/run_hld_stress_suite.py
```

---

## Current Research Directions

Planned next steps:

- best-attempt selection
- contradiction detection
- evaluator ensembles
- multi-stage architecture synthesis
- HLD → LLD refinement
- DSPy optimization integration
- evaluator calibration
- semantic consistency scoring
- architecture benchmark datasets

---

## Philosophy

This project explores a shift in software engineering:

> from **deterministic programming**  
> to **measurable probabilistic systems engineering**

The focus is not *"Can the model generate architecture?"*

The focus is:

> **"Can we observe, evaluate, and improve architecture generation systematically?"**

---

## Status

> **Experimental research project. Not production-ready.**

Built for:

- AI systems engineering
- evaluation-driven development
- cognitive architecture exploration
- iterative refinement research
