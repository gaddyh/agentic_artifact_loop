from artifact_loop.models import RawSpec
from artifact_loop.high_architect import HighArchitectStage


raw = RawSpec(
    text="""
    I want a WhatsApp-based assistant for solo service providers.
    It should let clients book appointments, reschedule, cancel,
    receive reminders, and sync with Google Calendar.
    """
)

stage = HighArchitectStage(threshold=0.95, max_attempts=3)
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