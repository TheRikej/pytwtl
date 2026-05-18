import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from antlr4_pipeline import parse_formula
from runtime_monitor import VERDICT_TRUE, VERDICT_UNKNOWN
from twtl import monitor_runtime, translate


def _accepts(dfa, word):
    state = next(iter(dfa.init))
    for symbol in word:
        nxt = dfa.next_states_of_fsa(state, symbol)
        if len(nxt) != 1:
            return False
        state = nxt[0]
    return state in dfa.final



def test_invalid_trailing_comma_is_rejected_by_parser():
    with pytest.raises(ValueError):
        parse_formula('[H^0 A]^[1,]')


def test_runtime_monitor_accepts_optional_high_formula_on_witness():
    mon = monitor_runtime(formula='[H^0 A]^[1]')

    initial = mon.current()
    assert initial[0] == VERDICT_UNKNOWN
    assert initial[1] == math.inf

    step1 = mon.step(set(['A']))
    assert step1 == (VERDICT_UNKNOWN, math.inf)

    mon.visualize_graphviz(path='monitor_automata_test.png', layout='dot', show_current=True)
    step2 = mon.step(set(['A']))
    assert step2 == (VERDICT_TRUE, 0)



def test_negated_proposition_parses_as_complemented_formula():
    _, dfa_norm = translate('!A')
    assert _accepts(dfa_norm, [set()]) is True
    assert _accepts(dfa_norm, [{'A'}]) is False


def test_negated_parenthesized_formula_parses_and_keeps_tree():
    _, dfa_norm = translate('!(A | B)')
    assert _accepts(dfa_norm, [set()]) is True
    assert _accepts(dfa_norm, [{'A'}]) is False
