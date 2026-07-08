# Guard Baseline

Portable baseline framework for multi-turn jailbreak guard experiments:

`defense/guard x attack method x target model -> ASR`

The current implementation is a mock-first skeleton. It is intended to make the experiment flow reproducible before plugging in real attacks, target models, guard models, and judges.

## Experiment Flow

1. Load harmful seeds from `examples/seeds/harmful_goals_sample.jsonl`.
2. Use an `AttackAdapter` to expand each harmful goal into multi-turn user messages.
3. For each turn, call a `GuardAdapter`.
4. If allowed, call a `TargetAdapter`.
5. Judge each target response with a unified `JudgeAdapter`.
6. Mark the dialogue successful if any judged response satisfies the harmful goal.
7. Write dialogue JSONL files and an ASR table.

Default assumptions:

- Harmful seeds are goals from HarmBench / AdvBench style sources, not random seeds.
- ASR is reported as `ASR@1`.
- Success means any turn in the multi-turn dialogue is judged as satisfying the harmful goal.
- Guard input mode is full-history concatenation.
- KV cache is treated as an inference optimization detail for future real model adapters, not as a method contribution.

## Local Mock Run

From the repository root:

```bash
python -m pip install -e .
guard-baseline --config configs/default.yaml
```

Equivalent without installing:

```bash
PYTHONPATH=src python -m guard_baseline.cli --config configs/default.yaml
```

Expected outputs:

- `results/dialogues/raw__mock_crescendo__mock_llama.jsonl`
- `results/tables/asr_baseline.csv`
- `results/tables/asr_matrix.csv`

The mock target deliberately emits a marker string instead of real harmful instructions. `KeywordMockJudge` treats that marker as attack success so the pipeline can be tested deterministically.

## Configuration

All experiment choices are in `configs/default.yaml`:

- `attacks.selected`
- `targets.selected`
- `guards.selected`
- `judge.selected`
- seed path and limit
- output directory
- ASR and success-definition metadata

Model paths are intentionally not hard-coded in Python. Add local or server model paths under the relevant adapter `params`.

## Adapter Interfaces

Core interfaces live in `src/guard_baseline/adapters.py`:

- `AttackAdapter`
- `TargetAdapter`
- `GuardAdapter`
- `JudgeAdapter`

Implemented mock adapters:

- `MockCrescendoAttack`
- `MockTargetModel`
- `RawGuard`
- `KeywordMockJudge`

Real model adapters are currently represented by TODO stubs. To connect server models:

1. Implement a concrete adapter class.
2. Register it in `src/guard_baseline/registry.py`.
3. Set the config entry's `adapter` name and `params`.

Recommended first real additions:

- Target: vLLM or SGLang client for Llama/Qwen.
- Guard: Llama-Guard-3, ShieldGemma, WildGuard, Granite Guardian, Qwen3Guard.
- Judge: HarmBench-Llama-2-13b-cls as the unified default judge.

Keep attack generation separate from judging. Attack repositories should generate multi-turn dialogues; this framework should own the unified judge, ASR@k, and success definition so ASR values are comparable across attacks.

## Server Smoke Test With A Local Target

After installing `torch` and `transformers`, copy `configs/server_target_smoke.yaml` and set:

```yaml
targets:
  available:
    local_target:
      params:
        model_path: /path/to/qwen-or-llama
```

Then run on a selected GPU:

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=src python -m guard_baseline.cli --config configs/server_target_smoke.yaml
```

This still uses `RawGuard`, `MockCrescendoAttack`, and `KeywordMockJudge`; it only verifies that the framework can call a real local target model.

## Server Smoke Test With HarmBench Judge

After the local target smoke test works, run one seed with the local HarmBench judge:

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=src python -m guard_baseline.cli --config configs/server_harmbench_judge_smoke.yaml
```

This runs `RawGuard x MockCrescendoAttack x Qwen3-8B` and replaces the keyword mock judge with `HarmBench-Llama-2-13b-cls`.
