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


class ReconstructedSpec(BaseModel):
    text: str


class EvaluationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    missing_requirements: list[str] = Field(default_factory=list)
    distorted_requirements: list[str] = Field(default_factory=list)
    hallucinated_requirements: list[str] = Field(default_factory=list)
    improvement_tip: str
    failure_reason: str | None = None


class StageAttempt(BaseModel):
    attempt_number: int
    output: HLD
    reconstructed: ReconstructedSpec
    evaluation: EvaluationResult


class StageResult(BaseModel):
    input: RawSpec
    final_output: HLD
    final_reconstruction: ReconstructedSpec
    final_evaluation: EvaluationResult
    attempts: list[StageAttempt]
