from artifact_loop.models import RawSpec, StageResult, StageAttempt
from artifact_loop.metrics import compute_metrics, compute_run_convergence
from artifact_loop.artifact_store import ArtifactStore


class ArtifactStage:
    def __init__(
        self,
        threshold: float = 0.85,
        max_attempts: int = 3,
        risk_threshold: float = 0.35,
        artifact_store: ArtifactStore | None = None,
        stage_name: str = "stage",
    ):
        self.threshold = threshold
        self.max_attempts = max_attempts
        self.risk_threshold = risk_threshold
        self.artifact_store = artifact_store
        self.stage_name = stage_name

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

        run_dir = None
        if self.artifact_store:
            run_dir = self.artifact_store.create_run_dir(self.stage_name)
            self.artifact_store.save_json(run_dir / "input.json", raw)

        for i in range(1, self.max_attempts + 1):
            attempt_dir = run_dir / f"attempt_{i:02d}" if run_dir else None

            output = self.produce(raw, feedback)
            evaluation = self.evaluate(raw, output)
            metrics = compute_metrics(evaluation)

            if self.artifact_store and attempt_dir:
                self.artifact_store.save_json(attempt_dir / "output.json", output)
                self.artifact_store.save_json(attempt_dir / "evaluation.json", evaluation)
                self.artifact_store.save_json(attempt_dir / "metrics.json", metrics)

            attempts.append(
                StageAttempt(
                    attempt_number=i,
                    output=output,
                    evaluation=evaluation,
                    metrics=metrics,
                )
            )

            accepted = not metrics.blocking_failure and metrics.risk_score <= self.risk_threshold
            if accepted:
                feedback = None
                break
            else:
                feedback = self.build_feedback(evaluation, metrics)
                if self.artifact_store and attempt_dir:
                    self.artifact_store.save_text(attempt_dir / "feedback.txt", feedback)

        last = attempts[-1]
        run_convergence = compute_run_convergence(attempts)

        result = StageResult(
            input=raw,
            final_output=last.output,
            final_evaluation=last.evaluation,
            attempts=attempts,
            run_convergence=run_convergence,
        )

        if self.artifact_store and run_dir:
            self.artifact_store.save_json(run_dir / "result.json", result)

        return result
