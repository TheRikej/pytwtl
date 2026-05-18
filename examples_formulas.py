"""Examples and formula language notes for PyTWTL.

Formula language (informal):
- Atomic proposition: A, B, C (symbols are case-sensitive).
- Hold: H^k A   (A must hold for k+1 steps; k=0 is a single step).
- Negation: !A, !(A | B)
- Conjunction: phi & psi
- Disjunction: phi | psi
- Concatenation: phi * psi (phi must be satisfied first, then psi)
- Within: [phi]^[a,b] (phi must be satisfied within a..b steps)
- Eventually: F(phi)

Traces are lists of sets of propositions, one set per time step:
    [ {'A'}, {'B'} ] means A holds at t=0, B holds at t=1.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from twtl import monitor_runtime, translate


def _run_monitor(formula: str, word: list[set[str]]) -> None:
    print(f"\nFormula: {formula}")
    print(f"Trace:   {word}")
    monitor = monitor_runtime(formula=formula)
    verdict, lookahead, _ = monitor.current()
    print(f"t=0 -> verdict={verdict}, lookahead={lookahead}")
    for i, symbol in enumerate(word, start=1):
        verdict, lookahead = monitor.step(symbol)
        print(f"t={i} -> verdict={verdict}, lookahead={lookahead}")


def example_basic_hold() -> None:
    formula = "H^1 A"
    word = [set(["A"]), set(["A"])]
    _run_monitor(formula, word)


def example_within_and_eventually() -> None:
    formula = "[H^0 A]^[0,2]"
    word = [set(), set(["A"])]
    _run_monitor(formula, word)

    formula_eventually = "F(A)"
    word_eventually = [set(), set(), set(["A"])]
    _run_monitor(formula_eventually, word_eventually)


def example_boolean_composition() -> None:
    formula = "(H^0 A & H^0 B) | !C"
    word = [set(["A", "B"])]
    _run_monitor(formula, word)

    word2 = [set(["C"])]
    _run_monitor(formula, word2)


def example_concatenation() -> None:
    formula = "H^0 A * (H^0 B | H^0 C)"
    word = [set(["A"]), set(["C"])]
    _run_monitor(formula, word)

    word_bad = [set(["B"]), set(["A"])]
    _run_monitor(formula, word_bad)


def example_translate_to_dfa() -> None:
    formula = "!(A | B)"
    _, dfa = translate(formula)
    print("\nTranslate example:")
    print(f"Formula: {formula}")
    print(f"DFA states: {len(dfa.states)}")


def run_all_examples() -> None:
    example_basic_hold()
    example_within_and_eventually()
    example_boolean_composition()
    example_concatenation()
    example_translate_to_dfa()


if __name__ == "__main__":
    run_all_examples()
