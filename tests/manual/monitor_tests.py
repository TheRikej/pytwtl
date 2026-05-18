import os
import sys

from matplotlib import pyplot as plt


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from twtl import monitor_runtime

formula = '[H^2 R2 & [H^2 R1]^[0, 8]]^[0, 20] & [H^2 R2 & [H^2 R3]^[0, 14]]^[0, 80]'
# formula = '[(H^2 A)*(H^2 B)]^[0]'
# formula = '([!([!(A)]^[0])]^[0])'

# mon = monitor_runtime(formula=formula)
mon = monitor_runtime('F(A) * (!B | H^0 C)')
print(mon._props)
print(len(mon.dfa.states), len(mon._sccs))
mon.dfa.show_diagram(path='monitor_automata.png', horizontal=True,)
# print(mon.dfa.show_diagram(horizontal=True,))
# plt.show()

mon.visualize(path='monitor.png', layout='dot', show_current=False)
# print(mon.step(set()))
# print(mon.step({'A', 'B'}))
# print(mon.step({'A', 'B'}))
# print(mon.step({'A'}))
# print(mon.step({'A'}))