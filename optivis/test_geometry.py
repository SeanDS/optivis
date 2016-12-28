from __future__ import unicode_literals, division

from unittest import TestCase
import math

from optivis.geometry import Scalar, Vector

class TestVector(TestCase):
    def setUp(self):
        self.a = Vector.origin()
        self.b = Vector(1.5, 8.3)
        self.unit_vector = Vector(1, 1)
        self.anti_unit_vector = Vector(-1, -1)

    def test_coordinates_init(self):
        # valid
        Vector(-1, 2)
        Vector(1, -2)
        Vector(4.61, -9.01)
        Vector("-3.141", "5.91")

        # invalid input types
        self.assertRaises(ValueError, Vector, "inv", "inv")
        self.assertRaises(TypeError, Vector, [], [])
        self.assertRaises(TypeError, Vector, {}, {})

        # test copy constructor
        self.assertEqual(self.a, Vector(self.a))
        self.assertEqual(self.b, Vector(self.b))

    def test_translate(self):
        self.assertEqual(self.a + self.b, self.b)
        self.assertEqual(self.b - self.b, self.a)

    def test_rotate(self):
        # rotation forward and back
        self.assertTrue(self.b.rotate(50).rotate(-50).tol_eq(self.b))

        # rotation through full circle
        self.assertTrue(self.b.rotate(360).tol_eq(self.b))

    def test_division(self):
        self.assertTrue((self.b / 2).tol_eq(Vector(self.b.x / 2, self.b.y / 2)))
        self.assertTrue((self.b / -3436.128115).tol_eq( \
        Vector(self.b.x / -3436.128115, self.b.y / -3436.128115)))

    def test_hypot(self):
        self.assertTrue(Scalar.tol_eq(self.a.length, math.sqrt(self.a.x ** 2 + self.a.y ** 2)))
        self.assertTrue(Scalar.tol_eq(self.b.length, math.sqrt(self.b.x ** 2 + self.b.y ** 2)))
        self.assertTrue(Scalar.tol_eq(self.unit_vector.length, math.sqrt(2)))
        self.assertTrue(Scalar.tol_eq(self.anti_unit_vector.length, math.sqrt(2)))

    def test_azimuth(self):
        # angle
        self.assertTrue(Scalar.tol_eq(self.a.azimuth, \
        math.degrees(math.atan2(self.a.y, self.a.x))))
        self.assertTrue(Scalar.tol_eq(self.b.azimuth, \
        math.degrees(math.atan2(self.b.y, self.b.x))))

    def test_flip(self):
        self.assertEqual(-self.unit_vector, self.anti_unit_vector)
        self.assertEqual(-self.b, Vector(-self.b.x, -self.b.y))

    def test_vector_calculus(self):
        # (1,1) - (1,1) - (1,1) = -(1,1)
        self.assertEqual(self.unit_vector - self.unit_vector \
        - self.unit_vector, -self.unit_vector)

    def test_n_sided_polygons(self):
        # test a whole bunch of polygons
        for i in xrange(3, 100):
            self._do_test_n_sided_polygon(i)

    def _do_test_n_sided_polygon(self, n):
        # external angle of each side w.r.t. last
        external_angle = 180 - (180 * (n - 2)) / n

        # side length
        side_vec = Vector(10.023522718, 0)

        # start vector
        vec = self.a

        # loop over the sides
        for i in range(n):
            # add the next side
            vec += side_vec.rotate(external_angle * i)

        # assert the vector is back at the origin
        self.assertTrue(vec.tol_eq(self.a), \
        "{0} != {1} ({2} sided polygon)".format(vec, self.a, n))

    def test_is_positive(self):
        self.assertTrue(Vector(1, 1).is_positive())
        self.assertTrue(Vector(0, 1000).is_positive())
        self.assertTrue(Vector(1000, 0).is_positive())
        self.assertTrue(Vector(294.1327, 1.95347).is_positive())
        self.assertTrue(Vector(0, 0).is_positive())
        self.assertFalse(Vector(-1, -1).is_positive())
        self.assertFalse(Vector(0, -1).is_positive())
        self.assertFalse(Vector(-1, 0).is_positive())
        self.assertFalse(Vector(-23592, -910.02436).is_positive())
