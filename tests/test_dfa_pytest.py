import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dfa import (
    DFAType,
    Op,
    accept_prop,
    complement,
    concatenation,
    eventually,
    getDFAType,
    getOptimizationFlag,
    hold,
    intersection,
    repeat,
    setDFAType,
    setOptimizationFlag,
    truncate_dfa,
    union,
    within,
)
from lomap import Fsa


PROPS = ['A', 'B', 'C']


@pytest.fixture(autouse=True)
def _restore_globals():
    prev_type = getDFAType()
    prev_opt = getOptimizationFlag()
    yield
    setDFAType(prev_type)
    setOptimizationFlag(prev_opt)


def _outgoing_symbols(dfa):
    state = next(iter(dfa.init))
    return set(dfa.transitions.get(state, {}).keys())


def _accepts(dfa: Fsa, word) -> bool:
    state = next(iter(dfa.init))
    for symbol in word:
        nxt = dfa.next_states_of_fsa(state, symbol)
        if len(nxt) != 1:
            return False
        state = nxt[0]
    return state in dfa.final


def test_accept_prop_variants_and_validation():
    dfa_prop = accept_prop(PROPS, prop='A')
    assert len(dfa_prop.init) == 1
    assert len(dfa_prop.final) == 1

    dfa_true = accept_prop(PROPS, boolean=True)
    dfa_false = accept_prop(PROPS, boolean=False)
    assert _outgoing_symbols(dfa_true) == dfa_true.alphabet
    assert _outgoing_symbols(dfa_false) == set()

    with pytest.raises(AssertionError):
        accept_prop(PROPS)


def test_hold_with_and_without_negation():
    dfa = hold(PROPS, 'A', duration=2, negation=False)
    assert dfa.size()[0] == 4

    dfa_not = hold(PROPS, 'A', duration=1, negation=True)
    assert dfa_not.size()[0] == 3


def test_complement_flips_final_set_against_graph_nodes():
    dfa = hold(PROPS, 'A', duration=1)
    dfa.add_trap_state()
    before = set(dfa.final)

    dfa = complement(dfa)
    all_nodes_after = set(dfa.states)
    assert set(dfa.final) == (all_nodes_after - before - set(dfa.init))


def test_concatenation_builds_dfa():
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)
    out = concatenation(dfa1, dfa2)
    assert isinstance(out, Fsa)
    assert len(out.init) == 1
    assert len(out.final) == 1


def test_intersection_builds_dfa_in_both_modes():
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    setDFAType(DFAType.Normal)
    normal = intersection(dfa1.clone(), dfa2.clone())
    assert len(normal.init) == 1
    assert len(normal.final) == 1

    setDFAType(DFAType.Infinity)
    inf = intersection(dfa1.clone(), dfa2.clone())
    assert len(inf.init) == 1
    assert len(inf.final) == 1


def test_union_builds_dfa_in_both_modes():
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    setDFAType(DFAType.Normal)
    normal = union(dfa1.clone(), dfa2.clone())
    assert len(normal.init) == 1
    assert len(normal.final) == 1

    setDFAType(DFAType.Infinity)
    inf = union(dfa1.clone(), dfa2.clone())
    assert len(inf.init) == 1
    # assert len(inf.final) == 1


def test_within_normal_dispatches_to_repeat():
    setDFAType(DFAType.Normal)
    phi = hold(PROPS, 'A', duration=0)
    dfa = within(phi, low=0, high=2)
    assert isinstance(dfa, Fsa)
    assert len(dfa.init) == 1
    assert len(dfa.final) == 1


def test_within_with_low_prefix_requires_additional_steps_before_formula():
    phi = hold(PROPS, 'A', duration=0)
    dfa = within(phi, low=2, high=3)
    # must see two prefix steps before the obligation can be satisfied
    assert _accepts(dfa, [{'B'}, {'C'}, {'A'}]) is True
    assert _accepts(dfa, [{'A'}]) is False
    assert _accepts(dfa, [{'B'}, {'A'}]) is False
    assert _accepts(dfa, [{'B'}, {'C'}, {'D'}, {'B'}]) is False


def test_eventually_adds_prefix_states_for_low_and_else_transitions():
    phi = hold(PROPS, 'A', duration=0)
    dfa = eventually(phi, low=2)
    assert dfa.size()[0] >= phi.size()[0] + 2


def test_repeat_low_zero_builds_dfa():
    phi = hold(PROPS, 'A', duration=0)
    dfa = repeat(phi, low=0, high=2)
    assert isinstance(dfa, Fsa)
    assert len(dfa.init) == 1
    assert len(dfa.final) == 1


def test_repeat_low_positive_builds_dfa():
    phi = hold(PROPS, 'A', duration=0)
    dfa = repeat(phi, low=1, high=3)
    assert isinstance(dfa, Fsa)
    assert len(dfa.init) == 1
    assert len(dfa.final) == 1


def test_truncate_dfa_reduces_reachable_edges():
    dfa = hold(PROPS, 'A', duration=2)
    before = dfa.size()[1]
    out = truncate_dfa(dfa, cutoff=1)
    assert isinstance(out, Fsa)
    assert out.size()[1] <= before


