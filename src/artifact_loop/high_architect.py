from artifact_loop.models import RawSpec, HLD, ReconstructedSpec, EvaluationResult
from artifact_loop.stages import ArtifactStage
from artifact_loop.llm import complete_structured


class HighArchitectStage(ArtifactStage):
    def produce(self, raw: RawSpec, feedback: str | None = None) -> HLD:
        user_content = f"Raw specification:\n{raw.text}"
        if feedback:
            user_content += f"\n\nPrevious attempt feedback:\n{feedback}"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior software architect. "
                    "Given a raw product specification, produce a structured high-level design. "
                    "Be precise and derive only what is stated or clearly implied by the spec."
                ),
            },
            {"role": "user", "content": user_content},
        ]
        return complete_structured(messages, HLD)

    def reconstruct(self, output: HLD) -> ReconstructedSpec:
        text = (
            f"Build a system called {output.system_name}. "
            f"Its goal is to {output.goal} "
            f"It supports: {', '.join(output.core_capabilities)}. "
            f"Main components: {', '.join(output.main_components)}."
        )
        return ReconstructedSpec(text=text)

    def evaluate(
        self,
        original: RawSpec,
        output: HLD,
        reconstructed: ReconstructedSpec,
    ) -> EvaluationResult:
        messages = [
            {
                "role": "system",
                "content": """
    You are a strict requirements preservation evaluator. You are given three artifacts:
    1. The original raw specification written by a human.
    2. The produced HLD (high-level design) in full JSON, including system_name, goal, users, core_capabilities, main_components, assumptions, and open_questions.
    3. A reconstructed specification derived from the HLD.

    You must judge all three layers:
    - Source preservation: does the HLD faithfully represent what was in the raw spec?
    - Artifact faithfulness: are the HLD's assumptions, open_questions, users, and components grounded in the raw spec, or were they invented?
    - Reconstruction fidelity: does the reconstructed text accurately reflect what the HLD claims?

    Definitions:
    - Missing requirement: something explicitly required in the original but absent from the HLD or reconstruction.
    - Distorted requirement: something from the original is present but changed in meaning, scope, actor, or constraint.
    - Hallucinated requirement: anything in the HLD (including assumptions, open_questions, users, components) that was not stated or strongly implied by the original.

    Scoring:
    - 1.0 = all original requirements preserved, no distortion, no hallucination anywhere in the HLD.
    - 0.8-0.9 = mostly preserved, only minor omissions or harmless wording changes.
    - 0.5-0.7 = important requirements missing or vague.
    - 0.2-0.4 = major misunderstanding.
    - 0.0-0.1 = almost unrelated.

    Important:
    - Do not reward nice architecture.
    - Penalize invented components, users, flows, constraints, UI, storage, auth, integrations, or assumptions unless clearly implied by the raw spec.
    - If there is any hallucinated requirement, passed must be false.
    - If there is any missing requirement, passed must be false.
    - If score is below 0.90, passed must be false.
    - Be strict.
    """,
            },
            {
                "role": "user",
                "content": f"""
    Original specification:
    {original.text}

    Produced HLD (full JSON):
    {output.model_dump_json(indent=2)}

    Reconstructed specification:
    {reconstructed.text}

    Return a structured evaluation.
    """,
            },
        ]

        result = complete_structured(messages, EvaluationResult)

        # deterministic gate: never trust the LLM pass flag blindly
        result.passed = (
            result.score >= self.threshold
            and len(result.missing_requirements) == 0
            and len(result.distorted_requirements) == 0
            and len(result.hallucinated_requirements) == 0
        )

        if not result.passed:
            result.failure_reason = (
                "Failed preservation gate: "
                f"missing={len(result.missing_requirements)}, "
                f"distorted={len(result.distorted_requirements)}, "
                f"hallucinated={len(result.hallucinated_requirements)}, "
                f"score={result.score}"
            )

        return result
