from artifact_loop.models import EvaluationResult, EvaluationMetrics, RunConvergenceMetrics, StageAttempt


def compute_metrics(result: EvaluationResult) -> EvaluationMetrics:
    fields = result.field_grounding
    total = len(fields) or 1

    def count(verdict: str) -> int:
        return sum(1 for f in fields if f.verdict == verdict)

    explicit = count("explicitly_supported")
    strong = count("strongly_implied")
    weak = count("weakly_implied")
    unsupported = count("unsupported")
    contradicted = count("contradicted")

    source_quotes = sum(1 for f in fields if f.source_quote)

    core_fields = [
        f for f in fields
        if f.field_path.startswith("core_capabilities")
    ]

    core_supported = [
        f for f in core_fields
        if f.verdict in {"explicitly_supported", "strongly_implied"}
    ]

    weak_confirmed = [
        f for f in fields
        if f.verdict == "weakly_implied"
        and not f.field_path.startswith("open_questions")
        and not f.field_path.startswith("assumptions")
    ]

    weak_assumptions = [
        f for f in fields
        if f.field_path.startswith("assumptions")
        and f.verdict == "weakly_implied"
    ]

    weak_open_questions = [
        f for f in fields
        if f.field_path.startswith("open_questions")
        and f.verdict == "weakly_implied"
    ]

    grounding_score = (
        1.0 * explicit +
        0.8 * strong +
        0.4 * weak +
        0.0 * unsupported -
        0.5 * contradicted
    ) / total

    preservation_score = 1.0 - min(
        1.0,
        (
            0.25 * len(result.missing_requirements)
            + 0.20 * len(result.distorted_requirements)
            + 0.20 * len(result.hallucinated_requirements)
        )
    )

    risk_score = min(
        1.0,
        (
            0.50 * len(result.hallucinated_requirements)
            + 0.70 * contradicted
            + 0.30 * unsupported
            + 0.35 * len(result.missing_requirements)
            + 0.25 * len(result.distorted_requirements)
            + 0.40 * len(weak_confirmed)
            + 0.10 * len(weak_assumptions)
            + 0.03 * len(weak_open_questions)
        )
    )

    blocking_failure = (
        len(result.missing_requirements) > 0
        or len(result.distorted_requirements) > 0
        or len(result.hallucinated_requirements) > 0
        or unsupported > 0
        or contradicted > 0
    )

    return EvaluationMetrics(
        total_fields=total,

        explicit_support_rate=explicit / total,
        strong_inference_rate=strong / total,
        weak_inference_rate=weak / total,
        unsupported_rate=unsupported / total,
        contradiction_rate=contradicted / total,

        source_quote_coverage=source_quotes / total,
        core_capability_coverage=len(core_supported) / max(len(core_fields), 1),

        hallucination_count=len(result.hallucinated_requirements),
        missing_count=len(result.missing_requirements),
        distortion_count=len(result.distorted_requirements),

        weak_confirmed_claims_count=len(weak_confirmed),
        weak_assumption_count=len(weak_assumptions),
        weak_open_question_count=len(weak_open_questions),

        grounding_score=max(0.0, min(1.0, grounding_score)),
        preservation_score=preservation_score,
        risk_score=risk_score,
        blocking_failure=blocking_failure,
    )


def compute_run_convergence(attempts: list[StageAttempt]) -> RunConvergenceMetrics:
    first = attempts[0].metrics
    last = attempts[-1].metrics

    initial_blockers = int(first.blocking_failure)
    final_blockers = int(last.blocking_failure)

    risk_reduction = max(0.0, first.risk_score - last.risk_score)

    hallucinations_removed = max(
        0,
        first.hallucination_count - last.hallucination_count,
    )

    converged = (
        not last.blocking_failure
        and last.risk_score <= 0.35
    )

    if last.blocking_failure:
        status = "FAIL"
    elif last.risk_score > 0.35:
        status = "PASS_WARN"
    else:
        status = "PASS"

    convergence_score = (
        0.35 * last.preservation_score
        + 0.25 * last.core_capability_coverage
        + 0.20 * (1.0 - last.risk_score)
        + 0.10 * (1.0 if converged else 0.0)
        + 0.10 * min(1.0, risk_reduction)
    )

    return RunConvergenceMetrics(
        attempts=len(attempts),
        converged=converged,
        status=status,

        initial_risk_score=first.risk_score,
        final_risk_score=last.risk_score,
        risk_reduction=risk_reduction,

        initial_blocking_failures=initial_blockers,
        final_blocking_failures=final_blockers,
        blocking_failures_removed=max(0, initial_blockers - final_blockers),

        initial_hallucination_count=first.hallucination_count,
        final_hallucination_count=last.hallucination_count,
        hallucinations_removed=hallucinations_removed,

        final_preservation_score=last.preservation_score,
        final_core_capability_coverage=last.core_capability_coverage,

        convergence_score=round(convergence_score, 4),
    )