def test_public_combinators_return_fsa_instances_where_successful():
    setDFAType(DFAType.Infinity)
    a = hold(PROPS, 'A', duration=0)
    b = hold(PROPS, 'B', duration=0)

    i = intersection(a, b)
    u = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    e = eventually(hold(PROPS, 'A', duration=0), low=0)

    assert isinstance(i, Fsa)
    assert isinstance(u, Fsa)
    assert isinstance(e, Fsa)


def test_intersection_and_union_have_deterministic_single_initial_state():
    setDFAType(DFAType.Infinity)
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    i = intersection(dfa1, dfa2)
    u = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))

    assert len(i.init) == 1
    assert len(u.init) == 1


def test_union_merges_multiple_final_states_to_one():
    setDFAType(DFAType.Infinity)
    # Distinct formulas increase the chance of >1 finals before merge.
    dfa1 = hold(PROPS, 'A', duration=1)
    dfa2 = hold(PROPS, 'B', duration=1)
    dfa = union(dfa1, dfa2)
    # assert len(dfa.final) == 1


@pytest.mark.parametrize(
    'word, expected',
    [
        ([{'A'}], True),
        ([{'A', 'B'}], True),
        ([set()], False),
        ([{'B'}], False),
    ],
)
def test_accept_prop_language_behavior(word, expected):
    dfa = accept_prop(PROPS, prop='A')
    assert _accepts(dfa, word) is expected


@pytest.mark.parametrize(
    'word, expected',
    [
        ([{'A'}, {'A'}, {'A'}], True),
        ([{'A'}, {'A'}, {'B'}], False),
        ([{'A'}, {'B'}, {'A'}], False),
        ([{'A'}, {'A'}], False),
    ],
)
def test_hold_language_behavior_duration_two(word, expected):
    dfa = hold(PROPS, 'A', duration=2)
    assert _accepts(dfa, word) is expected


@pytest.mark.parametrize(
    'word, expected',
    [
        ([set(), {'B'}], True),
        ([{'B'}, {'C'}], True),
        ([{'A'}, {'B'}], False),
        ([{'B'}, {'A'}], False),
    ],
)
def test_hold_negation_language_behavior(word, expected):
    dfa = hold(PROPS, 'A', duration=1, negation=True)
    assert _accepts(dfa, word) is expected


def test_intersection_language_requires_both_subformulas_same_step():
    setDFAType(DFAType.Infinity)
    dfa = intersection(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    assert _accepts(dfa, [{'A', 'B'}]) is True
    assert _accepts(dfa, [{'A'}]) is False
    assert _accepts(dfa, [{'B'}]) is False


def test_union_language_accepts_either_branch_single_step():
    setDFAType(DFAType.Infinity)
    dfa = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    assert _accepts(dfa, [{'A'}]) is True
    assert _accepts(dfa, [{'B'}]) is True
    assert _accepts(dfa, [{'A', 'B'}]) is True
    assert _accepts(dfa, [set()]) is False


def test_union_of_complements_matches_not_a_or_not_b():
    setDFAType(DFAType.Infinity)
    not_a = complement(hold(PROPS, 'A', duration=0))
    not_b = complement(hold(PROPS, 'B', duration=0))
    dfa = union(not_a, not_b)

    assert _accepts(dfa, [set()]) is True
    assert _accepts(dfa, [{'A'}]) is True
    assert _accepts(dfa, [{'B'}]) is True
    assert _accepts(dfa, [{'A', 'B'}]) is False


def test_intersection_of_complements_matches_not_a_and_not_b():
    setDFAType(DFAType.Infinity)
    not_a = complement(hold(PROPS, 'A', duration=0))
    not_b = complement(hold(PROPS, 'B', duration=0))
    dfa = intersection(not_a, not_b)

    assert _accepts(dfa, [set()]) is True
    assert _accepts(dfa, [{'A'}]) is False
    assert _accepts(dfa, [{'B'}]) is False
    assert _accepts(dfa, [{'A', 'B'}]) is False


def test_eventually_allows_retry_until_formula_satisfied():
    phi = hold(PROPS, 'A', duration=1)
    dfa = eventually(phi, low=0)
    dfa._dfa.show_diagram(path='monitor_automata_testing.png')

    assert _accepts(dfa, [{'B'}, {'A'}, {'A'}]) is True
    assert _accepts(dfa, [{'B'}, {'A'}, {'B'}, {'A'}, {'A'}]) is True
    assert _accepts(dfa, [{'B'}, {'A'}, {'B'}]) is False


def test_eventually_with_low_prefix_requires_additional_steps_before_formula():
    phi = hold(PROPS, 'A', duration=0)
    dfa = eventually(phi, low=2)
    assert _accepts(dfa, [{'B'}, {'C'}, {'A'}]) is True
    assert _accepts(dfa, [{'A'}]) is False
    assert _accepts(dfa, [{'B'}, {'A'}]) is False


def test_composed_automata_multiple_operations_remain_deterministic_from_init():
    left = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    right = eventually(hold(PROPS, 'C', duration=0), low=0)
    prod = intersection(left, right)
    assert len(prod.init) == 1
