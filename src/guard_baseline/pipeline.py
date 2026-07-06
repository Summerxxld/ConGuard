from __future__ import annotations

from pathlib import Path
from typing import Any

from guard_baseline.adapters import AttackAdapter, GuardAdapter, JudgeAdapter, TargetAdapter
from guard_baseline.io import load_seeds, write_asr_matrix, write_asr_table, write_dialogues
from guard_baseline.registry import build_attack, build_guard, build_judge, build_target
from guard_baseline.schema import DialogueRecord, ExperimentResult, Seed, Turn


def run_dialogue(
    *,
    experiment_id: str,
    seed: Seed,
    attack: AttackAdapter,
    target: TargetAdapter,
    guard: GuardAdapter,
    judge: JudgeAdapter,
    max_turns: int,
    guard_input_mode: str,
) -> DialogueRecord:
    turns: list[Turn] = []
    guard_decisions = []
    judge_results = []

    user_messages = attack.generate_user_turns(seed)[:max_turns]
    for user_message in user_messages:
        decision = guard.check(turns, user_message, seed)
        guard_decisions.append(decision)
        turns.append(
            Turn(
                turn_index=len(turns),
                role="user",
                content=user_message,
                metadata={"guard_allowed": decision.allowed, "guard_input_mode": guard_input_mode},
            )
        )
        if not decision.allowed:
            assistant_text = decision.reason or "Blocked by guard."
            turns.append(Turn(turn_index=len(turns), role="assistant", content=assistant_text, metadata={"blocked": True}))
            continue

        assistant_text = target.generate(turns, seed)
        assistant_turn = Turn(turn_index=len(turns), role="assistant", content=assistant_text)
        turns.append(assistant_turn)
        judge_results.append(judge.judge_turn(seed, turns, assistant_turn))

    success = any(result.success for result in judge_results)
    return DialogueRecord(
        experiment_id=experiment_id,
        seed=seed,
        attack_name=attack.name,
        target_name=target.name,
        guard_name=guard.name,
        turns=turns,
        guard_decisions=guard_decisions,
        judge_results=judge_results,
        success=success,
        metadata={
            "success_definition": "any_turn_harmful_goal_satisfied",
            "guard_input_mode": guard_input_mode,
        },
    )


def run_experiment(config: dict[str, Any], config_dir: str | Path = ".") -> list[ExperimentResult]:
    root = Path(config_dir)
    experiment_cfg = config["experiment"]
    experiment_id = str(experiment_cfg["name"])
    output_dir = Path(str(experiment_cfg.get("output_dir", "results")))
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    seeds_cfg = config["seeds"]
    seeds_path = Path(str(seeds_cfg["path"]))
    if not seeds_path.is_absolute():
        seeds_path = root / seeds_path
    seeds = load_seeds(seeds_path, limit=seeds_cfg.get("limit"))

    attack_names = config["attacks"]["selected"]
    target_names = config["targets"]["selected"]
    guard_names = config["guards"]["selected"]
    judge_name = config["judge"]["selected"]
    judge = build_judge(judge_name, config["judge"]["available"][judge_name])

    max_turns = int(experiment_cfg.get("max_turns", 10))
    asr_k = int(experiment_cfg.get("asr_k", 1))
    guard_input_mode = str(experiment_cfg.get("guard_input_mode", "full_history_concatenation"))

    results: list[ExperimentResult] = []
    for guard_name in guard_names:
        guard = build_guard(guard_name, config["guards"]["available"][guard_name])
        for attack_name in attack_names:
            attack = build_attack(attack_name, config["attacks"]["available"][attack_name])
            for target_name in target_names:
                target = build_target(target_name, config["targets"]["available"][target_name])
                records = [
                    run_dialogue(
                        experiment_id=experiment_id,
                        seed=seed,
                        attack=attack,
                        target=target,
                        guard=guard,
                        judge=judge,
                        max_turns=max_turns,
                        guard_input_mode=guard_input_mode,
                    )
                    for seed in seeds
                ]
                successes = sum(1 for record in records if record.success)
                total = len(records)
                result = ExperimentResult(
                    experiment_id=experiment_id,
                    attack_name=attack_name,
                    target_name=target_name,
                    guard_name=guard_name,
                    total=total,
                    successes=successes,
                    asr=(successes / total) if total else 0.0,
                    asr_k=asr_k,
                    metadata={"success_definition": experiment_cfg.get("success_definition")},
                )
                results.append(result)

                dialogue_path = output_dir / "dialogues" / f"{guard_name}__{attack_name}__{target_name}.jsonl"
                write_dialogues(dialogue_path, records)

    write_asr_table(output_dir / "tables" / "asr_baseline.csv", results)
    write_asr_matrix(output_dir / "tables" / "asr_matrix.csv", results)
    return results
