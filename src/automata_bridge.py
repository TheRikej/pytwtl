"""Bridges LOMAP FSAs with automata-lib DFAs/NFAs."""

from __future__ import annotations

import copy

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from lomap.classes.fsa import Fsa


def fsa_to_automata_dfa(fsa: Fsa) -> DFA:
    return fsa.to_automata_dfa()


def fsa_to_automata_nfa(fsa: Fsa) -> NFA:
    auto_dfa = fsa.to_automata_dfa()
    return NFA.from_dfa(auto_dfa)


def automata_dfa_to_fsa(dfa: DFA, props, template: Fsa | None = None) -> Fsa:
    fsa = Fsa(props, directed=True, multi=False)
    fsa.name = getattr(template, "name", "automata-lib DFA")
    if template is not None:
        if hasattr(template, "kind"):
            fsa.kind = template.kind
        if hasattr(template, "tree"):
            fsa.tree = copy.deepcopy(template.tree)

    fsa._sync_from_auto(dfa)

    return fsa
