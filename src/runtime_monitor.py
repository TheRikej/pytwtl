
import math

import networkx as nx

from lomap.classes.fsa import Fsa


VERDICT_TRUE = 'T'
VERDICT_FALSE = 'F'
VERDICT_UNKNOWN = '?'


class RuntimeMonitor(object):
    '''Runtime monitor with three-valued verdicts over DFA states.'''

    def __init__(self, dfa: Fsa):
        self.dfa = dfa
        self.verdict, self.lookahead = annotate_monitor(dfa)
        self.state = list(dfa.init.keys())[0]
        self.dead = False

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

        nxt = self.dfa.next_states_of_fsa(self.state, symbol)
        assert len(nxt) <= 1, 'Should be deterministic!'
        if not nxt:
            self.dead = True
            self.state = None
            return VERDICT_FALSE, 0

        self.state = nxt[0]
        return (self.verdict.get(self.state, VERDICT_UNKNOWN),
                self.lookahead.get(self.state, math.inf))

    def run(self, word):
        '''Consumes an iterable word and returns verdicts after each step.'''
        ret = []
        for symbol in word:
            ret.append(self.step(symbol))
        return ret

    def visualize(self, show_current=False):
        """Visualize the monitored DFA with verdicts and lookahead.

        - Nodes are labelled with their id, verdict and lookahead.
        - Node color: green=T, red=F, lightblue=?.
        - Current state (if any) is highlighted in yellow when `show_current`.
        Only `matplotlib` drawing is supported (consistent with other helpers).
        """
        import matplotlib.pyplot as plt
        g = self.dfa.g

        pos = nx.spring_layout(g)

        node_colors = []
        labels = {}
        for node in g.nodes():
            v = self.verdict.get(node, VERDICT_UNKNOWN)
            la = self.lookahead.get(node, math.inf)
            la_str = '∞' if math.isinf(la) else str(int(la))
            labels[node] = f"{node}\n{v} ({la_str})"

            if show_current and (not self.dead) and node == self.state:
                node_colors.append('yellow')
            elif v == VERDICT_TRUE:
                node_colors.append('green')
            elif v == VERDICT_FALSE:
                node_colors.append('red')
            else:
                node_colors.append('lightblue')

        # Draw main graph
        nx.draw(g, pos=pos, node_color=node_colors, with_labels=False)
        nx.draw_networkx_labels(g, pos=pos, labels=labels)
        edge_labels = nx.get_edge_attributes(g, 'label')
        nx.draw_networkx_edge_labels(g, pos=pos, edge_labels=edge_labels)

        # Draw an arrow marker for the initial state
        init = next(iter(self.dfa.init.keys()))
        # compute a marker position slightly left of the node
        node_pos = pos.get(init, (0.0, 0.0))
        try:
            mx = node_pos[0] - 0.12
            my = node_pos[1]
        except Exception:
            mx, my = (node_pos[0] - 0.12, node_pos[1])
        marker = f'__init_marker__'
        pos_marker = dict(pos)
        pos_marker[marker] = (mx, my)

        # draw marker node (triangle) and an arrow edge to the init node
        # nx.draw_networkx_nodes(g, pos=pos_marker, nodelist=[marker], node_color=['black'], node_shape='>', node_size=300)
        nx.draw_networkx_edges(g, pos=pos_marker, edgelist=[(marker, init)], arrows=True, arrowsize=20)

        plt.show()


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


def annotate_monitor(dfa):
    '''Annotates each DFA state with a verdict in {T, F, ?} and lookahead.

    The annotation follows SCC condensation and reverse topological
    propagation. Cyclic multi-state SCCs are marked as inconclusive with
    infinite lookahead.
    '''
    g = dfa.g
    finals = set(dfa.final)

    sccs, comp_of, dag = _build_scc_dag(g)
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
