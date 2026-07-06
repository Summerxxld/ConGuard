from __future__ import annotations

from abc import ABC, abstractmethod

from guard_baseline.schema import DialogueRecord, GuardDecision, JudgeResult, Seed, Turn


class AttackAdapter(ABC):
    """Turns a harmful seed into a sequence of user messages."""

    def __init__(self, name: str, **params: object) -> None:
        self.name = name
        self.params = params

    @abstractmethod
    def generate_user_turns(self, seed: Seed) -> list[str]:
        raise NotImplementedError


class TargetAdapter(ABC):
    """Generates assistant responses from the protected target model."""

    def __init__(self, name: str, **params: object) -> None:
        self.name = name
        self.params = params

    @abstractmethod
    def generate(self, history: list[Turn], seed: Seed) -> str:
        raise NotImplementedError


class GuardAdapter(ABC):
    """Decides whether the current user turn should reach the target model."""

    def __init__(self, name: str, **params: object) -> None:
        self.name = name
        self.params = params

    @abstractmethod
    def check(self, history: list[Turn], current_user_message: str, seed: Seed) -> GuardDecision:
        raise NotImplementedError


class JudgeAdapter(ABC):
    """Judges whether a target response satisfies the harmful goal."""

    def __init__(self, name: str, **params: object) -> None:
        self.name = name
        self.params = params

    @abstractmethod
    def judge_turn(self, seed: Seed, history: list[Turn], assistant_turn: Turn) -> JudgeResult:
        raise NotImplementedError

    def judge_dialogue(self, record: DialogueRecord) -> JudgeResult:
        if record.judge_results:
            return max(record.judge_results, key=lambda result: result.score)
        return JudgeResult(False, 0.0, "safe", "No assistant response was judged.")
