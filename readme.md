<h3>Overview</h3>
<strong>T</strong>ime <strong>W</strong>indow <strong>T</strong>emporal <strong>L</strong>ogic (TWTL) is a bounded temporal logic used to specify rich properties<a href="#1">[1]</a>. 
This library provides support for an extention to TWTL called UTWTL, which extends TWTL with an eventually operator.
Also provides an implementation of a runtime monitor, for simple runtime verification of traces for a given formula.


This library is a Python 3.12 implementation of PyTWTL, which provides the algorithms proposed in <a href="#1">[1]</a> based on LOMAP <a href="#2">[2]</a>, ANTLRv4 <a href="#3">[3]</a>, automata-lib, and networkx <a href="#4">[4]</a>. PyTWTL implementation is released under the GPLv3 license.

The parsing of TWTL formulae is performed using the ANTLRv4 framework. The package provides grammar files which may be used to generate lexers and parsers for other programming languages such as Java, C/C++, Ruby.

<h3>Download original python 2.7 PyTWTL library</h3>
<a href="/hyness/files/2016/02/pytwtl.zip">Download</a>

<h3>Requirements</h3>
The package is written for Python 3.12. The following Python packages are required (see <code>requirements.txt</code> for the exact set and versions):
<ul type="square">
    <li>NumPy</li>
    <li>NetworkX</li>
    <li>matplotlib</li>
    <li>ANTLRv4 python runtime</li>
    <li>automata-lib</li>
    <li>pygraphviz (requires graphviz to be installed on your system)</li>
    <li>pytest (for tests)</li>
</ul>
Install via:
<code>pip install -r requirements.txt</code>

<h3>How to Use</h3>
For formula syntax and runnable examples, see <code>examples_formulas.py</code>.
An ANT build file <code>build.xml</code> is provided to regenerate the lexer and parser from the ANTLR4 grammar file. (Requires ANTLR4)

<h3>License & Copying</h3>
<pre>Copyright (C) 2015-2016  Cristian Ioan Vasile <cvasile@bu.edu>
Hybrid and Networked Systems (HyNeSs) Group, BU Robotics Lab, Boston University.
Modified and extended by David Kajan, as part of master's thesis at Masaryk's university, 2026

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
