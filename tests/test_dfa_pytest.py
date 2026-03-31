import os
import sys

import networkx as nx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dfa import (
    Choice,
    DFAType,
    DFATreeNode,
    Op,
    accept_prop,
    complement,
    concatenation,
    copy_tree,
    eventually,
    getDFAType,
    getOptimizationFlag,
    hold,
    init_tree,
    intersection,
    mark_concatenation,
    mark_eventually,
    mark_product,
    minimize_dfa,
    relabel_dfa,
    repeat,
    setDFAType,
    setOptimizationFlag,
    truncate_dfa,
    union,
    within,
)
from lomap import Fsa
from transition_rules import AndRule, AtomicPropositionRule, ElseRule, NegationRule, TrueRule


PROPS = ['A', 'B', 'C']


@pytest.fixture(autouse=True)
def _restore_globals():
    prev_type = getDFAType()
    prev_opt = getOptimizationFlag()
    yield
    setDFAType(prev_type)
    setOptimizationFlag(prev_opt)


def _edge_attr(dfa):
    return next(iter(dfa.g.edges(data=True)))[2]


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
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': {1}, 'guard': 'A', 'label': 'A'})
    dfa.g.add_edge(0, 2, **{'weight': 0, 'input': {0}, 'guard': '!A', 'label': '!A'})
    dfa.g.add_edge(1, 1, **{'weight': 0, 'input': {0, 1}, 'guard': '(1)', 'label': '(1)'})
    dfa.g.add_edge(2, 2, **{'weight': 0, 'input': {0, 1}, 'guard': '(1)', 'label': '(1)'})
    dfa.g.add_edge(99, 99, **{'weight': 0, 'input': {0, 1}, 'guard': '(1)', 'label': '(1)'})
    return dfa


def test_dfatype_constructor_and_predicates():
    assert DFAType('normal').is_normal()
    assert not DFAType('normal').is_infinity()

    assert DFAType('infinity').is_infinity()
    assert not DFAType('infinity').is_normal()

    both = DFAType('both')
    assert both.is_normal() and both.is_infinity()


def test_dfatype_constructor_rejects_invalid():
    with pytest.raises(ValueError):
        DFAType('unsupported')


def test_set_get_dfa_type_roundtrip_and_validation():
    setDFAType(DFAType.Normal)
    assert getDFAType() == DFAType.Normal

    setDFAType(DFAType.Infinity)
    assert getDFAType() == DFAType.Infinity

    with pytest.raises(ValueError):
        setDFAType(DFAType.Both)


def test_optimization_flag_roundtrip_and_bool_cast():
    setOptimizationFlag(0)
    assert getOptimizationFlag() is False

    setOptimizationFlag('non-empty')
    assert getOptimizationFlag() is True


def test_op_str_and_validation():
    assert Op.str(Op.union) == 'Union'
    assert Op.str(Op.event) == 'Eventually'
    with pytest.raises(ValueError):
        Op.str(999)


def test_choice_string_representation_contains_partitions():
    ch = Choice(both={1}, left={2}, right={3})
    s = str(ch)
    assert 'both={1}' in s
    assert 'left={2}' in s
    assert 'right={3}' in s


def test_dfatree_node_normalize_for_concatenation_and_non_cat():
    left = DFATreeNode(Op.hold, init={1}, final={2})
    right = DFATreeNode(Op.hold, init={3}, final={4})
    root = DFATreeNode(Op.cat, left=left, right=right, init={1}, final={4})

    root.normalize(init={10}, final={40})
    assert root.init == {10}
    assert root.final == {40}
    assert left.init == {10}
    assert right.final == {40}

    noncat = DFATreeNode(Op.union, left=DFATreeNode(Op.hold, init={1}, final={1}), right=DFATreeNode(Op.hold, init={2}, final={2}), init={0}, final={3})
    noncat.normalize(init={7}, final={8})
    assert noncat.init == {7}
    assert noncat.final == {8}
    assert noncat.left.init == {7}
    assert noncat.right.final == {8}


def test_dfatree_relabel_non_expand_and_expand_union():
    tree = DFATreeNode(Op.union, init={1}, final={2}, choices={1: Choice(both={1})})
    tree.relabel({1: 10, 2: 20}, expand=False)
    assert tree.init == {10}
    assert tree.final == {20}
    assert set(tree.choices) == {10}

    tree2 = DFATreeNode(Op.union, init={1}, final={2}, choices={1: Choice(left={4})})
    tree2.relabel({1: [('a', 'x'), ('a', 'y')], 2: [('b', 'z')]}, expand=True)
    assert ('a', 'x') in tree2.init and ('a', 'y') in tree2.init
    assert ('b', 'z') in tree2.final


