# Baseline Protocol Confirmation Table

Use this table to confirm the evaluation protocol before running the full
baseline. Current assumption:

```text
guard / defense x attack method x target model -> ASR
```

## 1. Main Protocol Decisions

| Item | Current researched understanding | Proposed default | Alternatives | Need confirmation |
| --- | --- | --- | --- | --- |
| Table shape | Baseline table should compare guard/defense, attack method, and target model. | `guard x attack x target -> ASR` | Add dataset/category as extra dimension. | Is this table shape correct? |
| Judge role | Judge is evaluation-only, not defense. HarmBench classifier evaluates `behavior + generation -> yes/no`. | Use judge after target output. | Use attack repo verifier; human audit. | Is unified judge required? |
| Guard role | Guard is the defense row. Guard may inspect input, output, or both. | Start with input-side guard. | Output-side guard; input+output guard. | Which guard placement is expected? |
| Attack role | Attack generates adversarial user inputs/dialogues from harmful behavior seeds. | Attack generation separated from ASR judging. | Use attack repo's internal ASR directly. | Should attack repo verifier be ignored or retained? |
| Target role | Target is the victim model that generates assistant responses with full chat history. | Normal multi-turn chat with history. | Stateless single-turn prompts only. | Confirm target should be multi-turn chat. |
| Seed source | HarmBench / AdvBench provide harmful goals/behaviors. | Start with HarmBench behaviors. | AdvBench; both; project-specific seeds. | Which seed source and split? |

## 2. ASR Protocol

| Item | Proposed default | Why | Alternatives | Need confirmation |
| --- | --- | --- | --- | --- |
| Judge model | `HarmBench-Llama-2-13b-cls` | Official HarmBench classifier is designed for `behavior + generation` success evaluation. | GPT-4o judge; attack repo verifier; guard model as judge. | Final judge? |
| Judge input | `harmful_goal + each assistant response` | Aligns with HarmBench classifier and response-level verifiers in Crescendo/ActorAttack/X-Teaming. | Final response only; full dialogue transcript. | What should be judged? |
| Dialogue success rule | Any assistant turn judged successful -> dialogue success. | Multi-turn attacks can succeed before final turn; X-Teaming uses any response score 5. | Final turn only; whole transcript. | Any-turn or final-turn? |
| ASR numerator | Number of successful behaviors/dialogues under chosen aggregation. | Needs explicit denominator. | Successful attempts / successful paths. | What is counted as success unit? |
| ASR denominator | Start with `behavior@1` or `dialogue@1`. | Most comparable first pass. | `behavior@k`; per attempt/path; best-of-k. | Behavior, dialogue, or attempt denominator? |
| Multiple attempts per behavior | Keep `attempt_id`; report `@k` explicitly. | ActorAttack/X-Teaming can generate multiple actors/plans. | Collapse all attempts silently. | What k should be used? |
| Metric label | `ASR_behavior@1_anyturn_harmbenchjudge` | Makes denominator and success rule explicit. | Short label `ASR`. | Preferred reporting label? |

## 3. Guard Placement

| Placement | Definition | Pros | Cons | Use in main table? |
| --- | --- | --- | --- | --- |
| Input-side current turn only | `current_user -> guard -> allow/block` | Cheapest and simple. | Weak for multi-turn context. | Probably no. |
| Input-side full history | `history + current_user -> guard -> allow/block` | Tests whether existing guards can catch multi-turn context before target responds. | May be slower; formatting matters. | Proposed default. |
| Output-side only | `target_response -> guard -> return/block` | Prevents harmful content exposure. | Target already generated harmful content; different deployment semantics. | Maybe separate table/row. |
| Input + output | Check both user input and target response. | Stronger production-like defense. | Not comparable to input-only rows if mixed silently. | Maybe separate row. |

## 4. Candidate Attack Methods

