#  Copyright 2012 Machinalis S.R.L.
#
#  Author: Rafael Carrascosa <rcarrascosa@machinalis.com>
#
#  This file is part of REfO.
#
#  REfO is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation version 3 of the License, or
#  (at your option) any later version.
#
#  REfO is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with REfO.  If not, see <http://www.gnu.org/licenses/>.


class Instruction(object):
    """
    Non-opaque class to represent RE VM instructions.
    Instructions join among themselves to form code (a program).
    Instructions are joined like a linked list usign the `succ` and `split`
    attributes, thus forming a directed graph.
    """


class Atom(Instruction):
    def __init__(self, comparison_function, succ=None):
        self.comparison_function = comparison_function
        if succ is not None:
            self.succ = succ

    def __repr__(self):
        return "Atom({0})".format(repr(self.comparison_function))


class Accept(Instruction):
    succ = None

    def __repr__(self):
        return "Accept"


class Split(Instruction):
    def __init__(self, s1=None, s2=None):
        if s1 is not None:
            self.succ = s1
        if s2 is not None:
            self.split = s2

    def __repr__(self):
        return "Split({0}, {1})".format(repr(self.succ), repr(self.split))


class Save(Instruction):
    def __init__(self, record, succ=None):
        self.record = record
        if succ is not None:
            self.succ = succ

    def __repr__(self):
        return "Save({0})".format(repr(self.record))