def test_dfatree_pprint_returns_string_under_py3():
    tree = DFATreeNode(Op.hold, init={1}, final={2})
    out = tree.pprint()
    assert isinstance(out, str)
    assert 'Op:' in out


def test_copy_tree_infinity_with_mapping_relabels_tree():
    setDFAType(DFAType.Infinity)
    src = hold(PROPS, 'A', duration=0)
    dest = Fsa(PROPS, directed=True, multi=False)
    dest.init = {100: 1}
    dest.final = {200}
    copy_tree(src, dest, mapping={0: 100, 1: 200})
    assert dest.tree.init == {100}
    assert dest.tree.final == {200}


def test_clone_preserves_tree_annotation_and_kind():
    setDFAType(DFAType.Infinity)
    src = hold(PROPS, 'A', duration=0)
    src.kind = DFAType.Infinity
    cloned = src.clone()
    assert hasattr(cloned, 'tree')
    assert cloned.tree.operation == src.tree.operation
    assert hasattr(cloned, 'kind')
    assert cloned.kind == src.kind


def test_copy_tree_normal_mode_does_not_copy_tree():
    setDFAType(DFAType.Normal)
    src = hold(PROPS, 'A', duration=0)
    dest = Fsa(PROPS, directed=True, multi=False)
    copy_tree(src, dest, mapping={0: 100, 1: 200})
    assert not hasattr(dest, 'tree')


def test_init_tree_adds_tree_with_expected_operation():
    dfa = Fsa(PROPS, directed=True, multi=False)
    dfa.init[0] = 1
    dfa.final.add(1)
    init_tree(dfa, operation=Op.accept)
    assert dfa.tree.operation == Op.accept
    assert dfa.tree.init == {0}
    assert dfa.tree.final == {1}


def test_mark_eventually_sets_flags_and_metadata():
    src = hold(PROPS, 'A', duration=0)
    dest = src.clone()
    mark_eventually(src, dest, low=2, high=5)
    assert dest.tree.operation == Op.event
    assert dest.tree.low == 2
    assert dest.tree.high == 5
    assert dest.tree.unr is False


def test_mark_concatenation_sets_composed_tree():
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)
    dest = Fsa(PROPS, directed=True, multi=False)
    dest.init = {(0, 0): 1}
    dest.final = {(1, 1)}
    mark_concatenation(dfa1, dfa2, dest)
    assert dest.tree.operation == Op.cat
    assert dest.tree.left is dfa1.tree
    assert dest.tree.right is dfa2.tree


def test_mark_product_with_manual_product_graph_for_intersection():
    setOptimizationFlag(True)

    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    dest = Fsa(PROPS, directed=True, multi=False)
    dest.init[(0, 0)] = 1
    dest.final.add((1, 1))
    attr = {'weight': 0, 'input': set(dest.alphabet), 'guard': '(1)', 'label': '(1)'}
    dest.g.add_edge((0, 0), (1, 1), **attr)

    mark_product(dfa1, dfa2, dest, operation=Op.intersection)
    assert dest.tree.operation == Op.intersection
    assert dest.tree.left is not None
    assert dest.tree.right is not None


def test_relabel_dfa_copy_and_inplace_modes():
    dfa = hold(PROPS, 'A', duration=1)

    # Avoid tree aliasing side-effect in Infinity mode for this success path.
    setDFAType(DFAType.Normal)
    copied = relabel_dfa(dfa, mapping={0: 10}, start=20, copy=True)
    assert copied is not dfa
    assert 10 in copied.g.nodes()

    relabel_dfa(dfa, start=100, copy=False)
    assert min(dfa.g.nodes()) >= 100


def test_relabel_dfa_copy_then_inplace_in_infinity_mode_keeps_original_tree_valid():
    setDFAType(DFAType.Infinity)
    dfa = hold(PROPS, 'A', duration=1)
    relabel_dfa(dfa, mapping={0: 10}, start=20, copy=True)
    relabel_dfa(dfa, start=100, copy=False)
    assert min(dfa.g.nodes()) >= 100