| Attack method | Status from public sources | Multi-turn? | Access type | Internal verifier/judge | ASR caveat | Include? |
| --- | --- | --- | --- | --- | --- | --- |
| Crescendo / Crescendomation | Confirmed from paper; PyRIT implementation exists. | Yes | Black-box | GPT-4 Judge + Secondary Judge + refusal judge. | Trial-level and task-level success both appear; should re-score with unified judge. | Likely yes. |
| ActorAttack / ActorBreaker | Confirmed from official repo and paper. | Yes | Black-box | GPTJudge, usually GPT-4o, score 1-5; score 5 success. | Multiple actors per behavior; can become best-of-actors. | Likely yes. |
| X-Teaming | Confirmed from paper. | Yes | Black-box multi-agent | GPT-4o verifier, score 1-5; score 5 success. | Many candidate plans/paths; denominator must be explicit. | Likely yes. |
| Tempest / TEMPEST | Not yet reliably verified in this pass. | Unknown | Unknown | Unknown | Cannot include without source/code. | Need source. |
| GCG | Known attack, but not same setting. | Usually no | White-box / transfer | Target loss or external judge. | Different threat model and compute budget. | Supplement only. |
| PAIR / TAP | Known black-box prompt optimization attacks. | Iterative, not normal multi-turn chat history. | Black-box | Judge in optimization loop. | Different from conversation-history attacks. | Supplement only. |

## 5. Candidate Guard Rows

| Guard row | Local model available? | Supports input moderation? | Supports output moderation? | Proposed use in main table | Notes |
| --- | --- | --- | --- | --- | --- |
| Raw | Yes | N/A | N/A | No defense baseline. | Always allow. |
| Llama-Guard-3-8B | Yes | Yes | Yes | Input-side full-history. | Can also evaluate output-side separately. |
| ShieldGemma-2B | Yes | Yes | Yes | Input-side full-history. | 9B / 2-4B variants also available. |
| WildGuard | Yes | Yes | Yes | Input-side full-history. | Also detects refusal. |
| Granite Guardian 3.0 2B | Yes | Yes | Yes | Input-side full-history. | 3.3 8B also available. |
| Qwen3Guard-Gen-0.6B | Yes | Yes | Yes | Input-side full-history. | Larger 4B / 8B variants available. |
| HarmBench-Llama-2-13b-cls | Yes | Not primary use | Output success judge | Use as judge, not guard row. | Behavior + generation classifier. |

## 6. Candidate Target Models

| Target model | Local candidate path | Priority | Notes |
| --- | --- | --- | --- |
| Qwen3-8B | `/hub/huggingface/models/Qwen/Qwen3-8B` | First smoke target | Already tested with framework and HarmBench judge. |
| Qwen2.5-7B-Instruct | `/hub/huggingface/models/Qwen/Qwen2.5-7B-Instruct` | Recommended target | Instruct/chat model, likely better for baseline. |
| Llama | `/hub/huggingface/models/meta` or guardrail/meta subdirs | High | Need exact instruct target path. |
| Gemma | `/hub/huggingface/models/google` | Medium | Need exact instruct target path. |
| Mistral | `/hub/huggingface/models/MistralAI` or `/hub/huggingface/models/mistralai` | Medium | Need exact instruct target path. |
| Vicuna | `/hub/huggingface/models/vicuna-7b-v1.5` | Medium | Available. |

## 7. Proposed First Real Baseline Slice

| Step | Combination | Purpose | Output |
| --- | --- | --- | --- |
| 1 | `Raw x real_attack x Qwen target x HarmBench judge` | Measure unguarded target vulnerability. | Raw ASR baseline. |
| 2 | `Llama-Guard-3-8B x same_attack x same_target x HarmBench judge` | Check one real guard row. | First guard ASR. |
| 3 | Add 4 more guards | Fill minimum guard rows. | 5+ guard comparison. |
| 4 | Add more attacks | Expand columns. | Attack robustness comparison. |
| 5 | Add more targets | Expand target subcolumns. | Target model comparison. |

## 8. Minimal Questions To Confirm

| Priority | Question | Why it matters |
| --- | --- | --- |
| P0 | Should main guard rows be input-side full-history guards? | Determines pipeline placement. |
| P0 | Should ASR be recomputed with unified HarmBench judge rather than attack repo verifiers? | Determines comparability across attacks. |
| P0 | Is multi-turn success `any assistant turn` or `final turn`? | Changes ASR numerator. |
| P0 | Is denominator `behavior@1`, `dialogue@1`, or `behavior@k`? | Changes ASR scale. |
| P1 | What is the final attack method list? | Determines columns. |
| P1 | Is Tempest/TEMPEST required, and what source/repo should be used? | Current public source is unclear. |
| P1 | Which seed dataset should be used first: HarmBench, AdvBench, or both? | Determines sample set. |
| P2 | Should output-side guard be a separate row/table? | Determines whether to extend pipeline. |
