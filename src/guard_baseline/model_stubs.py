from __future__ import annotations

from guard_baseline.adapters import AttackAdapter, GuardAdapter, JudgeAdapter, TargetAdapter
from guard_baseline.schema import GuardDecision, JudgeResult, Seed, Turn


class NotConfiguredAdapter(RuntimeError):
    pass


class TODOAttackAdapter(AttackAdapter):
    def generate_user_turns(self, seed: Seed) -> list[str]:
        raise NotConfiguredAdapter(f"Attack adapter '{self.name}' is a TODO. Configure a real implementation first.")


class TODOTargetAdapter(TargetAdapter):
    def generate(self, history: list[Turn], seed: Seed) -> str:
        raise NotConfiguredAdapter(f"Target adapter '{self.name}' is a TODO. Configure a real implementation first.")


class TODOGuardAdapter(GuardAdapter):
    def check(self, history: list[Turn], current_user_message: str, seed: Seed) -> GuardDecision:
        raise NotConfiguredAdapter(f"Guard adapter '{self.name}' is a TODO. Configure a real implementation first.")


class TODOJudgeAdapter(JudgeAdapter):
    def judge_turn(self, seed: Seed, history: list[Turn], assistant_turn: Turn) -> JudgeResult:
        raise NotConfiguredAdapter(f"Judge adapter '{self.name}' is a TODO. Configure a real implementation first.")
