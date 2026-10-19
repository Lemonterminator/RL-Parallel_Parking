"""SAC smoke rehearsal on the easy parallel scene.

This is an engineering check that the environment, reward and O0 observation can be learned
from. It is **not** Stage-2 evidence: the evaluation set below is a handful of rehearsal seeds,
not the Hybrid-A*-filtered frozen set, and hyperparameters are Stable-Baselines3 defaults
(gamma from configs/reference.json). Do not tune anything against these numbers — §8 requires the
protocol to be frozen before any tuning happens.

    python -m parking_rl.experiments.smoke_sac --steps 300000 --out runs/smoke_sac
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from collections import Counter
from pathlib import Path

import numpy as np

from parking_rl.env import ParallelParkingEnv

EVAL_SEEDS = tuple(range(10_000, 10_100))


def _commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def evaluate(model, seeds: tuple[int, ...] = EVAL_SEEDS) -> dict[str, float]:
    env = ParallelParkingEnv()
    reasons: Counter[str] = Counter()
    returns, lengths = [], []
    for seed in seeds:
        obs, _ = env.reset(seed=seed)
        total, steps, done = 0.0, 0, False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total += reward
            steps += 1
            done = terminated or truncated
        reasons[info["end_reason"]] += 1
        returns.append(total)
        lengths.append(steps)
    n = len(seeds)
    return {
        "success": reasons["success"] / n,
        "collision": reasons["collision"] / n,
        "out_of_bounds": reasons["out_of_bounds"] / n,
        "timeout": reasons["time_limit"] / n,
        "mean_return": float(np.mean(returns)),
        "mean_length": float(np.mean(lengths)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--steps", type=int, default=300_000)
    parser.add_argument("--eval-every", type=int, default=25_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--out", type=Path, default=Path("runs/smoke_sac"))
    args = parser.parse_args(argv)

    import torch
    from stable_baselines3 import SAC
    from stable_baselines3.common.callbacks import BaseCallback

    args.out.mkdir(parents=True, exist_ok=True)
    log_path = args.out / "eval_log.jsonl"
    meta = {
        "commit": _commit(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "platform": platform.platform(),
        "steps": args.steps,
        "seed": args.seed,
        "eval_seeds": [EVAL_SEEDS[0], EVAL_SEEDS[-1]],
        "note": "smoke rehearsal; SB3 SAC defaults; not Stage-2 evidence",
    }
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    started = time.time()

    class PeriodicEval(BaseCallback):
        def _on_step(self) -> bool:
            if self.num_timesteps % args.eval_every == 0:
                row = {"timesteps": self.num_timesteps, "wall_s": round(time.time() - started, 1)}
                row.update(evaluate(self.model))
                with log_path.open("a") as handle:
                    handle.write(json.dumps(row) + "\n")
                print(json.dumps(row), flush=True)
            return True

    env = ParallelParkingEnv()
    env.reset(seed=args.seed)
    model = SAC(
        "MlpPolicy",
        env,
        gamma=env.reward_config.gamma,
        seed=args.seed,
        device=args.device,
        verbose=0,
    )
    model.learn(total_timesteps=args.steps, callback=PeriodicEval())
    model.save(args.out / "model")
    final = {"timesteps": args.steps, "wall_s": round(time.time() - started, 1)}
    final.update(evaluate(model))
    (args.out / "final.json").write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps(final), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
