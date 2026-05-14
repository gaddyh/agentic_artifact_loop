from pydantic import BaseModel, Field
from typing import Literal


class RawSpec(BaseModel):
    text: str


class HLD(BaseModel):
    system_name: str
    goal: str
    users: list[str] = Field(default_factory=list)
    core_capabilities: list[str] = Field(default_factory=list)
    main_components: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class FieldGrounding(BaseModel):
    field_path: str
    value: str
    verdict: Literal[
        "explicitly_supported",
        "strongly_implied",
        "weakly_implied",
        "unsupported",
        "contradicted",
    ]
    source_quote: str | None = None
    explanation: str


class EvaluationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    passed: bool

    field_grounding: list[FieldGrounding] = Field(default_factory=list)

    missing_requirements: list[str] = Field(default_factory=list)
    distorted_requirements: list[str] = Field(default_factory=list)
    hallucinated_requirements: list[str] = Field(default_factory=list)

    justified_inferences: list[str] = Field(default_factory=list)
    weak_inferences: list[str] = Field(default_factory=list)

    improvement_tip: str
    failure_reason: str | None = None


class EvaluationMetrics(BaseModel):
    total_fields: int

    explicit_support_rate: float
    strong_inference_rate: float
    weak_inference_rate: float
    unsupported_rate: float
    contradiction_rate: float

    source_quote_coverage: float
    core_capability_coverage: float

    hallucination_count: int
    missing_count: int
    distortion_count: int

    weak_confirmed_claims_count: int
    weak_assumption_count: int
    weak_open_question_count: int

    grounding_score: float
    preservation_score: float
    risk_score: float
    blocking_failure: bool


class RunConvergenceMetrics(BaseModel):
    attempts: int
    converged: bool

    initial_risk_score: float
    final_risk_score: float
    risk_reduction: float

    initial_blocking_failures: int
    final_blocking_failures: int
    blocking_failures_removed: int

    initial_hallucination_count: int
    final_hallucination_count: int
    hallucinations_removed: int

    final_preservation_score: float
    final_core_capability_coverage: float

    convergence_score: float


class StageAttempt(BaseModel):
    attempt_number: int
    output: HLD
    evaluation: EvaluationResult
    metrics: EvaluationMetrics


class StageResult(BaseModel):
    input: RawSpec
    final_output: HLD
    final_evaluation: EvaluationResult
    attempts: list[StageAttempt]
    run_convergence: RunConvergenceMetrics
