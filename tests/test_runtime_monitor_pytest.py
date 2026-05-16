import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lomap import Fsa
from runtime_monitor import (
    RuntimeMonitor,
    VERDICT_FALSE,
    VERDICT_TRUE,
    VERDICT_UNKNOWN,
    annotate_monitor,
)
from twtl import monitor_runtime


def _mk_complete_single_prop_dfa(final_states=None):
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = set(final_states or [])
    # complete transitions over alphabet {0, 1}
    dfa.g.add_edge(0, 0, **{'weight': 0, 'input': set([0, 1]), 'guard': '(1)', 'label': '(1)'})
    return dfa


def test_annotate_leaf_accepting_state():
    dfa = _mk_complete_single_prop_dfa(final_states=[0])
    verdict, lookahead = annotate_monitor(dfa)
    assert verdict[0] == VERDICT_TRUE
    assert lookahead[0] == 0


def test_annotate_leaf_rejecting_state():
    dfa = _mk_complete_single_prop_dfa(final_states=[])
    verdict, lookahead = annotate_monitor(dfa)
    assert verdict[0] == VERDICT_FALSE
    assert lookahead[0] == 0


def test_annotate_acyclic_state_inherits_true_from_successors():
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = {1}
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': set([0, 1]), 'guard': '(1)', 'label': '(1)'})

    verdict, lookahead = annotate_monitor(dfa)
    assert verdict[1] == VERDICT_TRUE
    assert lookahead[1] == 0
    assert verdict[0] == VERDICT_TRUE
    assert lookahead[0] == 1


def test_annotate_acyclic_state_with_mixed_successors_is_unknown():
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = {1}
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': set([1]), 'guard': 'A', 'label': 'A'})
    dfa.g.add_edge(0, 2, **{'weight': 0, 'input': set([0]), 'guard': '!A', 'label': '!A'})

    verdict, lookahead = annotate_monitor(dfa)
    assert verdict[1] == VERDICT_TRUE
    assert verdict[2] == VERDICT_FALSE
    assert verdict[0] == VERDICT_UNKNOWN
    assert lookahead[0] == 2


def test_annotate_multistate_scc_is_unknown_infinite():
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = set()
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': set([0]), 'guard': '!A', 'label': '!A'})
    dfa.g.add_edge(0, 0, **{'weight': 0, 'input': set([1]), 'guard': 'A', 'label': 'A'})
    dfa.g.add_edge(1, 0, **{'weight': 0, 'input': set([0, 1]), 'guard': '(1)', 'label': '(1)'})

    verdict, lookahead = annotate_monitor(dfa)
    assert verdict[0] == VERDICT_UNKNOWN
    assert verdict[1] == VERDICT_UNKNOWN
    assert math.isinf(lookahead[0])
    assert math.isinf(lookahead[1])


def test_runtime_monitor_step_and_dead_transition_behavior():
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = {1}
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': set([1]), 'guard': 'A', 'label': 'A'})

    mon = RuntimeMonitor(dfa)
    v0, k0, s0 = mon.current()
    assert v0 == VERDICT_UNKNOWN
    assert k0 == 1
    assert s0 == 0

    v1, _ = mon.step(set(['A']))
    assert v1 == VERDICT_TRUE

    # no transition from state 1 on empty symbol -> definitive false afterwards
    v2, k2 = mon.step(set())
    assert v2 == VERDICT_FALSE
    assert k2 == 0


def test_monitor_runtime_factory_uses_provided_dfa():
    dfa = _mk_complete_single_prop_dfa(final_states=[0])
    mon = monitor_runtime(dfa=dfa)
    v, k, s = mon.current()
    assert v == VERDICT_TRUE
    assert k == 0
    assert s == 0


def test_monitor_runtime_requires_formula_or_dfa():
    with pytest.raises(Exception, match='Must provide either a TWTL formula or an automaton!'):
        monitor_runtime()
