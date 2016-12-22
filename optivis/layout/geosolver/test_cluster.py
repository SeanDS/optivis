from __future__ import unicode_literals, division

from unittest import TestCase

from optivis.layout.geosolver.cluster import Rigid, Balloon, Hedgehog

class TestCluster(TestCase):
    def setUp(self):
        self.rigid = Rigid([1, 3, 4, 5])
        self.balloon = Balloon([1, 2, 3, 4])
        self.hedgehog = Hedgehog(1, [2, 3, 5])

    def test_valid_intersections(self):
        # intersections with self should yield self
        self.assertTrue(TestCluster.clusters_equal( \
        self.rigid.intersection(self.rigid), self.rigid))
        self.assertTrue(TestCluster.clusters_equal( \
        self.balloon.intersection(self.balloon), self.balloon))
        self.assertTrue(TestCluster.clusters_equal( \
        self.hedgehog.intersection(self.hedgehog), self.hedgehog))

        # other intersections
        self.assertTrue(TestCluster.clusters_equal( \
        self.rigid.intersection(self.balloon), Balloon([1, 3, 4])))
        self.assertTrue(TestCluster.clusters_equal( \
        self.rigid.intersection(self.hedgehog), Hedgehog(1, [3, 5])))
        self.assertTrue(TestCluster.clusters_equal( \
        self.balloon.intersection(self.hedgehog), Hedgehog(1, [2, 3])))

    def test_invalid_intersections(self):
        # less than 3 variables in balloons and hedgehogs
        with self.assertRaises(Exception):
            Balloon([1, 2])
            Hedgehog(1, [2])

    def test_nonetype_intersections(self):
        # less than 2 overlapping points
        self.assertIsNone(self.rigid.intersection(Rigid([5, 6, 7])))
        self.assertIsNone(self.balloon.intersection(Balloon([4, 5, 6])))
        self.assertIsNone(self.hedgehog.intersection(Hedgehog(1, [6, 7, 8])))

        # rigid overlapping a balloon with less than 3 shared points (but more
        # than 2)
        self.assertIsNone(self.rigid.intersection(Balloon([4, 5, 6])))

        # rigid overlapping a hedgehog without the hedgehog's central value
        # being in the rigid (but still with more than 2 shared points)
        self.assertIsNone(self.rigid.intersection(Hedgehog(6, [1, 3, 4, 5])))

        # two balloons with only 2 shared points
        self.assertIsNone(self.balloon.intersection(Balloon([3, 4, 5, 6])))

        # balloon overlapping a hedgehog without the hedgehog's central value
        # being in the balloon (but still with more than 2 shared points)
        self.assertIsNone(self.balloon.intersection(Hedgehog(5, [1, 2, 3, 4])))

        # two hedgehogs not sharing the same central point (but sharing 2 other
        # points)
        self.assertIsNone(self.hedgehog.intersection(Hedgehog(6, [1, 2, 3, 5])))

    def test_reverse(self):
        """Reverse intersections should be the same as forward intersections"""

        self.assertTrue(TestCluster.clusters_equal( \
        self.rigid.intersection(self.balloon), \
        self.balloon.intersection(self.rigid)))
        self.assertTrue(TestCluster.clusters_equal( \
        self.rigid.intersection(self.hedgehog), \
        self.hedgehog.intersection(self.rigid)))
        self.assertTrue(TestCluster.clusters_equal( \
        self.balloon.intersection(self.hedgehog), \
        self.hedgehog.intersection(self.balloon)))

    @staticmethod
    def clusters_equal(first, second):
        """Checks if the specified clusters are equal"""

        return set(first.vars) == set(second.vars) and first.name == second.name
