
import math
from functools import reduce
import operator as op

import networkx as nx

from automata.fa.dfa import DFA

from lomap.classes.fsa import Fsa


VERDICT_TRUE = 'T'
VERDICT_FALSE = 'F'
VERDICT_UNKNOWN = '?'


def _as_automata_dfa(dfa):
    if isinstance(dfa, DFA):
        return dfa
    if isinstance(dfa, Fsa):
        return dfa.to_automata_dfa()
    raise TypeError('Expected a LOMAP Fsa or automata-lib DFA.')


def _dfa_to_nx_graph(dfa: DFA):
    g = nx.DiGraph()
    g.add_nodes_from(dfa.states)
    for u, lookup in dfa.transitions.items():
        for _, v in lookup.items():
            g.add_edge(u, v)
    return g


def _create_complete_dfa(dfa: DFA | Fsa) -> DFA | Fsa:
    if isinstance(dfa, DFA):
        return dfa.to_complete()
    if isinstance(dfa, Fsa):
        dfa_clone = dfa.clone()
        dfa_clone.add_trap_state()
        return dfa_clone
    raise TypeError('Expected a LOMAP Fsa or automata-lib DFA.')


def _dfa_edge_labels(dfa: DFA):
    labels = {}
    for u, lookup in dfa.transitions.items():
        for symbol, v in lookup.items():
            labels.setdefault((u, v), set()).add(symbol)
    return labels


class RuntimeMonitor(object):
    '''Runtime monitor with three-valued verdicts over DFA states.'''

    def __init__(self, dfa: Fsa | DFA):
        self._props = getattr(dfa, "props", None)
        self.dfa = _as_automata_dfa(dfa)
        self._annotation_dfa = _as_automata_dfa(_create_complete_dfa(dfa))
        self._nx_graph = _dfa_to_nx_graph(self._annotation_dfa)
        self._sccs, self._comp_of, self._dag = _build_scc_dag(self._nx_graph)
        self.verdict, self.lookahead = annotate_monitor(
            self._annotation_dfa,
            precomputed=(self._nx_graph, self._sccs, self._comp_of, self._dag),
        )
        self.state = self.dfa.initial_state
        self.dead = False

    def _symbol_to_input(self, symbol):
        if isinstance(symbol, (set, list, tuple)) and self._props is not None:
            if not symbol:
                return 1
            return reduce(op.or_, [self._props.get(p, 0) for p in symbol], 0) + 1
        return symbol

    def current(self):
        '''Returns a tuple (verdict, lookahead, state).'''
        if self.dead:
            return VERDICT_FALSE, 0, None
        return (self.verdict.get(self.state, VERDICT_UNKNOWN),
                self.lookahead.get(self.state, math.inf),
                self.state)

    def step(self, symbol):
        '''Consumes one symbol (set of atomic propositions).'''
        if self.dead:
            return VERDICT_FALSE, 0

        sym = self._symbol_to_input(symbol)
        nxt = self.dfa.transitions.get(self.state, {}).get(sym)
        if nxt is None:
            self.dead = True
            self.state = None
            return VERDICT_FALSE, 0

        self.state = nxt
        return (self.verdict.get(self.state, VERDICT_UNKNOWN),
                self.lookahead.get(self.state, math.inf))

    def run(self, word):
        '''Consumes an iterable word and returns verdicts after each step.'''
        ret = []
        for symbol in word:
            ret.append(self.step(symbol))
        return ret

    def visualize(self, path='monitor.png', layout='dot', show_current=False):
        """Render a Graphviz visualization of the SCC condensation graph.

        Requires pygraphviz. Writes to `path` (e.g. .png or .svg).
        """
        import pygraphviz as pgv

        g = pgv.AGraph(directed=True, strict=False)
        g.graph_attr.update(rankdir='LR')

        sccs, comp_of, dag = self._sccs, self._comp_of, self._dag

        current_comp = None
        if show_current and (not self.dead) and self.state in comp_of:
            current_comp = comp_of[self.state]

        for cid, states in enumerate(sccs):
            rep = next(iter(states))
            v = self.verdict.get(rep, VERDICT_UNKNOWN)
            la = self.lookahead.get(rep, math.inf)
            la_str = '∞' if math.isinf(la) else str(int(la))
            states_label = ', '.join(str(s) for s in sorted(states))
            label = f"C{cid}\n{v} ({la_str})\n{states_label}"

            if current_comp == cid:
                fill = 'yellow'
            elif v == VERDICT_TRUE:
                fill = 'green'
            elif v == VERDICT_FALSE:
                fill = 'red'
            else:
                fill = 'lightblue'

            g.add_node(cid, label=label, style='filled', fillcolor=fill)

        for u, v in dag.edges():
            g.add_edge(u, v)

        init_marker = '__init__'
        init_comp = comp_of.get(self.dfa.initial_state)
        if init_comp is not None:
            g.add_node(init_marker, label='', shape='point', width=0.05, height=0.05)
            g.add_edge(init_marker, init_comp)

        g.layout(prog=layout)
        g.draw(path)
        return path


