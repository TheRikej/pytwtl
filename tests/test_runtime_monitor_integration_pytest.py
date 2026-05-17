import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from runtime_monitor import VERDICT_FALSE, VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime


def _run_formula_monitor(formula, word, filename=None):
    mon = monitor_runtime(formula=formula)
    if filename:
        mon.visualize_graphviz(path=filename, layout='dot', show_current=True)
    initial = mon.current()
    steps = [mon.step(symbol) for symbol in word]
    return initial, steps


def test_monitor_runtime_integration_formula_within_eventually_accepts_on_witness():
    formula = '[H^0 A]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_formula_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0,1] | [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_formula_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0,1] & [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(['A']), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_within_accepts_on_witness():
    formula = '[H^0 A]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(),set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_UNKNOWN, math.inf)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0] | [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_UNKNOWN, math.inf)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0] & [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(['A', 'B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_hold_true_accepts_any_word_of_length_two():
    formula = 'H^1 True'
    initial, steps = _run_formula_monitor(formula, [set(), set()])

    assert initial[0] == VERDICT_TRUE
    assert initial[1] == 2
    assert steps[0] == (VERDICT_TRUE, 1)
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_negated_proposition_is_immediately_decidable():
    formula = '!A'
    mon = monitor_runtime(formula=formula)

    assert mon.current()[0] == VERDICT_TRUE
    assert mon.step(set()) == (VERDICT_TRUE, 0)

    mon = monitor_runtime(formula=formula)
    assert mon.step(set(['A']))[0] == VERDICT_TRUE


def test_monitor_runtime_integration_concat_sequence_lookahead_decreases():
    formula = 'H^0 A * H^0 B'
    mon = monitor_runtime(formula=formula)

    initial = mon.current()
    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2

    step1 = mon.step(set(['A']))
    assert step1 == (VERDICT_UNKNOWN, 1)

    step2 = mon.step(set(['B']))
    assert step2 == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_concat_rejects_wrong_order():
    formula = 'H^0 A * H^0 B'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['B']))
    assert step1 == (VERDICT_FALSE, 0)


def test_monitor_runtime_integration_concat_with_disjunction_accepts_alternative():
    formula = 'H^0 A * (H^0 B | H^0 C)'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['A']))
    assert step1 == (VERDICT_UNKNOWN, 1)

    step2 = mon.step(set(['C']))
    assert step2 == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_accepts_symbol_with_extra_props():
    formula = 'H^0 A'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['A', 'B']))
    assert step1 == (VERDICT_TRUE, 0)
