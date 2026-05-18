license_text='''
    Module implements API for translating a TWTL formula to a DFA. 
    Copyright (C) 2015-2016  Cristian Ioan Vasile <cvasile@bu.edu>
    Hybrid and Networked Systems (HyNeSs) Group, BU Robotics Lab,
    Boston University

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
'''
.. module:: twtl.py
   :synopsis: Module implements API for translating a TWTL formula to a DFA.

.. moduleauthor:: Cristian Ioan Vasile <cvasile@bu.edu>

'''

import logging

from lomap.classes.fsa import Fsa
from dfa import minimize_dfa
from runtime_monitor import RuntimeMonitor


def monitor_runtime(formula=None, dfa:Fsa|None=None):
    '''Creates a three-valued runtime monitor for a TWTL/UTWTL DFA.

    If a DFA is not provided, the function translates the given formula.
    By default, infinity DFA is used for runtime monitoring.
    '''
    if formula is None and dfa is None:
        raise Exception('Must provide either a TWTL formula or an automaton!')
    if dfa is None:
        _, dfa = translate(formula)
    dfa = minimize_dfa(dfa)
    return RuntimeMonitor(dfa)


def translate(formula: str):
    '''Converts a TWTL formula into an FSA. It can returns both a normal FSA or
    the automaton corresponding to the relaxed infinity version of the
    specification.
    If kind is: (a) DFAType.Normal it returns only the normal version;
    (b) DFAType.Infinity it returns only the relaxed version; and
    (c) 'both' it returns both automata versions.
    If norm is True then the bounds of the TWTL formula are computed as well.
    
    The functions returns a tuple containing in order: (a) the alphabet;
    (b) the normal automaton (if requested); (c) the infinity version automaton
    (if requested); and (d) the bounds of the TWTL formula (if requested).
    
    The ``optimize'' flag is used to specify that the annotation data should be
    optimized. Note that the synthesis algorithm assumes an optimized automaton,
    while computing temporal relaxations is performed using an unoptimized
    automaton.
    '''
    from antlr4_pipeline import evaluate_dfa, parse_formula
    
    parsed = parse_formula(formula)
    t = parsed.tree
    alphabet = parsed.alphabet
    result= [alphabet]
    
    dfa = evaluate_dfa(t, alphabet)
    # dfa.kind = DFAType.Normal
    result.append(dfa)

    
    if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug('[spec] spec: {}'.format(formula))

    
    return tuple(result)

if __name__ == '__main__':
#     print translate('[H^3 !A]^[0, 8] * [H^2 B & [H^4 C]^[3, 9]]^[2, 19]',
#                     kind=DFAType.Normal, norm=True)
    
    res = translate('[H^2 A]^[0, 4] | [H^2 B]^[2, 5]',)
    
    print(res)
    print(res[1].states)

