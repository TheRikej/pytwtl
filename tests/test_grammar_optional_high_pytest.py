import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from antlr4_pipeline import parse_formula
from runtime_monitor import VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime, norm, translate


def test_optional_high_parses_and_sets_none_in_infinity_tree():
    _, dfa_inf = translate('[H^0 A]^[1]', kind='infinity')
    assert dfa_inf.tree.low == 1
    assert dfa_inf.tree.high is None


def test_explicit_high_still_parses_and_sets_value_in_infinity_tree():
    _, dfa_inf = translate('[H^0 A]^[1,3]', kind='infinity')
    assert dfa_inf.tree.low == 1
    assert dfa_inf.tree.high == 3


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
    assert math.isinf(initial[1])

    step1 = mon.step(set())
    assert step1[0] == VERDICT_UNKNOWN

    step2 = mon.step(set(['A']))
    assert step2 == (VERDICT_TRUE, 0)
