"""Interactive, one-trial-at-a-time visualization of the Ballot Theorem.

For each (a, b) pair with theoretical probability >= --min-probability,
run trials one at a time on command. Each trial plots the running margin
(count_a - count_b) against vote number: a line that stays above zero the
whole way is a success; a line that dips to zero or below means B was in
the lead at some point.

Usage:
    python scripts/one_by_one.py parameters/<file>.json [--min-probability 0.10]

Controls (typed in the terminal while a pair is active):
    <Enter>  run another trial
    s        skip to the next (a, b) pair
    q        quit
"""

import argparse
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from ballot_common import load_parameters, theoretical_probability


def simulate_path(a, b):
    """Shuffle a ballots for A and b ballots for B; return the running
    margin (count_a - count_b) after each ballot, plus overall success."""
    votes = [1] * a + [0] * b
    random.shuffle(votes)

    count_a = count_b = 0
    margins = []
    for vote in votes:
        if vote == 1:
            count_a += 1
        else:
            count_b += 1
        margins.append(count_a - count_b)

    success = all(margin > 0 for margin in margins)
    return margins, success


def run_pair_interactively(a, b, min_probability):
    theoretical = theoretical_probability(a, b)
    if theoretical < min_probability:
        print(f"Skipping a={a} b={b}: theoretical probability {theoretical:.2%} < {min_probability:.0%}")
        return

    print(f"\n=== a={a} b={b}  theoretical={theoretical:.2%} ===")
    print("Press Enter to run a trial, 's' to skip to the next pair, 'q' to quit.")

    plt.ion()
    fig, ax = plt.subplots()
    successes = total = 0

    while True:
        command = input("> ").strip().lower()
        if command == "q":
            plt.close(fig)
            sys.exit(0)
        if command == "s":
            break

        margins, success = simulate_path(a, b)
        total += 1
        successes += success

        ax.clear()
        ax.axhline(0, color="black", linewidth=0.8)
        ax.plot(range(1, len(margins) + 1), margins, color="green" if success else "red")
        ax.set_xlabel("vote number")
        ax.set_ylabel("count_a - count_b")
        outcome = "SUCCESS" if success else "FAILED (B led at some point)"
        ax.set_title(
            f"a={a} b={b}  trial {total}  {outcome}\n"
            f"successes/total = {successes}/{total} ({successes / total:.2%})"
            f"  theoretical={theoretical:.2%}"
        )
        fig.canvas.draw()
        plt.pause(0.001)

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("parameters", type=Path, help="JSON file of {a, b} pairs")
    parser.add_argument(
        "--min-probability",
        type=float,
        default=0.10,
        help="skip pairs whose theoretical probability is below this (default 0.10)",
    )
    args = parser.parse_args()

    for a, b in load_parameters(args.parameters):
        run_pair_interactively(a, b, args.min_probability)


if __name__ == "__main__":
    main()
