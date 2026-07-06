from __future__ import annotations

from typing import Any

from guard_baseline.adapters import AttackAdapter, GuardAdapter, JudgeAdapter, TargetAdapter
from guard_baseline.mock_adapters import KeywordMockJudge, MockCrescendoAttack, MockTargetModel, RawGuard
from guard_baseline.model_stubs import TODOAttackAdapter, TODOGuardAdapter, TODOJudgeAdapter, TODOTargetAdapter


ATTACK_ADAPTERS: dict[str, type[AttackAdapter]] = {
    "MockCrescendoAttack": MockCrescendoAttack,
    "TODO": TODOAttackAdapter,
}

TARGET_ADAPTERS: dict[str, type[TargetAdapter]] = {
    "MockTargetModel": MockTargetModel,
    "TODO": TODOTargetAdapter,
}

GUARD_ADAPTERS: dict[str, type[GuardAdapter]] = {
    "RawGuard": RawGuard,
    "TODO": TODOGuardAdapter,
}

JUDGE_ADAPTERS: dict[str, type[JudgeAdapter]] = {
    "KeywordMockJudge": KeywordMockJudge,
    "TODO": TODOJudgeAdapter,
}


def _build(registry: dict[str, Any], kind: str, name: str, spec: dict[str, Any]) -> Any:
    adapter_name = spec.get("adapter")
    if not isinstance(adapter_name, str):
        raise ValueError(f"{kind} '{name}' must define an adapter name.")
    adapter_cls = registry.get(adapter_name)
    if adapter_cls is None:
        raise ValueError(f"Unknown {kind} adapter '{adapter_name}' for '{name}'.")
    params = spec.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError(f"{kind} '{name}' params must be a mapping.")
    return adapter_cls(name=name, **params)


def build_attack(name: str, spec: dict[str, Any]) -> AttackAdapter:
    return _build(ATTACK_ADAPTERS, "attack", name, spec)


def build_target(name: str, spec: dict[str, Any]) -> TargetAdapter:
    return _build(TARGET_ADAPTERS, "target", name, spec)


def build_guard(name: str, spec: dict[str, Any]) -> GuardAdapter:
    return _build(GUARD_ADAPTERS, "guard", name, spec)


def build_judge(name: str, spec: dict[str, Any]) -> JudgeAdapter:
    return _build(JUDGE_ADAPTERS, "judge", name, spec)