def _build_scc_dag(g):
    sccs = list(nx.strongly_connected_components(g))
    comp_of = {}
    for cid, scc in enumerate(sccs):
        for u in scc:
            comp_of[u] = cid

    dag = nx.DiGraph()
    dag.add_nodes_from(range(len(sccs)))
    for u, v in g.edges():
        cu, cv = comp_of[u], comp_of[v]
        if cu != cv:
            dag.add_edge(cu, cv)

    return sccs, comp_of, dag


def annotate_monitor(dfa: Fsa | DFA, precomputed=None):
    '''Annotates each DFA state with a verdict in {T, F, ?} and lookahead.

    The annotation follows SCC condensation and reverse topological
    propagation. Cyclic multi-state SCCs are marked as inconclusive with
    infinite lookahead.
    '''
    # dfa.add_trap_state()
    dfa = _create_complete_dfa(dfa)
    # dfa.show_diagram(path='monitor_automata_test.png', horizontal=False)

    auto_dfa = _as_automata_dfa(dfa)
    if precomputed is None:
        g = _dfa_to_nx_graph(auto_dfa)
        sccs, comp_of, dag = _build_scc_dag(g)
    else:
        g, sccs, comp_of, dag = precomputed
    finals = set(auto_dfa.final_states)
    order = list(nx.topological_sort(dag))
    order.reverse()

    comp_verdict = {}
    comp_lookahead = {}

    for cid in order:
        states = sccs[cid]
        succ = list(dag.successors(cid))

        if len(states) > 1:
            comp_verdict[cid] = VERDICT_UNKNOWN
            comp_lookahead[cid] = math.inf
            continue

        q = next(iter(states))

        if not succ:
            if q in finals:
                comp_verdict[cid] = VERDICT_TRUE
            else:
                comp_verdict[cid] = VERDICT_FALSE
            comp_lookahead[cid] = 0
            continue

        # A singleton cyclic SCC with exits may postpone decisions forever.

        succ_verdicts = set(comp_verdict[s] for s in succ)
        succ_bounds = [comp_lookahead[s] for s in succ]

        if succ_verdicts == set([VERDICT_TRUE]):
            comp_verdict[cid] = VERDICT_TRUE
        elif succ_verdicts == set([VERDICT_FALSE]):
            comp_verdict[cid] = VERDICT_FALSE
        else:
            comp_verdict[cid] = VERDICT_UNKNOWN

        if any(math.isinf(v) for v in succ_bounds):
            comp_lookahead[cid] = math.inf
        elif any(g.has_edge(s, s) for s in states):
            if comp_verdict[cid] != (VERDICT_TRUE if q in finals else VERDICT_FALSE):
                comp_verdict[cid] = VERDICT_UNKNOWN
                comp_lookahead[cid] = math.inf
            else:
                comp_lookahead[cid] = 0
        else:
            comp_lookahead[cid] = 1 + max(succ_bounds)

    verdict = {q: comp_verdict[comp_of[q]] for q in g.nodes()}
    lookahead = {q: comp_lookahead[comp_of[q]] for q in g.nodes()}
    return verdict, lookahead
