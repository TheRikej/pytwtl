import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from runtime_monitor import VERDICT_FALSE, VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime


def _run_formula_monitor(formula, word, filename=None):
    mon = monitor_runtime(formula=formula)
    if filename:
        mon.visualize(path=filename, layout='dot', show_current=True)
    initial = mon.current()
    steps = [mon.step(symbol) for symbol in word]
    return initial, steps


def _final_verdict(formula, word):
    initial, steps = _run_formula_monitor(formula, word)
    return steps[-1][0] if steps else initial[0]


def test_monitor_runtime_integration_formula_within_eventually_accepts_on_witness():
    formula = '[H^0 A]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A'])],
        [set(['A', 'B'])],
        [set(), set(['A', 'C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_formula_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0,1] | [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A'])],
        [set(['B'])],
        [set(), set(['A', 'B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_formula_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0,1] & [H^0 B]^[0,1]'
    initial, steps = _run_formula_monitor(formula, [set(['A']), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2
    assert steps[0] == (VERDICT_UNKNOWN, 1)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['B']), set(['A'])],
        [set(['A', 'B'])],
        [set(), set(['A', 'B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_optional_high_within_accepts_on_witness():
    formula = '[H^0 A]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(),set(['A'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_UNKNOWN, math.inf)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A'])],
        [set(), set(), set(['A'])],
        [set(['A']), set(), set()],
        [set(['B']), set(['A'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_optional_high_disjunction_accepts_either_branch():
    formula = '[H^0 A]^[0] | [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(), set(['B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_UNKNOWN, math.inf)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A'])],
        [set(['B'])],
        [set(), set(['A', 'B'])],
        [set(), set(), set(['B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_optional_high_conjunction_needs_both_obligations():
    formula = '[H^0 A]^[0] & [H^0 B]^[0]'
    initial, steps = _run_formula_monitor(formula, [set(['A', 'B'])])

    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf
    assert steps[0] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A']), set(['B'])],
        [set(['B']), set(['A'])],
        [set(['A']), set(), set(['B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_hold_true_accepts_any_word_of_length_two():
    formula = 'H^1 True'
    initial, steps = _run_formula_monitor(formula, [set(), set()])

    assert initial[0] == VERDICT_TRUE
    assert initial[1] == 2
    assert steps[0] == (VERDICT_TRUE, 1)
    assert steps[1] == (VERDICT_TRUE, 0)

    for word in [
        [set(['A']), set()],
        [set(['B']), set(['C'])],
        [set(['A', 'B']), set(['C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_negated_proposition():
    formula = '!A'
    mon = monitor_runtime(formula=formula)

    assert mon.current()[0] == VERDICT_UNKNOWN
    assert mon.step(set()) == (VERDICT_TRUE, 0)

    mon = monitor_runtime(formula=formula)
    assert mon.step(set(['A']))[0] == VERDICT_FALSE


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

    for word in [
        [set(['A']), set(['B'])],
        [set(['A', 'C']), set(['B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_concat_rejects_wrong_order():
    formula = 'H^0 A * H^0 B'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['B']))
    assert step1 == (VERDICT_FALSE, 0)

    for word in [
        [set(['B'])],
        [set(['B']), set(['A'])],
        [set(), set(['B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_FALSE


def test_monitor_runtime_integration_concat_with_disjunction_accepts_alternative():
    formula = 'H^0 A * (H^0 B | H^0 C)'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['A']))
    assert step1 == (VERDICT_UNKNOWN, 1)

    step2 = mon.step(set(['C']))
    assert step2 == (VERDICT_TRUE, 0)

    for word in [
        [set(['A']), set(['B'])],
        [set(['A']), set(['C'])],
        [set(['A', 'B']), set(['C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_accepts_symbol_with_extra_props():
    formula = 'H^0 A'
    mon = monitor_runtime(formula=formula)

    step1 = mon.step(set(['A', 'B']))
    assert step1 == (VERDICT_TRUE, 0)

    for word in [
        [set(['A', 'C'])],
        [set(['A', 'B', 'C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE


def test_monitor_runtime_integration_complex_nested_boolean_combo():
    formula = '(H^0 A & H^0 B) | (!C * H^0 A)'

    for word in [
        [set(['A', 'B'])],
        [set(['A', 'B', 'C'])],
        [set(['A']), set(['A'])],
        [set(), set(['A'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE
    for word in [
        [set(['C'])],
        [set(['A', 'C'])],
        [set(['C']), set(['A'])],
        [set(['B', 'C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_FALSE
    
    for word in [
        [set()],
        [set(['A'])],
        [set(['B'])],
  
    ]:
        assert _final_verdict(formula, word) == VERDICT_UNKNOWN


def test_monitor_runtime_integration_complex_concat_within_and_disjunction():
    formula = '([H^0 A]^[0,2] * (H^0 B | H^0 C))'

    for word in [
        [set(['A']), set(['B'])],
        [set(), set(['A']), set(['C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE

    for word in [
        [set(['A', 'D']), set(), set(['B'])],
        [set(), set(), set(['B'])],
        [set(['A']), set(), set(), set(['C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_FALSE
    
    for word in [
        [set(['C'])],
        [set(['A'])],
        [set(), set(['A'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_UNKNOWN


def test_monitor_runtime_integration_de_morgan_style_composition():
    formula = '!(H^0 A | H^0 B) & !(H^0 C)'

    for word in [
        [set()],
        [set(['D'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE

    for word in [
        [set(['A', 'B', 'C'])],
        [set(['A'])],
        [set(['B'])],
        [set(['C'])],
        [set(['A', 'C'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_FALSE


def test_monitor_runtime_integration_mixed_eventually_concat_and_negation():
    formula = 'F(A) * (!B | H^0 C)'

    for word in [
        [set(['A']), set()],
        [set(), set(['A']), set(['C'])],
        [set(), set(['A']), set(['D'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_TRUE

    for word in [
        [set(['A']), set(['B'])],
        [set(), set(['A']), set(['B'])],
    ]:
        assert _final_verdict(formula, word) == VERDICT_FALSE