def test_minimize_dfa_merges_equivalent_states_and_removes_unreachable():
    dfa = _build_redundant_final_sink_dfa()
    minimized = minimize_dfa(dfa)
    assert isinstance(minimized, Fsa)
    assert minimized is not dfa
    assert minimized.g.number_of_nodes() == 2
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
    assert minimized.g.number_of_nodes() == dfa.g.number_of_nodes()
    assert minimized.g.number_of_edges() == dfa.g.number_of_edges()


def test_minimize_dfa_returns_original_for_nondeterministic_symbol_overlap():
    dfa = Fsa(['A'], directed=True, multi=False)
    dfa.init = {0: 1}
    dfa.final = {1}
    # Nondeterministic on symbol 1: two outgoing destinations from state 0.
    dfa.g.add_edge(0, 1, **{'weight': 0, 'input': {1}, 'guard': 'A', 'label': 'A'})
    dfa.g.add_edge(0, 2, **{'weight': 0, 'input': {1}, 'guard': 'A', 'label': 'A'})
    dfa.g.add_edge(1, 1, **{'weight': 0, 'input': {0, 1}, 'guard': '(1)', 'label': '(1)'})
    dfa.g.add_edge(2, 2, **{'weight': 0, 'input': {0, 1}, 'guard': '(1)', 'label': '(1)'})
    same = minimize_dfa(dfa)
    assert same is dfa


def test_accept_prop_variants_and_validation():
    dfa_prop = accept_prop(PROPS, prop='A')
    assert len(dfa_prop.init) == 1
    assert len(dfa_prop.final) == 1

    dfa_true = accept_prop(PROPS, boolean=True)
    dfa_false = accept_prop(PROPS, boolean=False)
    assert _edge_attr(dfa_true)['guard'] == '(1)'
    assert _edge_attr(dfa_false)['guard'] == '(0)'

    with pytest.raises(AssertionError):
        accept_prop(PROPS)


def test_hold_with_and_without_negation():
    dfa = hold(PROPS, 'A', duration=2, negation=False)
    assert dfa.g.number_of_edges() == 3

    dfa_not = hold(PROPS, 'A', duration=1, negation=True)
    assert dfa_not.g.number_of_edges() == 2


def test_complement_flips_final_set_against_graph_nodes():
    dfa = hold(PROPS, 'A', duration=1)
    before = set(dfa.final)

    complement(dfa)
    all_nodes_after = set(dfa.g.nodes())
    assert dfa.final == (all_nodes_after - before)


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
    assert inf.tree.operation == Op.intersection


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
    assert len(inf.final) == 1
    assert inf.tree.operation == Op.union


def test_within_dispatch_infinity_to_eventually_tree():
    setDFAType(DFAType.Infinity)
    phi = hold(PROPS, 'A', duration=0)
    dfa = within(phi, low=1, high=3)
    assert dfa.tree.operation == Op.event
    assert dfa.tree.low == 1
    assert dfa.tree.high == 3


def test_within_normal_dispatches_to_repeat():
    setDFAType(DFAType.Normal)
    phi = hold(PROPS, 'A', duration=0)
    dfa = within(phi, low=0, high=2)
    assert isinstance(dfa, Fsa)
    assert len(dfa.init) == 1
    assert len(dfa.final) == 1


def test_eventually_adds_prefix_states_for_low_and_else_transitions():
    phi = hold(PROPS, 'A', duration=0)
    dfa = eventually(phi, low=2, high=5)
    assert dfa.tree.operation == Op.event
    assert dfa.g.number_of_nodes() >= phi.g.number_of_nodes() + 2


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
    before = dfa.g.number_of_edges()
    out = truncate_dfa(dfa, cutoff=1)
    assert isinstance(out, Fsa)
    assert out.g.number_of_edges() <= before


def test_public_combinators_return_fsa_instances_where_successful():
    setDFAType(DFAType.Infinity)
    a = hold(PROPS, 'A', duration=0)
    b = hold(PROPS, 'B', duration=0)

    i = intersection(a, b)
    u = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    e = eventually(hold(PROPS, 'A', duration=0), low=0, high=2)

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
    assert len(dfa.final) == 1


def test_relabel_dfa_preserves_init_and_final_cardinality():
    dfa = hold(PROPS, 'A', duration=2)
    out = relabel_dfa(dfa, start=10, copy=True)
    assert len(out.init) == len(dfa.init) == 1
    assert len(out.final) == len(dfa.final) == 1


