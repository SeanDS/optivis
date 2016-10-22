# -*- coding: utf-8 -*-

"""Selection constraints"""

from __future__ import unicode_literals, division

from optivis.layout.geosolver.constraint import Constraint
from optivis.layout.geosolver.tolerance import tol_eq
from optivis.layout.geosolver.intersections import *

class SelectionConstraint(Constraint):
    """constraints for solution selection"""

class NotCounterClockwiseConstraint(SelectionConstraint):
    """select triplets that are not counter clockwise (clockwise or degenerate)"""

    def __init__(self,v1,v2,v3):
        """init constraint with names of point variables"""
        self._variables = [v1,v2,v3]

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self._variables[0]]
        p2 = map[self._variables[1]]
        p3 = map[self._variables[2]]
        return not is_counterclockwise(p1,p2,p3)

    def __str__(self):
         return "NotCounterClockwiseConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._variables[2])+")"

class NotClockwiseConstraint(SelectionConstraint):
    """select triplets that are not clockwise (counterclockwise or degenerate)"""

    def __init__(self,v1,v2,v3):
        """init constraint with names of point variables"""
        self._variables = [v1,v2,v3]

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self._variables[0]]
        p2 = map[self._variables[1]]
        p3 = map[self._variables[2]]
        return not is_clockwise(p1,p2,p3)

    def __str__(self):
         return "NotClockwiseConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._variables[2])+")"

class NotObtuseConstraint(SelectionConstraint):
    """select triplets that are not obtuse (acute or degenerate)"""

    def __init__(self,v1,v2,v3):
        """init constraint with names of point variables"""
        self._variables = [v1,v2,v3]

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self._variables[0]]
        p2 = map[self._variables[1]]
        p3 = map[self._variables[2]]
        return not is_obtuse(p1,p2,p3)

    def __str__(self):
         return "NotObtuseConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._variables[2])+")"

class NotAcuteConstraint(SelectionConstraint):
    """select triplets that are not acute (obtuse or degenerate)"""

    def __init__(self,v1,v2,v3):
        """init constraint with names of point variables"""
        self._variables = [v1,v2,v3]

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self._variables[0]]
        p2 = map[self._variables[1]]
        p3 = map[self._variables[2]]
        return not is_acute(p1,p2,p3)

    def __str__(self):
         return "NotAcuteConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._variables[2])+")"

class FunctionConstraint(SelectionConstraint):
    """select solutions where function returns true when applied to given variables"""

    def __init__(self,function, vars):
        """init constraint with function and a sequence of variables"""
        self._variables = vars
        self._function = function

    def satisfied(self, map):
        """return True iff given solution (map) for given variables applied to function gives True"""
        values = []
        for var in self._variables:
            values.append(map[var])
        return apply(self._function, values)==True

    def __str__(self):
         return "FunctionConstraint("+self._function.__name__+","+str(map(str, self._variables))+")"

def fnot(function):
    notf = lambda *args: not apply(function,args)
    notf.__name__ = str("fnot("+function.__name__+")")
    return notf

def test():
    print FunctionConstraint(is_right_handed, ['a','b','c','d'])
    print FunctionConstraint(fnot(is_right_handed), ['a','b','c','d'])

if __name__ == "__main__": test()
