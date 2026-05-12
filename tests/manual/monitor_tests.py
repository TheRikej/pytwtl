import os
import sys

from matplotlib import pyplot as plt


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from twtl import monitor_runtime

mon = monitor_runtime('[!(H^150 A)]^[0]')
print(mon.dfa.size())
mon.dfa.visualize()
plt.show()

mon.visualize()
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})