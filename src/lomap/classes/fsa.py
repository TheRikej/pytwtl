# Copyright (C) 2012-2015, Alphan Ulusoy (alphan@bu.edu)
#
# Modified in 2026 by David Kajan, Masaryk University, Brno
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

from functools import reduce
import copy
import re
import operator as op
from automata.fa.dfa import DFA as AutoDFA
import logging

# Logger configuration
logger = logging.getLogger(__name__)
#logger.addHandler(logging.NullHandler())

class Fsa(object):
	"""
	Base class for deterministic finite state automata.
	"""
	
	def __init__(self, props=None, directed=True, multi=True):
		"""
		LOMAP Fsa Automaton object constructor
		"""
		self.name = 'Unnamed system model'
		self.directed = directed
		self.multi = bool(multi)
		self._dfa = None
		self._allow_partial = True
		
		if type(props) is dict:
			self.props = dict(props)
		else:
			self.props = list(props) if props is not None else []
			# Form the bitmap dictionary of each proposition
			# Note: range goes upto rhs-1
			self.props = dict(zip(self.props, map(lambda x: 2 ** x, range(0, len(self.props)))))

		# Alphabet is the power set of propositions, where each element
		# is a symbol that corresponds to a tuple of propositions
		# Note: range goes upto rhs-1
		self.alphabet = set(range(1, 2 ** len(self.props)+1))
		self._dfa = AutoDFA.empty_language(set(self.alphabet))
	
	def __repr__(self):
		return '''
Name: {name}
Directed: {directed}
Multi: {multi}
Props: {props}
Alphabet: {alphabet} 
Initial: {init}
Final: {final}
States: {states}
Transitions: {transitions}
		'''.format(name=self.name, directed=self.directed, multi=self.multi,
				   props=self.props, alphabet=self.alphabet,
				   init=self.init.keys(), final=set(self.final),
				   states=self.states,
				   transitions=sum(len(v) for v in self.transitions.values()))
	
	def clone(self):
		ret = Fsa(self.props, self.directed, self.multi)
		ret.name = str(self.name)
		ret._dfa = self._dfa
		ret._allow_partial = self._allow_partial
		if hasattr(self, 'tree'):
			ret.tree = copy.deepcopy(self.tree)
		if hasattr(self, 'kind'):
			ret.kind = self.kind
		return ret

	class _InitProxy(object):
		def __init__(self, parent):
			self._parent = parent
		def keys(self):
			init = self._parent._dfa.initial_state if self._parent._dfa is not None else None
			return [] if init is None else [init]
		def __iter__(self):
			return iter(self.keys())
		def items(self):
			return [(k, 1) for k in self.keys()]
		def __len__(self):
			return len(self.keys())
		def __contains__(self, key):
			return key in self.keys()
		def __getitem__(self, key):
			if key in self:
				return 1
			raise KeyError(key)
		def __setitem__(self, key, value):
			self._parent._set_initial_state(key)
		def __delitem__(self, key):
			if key in self:
				self._parent._set_initial_state(None)
		def clear(self):
			self._parent._set_initial_state(None)

	class _FinalProxy(object):
		def __init__(self, parent):
			self._parent = parent
		def __iter__(self):
			return iter(self._parent._get_final_states())
		def __len__(self):
			return len(self._parent._get_final_states())
		def __contains__(self, key):
			return key in self._parent._get_final_states()
		def add(self, key):
			self._parent._set_final_states(self._parent._get_final_states() | {key})
		def discard(self, key):
			finals = set(self._parent._get_final_states())
			finals.discard(key)
			self._parent._set_final_states(finals)
		def remove(self, key):
			finals = set(self._parent._get_final_states())
			finals.remove(key)
			self._parent._set_final_states(finals)
		def clear(self):
			self._parent._set_final_states(set())

	def _get_final_states(self):
		return set() if self._dfa is None else set(self._dfa.final_states)

	def _set_initial_state(self, initial_state):
		if initial_state is None:
			self._dfa = AutoDFA.empty_language(set(self.alphabet))
			return
		transitions = {state: dict(lookup) for state, lookup in self.transitions.items()}
		states = set()
		for src, lookup in transitions.items():
			states.add(src)
			states.update(lookup.values())
		states |= set(self._get_final_states()) | {initial_state}
		for state in states:
			transitions.setdefault(state, {})
		self._dfa = AutoDFA(
			states=states,
			input_symbols=set(self.alphabet),
			transitions=transitions,
			initial_state=initial_state,
			final_states=set(self._get_final_states()),
			allow_partial=self._allow_partial,
		)

	def _set_final_states(self, finals):
		initial_state = self._dfa.initial_state if self._dfa is not None else None
		if initial_state is None:
			self._dfa = AutoDFA.empty_language(set(self.alphabet))
			return
		transitions = {state: dict(lookup) for state, lookup in self.transitions.items()}
		states = set()
		for src, lookup in transitions.items():
			states.add(src)
			states.update(lookup.values())
		states |= set(finals) | {initial_state}
		for state in states:
			transitions.setdefault(state, {})
		self._dfa = AutoDFA(
			states=states,
			input_symbols=set(self.alphabet),
			transitions=transitions,
			initial_state=initial_state,
			final_states=set(finals),
			allow_partial=self._allow_partial,
		)

	@property
	def init(self):
		return Fsa._InitProxy(self)

	@init.setter
	def init(self, value):
		if not value:
			self._set_initial_state(None)
			return
		self._set_initial_state(next(iter(value.keys())))

	@property
	def final(self):
		return Fsa._FinalProxy(self)

	@final.setter
	def final(self, value):
		self._set_final_states(set(value))

	@property
	def states(self):
		return set() if self._dfa is None else set(self._dfa.states)

	@property
	def transitions(self):
		if self._dfa is None:
			return {}
		return {state: dict(lookup) for state, lookup in self._dfa.transitions.items()}

	def iter_transitions(self):
		for src, lookup in self.transitions.items():
			for symbol, dest in lookup.items():
				yield src, dest, symbol

	def size(self):
		return (len(self.states), sum(len(v) for v in self.transitions.values()))

	def has_transition(self, src, dest):
		return any(d == dest for d in self.transitions.get(src, {}).values())

	def transition_symbols(self, src, dest):
		return {symbol for symbol, dst in self.transitions.get(src, {}).items() if dst == dest}

	def add_transition(self, src, symbol, dest):
		states = set(self.states) | {src, dest}
		transitions = {state: dict(self.transitions.get(state, {})) for state in states}
		transitions.setdefault(src, {})[symbol] = dest
		initial_state = self._dfa.initial_state if self._dfa is not None else src
		finals = set(self.final)
		self._dfa = AutoDFA(
			states=states,
			input_symbols=set(self.alphabet),
			transitions=transitions,
			initial_state=initial_state,
			final_states=finals,
			allow_partial=self._allow_partial,
		)

	def add_transition_symbols(self, src, symbols, dest):
		states = set(self.states) | {src, dest}
		transitions = {state: dict(self.transitions.get(state, {})) for state in states}
		transitions.setdefault(src, {})
		for symbol in symbols:
			transitions[src][symbol] = dest
		initial_state = self._dfa.initial_state if self._dfa is not None else src
		finals = set(self.final)
		self._dfa = AutoDFA(
			states=states,
			input_symbols=set(self.alphabet),
			transitions=transitions,
			initial_state=initial_state,
			final_states=finals,
			allow_partial=self._allow_partial,
		)

	def _sync_from_auto(self, auto_dfa: AutoDFA):
		self.alphabet = set(auto_dfa.input_symbols)
		self._dfa = auto_dfa
		self._allow_partial = True

	@classmethod
	def from_automata_dfa(cls, auto_dfa: AutoDFA, props, template=None):
		fsa = cls(props, directed=True, multi=False)
		fsa.name = getattr(template, 'name', 'automata-lib DFA')
		if template is not None:
			if hasattr(template, 'kind'):
				fsa.kind = template.kind
			if hasattr(template, 'tree'):
				fsa.tree = copy.deepcopy(template.tree)
		fsa._sync_from_auto(auto_dfa)
		return fsa

	def to_automata_dfa(self) -> AutoDFA:
		if self._dfa is None:
			self._dfa = AutoDFA.empty_language(set(self.alphabet))
		return self._dfa


	def get_guard_bitmap(self, guard):
		"""
		Creates the bitmaps from guard string. The guard is a boolean expression
		over the atomic propositions.
		"""
		# Get sets for all props
		for key in self.props:
			guard = re.sub(r'\b%s\b' % key, "self.symbols_w_prop('%s')" % key, guard)

		# Handle (1)
		guard = re.sub(r'\(1\)', 'self.alphabet', guard)
		# Handle (0)
		guard = re.sub(r'\(0\)', 'set()', guard)

		# Handler negated sets
		guard = re.sub(r'!self.symbols_w_prop', 'self.symbols_wo_prop', guard)

		# Convert logic connectives
		guard = re.sub(r'\&\&', '&', guard)
		guard = re.sub(r'\|\|', '|', guard)

		return eval(guard)

	def add_trap_state(self):
		"""
		Adds a trap state and completes the automaton. Returns True whenever a
		trap state has been added to the automaton.
		"""
		self._dfa = self._dfa.to_complete()
		return None
	
	def remove_trap_states(self):
		'''
		Removes all states of the automaton which do not reach a final state.
		Returns True whenever trap states have been removed from the automaton.
		'''
		auto_dfa = self.to_automata_dfa()
		states = set(auto_dfa.states)
		finals = set(auto_dfa.final_states)
		transitions = {state: dict(auto_dfa.transitions.get(state, {})) for state in states}

		reverse = {state: set() for state in states}
		for src, lookup in transitions.items():
			for _, dest in lookup.items():
				reverse.setdefault(dest, set()).add(src)

		reachable = set()
		stack = list(finals)
		while stack:
			state = stack.pop()
			if state in reachable:
				continue
			reachable.add(state)
			stack.extend(reverse.get(state, set()))

		kept = reachable & states
		removed = states - kept
		if auto_dfa.initial_state not in kept:
			kept = set()

		new_transitions = {
			state: {sym: dest for sym, dest in transitions.get(state, {}).items() if dest in kept}
			for state in kept
		}
		pruned = AutoDFA(
			states=kept or {auto_dfa.initial_state},
			input_symbols=set(auto_dfa.input_symbols),
			transitions=new_transitions if kept else {auto_dfa.initial_state: {}},
			initial_state=auto_dfa.initial_state,
			final_states=finals & kept,
			allow_partial=True,
		)
		self._sync_from_auto(pruned)
		return len(removed) == 0

	def unify_accepting_states(self, new_state='accept'):
		'''
		Unifies all accepting states into a single accepting state.
		
		Any edge leading to any accepting state will be redirected to the new
		accepting state, and all edges leaving any accepting state will be
		converted into self-loops on the new accepting state.
		Returns the name of the new accepting state, or None if there were no
		accepting states.
		'''
		accepting = set(self.final)
		if not accepting:
			return None

		base_name = 'accept' if new_state is None else str(new_state)
		candidate = base_name
		suffix = 0
		states = set(self.states)
		while candidate in states:
			suffix += 1
			candidate = '{}_{}'.format(base_name, suffix)
		new_state = candidate
		states.add(new_state)

		transitions = {state: dict(self.transitions.get(state, {})) for state in states}
		transitions.setdefault(new_state, {})

		for src, lookup in transitions.items():
			for symbol, dest in list(lookup.items()):
				if dest in accepting:
					lookup[symbol] = new_state

		for symbol in self.alphabet:
			transitions[new_state][symbol] = new_state

		removable = accepting - set(self.init.keys())
		states -= removable
		for state in removable:
			transitions.pop(state, None)
		for src in list(transitions.keys()):
			transitions[src] = {sym: dst for sym, dst in transitions[src].items() if dst in states}

		if self.init:
			init_state = next(iter(self.init.keys()))
			if init_state in accepting:
				self.init = {new_state: 1}
		self._dfa = AutoDFA(
			states=states,
			input_symbols=set(self.alphabet),
			transitions=transitions,
			initial_state=next(iter(self.init.keys())) if self.init else new_state,
			final_states=set([new_state]),
			allow_partial=self._allow_partial,
		)
		return new_state

	def symbols_w_prop(self, prop):
		"""
		Returns symbols from the automaton's alphabet which contain the given
		atomic proposition.
		"""
		return set(filter(lambda symbol: True if self.props[prop] & (symbol - 1) else False, self.alphabet))

	def symbols_wo_prop(self, prop):
		"""
		Returns symbols from the automaton's alphabet which does not contain the
		given atomic proposition.
		"""
		return self.alphabet.difference(self.symbols_w_prop(prop))

	def bitmap_of_props(self, props):
		"""
		Returns bitmap corresponding the set of atomic propositions.
		"""
		return reduce(op.or_, [self.props.get(p, 0) for p in props], 0) + 1

	def next_states_of_fsa(self, q, props):
		"""
		Returns the next states of state q given input proposition set props. 
		"""
		# Get the bitmap representation of props
		prop_bitmap = self.bitmap_of_props(props)
		dest = self.transitions.get(q, {}).get(prop_bitmap)
		return [dest] if dest is not None else []

	def determinize(self):
		"""
		Determinizes the automaton using subset construction.

		The method supports epsilon transitions encoded by an edge attribute
		``epsilon=True`` or by an empty ``input`` set.
		"""
		if not self.init:
			return Fsa(self.props, self.directed, False)

		auto_dfa = self.to_automata_dfa()
		det = Fsa(self.props, self.directed, False)
		det.name = 'Determinized %s' % self.name
		det._sync_from_auto(auto_dfa)
		return det

