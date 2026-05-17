import os
import sys

from matplotlib import pyplot as plt


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from twtl import monitor_runtime

# formula = '[H^2 R2 & [H^2 R1]^[0, 8]]^[0, 20] & [H^2 R2 & [H^2 R3]^[0, 14]]^[0]'
formula = '[(H^1 B)]^[2, 4]'
mon = monitor_runtime(formula=formula)
# mon = monitor_runtime('[(H^4 A * B) | H^3 B]^[0]')
mon.dfa.show_diagram(path='monitor_automata.png', horizontal=False)
print(mon.dfa.input_symbols)
# mon.dfa.visualize()
# plt.show()

mon.visualize_graphviz(path='monitor.png', layout='dot', show_current=True)
print(len(mon._comp_of))
# print(mon.step(set()))
print(mon.step({'A', 'B'}))
print(mon.step({'A', 'B'}))
print(mon.step({'A'}))
print(mon.step({'A'}))