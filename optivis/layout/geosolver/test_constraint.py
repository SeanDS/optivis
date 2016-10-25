from __future__ import unicode_literals, division

from unittest import TestCase

from optivis.layout.geosolver.constraint import ConstraintGraph, PlusConstraint

class TestConstraints(TestCase):
    def setUp(self):
        self.problem = ConstraintGraph()

        self.problem.add_variable('a')
        self.problem.add_variable('b')
        self.problem.add_variable('d')
        self.problem.add_variable('f')
        self.problem.add_variable('g')

        # create plus constraints
        self.plus1 = PlusConstraint('a', 'b', 'c')
        self.plus2 = PlusConstraint('c', 'd', 'e')
        self.plus3 = PlusConstraint('e', 'f', 'g')

        self.problem.add_constraint(self.plus1)
        self.problem.add_constraint(self.plus2)
        self.problem.add_constraint(self.plus3)

    def test_variables(self):
        # all variables including implictly defined ones should be there
        self.assertIn('a', self.plus1.variables())
        self.assertIn('b', self.plus1.variables())
        self.assertIn('c', self.plus1.variables())
        self.assertIn('c', self.plus2.variables())
        self.assertIn('d', self.plus2.variables())
        self.assertIn('e', self.plus2.variables())
        self.assertIn('e', self.plus3.variables())
        self.assertIn('f', self.plus3.variables())
        self.assertIn('g', self.plus3.variables())

    def test_get_constraints_on(self):
        # all of the variables should have plus as a constraint
        self.assertIn(self.plus1, self.problem.get_constraints_on('a'))
        self.assertIn(self.plus1, self.problem.get_constraints_on('b'))
        self.assertIn(self.plus1, self.problem.get_constraints_on('c'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('c'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('d'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('e'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('e'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('f'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('g'))

    def test_get_constraints_on_all(self):
        # a and b only have plus1
        self.assertEqual(self.problem.get_constraints_on_all(['a', 'b']), \
        [self.plus1])

        # adding c shouldn't change the fact
        self.assertEqual(self.problem.get_constraints_on_all(['a', 'b', 'c']), \
        [self.plus1])

    def test_get_constraints_on_any(self):
        # c has two constraints, so we should see them
        # use sets to avoid differences in order
        self.assertEqual(set(self.problem.get_constraints_on_any(['a', 'b', \
        'c'])), set([self.plus1, self.plus2]))

        # e too
        self.assertEqual(set(self.problem.get_constraints_on_any(['a', 'b', \
        'c', 'd', 'e', 'f', 'g'])), set([self.plus1, self.plus2, self.plus3]))
