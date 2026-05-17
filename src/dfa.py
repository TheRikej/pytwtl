license_text='''
    Module implements Time-Window Temporal Logic operations. 
    Copyright (C) 2015-2016  Cristian Ioan Vasile <cvasile@bu.edu>
    Hybrid and Networked Systems (HyNeSs) Group, BU Robotics Lab,
    Boston University

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
'''
.. module:: dfa.py
   :synopsis: Module implements Time-Window Temporal Logic operations.

.. moduleauthor:: Cristian Ioan Vasile <cvasile@bu.edu>
   

'''

import logging
import copy
import math

from transition_rules import *
logger = logging.getLogger(__name__)
import itertools as it
from io import StringIO

import networkx as nx

from automata.fa.dfa import DFA as AutoDFA
from automata.fa.nfa import NFA as AutoNFA
from lomap import Fsa


class DFAType(object):
    '''Class defining the two DFA types, normal DFA and infinity DFA.'''
    Normal, Infinity, Both = range(3)
    def __init__(self, type: int|str):
        if type in (self.Normal, 'Normal', 'normal'):
            self.type = self.Normal
        elif type in (self.Infinity, 'Infinity', 'infinity'):
            self.type = self.Infinity
        elif type in (self.Both, 'Both', 'both'):
            self.type = self.Both
        else:
            raise ValueError('Unknown DFA type!')
    
    def is_normal(self) -> bool:
        return self.type in (self.Normal, self.Both)
    
    def is_infinity(self) -> bool:
        return self.type in (self.Infinity, self.Both)
    

        
'''The DFA type to generate.'''
dfa_type = DFAType.Infinity

def setDFAType(val):
    '''Sets the DFA generation method.'''
    global dfa_type
    if val not in (DFAType.Normal, DFAType.Infinity):
        raise ValueError()
    dfa_type = val
def getDFAType():
    '''Retrieves the DFA generation method.'''
    global dfa_type
    return dfa_type

optimize = True
def setOptimizationFlag(val=True):
    '''Sets the optimization flag'''
    global optimize
    optimize = bool(val)
def getOptimizationFlag():
    '''Retrieves the optimization flag.'''
    global optimize
    return optimize

class Op(object):
    '''Class defining the operation codes for the TWTL operators.'''
    nop, accept, hold, neg, cat, intersection, union, within, event = range(9)
    operations = (nop, accept, hold, neg, cat, intersection, union, within, event)
    names = ['NoOperation', 'AcceptProp', 'Hold', 'Negation',
             'Concatenation', 'Intersection', 'Union', 'Within', 'Eventually']
    @classmethod
    def str(cls, op):
        if op in cls.operations:
            return cls.names[op]
        raise ValueError('Unknown operation!')


class Choice(object):
    '''Class defining the choices for disjunction operators.'''
    __slots__ = ['both', 'left', 'right']
    
    def __init__(self, both=None, left=None, right=None):
        self.both = set(both) if both is not None else set()
        self.left = set(left) if left is not None else set()
        self.right = set(right) if right is not None else set()
    
    def __repr__(self): return self.__str__()
    def __str__(self):
        return 'both={} left={} right={}'.format(self.both, self.left, self.right)


class DFATreeNode(object):
    '''Class defining a tree node to store information about TWTL operators
    used to compute relaxed control policies with respect to deadlines. 
    Each node stores the associated operation, the initial and final states of
    the automaton corresponding to the formula associated with the tree, the
    left and right subtrees, some flags used for sanity checks and additional
    data specific to the associated operation.
    '''
    def __init__(self, operation=Op.nop, left=None, right=None,
                 init = None, final = None,
                 wdf=True, wwf=True, unr=True, ndj=0, **kwargs):
        self.operation = operation
        self.left = left
        self.right = right
        self.wdf = wdf # within-disjunction free
        self.wwf = wwf # within-within free
        self.unr = unr # un-relaxable, i.e. within free
        # number of disjunction operators
        self.ndj = ndj + (self.operation == Op.union)
        self.init = set(init)
        self.final = set(final)
        
        if self.operation == Op.event:
            self.low = kwargs.get('low', 0)
            self.high = kwargs.get('high', 0)
        elif self.operation == Op.union:
            self.choices = kwargs.get('choices', None)
    
    def relabel(self, mapping, expand=False):
        '''Relabels the data about the DFA states which are stored within the
        nodes of the tree. The map `mapping` is used to translate the states'
        labels. If `expand` is set, then the `mapping` is treated as a
        multi-valued map and each state is replicated as needed.
        '''
        stack = [self]
        while stack:
            tree = stack.pop()
            if expand:
                init_expanded = list(it.chain.from_iterable([mapping[u] for u in tree.init]))
                final_expanded = list(it.chain.from_iterable([mapping[u] for u in tree.final]))
                logging.debug('state: %s \n init: %s\n final: %s',
                              Op.str(tree.operation),
                              init_expanded,
                              final_expanded)
                tree.init = set(init_expanded)
                tree.final = set(final_expanded)
                if tree.operation == Op.union:
                    tree.choices = dict([(key, v)
                                            for k, v in tree.choices.items()
                                                for key in mapping[k]])
            else:
                tree.init = set([mapping[u] for u in tree.init])
                tree.final = set([mapping[u] for u in tree.final])
                if tree.operation == Op.union:
                    tree.choices = dict([(mapping[k], v)
                                          for k, v in tree.choices.items()])
            if tree.right is not None:
                stack.append(tree.right)
            if tree.left is not None:
                stack.append(tree.left)
    
    def normalize(self, init, final):
        '''Resets the initial and final sets of states in the tree such that it
        eliminates unreachable start or end configurations, i.e. (1) a
        sub-formula must start and end at the same states as the formula it is
        part of in the case of disjunction, conjunction, hold, accept and
        eventually operators; and (2) in case of concatenation, the left
        sub-formula must start at the same states as the larger formula, while
        the right sub-formula must end at same final states as the larger
        formula. 
        '''
#         return
        if self.operation == Op.cat:
            if init is not None:
                self.init = set(init)
                self.left.normalize(init, None)
            if final is not None:
                self.final = set(final)
                self.right.normalize(None, final)
        else:
            if init is not None:
                self.init = set(init)
            if final is not None:
                self.final = set(final)
            if init is not None or final is not None:
                if self.left is not None:
                    self.left.normalize(init, final)
                if self.right is not None:
                    self.right.normalize(init, final)
    
    def pprint(self, level=0, indent=2):
        '''Returns a multi-line string representation of the whole tree.'''
        ret = StringIO()
        print(' '*(level*indent), str(self), file=ret)
        print(' '*(level*indent), 'Init:', self.init, file=ret)
        print(' '*(level*indent), 'Final:', self.final, file=ret)
        if self.operation == Op.union:
            print(' '*(level*indent), 'Choices:', file=ret)
            for k, v in self.choices.items():
                print(' '*((level+1)*indent), k, '->', v, file=ret)
        if self.left is not None:
            print(' '*(level*indent), 'Left:', file=ret)
            print(self.left.pprint(level=level+1), end='', file=ret)
        if self.right is not None:
            print(' '*(level*indent), 'Right:', file=ret)
            print(self.right.pprint(level=level+1), end='', file=ret)
        ret_str = str(ret.getvalue())
        ret.close()
        return ret_str
    
    def __str__(self):
        return 'Op: {} Flags[WDF, WWF, UNR]: {} {} {}'.\
                format(Op.str(self.operation), self.wdf, self.wwf, self.unr)


def copy_tree(dfa_src: Fsa, dfa_dest: Fsa, mapping:dict|None=None):
    '''Copies the tree from the source to the destination automaton and
    translates the tree data using the mapping dictionary.
    '''
    # Some DFAs (e.g., manually created FSAs or clones from legacy LOMAP API)
    # do not carry annotation tree metadata.
    if getDFAType() == DFAType.Infinity and hasattr(dfa_src, 'tree'):
        dfa_dest.tree = copy.deepcopy(dfa_src.tree)
        if mapping is not None:
            dfa_dest.tree.relabel(mapping)

def init_tree(dfa: Fsa, operation=Op.nop):
    '''Creates a new AST tree node and adds it to the automaton `dfa`. The 
    operation corresponding to the tree node is given by the `operation`
    parameter (default=`Op.nop`).
    '''
    if DFAType.Infinity:
        assert operation in Op.operations
        dfa.tree = DFATreeNode(operation, init=dfa.init.keys(), final=dfa.final)

def mark_eventually(dfa_src: Fsa, dfa_dest: Fsa, low: int, high: int | None = None):
    '''Creates a new AST tree node corresponding to a within operator and adds
    it to the destination automaton `dfa_dest`. The child subtree is copied from
    the source automaton `dfa_src`.
    '''
    # create new AST tree
    dfa_dest.tree = DFATreeNode(Op.event, left=dfa_src.tree, right=None,
                                init=dfa_dest.init.keys(), final=dfa_dest.final,
                                low=low, high=math.inf if high is None else high)
    # update flags
    dfa_dest.tree.wdf = (dfa_src.tree.ndj == 0)
    assert dfa_dest.tree.wdf, 'Need within-disjunction free form!'
    dfa_dest.tree.wwf = dfa_src.tree.unr
    dfa_dest.tree.unr = False
    dfa_dest.tree.ndj = dfa_src.tree.ndj

def mark_concatenation(dfa_src1: Fsa, dfa_src2: Fsa, dfa_dest: Fsa):
    '''Creates a new AST tree node corresponding to a concatenation operator and
    adds it to the destination automaton `dfa_dest`. The children subtrees are
    copied from the source automata `dfa_src1` and `dfa_src2`.
    '''
    # create new AST tree
    dfa_dest.tree = DFATreeNode(Op.cat, left=dfa_src1.tree, right=dfa_src2.tree,
                                init=dfa_dest.init.keys(), final=dfa_dest.final)
    # update flags
    dfa_dest.tree.wdf = dfa_src1.tree.wdf and dfa_src2.tree.wdf
    dfa_dest.tree.wwf = dfa_src1.tree.wwf and dfa_src2.tree.wwf
    dfa_dest.tree.unr = dfa_src1.tree.unr and dfa_src2.tree.unr
    dfa_dest.tree.ndj = dfa_src1.tree.ndj + dfa_src2.tree.ndj

def mark_product(dfa_src1: Fsa, dfa_src2: Fsa, dfa_dest: Fsa, operation:int, choices:Choice|None=None):
    '''Creates a new AST tree node corresponding to a disjunction or conjunction
    operator and adds it to the destination automaton `dfa_dest`. The children
    subtrees are copied from the source automata `dfa_src1` and `dfa_src2`.
    '''
    # relabel data in left tree
    mapping = dict([(u, []) for u in dfa_src1.states])
    for state in dfa_dest.states:
        if not isinstance(state, tuple) or len(state) != 2:
            continue
        u, v = state
        if u in mapping:
            mapping[u].append((u, v))
    # dfa_src1.tree.relabel(mapping, expand=True)
    # relabel data in right tree
    mapping = dict([(v, []) for v in dfa_src2.states])
    for state in dfa_dest.states:
        if not isinstance(state, tuple) or len(state) != 2:
            continue
        u, v = state
        if v in mapping:
            mapping[v].append((u, v))
    dfa_src2.tree.relabel(mapping, expand=True)
    # create new AST tree
    dfa_dest.tree = DFATreeNode(operation, left=dfa_src1.tree,
                                right=dfa_src2.tree,
                                init=dfa_dest.init.keys(), final=dfa_dest.final,
                                choices=choices)
    # update init and final states of AST nodes
    if getOptimizationFlag():
        dfa_dest.tree.normalize(init=dfa_dest.init.keys(), final=dfa_dest.final)
    # update flags
    dfa_dest.tree.wdf = dfa_src1.tree.wdf and dfa_src2.tree.wdf
    dfa_dest.tree.wwf = dfa_src1.tree.wwf and dfa_src2.tree.wwf
    dfa_dest.tree.unr = dfa_src1.tree.unr and dfa_src2.tree.unr
    dfa_dest.tree.ndj = dfa_src1.tree.ndj + dfa_src2.tree.ndj\
                        + (operation == Op.union)


def relabel_dfa(dfa: Fsa, mapping:dict|None=None, start=0, copy=False):
    '''Relabels the DFA. The new labels are given by the mapping dictionary. By
    default, it relabels the states with integers with the lowest one given by
    start. The dictionary can be a partial mapping of the nodes. The states
    which are not specified are labeled with integers starting from start.
    If copy is True a new copy of the DFA is returned, otherwise it performs an
    in-place relabeling.
    '''
    if mapping is None: # default mapping
        mapping = dict()
    keys = mapping.keys()
    nodes = [u for u in dfa.states if u not in keys]
    mapping.update(dict(zip(nodes, it.count(start))))
    
    if copy: # create new dfa
        ret = Fsa(dfa.props, dfa.directed, dfa.multi)
        ret.name = str(dfa.name)
    else: # in-place relabeling
        ret = dfa
    transitions = {state: dict(lookup) for state, lookup in dfa.transitions.items()}
    new_states = set(mapping.values())
    new_transitions = {mapping[state]: {} for state in dfa.states}
    for src, lookup in transitions.items():
        for sym, dst in lookup.items():
            new_transitions[mapping[src]][sym] = mapping[dst]
    old_init = next(iter(dfa.init.keys())) if dfa.init else None
    new_init = mapping.get(old_init, next(iter(new_states))) if new_states else None
    ret._sync_from_auto(AutoDFA(
        states=new_states,
        input_symbols=set(dfa.alphabet),
        transitions=new_transitions,
        initial_state=new_init,
        final_states=set([mapping[u] for u in dfa.final]),
        allow_partial=True,
    ))
    # copy tree
    copy_tree(dfa, ret, mapping=mapping)
    return ret


def _auto_from_fsa(dfa: Fsa) -> AutoDFA:
    return dfa.to_automata_dfa()


def _fsa_from_auto(auto_dfa: AutoDFA, template: Fsa) -> Fsa:
    return Fsa.from_automata_dfa(auto_dfa, template.props, template=template)


def _shortest_path_length(transitions: dict, source, target):
    if source == target:
        return 0
    visited = set([source])
    frontier = [(source, 0)]
    while frontier:
        state, dist = frontier.pop(0)
        for _, nxt in transitions.get(state, {}).items():
            if nxt == target:
                return dist + 1
            if nxt not in visited:
                visited.add(nxt)
                frontier.append((nxt, dist + 1))
    raise nx.NetworkXNoPath


def _truncate_auto_dfa(auto_dfa: AutoDFA, cutoff: int) -> AutoDFA:
    transitions = {state: dict(auto_dfa.transitions.get(state, {})) for state in auto_dfa.states}
    visited = set([auto_dfa.initial_state])
    frontier = [(auto_dfa.initial_state, 0)]
    kept_edges = set()

    while frontier:
        state, depth = frontier.pop(0)
        if depth >= cutoff:
            continue
        for sym, nxt in transitions.get(state, {}).items():
            kept_edges.add((state, sym, nxt))
            if nxt not in visited:
                visited.add(nxt)
                frontier.append((nxt, depth + 1))

    kept_states = set([auto_dfa.initial_state]) | {dst for _, _, dst in kept_edges} | {src for src, _, _ in kept_edges}
    new_transitions = {state: {} for state in kept_states}
    for src, sym, dst in kept_edges:
        if src in new_transitions and dst in kept_states:
            new_transitions[src][sym] = dst

    # remove states which do not reach a final state
    reverse = {state: set() for state in kept_states}
    for src, lookup in new_transitions.items():
        for _, dst in lookup.items():
            reverse.setdefault(dst, set()).add(src)
    reachable = set()
    stack = list(auto_dfa.final_states & kept_states)
    while stack:
        state = stack.pop()
        if state in reachable:
            continue
        reachable.add(state)
        stack.extend(reverse.get(state, set()))
    kept_states &= reachable | {auto_dfa.initial_state}

    new_transitions = {
        state: {sym: dst for sym, dst in new_transitions.get(state, {}).items() if dst in kept_states}
        for state in kept_states
    }

    return AutoDFA(
        states=kept_states,
        input_symbols=set(auto_dfa.input_symbols),
        transitions=new_transitions,
        initial_state=auto_dfa.initial_state,
        final_states=set(auto_dfa.final_states) & kept_states,
        allow_partial=True,
    )



def minimize_dfa(dfa: Fsa) -> Fsa:
    """Minimizes a deterministic DFA using automata-lib.

    The input and output remain LOMAP FSA instances for compatibility.
    """
    try:
        auto_dfa = dfa.to_automata_dfa()
        min_auto = auto_dfa.minify(retain_names=False)
        return Fsa.from_automata_dfa(min_auto, dfa.props, template=dfa)
    except Exception as exc:
        logger.warning('[minimize_dfa] automata-lib minimization failed (%s). Returning original DFA.', exc)
        return dfa



def accept_prop(props: list[str], prop:str|None=None, boolean:bool|None=None):
    '''Creates a DFA which accepts:
    1) all symbols which contain proposition prop, if prop is not None;
    2) all symbols, if boolean is True;
    3) no symbol, if boolean is False.
    '''
    if prop is not None:
        assert prop in props
        guard = prop
        label = AtomicPropositionRule(prop)
        name = '(Prop ' + str(prop) + ')'
        logger.debug('[accent_prop] Prop: {} Props: {}'.format(prop, props))
    elif boolean is not None:
        assert type(boolean) == bool
        guard = '(1)' if boolean else '(0)'
        label = TrueRule() if boolean else EmptyRule() #TODO: check logic of EmptyRule
        name = '(Bool ' + str(boolean) + ')'
        logger.debug('[accent_prop] Boolean: {} Props: {}'.format(boolean, props))
    else:
        raise AssertionError('Either prop or boolean must be given!')
    
    template = Fsa(props, directed=True, multi=False)
    template.name = name
    bitmaps = template.get_guard_bitmap(guard)
    input_symbols = set(template.alphabet)

    transitions = {0: {}, 1: {}}
    for symbol in bitmaps:
        transitions[0][symbol] = 1

    auto_dfa = AutoDFA(
        states={0, 1},
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=0,
        final_states={1},
        allow_partial=True,
    )
    dfa = _fsa_from_auto(auto_dfa, template)
    init_tree(dfa, operation=Op.accept)
    return dfa

def hold(props: list[str], prop: str, duration: int, negation:bool=False, boolean:bool|None=None):
    '''Creates a DFA which accepts a sequence of symbols all containing
    proposition prop. The length of the sequence is duration+1 corresponding to
    duration time intervals. If negation is True, then the symbols must not
    contain prop instead.
    '''
    if boolean is not None:
        assert type(boolean) == bool
        guard = '(1)' if boolean else '(0)'
        label = TrueRule() if boolean else EmptyRule()
        name_prop = str(boolean)
    else:
        assert prop in props
        guard = prop if not negation else '!' + prop
        label = AtomicPropositionRule(prop) if not negation else NegationRule(AtomicPropositionRule(prop))
        name_prop = 'not ' + prop if negation else prop
    template = Fsa(props, directed=True, multi=False)
    template.name = '(Hold {} {} )'.format(duration, name_prop)
    bitmaps = template.get_guard_bitmap(guard)
    input_symbols = set(template.alphabet)

    total_states = duration + 2
    states = set(range(total_states))
    transitions = {state: {} for state in states}
    for state in range(total_states - 1):
        for symbol in bitmaps:
            transitions[state][symbol] = state + 1

    for symbol in input_symbols:
        transitions[total_states - 1][symbol] = total_states - 1

    auto_dfa = AutoDFA(
        states=states,
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=0,
        final_states={total_states - 1},
        allow_partial=True,
    )
    dfa = _fsa_from_auto(auto_dfa, template)
    init_tree(dfa, operation=Op.hold)
    logger.debug('[hold] Prop: {} Duration: {} Negation: {} Boolean: {} Props: {}'.format(prop, duration, negation, boolean, props))
    return dfa

def complement(dfa: Fsa) -> Fsa:
    """Complements the DFA using automata-lib while preserving Fsa wrapper."""
    try:
        auto_dfa = dfa.to_automata_dfa()
        comp_auto = auto_dfa.complement(minify=False)
        comp_fsa = Fsa.from_automata_dfa(comp_auto, dfa.props, template=dfa)
        dfa._sync_from_auto(comp_auto)
        dfa.init = comp_fsa.init
        dfa.final = comp_fsa.final
        dfa.alphabet = comp_fsa.alphabet
        return dfa
    except Exception as exc:
        logger.warning('[complement] automata-lib complement failed (%s). Falling back to trap-state complement.', exc)
        dfa.add_trap_state()
        dfa.final = set(dfa.states) - set(dfa.final)
        return dfa

def concatenation(dfa1: Fsa, dfa2: Fsa) -> Fsa:
    '''Creates a DFA which accepts the language of concatenated word accepted by
    dfa1 and dfa2. Is assumes that concatenation is non-ambiguous, i.e. every
    word in the resulting language can be uniquely decomposed into a prefix word
    from the language accepted by dfa1 and a suffix word from the language
    accepted by dfa2.
    Theorem: card(lang(concatenate(dfa1, dfa2))) ==
                                             card(lang(dfa1)) x card(lang(dfa2))
    '''
    assert dfa1.directed == dfa2.directed and dfa1.multi == dfa2.multi
    assert dfa1.props == dfa2.props
    assert dfa1.alphabet == dfa2.alphabet
    assert len(dfa1.init) == 1 and len(dfa2.init) == 1
    # assert len(dfa1.final) == 1 and len(dfa2.final) == 1
    template = Fsa(dfa1.props, dfa1.directed, dfa1.multi)

    dfa1_final = dfa1.unify_accepting_states()
    if dfa1_final is None:
        return dfa1
    relabel_dfa(dfa2, start=max(filter(lambda x: isinstance(x, int) or isinstance(x, str) and x.isdigit(), dfa1.states)) + 1)


    dfa2_init = dfa2.init.keys()[0]
    transitions = {state: dict(lookup) for state, lookup in dfa1.transitions.items()}
    transitions.update({state: dict(lookup) for state, lookup in dfa2.transitions.items()})


    for symbol in dfa1.alphabet:
        if symbol in transitions[dfa2_init]:
            transitions[dfa1_final][symbol] = transitions[dfa2_init][symbol]
        else:
            transitions[dfa1_final].pop(symbol, None)
    
    transitions.pop(dfa2_init, None)

    dfa = AutoDFA(
        states=dfa1.states.union(dfa2.states) - set([dfa2_init]),
        input_symbols=dfa1.alphabet,
        transitions=transitions,
        initial_state=dfa1.init.keys()[0],
        final_states=set(dfa2.final),
        allow_partial=True,
    )

    logger.debug('[concatenation] DFA1: {} DFA2: {}'.format(dfa1.name, dfa2.name))
    return _fsa_from_auto(dfa, template)

def intersection(dfa1: Fsa, dfa2: Fsa) -> Fsa:
    '''Creates a DFA which accepts the intersection of the languages
    corresponding to the two DFAs. The conjunction operation of TWTL is mapped
    to intersection.
    If an infinity DFA is generated, the corresponding meta-data is copied as
    well.
    '''
    assert dfa1.directed == dfa2.directed and dfa1.multi == dfa2.multi
    assert dfa1.props == dfa2.props
    assert dfa1.alphabet == dfa2.alphabet
    assert len(dfa1.init) == 1 and len(dfa2.init) == 1
    assert len(dfa1.final) >= 1 and len(dfa2.final) >= 1

    template = Fsa(dfa1.props, dfa1.directed, dfa1.multi)
    template.name = '(Intersection {} {} )'.format(dfa1.name, dfa2.name)

    auto1 = _auto_from_fsa(dfa1)
    auto2 = _auto_from_fsa(dfa2)
    auto_int = auto1.intersection(
        auto2
    )
    dfa = _fsa_from_auto(auto_int, template)

    # if getDFAType() == DFAType.Infinity and hasattr(dfa1, 'tree') and hasattr(dfa2, 'tree'):
    #     mark_product(dfa1, dfa2, dfa, Op.intersection)

    # if getDFAType() == DFAType.Normal:
    #     dfa = minimize_dfa(dfa)

    relabel_dfa(dfa)

    logger.debug('[intersection] DFA1: {} DFA2: {}'.format(dfa1.name, dfa2.name))
    return dfa

def union(dfa1: Fsa, dfa2: Fsa) -> Fsa:
    '''Creates a DFA which accepts the union of the languages corresponding to
    the two DFAs. The disjunction operation of TWTL is mapped to union.
    If an infinity DFA is generated, the corresponding meta-data is copied as
    well.
    '''
    assert dfa1.directed == dfa2.directed and dfa1.multi == dfa2.multi
    assert dfa1.props == dfa2.props
    assert dfa1.alphabet == dfa2.alphabet
    # assert len(dfa1.init) == 1 and len(dfa2.init) == 1
    # assert len(dfa1.final) == 1 and len(dfa2.final) == 1
    
    template = Fsa(dfa1.props, dfa1.directed, dfa1.multi)
    template.name = '(Union {} {} )'.format(dfa1.name, dfa2.name)

    auto1 = _auto_from_fsa(dfa1)
    auto2 = _auto_from_fsa(dfa2)
    auto_union = auto1.union(
        auto2
    )
    dfa = _fsa_from_auto(auto_union, template)

    # if getDFAType() == DFAType.Infinity and hasattr(dfa1, 'tree') and hasattr(dfa2, 'tree'):
    #     mark_product(dfa1, dfa2, dfa, Op.union)

    # if getDFAType() == DFAType.Normal:
    #     dfa = minimize_dfa(dfa)

    relabel_dfa(dfa)

    logger.debug('[union] DFA1: {} DFA2: {}'.format(dfa1.name, dfa2.name))
    return dfa

def within(phi_dfa: Fsa, low: int, high: int | None) -> Fsa:
    '''Creates either a normal or infinity version DFA corresponding to a within
    operator which encloses the formula corresponding to dfa.
    '''
    # assert len(phi.init) == 1 and len(phi.final) == 1
    # phi_dfa.remove_trap_states()

    if high is None:
        return eventually(phi_dfa, low)
    return repeat(phi_dfa, low, high)


def eventually(phi_dfa: Fsa, low: int) -> Fsa:
    '''Creates a DFA which accepts the infinity version of a within operator
    which encloses the formula corresponding to phi_dfa.
    NOTE: Assumes that phi_dfa contains no ``trap'' states, i.e. states which do
    not reach a final state. 
    '''
    template = Fsa(phi_dfa.props, phi_dfa.directed, False)
    template.name = '(Eventually {} {})'.format(phi_dfa.name, low)

    auto_dfa = _auto_from_fsa(phi_dfa).to_complete()
    auto_nfa = AutoNFA.from_dfa(auto_dfa)

    states = set(auto_nfa.states)
    input_symbols = set(auto_nfa.input_symbols)
    transitions = {
        state: {sym: set(dests) for sym, dests in auto_nfa.transitions.get(state, {}).items()}
        for state in states
    }

    original_init = auto_nfa.initial_state
    original_states = list(states)
    initial_state = original_init

    if low > 0:
        prefix_states = [('prefix', i) for i in range(low)]
        states.update(prefix_states)
        for i, state in enumerate(prefix_states):
            transitions.setdefault(state, {})
            next_state = prefix_states[i + 1] if i + 1 < low else original_init
            for sym in input_symbols:
                transitions[state].setdefault(sym, set()).add(next_state)
        initial_state = prefix_states[0]

    for state in original_states:
        transitions.setdefault(state, {})
        transitions[state].setdefault('', set()).add(original_init)

    nfa = AutoNFA(
        states=states,
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=initial_state,
        final_states=set(auto_nfa.final_states)
    )
    auto_event = AutoDFA.from_nfa(nfa, minify=True)
    dfa = _fsa_from_auto(auto_event, template)
    dfa.unify_accepting_states()
    # if hasattr(phi_dfa, 'tree'):
        # mark_eventually(phi_dfa, dfa, low)
    logger.debug('[eventually] Low: {} DFA: {}'.format(low, phi_dfa.name))
    return dfa

def repeat(phi_dfa: Fsa, low: int, high: int) -> Fsa:
    '''Creates a DFA which accepts the language associated with a within
    operator which encloses the formula corresponding to phi_dfa.
    '''
    assert len(phi_dfa.init) == 1
    # assert len(phi_dfa.final) == 1
    
    auto_phi = _auto_from_fsa(phi_dfa)
    init_state = auto_phi.initial_state
    if len(auto_phi.final_states) != 1:
        raise ValueError('repeat() expects exactly one final state')
    final_state = next(iter(auto_phi.final_states))

    transitions = {state: dict(auto_phi.transitions.get(state, {})) for state in auto_phi.states}
    b = _shortest_path_length(transitions, init_state, final_state)
    d = high - low - b + 2

    input_symbols = set(auto_phi.input_symbols)
    combined_transitions = {}
    combined_states = set()
    inits = []
    final_marker = ('final',)

    for k in range(d):
        mapping = {state: (k, state) for state in auto_phi.states}
        mapping[final_state] = final_marker

        copy_states = set(mapping.values())
        copy_transitions = {state: {} for state in copy_states}
        for src, lookup in transitions.items():
            for sym, dst in lookup.items():
                copy_transitions[mapping[src]][sym] = mapping[dst]

        auto_copy = AutoDFA(
            states=copy_states,
            input_symbols=input_symbols,
            transitions=copy_transitions,
            initial_state=mapping[init_state],
            final_states={final_marker},
            allow_partial=True,
        )
        auto_copy = _truncate_auto_dfa(auto_copy, cutoff=(high - low + 1) - k)

        combined_states |= set(auto_copy.states)
        for src, lookup in auto_copy.transitions.items():
            combined_transitions.setdefault(src, {})
            combined_transitions[src].update(lookup)
        inits.append(auto_copy.initial_state)

    combined_states.add(final_marker)

    # create restart transitions
    current_states = set([inits[0]])
    for rstate in inits[1:]:
        next_states = set()
        for state in current_states:
            outgoing = combined_transitions.get(state, {})
            next_states.update(outgoing.values())
            missing = input_symbols - set(outgoing.keys())
            if state != final_marker and missing:
                combined_transitions.setdefault(state, {})
                for sym in missing:
                    combined_transitions[state][sym] = rstate
        current_states = next_states | set([rstate])

    initial_state = inits[0]
    if low > 0:
        prefix_states = [('prefix', i) for i in range(low)]
        combined_states.update(prefix_states)
        for i, state in enumerate(prefix_states):
            combined_transitions.setdefault(state, {})
            next_state = prefix_states[i + 1] if i + 1 < low else initial_state
            for sym in input_symbols:
                combined_transitions[state][sym] = next_state
        initial_state = prefix_states[0]

    for state in combined_states:
        combined_transitions.setdefault(state, {})

    auto_repeat = AutoDFA(
        states=combined_states,
        input_symbols=input_symbols,
        transitions=combined_transitions,
        initial_state=initial_state,
        final_states={final_marker},
        allow_partial=True,
    )
    if getDFAType() == DFAType.Normal:
        auto_repeat = auto_repeat.minify(retain_names=False)

    template = Fsa(phi_dfa.props, phi_dfa.directed, phi_dfa.multi)
    template.name = '(Repeat {} {} {} )'.format(phi_dfa.name, low, high)
    dfa = _fsa_from_auto(auto_repeat, template)
    dfa.unify_accepting_states()
    relabel_dfa(dfa)
    logger.debug('[within] Low: {} High: {} DFA: {}'.format(low, high, phi_dfa.name))
    return dfa

def truncate_dfa(dfa: Fsa, cutoff: int) -> Fsa:
    '''Returns a dfa which accepts only the words of length at most cutoff from
    the language associated with the given dfa.
    Note: It assumes that the given dfa has a finite language, i.e. it is a DAG.
    
    Adapted from networkx.algorithms.shortest_paths.unweighted.single_source_shortest_path_length
    NetworkX is available at http://networkx.github.io.
    '''
    assert len(dfa.init) == 1 # deterministic model
    auto_dfa = _auto_from_fsa(dfa)
    truncated = _truncate_auto_dfa(auto_dfa, cutoff=cutoff)
    updated = _fsa_from_auto(truncated, dfa)
    dfa._sync_from_auto(truncated)
    dfa.init = updated.init
    dfa.final = updated.final
    dfa.alphabet = updated.alphabet
    return dfa
