<h3>Overview</h3>
<strong>T</strong>ime <strong>W</strong>indow <strong>T</strong>emporal <strong>L</strong>ogic (TWTL) is a bounded temporal logic used to specify rich properties<a href="#1">[1]</a>. Relaxed versions of TWTL formulae are also considered in the sense of extending the deadlines of time windows. An automata based approach is proposed to solve synthesis, verification and learning problems. The key ingredient is a construction algorithm of annotated Deterministic Finite State Automata (DFA) from TWTL properties. See <a href="#1">[1]</a> for more details. 

This library is a python 3.12 implementation of PyTWTL, which provides an implementation of the algorithms proposed in <a href="#1">[1]</a> based on LOMAP <a href="#2">[2]</a>, ANTLRv4 <a href="#3">[3]</a> and networkx <a href="#4">[4]</a> libraries. PyTWTL implementation is released under the GPLv3 license.
The library can be used to:
<ul type="square">
    <li>construct DFAs and annotated DFAs from TWTL formulae;</li>
    <li>monitor the satisfaction of a TWTL formula;</li>
    <li>monitor the satisfaction of an arbitrary relaxation of a TWTL formula;</li>
    <li>compute the temporal relaxation of a trace with respect to a TWTL formula;</li>
    <li>compute a satisfying control policy with respect to a TWTL formula;</li>
    <li>compute a minimally relaxed control policy with respect to a TWTL formula;</li>
    <li>verify if all traces of a system satisfy some relaxed version of a TWTL formula;</li>
    <li>learn the parameters of a TWTL formula, i.e. the deadlines.</li>
</ul>

The parsing of TWTL formulae is performed using the ANTLRv4 framework. The package provides grammar files which may be used to generate lexers and parsers for other programming languages such as Java, C/C++, Ruby.

<h3>Citation</h3>
If you use TWTL or PyTWTL, then please consider citing the reference paper:

Cristian-Ioan Vasile, Derya Aksaray, and Calin Belta. <em>"Time Window Temporal Logic"</em>, arXiv preprint, <a href="http://arxiv.org/abs/1602.04294" target="_blank">arXiv:1602.04294</a>, 2016.
<a href="/hyness/files/2016/02/twtl.txt" target="_blank"><strong>[bib]</strong></a>

<h3>Download original python 2.7 PyTWTL library</h3>
<a href="/hyness/files/2016/02/pytwtl.zip">Download</a>

<h3>Requirements</h3>
The package is written for python 3.12. The following python packages are required:
<ul type="square">
    <li>NumPy</li>
    <li>NetworkX</li>
    <li>ParallelPython</li>
    <li>matplotlib</li>
    <li>setuptools</li>
    <li>ANTLRv4 python runtime</li>
</ul>
You can install the packages using:
<code>pip install --user networkx numpy matplotlib pp antlr4-python3-runtime setuptools</code>

<h3>How to Use</h3>
See <code>examples_tcs.py</code> for examples of the algorithms and the PyTWTL API.
An ANT build file <code>build.xml</code> is provided to generate the lexer and parser from the ANTLR4 grammar file.

<h3>License & Copying</h3>
<pre>Copyright (C) 2015-2016  Cristian Ioan Vasile <cvasile@bu.edu>
Hybrid and Networked Systems (HyNeSs) Group, BU Robotics Lab,
Boston University. Modified and extended by David Kajan, as part of master's thesis on Masaryk's university

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see &lt;http://www.gnu.org/licenses/&gt;.
</pre>

A copy of the GNU General Public License is included in the source folder in a file called 'gpl.txt'.


<h3>References</h3>
<p id="1">[1] Cristian-Ioan Vasile, Derya Aksaray, and Calin Belta. <em>"Time Window Temporal Logic."</em> arXiv preprint, <a href="http://arxiv.org/abs/1602.04294" target="_blank">arXiv:1602.04294</a>, 2016.</p>
<p id="2">[2] Alphan Ulusoy, Stephen L. Smith, Xu Chu Ding, Calin Belta, and Daniela Rus. <em>"Optimality and robustness in multi-robot path planning with temporal logic constraints."</em> The International Journal of Robotics Research 32, no. 8 (2013): 889-911.</p>
<p id="3">[3] Terence Parr. <em>"The Definitive ANTLR Reference: Building Domain-Specific Languages."</em> Pragmatic Bookshelf, 2007. ISBN 978-0978739256.</p>
<p id="4">[4] Aric A. Hagberg, Daniel A. Schult, and Pieter J. Swart. <em>"Exploring network structure, dynamics, and function using NetworkX."</em> 2008.</p>