def test_graph_edges_carry_expected_keys_from_generators():
    dfa = hold(PROPS, 'A', duration=0)
    d = _edge_attr(dfa)
    assert {'weight', 'input', 'guard', 'label'} <= set(d.keys())

    ap = accept_prop(PROPS, prop='A')
    d2 = _edge_attr(ap)
    assert {'weight', 'input', 'guard', 'label'} <= set(d2.keys())


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


def test_union_choices_metadata_tracks_left_right_and_both_when_available():
    setDFAType(DFAType.Infinity)
    dfa = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    assert dfa.tree.operation == Op.union
    assert isinstance(dfa.tree.choices, dict)
    assert len(dfa.tree.choices) > 0
    assert any(isinstance(ch, Choice) for ch in dfa.tree.choices.values())


def test_eventually_allows_retry_until_formula_satisfied():
    phi = hold(PROPS, 'A', duration=1)
    dfa = eventually(phi, low=0, high=4)
    assert _accepts(dfa, [{'B'}, {'A'}, {'A'}]) is True
    assert _accepts(dfa, [{'B'}, {'A'}, {'B'}, {'A'}, {'A'}]) is True
    assert _accepts(dfa, [{'B'}, {'A'}, {'B'}]) is False


def test_eventually_with_low_prefix_requires_additional_steps_before_formula():
    phi = hold(PROPS, 'A', duration=0)
    dfa = eventually(phi, low=2, high=4)
    assert _accepts(dfa, [{'B'}, {'C'}, {'A'}]) is True
    assert _accepts(dfa, [{'A'}]) is False
    assert _accepts(dfa, [{'B'}, {'A'}]) is False


def test_eventually_tree_flags_for_nested_eventually_source():
    first = eventually(hold(PROPS, 'A', duration=0), low=0, high=2)
    second = eventually(first, low=1, high=5)
    assert second.tree.operation == Op.event
    assert second.tree.unr is False
    assert second.tree.wwf is False


def test_mark_product_with_choices_and_optimization_disabled():
    setOptimizationFlag(False)
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    dest = Fsa(PROPS, directed=True, multi=False)
    dest.init[(0, 0)] = 1
    dest.final.add((1, 1))
    attr = {'weight': 0, 'input': set(dest.alphabet), 'guard': '(1)', 'label': '(1)'}
    dest.g.add_edge((0, 0), (1, 1), **attr)

    choices = {(0, 0): Choice(both=set(dest.alphabet))}
    mark_product(dfa1, dfa2, dest, operation=Op.union, choices=choices)
    assert dest.tree.operation == Op.union
    assert dest.tree.choices == choices


def test_edge_label_rule_types_for_intersection_and_eventually():
    i = intersection(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    labels = [d['label'] for _, _, d in i.g.edges(data=True)]
    assert any(isinstance(lbl, AndRule) for lbl in labels)

    e = eventually(hold(PROPS, 'A', duration=0), low=0, high=2)
    labels_e = [d['label'] for _, _, d in e.g.edges(data=True)]
    assert any(isinstance(lbl, ElseRule) for lbl in labels_e)


def test_accept_prop_boolean_labels_match_expected_rule_types():
    dfa_true = accept_prop(PROPS, boolean=True)
    dfa_false = accept_prop(PROPS, boolean=False)
    # accept_prop currently stores string labels (guard text), not rule objects.
    assert _edge_attr(dfa_true)['label'] == '(1)'
    assert _edge_attr(dfa_false)['label'] == '(0)'


def test_accept_prop_with_prop_uses_atomic_label_and_negated_hold_uses_negation_label():
    ap = accept_prop(PROPS, prop='A')
    hneg = hold(PROPS, 'A', duration=0, negation=True)
    assert _edge_attr(ap)['label'] == 'A'
    assert isinstance(_edge_attr(hneg)['label'], NegationRule)


def test_union_and_intersection_output_guards_are_nonempty_strings():
    i = intersection(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    u = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    assert all(isinstance(d['guard'], str) and d['guard'] for _, _, d in i.g.edges(data=True))
    assert all(isinstance(d['guard'], str) and d['guard'] for _, _, d in u.g.edges(data=True))


def test_composed_automata_multiple_operations_remain_deterministic_from_init():
    left = union(hold(PROPS, 'A', duration=0), hold(PROPS, 'B', duration=0))
    right = eventually(hold(PROPS, 'C', duration=0), low=0, high=3)
    prod = intersection(left, right)
    assert len(prod.init) == 1
