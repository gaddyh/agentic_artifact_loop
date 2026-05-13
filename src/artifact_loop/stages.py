from artifact_loop.models import RawSpec, StageResult, StageAttempt


class ArtifactStage:
    def __init__(self, threshold: float = 0.85, max_attempts: int = 3):
        self.threshold = threshold
        self.max_attempts = max_attempts

    def produce(self, raw: RawSpec, feedback: str | None = None):
        raise NotImplementedError

    def reconstruct(self, output):
        raise NotImplementedError

    def evaluate(self, original: RawSpec, output, reconstructed):
        raise NotImplementedError

    def run(self, raw: RawSpec) -> StageResult:
        attempts = []
        feedback = None

        for i in range(1, self.max_attempts + 1):
            output = self.produce(raw, feedback)
            reconstructed = self.reconstruct(output)
            evaluation = self.evaluate(raw, output, reconstructed)

            attempts.append(
                StageAttempt(
                    attempt_number=i,
                    output=output,
                    reconstructed=reconstructed,
                    evaluation=evaluation,
                )
            )

            if evaluation.score >= self.threshold:
                break

            feedback = evaluation.improvement_tip

        last = attempts[-1]

        return StageResult(
            input=raw,
            final_output=last.output,
            final_reconstruction=last.reconstructed,
            final_evaluation=last.evaluation,
            attempts=attempts,
        )
