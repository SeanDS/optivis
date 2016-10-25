# -*- coding: utf-8 -*-

"""Selection constraints"""

from __future__ import unicode_literals, division

import abc

from optivis.layout.geosolver.constraint import Constraint
from optivis.layout.geosolver.tolerance import tol_eq
from optivis.layout.geosolver.intersections import *

class SelectionConstraint(Constraint):
    """constraints for solution selection"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, variables):
        self.name = unicode(name)
        self.variables = list(variables)

    def __unicode__(self):
        return "{0}({1})".format(self.name, ", ".join(self.variables))

    def __str__(self):
        return unicode(self).encode("utf-8")

class NotCounterClockwiseConstraint(SelectionConstraint):
    """select triplets that are not counter clockwise (clockwise or degenerate)"""

    def __init__(self, v1, v2, v3):
        """init constraint with names of point variables"""
        super(NotCounterClockwiseConstraint, self).__init__( \
        "NotCounterClockwiseConstraint", [v1, v2, v3])

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self.variables[0]]
        p2 = map[self.variables[1]]
        p3 = map[self.variables[2]]
        return not is_counterclockwise(p1, p2, p3)

class NotClockwiseConstraint(SelectionConstraint):
    """select triplets that are not clockwise (counterclockwise or degenerate)"""

    def __init__(self, v1, v2, v3):
        """init constraint with names of point variables"""
        super(NotClockwiseConstraint, self).__init__("NotClockwiseConstraint", \
        [v1, v2, v3])

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self.variables[0]]
        p2 = map[self.variables[1]]
        p3 = map[self.variables[2]]
        return not is_clockwise(p1, p2, p3)

class NotObtuseConstraint(SelectionConstraint):
    """select triplets that are not obtuse (acute or degenerate)"""

    def __init__(self, v1, v2, v3):
        """init constraint with names of point variables"""
        super(NotObtuseConstraint, self).__init__("NotObtuseConstraint", \
        [v1, v2, v3])

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self.variables[0]]
        p2 = map[self.variables[1]]
        p3 = map[self.variables[2]]
        return not is_obtuse(p1, p2, p3)

class NotAcuteConstraint(SelectionConstraint):
    """select triplets that are not acute (obtuse or degenerate)"""

    def __init__(self,v1, v2, v3):
        """init constraint with names of point variables"""
        super(NotAcuteConstraint, self).__init__("NotAcuteConstraint", \
        [v1, v2, v3])

    def satisfied(self, map):
        """return True iff mapping from variable names to points satisfies constraint"""
        p1 = map[self.variables[0]]
        p2 = map[self.variables[1]]
        p3 = map[self.variables[2]]
        return not is_acute(p1, p2, p3)

class FunctionConstraint(SelectionConstraint):
    """select solutions where function returns true when applied to given variables"""

    def __init__(self, function, variables):
        """init constraint with function and a sequence of variables"""
        super(FunctionConstraint, self).__init__("FunctionConstraint", \
        variables)

        self.function = function

    def satisfied(self, map):
        """return True iff given solution (map) for given variables applied to function gives True"""
        values = []
        for variable in self.variables:
            values.append(map[variable])
        return apply(self.function, values)==True

    def __unicode__(self):
        return "{0}({1}, {2})".format(self.name, self.function.__name__, \
        ", ".join(self.variables))

def fnot(function):
    notf = lambda *args: not apply(function,args)
    notf.__name__ = str("fnot("+function.__name__+")")
    return notf

def test():
    print FunctionConstraint(is_right_handed, ['a','b','c','d'])
    print FunctionConstraint(fnot(is_right_handed), ['a','b','c','d'])

if __name__ == "__main__": test()
