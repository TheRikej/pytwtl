import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from twtl import monitor_runtime

mon = monitor_runtime('[!A]^[0,4]')
mon.visualize()
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})
mon.step({'A'})