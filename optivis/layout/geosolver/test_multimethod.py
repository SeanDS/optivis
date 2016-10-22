from __future__ import unicode_literals, division

from unittest import TestCase

from optivis.layout.geosolver.multimethod import MultiVariable, SumProdMethod
from optivis.layout.geosolver.method import MethodGraph

class TestSumProdMethod(TestCase):
    def setUp(self):
        # graph
        self.graph = MethodGraph()

        # multivariables
        self.x = MultiVariable('x')
        self.y = MultiVariable('y')
        self.z = MultiVariable('z')

    def test_sum_prod_method(self):
        self.graph.add_variable('a', 1)
        self.graph.add_variable('b', 2)

        self.graph.add_variable(self.x)

        # add sum product method
        self.graph.add_method(SumProdMethod('a', 'b', self.x))

        self.graph.add_variable('p', 3)
        self.graph.add_variable('q', 4)

        self.graph.add_variable(self.y)

        # add sum product method
        self.graph.add_method(SumProdMethod('p', 'q', self.y))

        self.graph.add_variable(self.z)

        # add sum product method
        self.graph.add_method(SumProdMethod(self.x, self.y, self.z))

        self.assertEqual(self.graph.get(self.z), \
        set([36, 21, 24, 9, 10, 14, 15]))
