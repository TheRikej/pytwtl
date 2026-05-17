import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dfa import (
    Choice,
    DFAType,
    DFATreeNode,
    Op,
    copy_tree,
    getDFAType,
    getOptimizationFlag,
    hold,
    init_tree,
    mark_concatenation,
    mark_eventually,
    mark_product,
    minimize_dfa,
    relabel_dfa,
    setDFAType,
    setOptimizationFlag,
    union,
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

    noncat = DFATreeNode(
        Op.union,
        left=DFATreeNode(Op.hold, init={1}, final={1}),
        right=DFATreeNode(Op.hold, init={2}, final={2}),
        init={0},
        final={3},
    )
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
    dest.add_transition_symbols((0, 0), set(dest.alphabet), (1, 1))

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
    assert 10 in copied.states

    relabel_dfa(dfa, start=100, copy=False)
    assert min(dfa.states) >= 100


def test_relabel_dfa_copy_then_inplace_in_infinity_mode_keeps_original_tree_valid():
    setDFAType(DFAType.Infinity)
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


def test_mark_product_with_choices_and_optimization_disabled():
    setOptimizationFlag(False)
    dfa1 = hold(PROPS, 'A', duration=0)
    dfa2 = hold(PROPS, 'B', duration=0)

    dest = Fsa(PROPS, directed=True, multi=False)
    dest.init[(0, 0)] = 1
    dest.final.add((1, 1))
    dest.add_transition_symbols((0, 0), set(dest.alphabet), (1, 1))

    choices = {(0, 0): Choice(both=set(dest.alphabet))}
    mark_product(dfa1, dfa2, dest, operation=Op.union, choices=choices)
    assert dest.tree.operation == Op.union
    assert dest.tree.choices == choices
