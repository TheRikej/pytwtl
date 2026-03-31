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

import sys
import os
import subprocess
import logging


logger = logging.getLogger(__name__)


_lomap_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _binary_path(rel_path):
	path = os.path.join(_lomap_root, rel_path)
	if not os.path.exists(path):
		return None
	return path

# Initialize binaries
if sys.platform[0:5] == 'linux':
	ltl2ba_binary = _binary_path('binaries/linux/ltl2ba')
	scheck_binary = _binary_path('binaries/linux/scheck2')
elif sys.platform == 'darwin':
	ltl2ba_binary = _binary_path('binaries/mac/ltl2ba')
	scheck_binary = _binary_path('binaries/mac/scheck2')
else:
	sys.stderr.write('%s platform not supported yet!\n' % sys.platform)
	sys.stderr.write('Binaries will not work!\n')
	ltl2ba_binary = None
	scheck_binary = None
	
if ltl2ba_binary is None or scheck_binary is None:
	logger.info('LOMAP third-party binaries are not bundled. LTL/Buchi conversion utilities will be unavailable.')

# Best-effort chmod when binaries are present but not executable.
if ltl2ba_binary is not None and scheck_binary is not None:
	if not os.access(ltl2ba_binary, os.X_OK) or not os.access(scheck_binary, os.X_OK):
		try:
			subprocess.Popen(['chmod', '+x', ltl2ba_binary, scheck_binary], stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
		except Exception as ex:
			logger.warning("Could not set execute permission for bundled binaries: %s", ex)
