"""Shared helpers for the ballot theorem experiment scripts."""

import json


def theoretical_probability(a, b):
    return max(0.0, (a - b) / (a + b))


def load_parameters(path):
    with open(path) as f:
        pairs = json.load(f)
    return [(pair["a"], pair["b"]) for pair in pairs]
