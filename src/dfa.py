license_text='''
    Module implements Time-Window Temporal Logic operations. 
    Copyright (C) 2015-2016  Cristian Ioan Vasile <cvasile@bu.edu>
    Hybrid and Networked Systems (HyNeSs) Group, BU Robotics Lab,
    Boston University

    Modified in 2026 by David Kajan, Masaryk University, Brno

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

    module:: dfa.py
   :synopsis: Module implements Time-Window Temporal Logic operations.

.. moduleauthor:: Cristian Ioan Vasile <cvasile@bu.edu>
'''

import logging

logger = logging.getLogger(__name__)
import itertools as it

from automata.fa.dfa import DFA as AutoDFA
from automata.fa.nfa import NFA as AutoNFA
from lomap import Fsa



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
    return ret


def _auto_from_fsa(dfa: Fsa) -> AutoDFA:
    return dfa.to_automata_dfa()


def _fsa_from_auto(auto_dfa: AutoDFA, template: Fsa) -> Fsa:
    return Fsa.from_automata_dfa(auto_dfa, template.props, template=template)




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
        name = '(Prop ' + str(prop) + ')'
        logger.debug('[accent_prop] Prop: {} Props: {}'.format(prop, props))
    elif boolean is not None:
        assert type(boolean) == bool
        guard = '(1)' if boolean else '(0)'
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

    for symbol in input_symbols:
        transitions[1][symbol] = 1

    auto_dfa = AutoDFA(
        states={0, 1},
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=0,
        final_states={1},
        allow_partial=True,
    )
    dfa = _fsa_from_auto(auto_dfa, template)
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
        name_prop = str(boolean)
    else:
        assert prop in props
        guard = prop if not negation else '!' + prop
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
    logger.debug('[hold] Prop: {} Duration: {} Negation: {} Boolean: {} Props: {}'.format(prop, duration, negation, boolean, props))
    return dfa

def complement(dfa: Fsa) -> Fsa:
    """Complements the DFA using automata-lib while preserving Fsa wrapper."""
    auto_dfa = dfa.to_automata_dfa().to_complete()
    comp_auto = AutoDFA(
        states=auto_dfa.states,
        input_symbols=auto_dfa.input_symbols,
        transitions=auto_dfa.transitions,
        initial_state=auto_dfa.initial_state,
        final_states=set(auto_dfa.states) - set(auto_dfa.final_states) - set([auto_dfa.initial_state]),
        allow_partial=True,
    )
    comp_fsa = Fsa.from_automata_dfa(comp_auto, dfa.props, template=dfa)
    return comp_fsa


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
    auto_int = auto1.intersection(auto2)
    dfa = _fsa_from_auto(auto_int, template)

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
    
    template = Fsa(dfa1.props, dfa1.directed, dfa1.multi)
    template.name = '(Union {} {} )'.format(dfa1.name, dfa2.name)

    auto1 = _auto_from_fsa(dfa1)
    auto2 = _auto_from_fsa(dfa2)
    auto_union = auto1.union(
        auto2
    )
    dfa = _fsa_from_auto(auto_union, template)

    relabel_dfa(dfa)

    logger.debug('[union] DFA1: {} DFA2: {}'.format(dfa1.name, dfa2.name))
    return dfa

def within(phi_dfa: Fsa, low: int, high: int | None) -> Fsa:
    '''Creates either a normal or infinity version DFA corresponding to a within
    operator which encloses the formula corresponding to dfa.
    '''
    if high is None:
        return eventually(phi_dfa, low)
    return repeat(phi_dfa, low, high)


def eventually(phi_dfa: Fsa, low: int) -> Fsa:
    '''Creates a DFA which accepts an eventually operator
    which encloses the formula corresponding to phi_dfa.
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
    
    template = Fsa(phi_dfa.props, phi_dfa.directed, False)

    dfa_f = eventually(phi_dfa, 0)
    
    hold_dfa = hold(phi_dfa.props, None, high - low + 1, boolean=True)
    line = complement(hold_dfa)

    dfa = _auto_from_fsa(dfa_f).intersection(_auto_from_fsa(line))
    template = Fsa(phi_dfa.props, phi_dfa.directed, phi_dfa.multi)
    template.name = '(Repeat {} {} {} )'.format(phi_dfa.name, low, high)

    base_fsa = _fsa_from_auto(dfa, template)

    if low > 0:
        prefix_dfa = hold(phi_dfa.props, None, low - 1, boolean=True)
        final = concatenation(prefix_dfa, base_fsa)
    else:
        final = base_fsa

    final.unify_accepting_states()
    relabel_dfa(dfa_f)
    logger.debug('[within] Low: {} High: {} DFA: {}'.format(low, high, phi_dfa.name))
    return final
