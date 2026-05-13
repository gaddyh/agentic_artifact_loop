# Agentic Artifact Loop

A framework for iterative artifact generation with self-evaluation and refinement.

## Core Idea

RawSpec → HighArchitect → HLD → Reconstruct RawSpec → Evaluate preservation → retry if needed

## Installation

```bash
pip install -e .
```

## Running the Example

```bash
python examples/run_high_architect.py
```

## Project Structure

- `src/artifact_loop/models.py` - Pydantic models for artifacts and evaluation results
- `src/artifact_loop/stages.py` - Base class for artifact stages with retry logic
- `src/artifact_loop/high_architect.py` - HighArchitect stage implementation (currently fake/deterministic)
- `src/artifact_loop/llm.py` - Placeholder for LLM integration
- `src/artifact_loop/run.py` - Placeholder for main run loop

## Current Status

First version uses fake/deterministic outputs. LLM integration will be added later.
