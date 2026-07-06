from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from guard_baseline.schema import DialogueRecord, ExperimentResult, Seed, to_dict


def read_jsonl(path: str | Path) -> list[dict[str, object]]:
    jsonl_path = Path(path)
    rows: list[dict[str, object]] = []
    with jsonl_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object at {jsonl_path}:{line_number}")
            rows.append(row)
    return rows


def load_seeds(path: str | Path, limit: int | None = None) -> list[Seed]:
    rows = read_jsonl(path)
    seeds = [
        Seed(
            seed_id=str(row["seed_id"]),
            source=str(row["source"]),
            harmful_goal=str(row["harmful_goal"]),
            category=str(row["category"]) if row.get("category") is not None else None,
            metadata={k: v for k, v in row.items() if k not in {"seed_id", "source", "harmful_goal", "category"}},
        )
        for row in rows
    ]
    return seeds[:limit] if limit else seeds


def write_dialogues(path: str | Path, records: Iterable[DialogueRecord]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(to_dict(record), ensure_ascii=False) + "\n")


def write_asr_table(path: str | Path, results: Iterable[ExperimentResult]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["experiment_id", "guard", "attack", "target", "asr", "successes", "total", "asr_k"]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "experiment_id": result.experiment_id,
                    "guard": result.guard_name,
                    "attack": result.attack_name,
                    "target": result.target_name,
                    "asr": f"{result.asr:.6f}",
                    "successes": result.successes,
                    "total": result.total,
                    "asr_k": result.asr_k,
                }
            )


def write_asr_matrix(path: str | Path, results: Iterable[ExperimentResult]) -> None:
    result_list = list(results)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    guards = sorted({result.guard_name for result in result_list})
    columns = sorted({f"{result.attack_name}__{result.target_name}" for result in result_list})
    values = {
        (result.guard_name, f"{result.attack_name}__{result.target_name}"): f"{result.asr:.6f}"
        for result in result_list
    }

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["guard", *columns])
        for guard in guards:
            writer.writerow([guard, *[values.get((guard, column), "") for column in columns]])
