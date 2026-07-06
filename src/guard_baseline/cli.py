from __future__ import annotations

import argparse
from pathlib import Path

from guard_baseline.config import load_config
from guard_baseline.pipeline import run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multi-turn guard baseline experiments.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_config(config_path)
    results = run_experiment(config, config_dir=config_path.parent.parent if config_path.parent.name == "configs" else Path("."))
    for result in results:
        print(
            f"{result.guard_name} x {result.attack_name} x {result.target_name}: "
            f"ASR={result.asr:.3f} ({result.successes}/{result.total})"
        )


if __name__ == "__main__":
    main()
