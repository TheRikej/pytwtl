"""Bridges LOMAP FSAs with automata-lib DFAs/NFAs."""

from __future__ import annotations

import copy
from typing import Iterable

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from lomap.classes.fsa import Fsa
from transition_rules import TrueRule


def _safe_initial_state(init: dict) -> object:
    if not init:
        return None
    return next(iter(init.keys()))


def fsa_to_automata_dfa(fsa: Fsa) -> DFA:
    states = set(fsa.g.nodes()) | set(fsa.init.keys()) | set(fsa.final)
    input_symbols = set(fsa.alphabet)

    if not states:
        return DFA.empty_language(input_symbols)

    transitions = {state: {} for state in states}
    for u, v, data in fsa.g.edges(data=True):
        symbols = data.get("input", set()) or set()
        for symbol in symbols:
            prev = transitions[u].get(symbol)
            if prev is not None and prev != v:
                raise ValueError(
                    f"Nondeterministic transition from {u} on {symbol}: {prev} vs {v}"
                )
            transitions[u][symbol] = v

    initial_state = _safe_initial_state(fsa.init)
    if initial_state is None:
        return DFA.empty_language(input_symbols)

    return DFA(
        states=states,
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=initial_state,
        final_states=set(fsa.final),
        allow_partial=True,
    )


def fsa_to_automata_nfa(fsa: Fsa) -> NFA:
    states = set(fsa.g.nodes()) | set(fsa.init.keys()) | set(fsa.final)
    input_symbols = set(fsa.alphabet)

    if not states:
        return NFA(
            states={0},
            input_symbols=input_symbols,
            transitions={0: {}},
            initial_state=0,
            final_states=set(),
        )

    transitions = {state: {} for state in states}
    for u, v, data in fsa.g.edges(data=True):
        symbols = data.get("input", set()) or set()
        if data.get("epsilon", False) or not symbols:
            transitions[u].setdefault("", set()).add(v)
        for symbol in symbols:
            transitions[u].setdefault(symbol, set()).add(v)

    initial_state = _safe_initial_state(fsa.init)
    if initial_state is None:
        initial_state = next(iter(states))

    return NFA(
        states=states,
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state=initial_state,
        final_states=set(fsa.final),
    )


def automata_dfa_to_fsa(dfa: DFA, props, template: Fsa | None = None) -> Fsa:
    fsa = Fsa(props, directed=True, multi=False)
    fsa.name = getattr(template, "name", "automata-lib DFA")
    if template is not None:
        if hasattr(template, "kind"):
            fsa.kind = template.kind
        if hasattr(template, "tree"):
            fsa.tree = copy.deepcopy(template.tree)

    fsa.alphabet = set(dfa.input_symbols)
    fsa.init = {dfa.initial_state: 1}
    fsa.final = set(dfa.final_states)

    fsa.g.add_nodes_from(dfa.states)

    edge_symbols = {}
    for u, lookup in dfa.transitions.items():
        for symbol, v in lookup.items():
            edge_symbols.setdefault((u, v), set()).add(symbol)

    for (u, v), symbols in edge_symbols.items():
        guard = "(1)" if symbols == fsa.alphabet else "(auto)"
        fsa.g.add_edge(
            u,
            v,
            **{"weight": 0, "input": set(symbols), "guard": guard, "label": TrueRule()},
        )

    return fsa
