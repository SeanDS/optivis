from __future__ import unicode_literals, division

import numpy as np
from unittest import TestCase

from optivis.layout.geosolver.selconstr import FunctionConstraint, \
NotClockwiseConstraint, NotCounterClockwiseConstraint, NotObtuseConstraint, \
NotAcuteConstraint
from optivis.geometry import is_clockwise

class TestFunctionConstraint(TestCase):
    def setUp(self):
        # function constraint to check if a triangle is clockwise
        self.constraint = FunctionConstraint(is_clockwise, \
        ['a', 'b', 'c'])

    def test_function(self):
        # clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 1]), \
        'b': np.array([1, 0]), 'c': np.array([0, -1])}))

        # counter clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': np.array([0, -1]), \
        'b': np.array([1, 0]), 'c': np.array([0, 1])}))

class TestNotClockwiseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotClockwiseConstraint('a', 'b', 'c')

    def test_notclockwise(self):
        # counter clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': np.array([1, 0]), \
        'b': np.array([0, 1]), 'c': np.array([0, -1])}))

        # clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': np.array([1, 0]), \
        'b': np.array([0, -1]), 'c': np.array([0, 1])}))

        # edge case: 3 points on top of each other
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([0, 0]), 'c': np.array([0, 0])}))

class TestNotCounterClockwiseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotCounterClockwiseConstraint('a', 'b', 'c')

    def test_notcounterclockwise(self):
        # clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': np.array([1, 0]), \
        'b': np.array([0, -1]), 'c': np.array([0, 1])}))

        # counter clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': np.array([1, 0]), \
        'b': np.array([0, 1]), 'c': np.array([0, -1])}))

        # edge case: 3 points on top of each other
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([0, 0]), 'c': np.array([0, 0])}))

class TestNotObtuseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotObtuseConstraint('a', 'b', 'c')

    def test_notobtuse(self):
        # obtuse should be true
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([0, 1])}))

        # acute should be false
        self.assertFalse(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([2, 1])}))

        # edge case: 90 degrees
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([1, 1])}))

class TestNotAcuteConstraint(TestCase):
    def setUp(self):
        self.constraint = NotAcuteConstraint('a', 'b', 'c')

    def test_notacute(self):
        # acute should be true
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([2, 1])}))

        # obtuse should be true
        self.assertFalse(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([0, 1])}))

        # edge case: 90 degrees
        self.assertTrue(self.constraint.satisfied({'a': np.array([0, 0]), \
        'b': np.array([1, 0]), 'c': np.array([1, 1])}))
