from artifact_loop.models import RawSpec, HLD, EvaluationResult
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

    def evaluate(
        self,
        original: RawSpec,
        output: HLD,
    ) -> EvaluationResult:
        messages = [
            {
                "role": "system",
                "content": """
You are a strict requirements grounding evaluator.

You are given:
1. The original raw specification written by a human.
2. A produced HLD JSON.

Your job is to verify whether every meaningful claim in the HLD is grounded in the raw specification.

You are NOT judging whether the architecture is good.
You are NOT rewarding completeness, elegance, scalability, or best practices.
You are ONLY judging source grounding and requirement preservation.

Evaluate each HLD field:

- system_name
- goal
- users
- core_capabilities
- main_components
- assumptions
- open_questions

For every meaningful value in the HLD, classify its grounding:

1. explicitly_supported
   The raw spec directly states this idea.

2. strongly_implied
   The raw spec does not say it word-for-word, but it is necessary or very strongly implied.
   Example: if raw spec says "clients book appointments via WhatsApp",
   "WhatsApp integration" is strongly implied.

3. weakly_implied
   The HLD claim may be reasonable, but the raw spec does not clearly require it.
   Weak inferences are allowed only as open_questions or assumptions, not as confirmed requirements.

4. unsupported
   The HLD added a user, component, constraint, feature, assumption, integration, UI, workflow, or technical detail not grounded in the raw spec.

5. contradicted
   The HLD says something that conflicts with the raw spec.

Definitions:

Missing requirement:
- A requirement explicitly stated in the raw spec but absent from the HLD.

Distorted requirement:
- A raw requirement is included, but its meaning, actor, scope, timing, or constraint changed.

Hallucinated requirement:
- Any HLD claim marked unsupported or contradicted.
- Any weak inference presented as a confirmed capability/component instead of an assumption or open question.

Justified inference:
- A strongly implied HLD claim that is acceptable because it is necessary to satisfy the raw spec.

Weak inference:
- A plausible but not necessary idea. It should not be treated as a confirmed requirement.

Scoring:

Start from 1.0.

Subtract:
- 0.25 for each missing core requirement.
- 0.20 for each distorted core requirement.
- 0.20 for each unsupported confirmed capability, component, user, integration, or workflow.
- 0.10 for each unsupported assumption or open question.
- 0.10 for each weak inference incorrectly presented as a confirmed requirement.
- 0.40 for any contradiction.

Clamp score between 0.0 and 1.0.

Pass policy:
- passed must be false if there are any missing_requirements.
- passed must be false if there are any distorted_requirements.
- passed must be false if there are any hallucinated_requirements.
- passed must be false if score < 0.90.
- passed may be true only when all core raw requirements are preserved and every HLD claim is explicitly_supported or strongly_implied.

Important:
- Do not penalize reasonable architectural labels that are strongly implied.
  Example: "Notification and Reminder Module" is strongly implied if reminders are explicitly required.
- Do penalize invented implementation details.
  Example: "PostgreSQL database", "web dashboard", "OAuth", "multi-language support", "admin panel" are unsupported unless present or strongly implied.
- Use short exact quotes from the raw spec when possible.
- If no exact quote exists, source_quote should be null and the explanation must say why it is implied.
- Be strict, but not stupid: architecture requires naming implied components.
""",
            },
            {
                "role": "user",
                "content": f"""
Original raw specification:
{original.text}

Produced HLD JSON:
{output.model_dump_json(indent=2)}

Return the structured evaluation.
""",
            },
        ]

        result = complete_structured(messages, EvaluationResult)

        result.passed = (
            result.score >= self.threshold
            and len(result.missing_requirements) == 0
            and len(result.distorted_requirements) == 0
            and len(result.hallucinated_requirements) == 0
        )

        if not result.passed:
            result.failure_reason = (
                "Failed grounding gate: "
                f"missing={len(result.missing_requirements)}, "
                f"distorted={len(result.distorted_requirements)}, "
                f"hallucinated={len(result.hallucinated_requirements)}, "
                f"score={result.score}"
            )

        return result
