from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Role = Literal["system", "user", "assistant", "guard"]


@dataclass(slots=True)
class Seed:
    seed_id: str
    source: str
    harmful_goal: str
    category: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Turn:
    turn_index: int
    role: Role
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GuardDecision:
    allowed: bool
    score: float | None = None
    label: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JudgeResult:
    success: bool
    score: float
    label: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DialogueRecord:
    experiment_id: str
    seed: Seed
    attack_name: str
    target_name: str
    guard_name: str
    turns: list[Turn]
    guard_decisions: list[GuardDecision]
    judge_results: list[JudgeResult]
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExperimentResult:
    experiment_id: str
    attack_name: str
    target_name: str
    guard_name: str
    total: int
    successes: int
    asr: float
    asr_k: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


def to_dict(value: Any) -> Any:
    return asdict(value)
