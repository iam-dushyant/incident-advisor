from __future__ import annotations
import argparse, json, random
from pathlib import Path
from .templates import SCENARIOS, render
from dataclasses import dataclass

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rows-per-class", type=int, default=800)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    rng = random.Random(a.seed)
    rows = []
    for scenario in SCENARIOS:
        for _ in range(a.rows_per_class):
            event = render(scenario, rng)
            event["label"] = scenario.label
            rows.append(event)

    rng.shuffle(rows)
    path = Path(a.out); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(rows)} rows to {path}")

if __name__ == "__main__":
    main()