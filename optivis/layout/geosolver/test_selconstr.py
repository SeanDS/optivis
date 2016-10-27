from __future__ import unicode_literals, division

from unittest import TestCase

from optivis.layout.geosolver.selconstr import FunctionConstraint
from optivis.layout.geosolver.vector import vector
from optivis.layout.geosolver.intersections import is_clockwise

class TestFunctionConstraint(TestCase):
    def setUp(self):
        # function constraint to check if a triangle is clockwise
        self.func_constraint = FunctionConstraint(is_clockwise, \
        ['a','b','c'])

    def test_clockwise(self):
        self.assertTrue(self.func_constraint.satisfied({'a': vector([0, 1]), \
        'b': vector([1, 0]), 'c': vector([0, -1])}))
