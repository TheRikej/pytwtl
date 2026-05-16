import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dfa import Op, DFAType
from antlr4_pipeline import parse_formula
from runtime_monitor import VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime, norm, translate


def _accepts(dfa, word):
    state = next(iter(dfa.init))
    for symbol in word:
        nxt = dfa.next_states_of_fsa(state, symbol)
        if len(nxt) != 1:
            return False
        state = nxt[0]
    return state in dfa.final


def test_optional_high_parses_and_sets_none_in_infinity_tree():
    _, dfa_inf = translate('[H^0 A]^[1]', kind='infinity')
    assert dfa_inf.tree.low == 1
    assert math.isinf(dfa_inf.tree.high)


def test_explicit_high_still_parses_and_sets_value_in_infinity_tree():
    _, dfa_inf = translate('[H^0 A]^[1,3]', kind='infinity')
    assert dfa_inf.kind == DFAType.Infinity
    assert norm('[H^0 A]^[1,3]') == (1, 3)


def test_norm_with_optional_high_returns_none_upper_bound():
    # H^0 A has bound (0, 0), so [H^0 A]^[1] yields (1, None)
    assert norm('[H^0 A]^[1]') == (1, None)


def test_invalid_trailing_comma_is_rejected_by_parser():
    with pytest.raises(ValueError):
        parse_formula('[H^0 A]^[1,]')


def test_runtime_monitor_accepts_optional_high_formula_on_witness():
    mon = monitor_runtime(formula='[H^0 A]^[1]')

    initial = mon.current()
    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == 2

    step1 = mon.step(set(['A']))
    assert step1 == (VERDICT_UNKNOWN, 1)

    step2 = mon.step(set(['A']))
    assert step2 == (VERDICT_TRUE, 0)


def test_hold_true_parses_and_builds_hold_tree():
    _, dfa_inf = translate('H^1 True', kind='infinity')
    assert norm('H^1 True') == (1, 1)
    assert dfa_inf.tree.operation == Op.hold


def test_negated_proposition_parses_as_complemented_formula():
    _, dfa_norm = translate('!A', kind='normal')
    assert _accepts(dfa_norm, [set()]) is True
    assert _accepts(dfa_norm, [{'A'}]) is False


def test_negated_parenthesized_formula_parses_and_keeps_tree():
    _, dfa_norm = translate('!(A | B)', kind='normal')
    assert _accepts(dfa_norm, [set()]) is True
    assert _accepts(dfa_norm, [{'A'}]) is False
