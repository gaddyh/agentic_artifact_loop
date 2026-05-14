from artifact_loop.models import RawSpec, StageResult, StageAttempt
from artifact_loop.metrics import compute_metrics, compute_run_convergence


class ArtifactStage:
    def __init__(self, threshold: float = 0.85, max_attempts: int = 3, risk_threshold: float = 0.35):
        self.threshold = threshold
        self.max_attempts = max_attempts
        self.risk_threshold = risk_threshold

    def produce(self, raw: RawSpec, feedback: str | None = None):
        raise NotImplementedError

    def evaluate(self, original: RawSpec, output):
        raise NotImplementedError

    def build_feedback(self, evaluation, metrics) -> str:
        return f"""
The previous attempt did not pass the deterministic quality gate.

Blocking failure: {metrics.blocking_failure}
Risk score: {metrics.risk_score}
Risk threshold: {self.risk_threshold}

Missing requirements:
{evaluation.missing_requirements}

Distorted requirements:
{evaluation.distorted_requirements}

Hallucinated requirements:
{evaluation.hallucinated_requirements}

Unsupported / contradicted / weak fields:
{[
    {
        "field": f.field_path,
        "value": f.value,
        "verdict": f.verdict,
        "explanation": f.explanation,
    }
    for f in evaluation.field_grounding
    if f.verdict in ("unsupported", "contradicted", "weakly_implied")
]}

Improvement tip:
{evaluation.improvement_tip}

Revise the output to:
- preserve all explicit requirements
- remove unsupported confirmed claims
- keep assumptions minimal
- keep open questions only when useful and clearly grounded
"""

    def run(self, raw: RawSpec) -> StageResult:
        attempts = []
        feedback = None

        for i in range(1, self.max_attempts + 1):
            output = self.produce(raw, feedback)
            evaluation = self.evaluate(raw, output)
            metrics = compute_metrics(evaluation)

            attempts.append(
                StageAttempt(
                    attempt_number=i,
                    output=output,
                    evaluation=evaluation,
                    metrics=metrics,
                )
            )

            if not metrics.blocking_failure and metrics.risk_score <= self.risk_threshold:
                break

            feedback = self.build_feedback(evaluation, metrics)

        last = attempts[-1]
        run_convergence = compute_run_convergence(attempts)

        return StageResult(
            input=raw,
            final_output=last.output,
            final_evaluation=last.evaluation,
            attempts=attempts,
            run_convergence=run_convergence,
        )
