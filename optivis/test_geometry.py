from __future__ import unicode_literals, division

from unittest import TestCase
import math

import optivis.geometry as geometry

class TestCoordinates(TestCase):
    def setUp(self):
        self.a = geometry.Coordinates(0, 0)
        self.b = geometry.Coordinates(1.5, 8.3)
        self.unit_vector = geometry.Coordinates(1, 1)
        self.anti_unit_vector = geometry.Coordinates(-1, -1)

    def test_coordinates_init(self):
        # valid
        geometry.Coordinates(-1, 2)
        geometry.Coordinates(1, -2)
        geometry.Coordinates(4.61, -9.01)
        geometry.Coordinates("-3.141", "5.91")

        # not enough inputs
        self.assertRaises(ValueError, geometry.Coordinates, "invalid")

        # invalid input types
        self.assertRaises(ValueError, geometry.Coordinates, "inv", "inv")
        self.assertRaises(TypeError, geometry.Coordinates, [], [])
        self.assertRaises(TypeError, geometry.Coordinates, {}, {})

    def test_translate(self):
        self.assertEqual(self.a + self.b, self.b)
        self.assertEqual(self.b - self.b, self.a)

    def test_rotate(self):
        # rotation forward and back
        self.assertEqual(self.b.rotate(50).rotate(-50), self.b)

        # rotation through full circle
        self.assertEqual(self.b.rotate(360), self.b)

    def test_azimuth(self):
        # angle
        self.assertEqual(self.a.azimuth, \
        math.degrees(math.atan2(self.a.y, self.a.x)))
        self.assertEqual(self.b.azimuth, \
        math.degrees(math.atan2(self.b.y, self.b.x)))

    def test_flip(self):
        self.assertEqual(self.unit_vector.flip(), self.anti_unit_vector)

    def test_vector_calculus(self):
        # (1,1) - (1,1) - (1,1) = -(1,1)
        self.assertEqual(self.unit_vector - self.unit_vector \
        - self.unit_vector, self.unit_vector.flip())
