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


class Nfa(Fsa):
	"""
	Base class for nondeterministic finite automata with epsilon transitions.
	"""

	def __init__(self, props=None, directed=True, multi=True):
		"""
		LOMAP NFA automaton object constructor.
		"""
		super().__init__(props=props, directed=directed, multi=multi)

	def clone(self):
		ret = Nfa(self.props, self.directed, self.multi)
		ret.g = self.g.copy()
		ret.name = str(self.name)
		ret.init = dict(self.init)
		ret.final = set(self.final)
		if hasattr(self, 'tree'):
			import copy
			ret.tree = copy.deepcopy(self.tree)
		if hasattr(self, 'kind'):
			ret.kind = self.kind
		return ret

	def add_epsilon_transition(self, source, target, weight=0, label='ε', **attrs):
		"""
		Adds an epsilon transition between ``source`` and ``target``.
		"""
		data = dict(attrs)
		data.update({'weight': weight, 'input': set(), 'epsilon': True, 'guard': '(0)', 'label': label})
		self.g.add_edge(source, target, **data)

	def next_states_of_nfa(self, q, props):
		"""
		Returns the epsilon-closed next states of state ``q`` given an input
		proposition set ``props``.
		"""
		prop_bitmap = self.bitmap_of_props(props)
		next_states = set()
		for state in self.epsilon_closure(q):
			for _, v, d in self.g.out_edges(state, data=True):
				inputs = self._edge_input_symbols(d)
				if prop_bitmap in inputs:
					next_states.update(self.epsilon_closure({v}))
		return list(next_states)