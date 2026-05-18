import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dfa import (
    hold,
    minimize_dfa,
    relabel_dfa,
)
from lomap import Fsa


PROPS = ['A', 'B', 'C']



def _accepts(dfa, word):
    state = next(iter(dfa.init))
    for symbol in word:
        nxt = dfa.next_states_of_fsa(state, symbol)
        if len(nxt) != 1:
            return False
        state = nxt[0]
    return state in dfa.final


def _build_redundant_final_sink_dfa():
    dfa = Fsa(['A'], directed=True, multi=False)
    # states: 0(init), 1(final sink), 2(final sink, equivalent to 1), 99(unreachable)
    dfa.init = {0: 1}
    dfa.final = {1, 2}
    dfa.add_transition_symbols(0, {2}, 1)
    dfa.add_transition_symbols(0, {1}, 2)
    dfa.add_transition_symbols(1, {2, 1}, 1)
    dfa.add_transition_symbols(2, {2, 1}, 2)
    dfa.add_transition_symbols(99, {2, 1}, 99)
    return dfa


def test_relabel_dfa_copy_and_inplace_modes():
    dfa = hold(PROPS, 'A', duration=1)

    copied = relabel_dfa(dfa, mapping={0: 10}, start=20, copy=True)
    assert copied is not dfa
    assert 10 in copied.states

    relabel_dfa(dfa, start=100, copy=False)
    assert min(dfa.states) >= 100


def test_relabel_dfa_copy_then_inplace_in_infinity_mode_keeps_original_tree_valid():
    dfa = hold(PROPS, 'A', duration=1)
    relabel_dfa(dfa, mapping={0: 10}, start=20, copy=True)
    relabel_dfa(dfa, start=100, copy=False)
    assert min(dfa.states) >= 100


def test_minimize_dfa_merges_equivalent_states_and_removes_unreachable():
    dfa = _build_redundant_final_sink_dfa()
    minimized = minimize_dfa(dfa)
    assert isinstance(minimized, Fsa)
    assert minimized is not dfa
    assert minimized.size()[0] == 2
    assert len(minimized.init) == 1
    assert len(minimized.final) == 1


def test_minimize_dfa_preserves_language_on_representative_words():
    dfa = _build_redundant_final_sink_dfa()
    minimized = minimize_dfa(dfa)
    words = [
        [set()],
        [{'A'}],
        [set(), {'A'}],
        [{'A'}, set(), {'A'}],
    ]
    for w in words:
        assert _accepts(dfa, w) == _accepts(minimized, w)


def test_minimize_dfa_keeps_non_equivalent_chain_structure_for_hold():
    dfa = hold(PROPS, 'A', duration=3)
    minimized = minimize_dfa(dfa)
    assert minimized.size()[0] == dfa.size()[0]
    assert minimized.size()[1] == dfa.size()[1]


def test_relabel_dfa_preserves_init_and_final_cardinality():
    dfa = hold(PROPS, 'A', duration=2)
    out = relabel_dfa(dfa, start=10, copy=True)
    assert len(out.init) == len(dfa.init) == 1
    assert len(out.final) == len(dfa.final) == 1