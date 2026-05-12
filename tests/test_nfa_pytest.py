import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lomap import Nfa


def test_nfa_determinize_supports_epsilon_closure_and_merges_symbols():
	nfa = Nfa(['A'], directed=True, multi=False)
	nfa.init = {'q0': 1}
	nfa.final = {'q2'}
	nfa.g.add_node('q0')
	nfa.g.add_node('q1')
	nfa.g.add_node('q2')
	nfa.add_epsilon_transition('q0', 'q1')
	nfa.g.add_edge('q1', 'q2', **{'weight': 0, 'input': set([0, 1]), 'guard': 'A or !A', 'label': 'A'})

	dfa = nfa.determinize()

	assert dfa.init == {0: 1}
	assert dfa.final == {1}
	assert dfa.next_states_of_fsa(0, {'A'}) == [1]
	edge_data = next(iter(dfa.g.edges(data=True)))[2]
	assert edge_data['input'] == {0, 1}