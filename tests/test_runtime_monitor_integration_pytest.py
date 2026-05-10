import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from runtime_monitor import VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime


def _run_formula_monitor(formula, word):
    mon = monitor_runtime(formula=formula)
    initial = mon.current()
    steps = [mon.step(symbol) for symbol in word]
    return initial, steps


def test_monitor_runtime_integration_formula_within_eventually_accepts_on_witness():
    formula = '[H^0 A]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_formula_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0,1] | [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_formula_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0,1] & [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(['A']), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_within_accepts_on_witness():
    formula = '[H^0 A]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0] | [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)


def test_monitor_runtime_integration_optional_high_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0] & [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(['A']), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert math.isinf(initial[1])
    assert steps[0][0] == VERDICT_UNKNOWN
    assert math.isinf(steps[0][1])
    assert steps[1] == (VERDICT_TRUE, 0)
