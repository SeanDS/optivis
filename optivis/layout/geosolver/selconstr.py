# -*- coding: utf-8 -*-

"""Selection constraints"""

from __future__ import unicode_literals, division

import abc

from optivis.layout.geosolver.constraint import Constraint
from optivis.geometry import is_clockwise, is_counterclockwise, is_obtuse, \
is_acute

class SelectionConstraint(Constraint):
    """Constraints for solution selection"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, variables):
        self.name = unicode(name)
        self.variables = list(variables)

    @abc.abstractmethod
    def satisfied(self, mapping):
        raise NotImplementedError

    def __unicode__(self):
        return "{0}({1})".format(self.name, ", ".join(self.variables))

    def __str__(self):
        return unicode(self).encode("utf-8")

class FunctionConstraint(SelectionConstraint):
    """Selects solutions where function returns True when applied to specified \
    variables"""

    def __init__(self, function, variables, name="FunctionConstraint"):
        """Instantiate a FunctionConstraint

        :param function: callable to call to check the constraint
        :param variables: list of variables as arguments for the function
        """

        # call parent constructor
        super(FunctionConstraint, self).__init__(name, variables)

        # set the function
        self.function = function

    def satisfied(self, mapping):
        """Check if mapping from variable names to points satisfies this \
        constraint

        :param mapping: map from variables to their points
        """

        # return whether the result of the function with the variables as
        # arguments is True or not
        return self.function(*[mapping[variable] for variable in \
        self.variables]) is True

    def __unicode__(self):
        return "{0}({1}, {2})".format(self.name, self.function.__name__, \
        ", ".join(self.variables))

class NotClockwiseConstraint(FunctionConstraint):
    """Selects triplets that are not clockwise (i.e. counter clockwise or \
    degenerate)"""

    def __init__(self, v1, v2, v3):
        """Instantiate a NotClockwiseConstraint

        :param v1: first variable
        :param v2: second variable
        :param v3: third variable
        """

        # create function to evaluate
        # checks if the points do not form a clockwise set
        function = lambda x, y, z: not is_clockwise(x, y, z)

        # call parent constructor
        super(NotClockwiseConstraint, self).__init__(function, [v1, v2, v3], \
        name="NotClockwiseConstraint")

class NotCounterClockwiseConstraint(FunctionConstraint):
    """Selects triplets that are not counter clockwise (i.e. clockwise or \
    degenerate)"""

    def __init__(self, v1, v2, v3):
        """Instantiate a NotCounterClockwiseConstraint

        :param v1: first variable
        :param v2: second variable
        :param v3: third variable
        """

        # create function to evaluate
        # checks if the points do not form a counter clockwise set
        function = lambda x, y, z: not is_counterclockwise(x, y, z)

        # call parent constructor
        super(NotCounterClockwiseConstraint, self).__init__(function, \
        [v1, v2, v3], name="NotCounterClockwiseConstraint")

class NotObtuseConstraint(FunctionConstraint):
    """Selects triplets that are not obtuse (i.e. acute or degenerate)"""

    def __init__(self, v1, v2, v3):
        """Instantiate a NotObtuseConstraint

        :param v1: first variable
        :param v2: second variable
        :param v3: third variable
        """

        # create function to evaluate
        # checks if the points do not form an obtuse angle
        function = lambda x, y, z: not is_obtuse(x, y, z)

        # call parent constructor
        super(NotObtuseConstraint, self).__init__(function, [v1, v2, v3], \
        name="NotObtuseConstraint")

class NotAcuteConstraint(FunctionConstraint):
    """Selects triplets that are not acute (i.e. obtuse or degenerate)"""

    def __init__(self,v1, v2, v3):
        """Instantiate a NotAcuteConstraint

        :param v1: first variable
        :param v2: second variable
        :param v3: third variable
        """

        # create function to evaluate
        # checks if the points do not form an acute angle
        function = lambda x, y, z: not is_acute(x, y, z)

        # call parent constructor
        super(NotAcuteConstraint, self).__init__(function, [v1, v2, v3], \
        name="NotAcuteConstraint")

def fnot(function):
    notf = lambda *args: not apply(function,args)
    notf.__name__ = str("fnot("+function.__name__+")")
    return notf

def test():
    print FunctionConstraint(is_right_handed, ['a','b','c','d'])
    print FunctionConstraint(fnot(is_right_handed), ['a','b','c','d'])

if __name__ == "__main__": test()
