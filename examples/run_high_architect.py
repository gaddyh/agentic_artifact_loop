from artifact_loop.models import RawSpec
from artifact_loop.high_architect import HighArchitectStage
from artifact_loop.artifact_store import ArtifactStore


raw = RawSpec(
    text="""
    I want a WhatsApp-based assistant for solo service providers.
    It should let clients book appointments, reschedule, cancel,
    receive reminders, and sync with Google Calendar.
    """
)

store = ArtifactStore(base_dir="results/runs")
stage = HighArchitectStage(
    threshold=0.95,
    risk_threshold=0.35,
    max_attempts=3,
    artifact_store=store,
    stage_name="high_architect",
)
result = stage.run(raw)

print("\n=== FINAL HLD ===")
print(result.final_output.model_dump_json(indent=2))

print("\n=== EVALUATION ===")
print(result.final_evaluation.model_dump_json(indent=2))

print("\n=== ATTEMPTS ===")
for attempt in result.attempts:
    print(f"\n--- Attempt {attempt.attempt_number} ---")
    print("HLD:")
    print(attempt.output.model_dump_json(indent=2))
    print("Evaluation:")
    print(attempt.evaluation.model_dump_json(indent=2))

print("\n=== ATTEMPTS ===")
for attempt in result.attempts:
    print("\nMetrics:")
    print(attempt.metrics.model_dump_json(indent=2))

print("\n=== RUN CONVERGENCE ===")
print(result.run_convergence.model_dump_json(indent=2))