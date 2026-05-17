# Copyright (C) 2012-2015, Alphan Ulusoy (alphan@bu.edu)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from .fsa import Fsa
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class Nfa(Fsa):
	"""
	Base class for nondeterministic finite automata with epsilon transitions.
	"""

	def __init__(self, props=None, directed=True, multi=True):
		"""
		LOMAP NFA automaton object constructor.
		"""
		super().__init__(props=props, directed=directed, multi=multi)
		self._nfa = NFA(
			states={0},
			input_symbols=set(self.alphabet),
			transitions={0: {}},
			initial_state=0,
			final_states=set(),
		)

	def clone(self):
		ret = Nfa(self.props, self.directed, self.multi)
		ret.name = str(self.name)
		ret._nfa = self._nfa
		if hasattr(self, 'tree'):
			import copy
			ret.tree = copy.deepcopy(self.tree)
		if hasattr(self, 'kind'):
			ret.kind = self.kind
		return ret

	@property
	def init(self):
		return {self._nfa.initial_state: 1}

	@init.setter
	def init(self, value):
		if not value:
			return
		initial_state = next(iter(value.keys()))
		transitions = {state: {sym: set(dests) for sym, dests in lookup.items()} for state, lookup in self._nfa.transitions.items()}
		transitions.setdefault(initial_state, {})
		self._nfa = NFA(
			states=set(self._nfa.states) | {initial_state},
			input_symbols=set(self._nfa.input_symbols),
			transitions=transitions,
			initial_state=initial_state,
			final_states=set(self._nfa.final_states),
		)

	@property
	def final(self):
		return set(self._nfa.final_states)

	@final.setter
	def final(self, value):
		finals = set(value)
		self._nfa = NFA(
			states=set(self._nfa.states) | finals,
			input_symbols=set(self._nfa.input_symbols),
			transitions=self._nfa.transitions,
			initial_state=self._nfa.initial_state,
			final_states=finals,
		)

	@property
	def states(self):
		return set(self._nfa.states)

	@property
	def transitions(self):
		return {state: {sym: set(dests) for sym, dests in lookup.items()} for state, lookup in self._nfa.transitions.items()}

	def iter_transitions(self):
		for src, lookup in self._nfa.transitions.items():
			for sym, dests in lookup.items():
				for dest in dests:
					yield src, dest, sym

	def size(self):
		return (len(self.states), sum(len(v) for v in self._nfa.transitions.values()))

	def add_epsilon_transition(self, source, target, weight=0, label='ε', **attrs):
		"""
		Adds an epsilon transition between ``source`` and ``target``.
		"""
		transitions = {state: {sym: set(dests) for sym, dests in lookup.items()} for state, lookup in self._nfa.transitions.items()}
		transitions.setdefault(source, {}).setdefault('', set()).add(target)
		states = set(self._nfa.states) | {source, target}
		self._nfa = NFA(
			states=states,
			input_symbols=set(self._nfa.input_symbols),
			transitions=transitions,
			initial_state=self._nfa.initial_state,
			final_states=set(self._nfa.final_states),
		)

	def add_transition_symbols(self, src, symbols, dest):
		transitions = {state: {sym: set(dests) for sym, dests in lookup.items()} for state, lookup in self._nfa.transitions.items()}
		transitions.setdefault(src, {})
		for symbol in symbols:
			transitions[src].setdefault(symbol, set()).add(dest)
		states = set(self._nfa.states) | {src, dest}
		self._nfa = NFA(
			states=states,
			input_symbols=set(self._nfa.input_symbols),
			transitions=transitions,
			initial_state=self._nfa.initial_state,
			final_states=set(self._nfa.final_states),
		)

	def next_states_of_nfa(self, q, props):
		"""
		Returns the epsilon-closed next states of state ``q`` given an input
		proposition set ``props``.
		"""
		prop_bitmap = self.bitmap_of_props(props)
		auto_nfa = self.to_automata_nfa()
		lambda_closures = auto_nfa._get_lambda_closures()
		current_states = lambda_closures.get(q, frozenset([q]))
		next_states = auto_nfa._get_next_current_states(current_states, prop_bitmap)
		return list(next_states)

	def to_automata_nfa(self) -> NFA:
		return self._nfa

	def determinize(self):
		"""Determinize the NFA using automata-lib subset construction."""
		auto_nfa = self.to_automata_nfa()
		auto_dfa = DFA.from_nfa(auto_nfa, minify=False)
		return Fsa.from_automata_dfa(auto_dfa, self.props, template=self)