"""Monte Carlo verification of the Ballot Theorem.

Ballot theorem: if candidate A receives a votes and candidate B receives b
votes (a > b), and all (a+b choose a) orderings of the votes are equally
likely, the probability that A is strictly ahead of B throughout the count
is (a - b) / (a + b).

Usage:
    python scripts/experiment.py parameters/<file>.json [--trials 10000] [--output results/<file>.csv]
"""

import argparse
import csv
import random
from pathlib import Path

from ballot_common import load_parameters, theoretical_probability


def simulate_trial(a, b):
    """Shuffle a ballots for A and b ballots for B; return True if A is
    strictly ahead after every ballot is counted."""
    votes = [1] * a + [0] * b
    random.shuffle(votes)

    count_a = count_b = 0
    for vote in votes:
        if vote == 1:
            count_a += 1
        else:
            count_b += 1
        if count_a <= count_b:
            return False
    return True


def experimental_probability(a, b, trials):
    successes = sum(simulate_trial(a, b) for _ in range(trials))
    return successes / trials


def write_results(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["a", "b", "theoretical", "experimental", "difference", "trials"])
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameters", type=Path, help="JSON file of {a, b} pairs")
    parser.add_argument("--trials", type=int, default=10000, help="trials per (a, b) pair")
    parser.add_argument("--output", type=Path, default=None, help="results CSV path")
    args = parser.parse_args()

    output = args.output or Path("results") / f"{args.parameters.stem}_results.csv"

    rows = []
    for a, b in load_parameters(args.parameters):
        theoretical = round(theoretical_probability(a, b), 4)
        experimental = round(experimental_probability(a, b, args.trials), 4)
        difference = round(experimental - theoretical, 4)
        rows.append((a, b, theoretical, experimental, difference, args.trials))
        print(
            f"a={a:>6} b={b:>6}  theoretical={theoretical:.4f}  "
            f"experimental={experimental:.4f}  difference={difference:.4f}"
        )

    write_results(rows, output)
    print(f"\nWrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
