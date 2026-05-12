import os
import sys

from matplotlib import pyplot as plt


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from twtl import monitor_runtime

# mon = monitor_runtime('A')
mon = monitor_runtime('[(H^4 A * B) | H^3 B]^[0]')
mon.dfa.show_diagram(path='monitor_automata.png', horizontal=False)
# mon.dfa.visualize()
# plt.show()

mon.visualize_graphviz(path='monitor.png', layout='dot', show_current=True)
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})