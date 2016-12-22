# -*- coding: utf-8 -*-

"""Geometry classes for representing vectors and performing geometric
transformations on sets of vectors"""

from __future__ import unicode_literals, division

import numpy as np
import numpy.linalg as linalg
import logging

class Vector(np.ndarray):
    """Column vector in Cartesian coordinates"""

    def __new__(cls, x, y=None):
        """Vector-specific object initialisation

        This is required because numpy supports slicing and other template-based
        initialisations that return NEW objects. To allow the new objects to be
        of type Vector, and not ndarray, this __new__ method is required.

        See https://docs.scipy.org/doc/numpy/user/basics.subclassing.html#new-from-template
        """

        if y is None:
            #'copy constructor
            y = x.y
            x = x.x

        obj = np.asarray([[x], [y]]).view(cls)

        return obj

    @property
    def x(self):
        return self[0][0]

    @x.setter
    def x(self, x):
        self[0][0] = x

    @property
    def y(self):
        return self[1][0]

    @y.setter
    def y(self, y):
        self[1][0] = y

    def __unicode__(self):
        """String representation of the vector's coordinates"""

        return "({0:.3f}, {1:.3f})".format(self.x, self.y)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of the coordinates"""

        return unicode(self)

    @classmethod
    def origin(cls):
        """The coordinates of the origin"""

        return cls(0, 0)

    def pre_multiply(self, other):
        """Pre-multiplies the vector by other"""

        # do multiplication
        resultant = other * self

        # check the shape matches
        if resultant.shape != self.shape:
            raise Exception("Pre-multiplication did not yield a column vector")

        return resultant.view(Vector)

    def post_multiply(self, other):
        """Post-multiplies the vector by other"""

        # do multiplication
        resultant = self * other

        # check the shape matches
        if resultant.shape != self.shape:
            raise Exception("Post-multiplication did not yield a column vector")

        return resultant

    def rotate(self, azimuth):
        """Rotation of coordinates about the origin using a left-handed \
        coordinate system

        :param azimuth: the angle in degrees to rotate in a clockwise direction
        """

        # validate azimuth
        azimuth = float(azimuth)

        # apply rotation matrix to x and y
        x = self.x * np.cos(np.radians(azimuth)) \
        - self.y * np.sin(np.radians(azimuth))
        y = self.x * np.sin(np.radians(azimuth)) \
        + self.y * np.cos(np.radians(azimuth))

        # return new coordinates
        return Vector(x, y)

    @property
    def azimuth(self):
        """Azimuth defined by the coordinate with respect to the origin"""

        return np.degrees(np.arctan2(self.y, self.x))

    def length(self):
        """Length between point defined by coordinates and the origin"""

        return np.hypot(self.x, self.y)

    def is_positive(self):
        """Checks if the coordinates are all positive

        Assumes 0 is positive.
        """

        return self.x >= 0 and self.y >= 0

def cc_int(p1, r1, p2, r2):
    """Intersect circle (p1, r1) with circle (p2, r2)

    :param p1: vector representing centre of first circle
    :type p1: :class:`.np.ndarray`
    :param r1: scalar representing the radius of first circle
    :type r1: float
    :param p2: vector representing centre of second circle
    :type p2: :class:`.np.ndarray`
    :param r2: scalar representing the radius of first circle
    :type r2: float
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cc_int %s %s %s %s", p1, r1, p2, \
    r2)

    # distance between circle centres
    d = linalg.norm(p2-p1)

    # check if d < 0 within tolerance
    if np.allclose(d, 0.0) or np.less(d, 0.0):
        # no solutions
        return []

    u = ((r1*r1 - r2*r2) / d + d) / 2

    a = r1*r1
    b = u*u

    # check that a < b within tolerance
    # FIXME: what's going on here? this used to be tol_lt, but elif block seems to repeat earlier check
    if not np.allclose(a, b) and np.less(a, b):
        return []
    elif a < b:
        v = 0.0
    else:
        v = np.sqrt(a-b)

    s = (p2-p1) * u / d

    if np.allclose(linalg.norm(s),0):
        p3a = p1 + np.array([p2[1]-p1[1], p1[0]-p2[0]]) * r1/d

        if np.allclose(r1/d, 0):
            return [p3a]
        else:
            p3b = p1+np.array([p1[1]-p2[1], p2[0]-p1[0]]) * r1/d

            return [p3a, p3b]
    else:
        p3a = p1 + s + np.array([s[1], -s[0]]) * v / linalg.norm(s)

        if np.allclose(v / linalg.norm(s),0):
            return [p3a]
        else:
            p3b = p1 + s + np.array([-s[1], s[0]]) * v / linalg.norm(s)

            return [p3a,p3b]

def cl_int(p1, r, p2, v):
    """Intersect circle (p1, r) with line (p2, v)

    :param p1: vector representing centre of circle
    :type p1: :class:`.np.ndarray`
    :param r: scalar representing the radius of circle
    :type r1: float
    :param p2: vector representing a point on the line
    :type p2: :class:`.np.ndarray`
    :param v: vector representing the direction of the line
    :type v: :class:`.np.ndarray`
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cl_int %s %s %s %s", p1, r, p2, \
    v)

    # distance between centre of circle and start of line
    p = p2 - p1

    # squared length of line
    d2 = v[0]*v[0] + v[1]*v[1]

    D = p[0]*v[1] - v[0]*p[1]
    E = r*r*d2 - D*D

    # check that d2 and E are both > 0 within tolerance
    if not np.allclose(d2, 0.0) and np.greater(d2, 0.0) \
    and not np.allclose(E, 0.0) and np.greater(E, 0.0):
        sE = np.sqrt(E)
        x1 = p1[0] + (D * v[1] + np.sign(v[1])*v[0]*sE) / d2
        x2 = p1[0] + (D * v[1] - np.sign(v[1])*v[0]*sE) / d2
        y1 = p1[1] + (-D * v[0] + np.absolute(v[1])*sE) / d2
        y2 = p1[1] + (-D * v[0] - np.absolute(v[1])*sE) / d2

        return [np.array([x1, y1]), np.array([x2, y2])]
    elif np.allclose(E, 0):
        x1 = p1[0] + D * v[1] / d2
        y1 = p1[1] + -D * v[0] / d2

        return [np.array([x1, y1])]
    else:
        return []

def cr_int(p1, r, p2, v):
    """Intersect a circle (p1, r) with ray (p2, v) (a half-line)

    :param p1: vector representing centre of circle
    :type p1: :class:`.np.ndarray`
    :param r: scalar representing the radius of circle
    :type r1: float
    :param p2: vector representing a point on the ray
    :type p2: :class:`.np.ndarray`
    :param v: vector representing the direction of the ray
    :type v: :class:`.np.ndarray`
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cr_int %s %s %s %s", p1, r, p2, \
    v)

    solutions = []

    # loop over solutions of the circle and line intercept
    for s in cl_int(p1, r, p2, v):
        a = np.dot(s-p2, v)

        # check if a is >= 0 within tolerance
        if np.allclose(a, 0.0) or np.greater(a, 0.0):
            solutions.append(s)

    return solutions

def ll_int(p1, v1, p2, v2):
    """Intersect two lines

    :param p1: vector representing a point on the first line
    :type p1: :class:`.np.ndarray`
    :param v1: vector represting the direction of the first line
    :type v1: :class:`.np.ndarray`
    :param p2: vector representing a point on the second line
    :type p2: :class:`.np.ndarray`
    :param v2: vector represting the direction of the second line
    :type v2: :class:`.np.ndarray`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("ll_int %s %s %s %s", p1, v1, p2, \
    v2)

    if np.allclose(v1[0]*v2[1] - v1[1]*v2[0], 0.0):
        # lines don't intersect
        return []
    elif not np.allclose(v2[1], 0.0):
        d = p2-p1
        r2 = -v2[0]/v2[1]
        f = v1[0] + v1[1]*r2
        t1 = (d[0] + d[1]*r2) / f
    else:
        d = p2-p1
        t1 = d[1]/v1[1]

    return [p1 + v1*t1]

def lr_int(p1, v1, p2, v2):
    """Intersect line with ray

    :param p1: vector representing a point on the line
    :type p1: :class:`.np.ndarray`
    :param v1: vector represting the direction of the line
    :type v1: :class:`.np.ndarray`
    :param p2: vector representing a point on the ray
    :type p2: :class:`.np.ndarray`
    :param v2: vector represting the direction of the ray
    :type v2: :class:`.np.ndarray`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("lr_int %s %s %s %s", p1, v1, p2, \
    v2)

    # assume ray is a line and get intersection with line
    s = ll_int(p1, v1, p2, v2)

    a = np.dot(s[0]-p2, v2)

    # check if s > 0 and a >= 0 within tolerance
    if len(s) > 0 and np.allclose(a, 0.0) or np.greater(a, 0.0):
        return s
    else:
        # lines intersect behind ray
        return []

def rr_int(p1, v1, p2, v2):
    """Intersect ray with ray

    :param p1: vector representing a point on the first ray
    :type p1: :class:`.np.ndarray`
    :param v1: vector represting the direction of the first ray
    :type v1: :class:`.np.ndarray`
    :param p2: vector representing a point on the second ray
    :type p2: :class:`.np.ndarray`
    :param v2: vector represting the direction of the second ray
    :type v2: :class:`.np.ndarray`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("rr_int %s %s %s %s", p1, v1, p2, \
    v2)

    # assume rays are lines and get intersection
    s = ll_int(p1,v1,p2,v2)

    a1 = np.dot(s[0]-p1,v1)
    a2 = np.dot(s[0]-p2,v2)

    # check len(s) > 0 and a1 >= 0 and a2 >= 0 within tolerance
    if len(s) > 0 and np.allclose(a1, 0.0) or np.greater(a1, 0.0) \
    and np.allclose(a2, 0.0) or np.greater(a2, 0.0):
        return s
    else:
        # lines intersect behind rays
        return []

def angle_3p(p1, p2, p3):
    """Calculates the angle rotating vector p2p1 to vector p2p3

    The angle is signed and in the range [-pi, pi] corresponding to a clockwise
    rotation. If p1-p2-p3 is clockwise, then angle > 0.

    If the angle is degenerate (i.e. the triangle has zero area), None is
    returned.

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: angle in radians, or None
    :rtype: float
    """

    # distances between points
    d21 = linalg.norm(p2-p1)
    d23 = linalg.norm(p3-p2)

    if np.allclose(d21, 0) or np.allclose(d23, 0):
        # degenerate angle
        return None

    # vectors between points
    v21 = (p1-p2) / d21
    v23 = (p3-p2) / d23

    # calculate vector rotating v21 to v23
    t = np.dot(v21, v23)

    # clip to +/-1.0 to fix floating point errors
    if t > 1.0:
        t = 1.0
    elif t < -1.0:
        t = -1.0

    # calculate angle from rotation vector
    angle = np.arccos(t)

    if is_counterclockwise(p1, p2, p3):
        # flip angle
        angle = -angle

    return angle

def distance_2p(p1, p2):
    """Calculates the Euclidean distance between two points

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :returns: distance between the points
    :rtype: float
    """

    # calculate the norm on the vector between the two points
    return linalg.norm(p2-p1)

def is_clockwise(p1, p2, p3):
    """Calculates whether or not triangle p1, p2, p3 is orientated clockwise

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: True if clockwise, otherwise False
    :rtype: boolean
    """

    u = p2-p1
    v = p3-p2;
    perp_u = np.array([-u[1], u[0]])

    a = np.dot(perp_u, v)

    # check a < 0 within tolerance
    return not np.allclose(a, 0.0) and np.less(a, 0.0)

def is_counterclockwise(p1, p2, p3):
    """Calculates whether or not triangle p1, p2, p3 is orientated \
    counter-clockwise

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: True if counter-clockwise, otherwise False
    :rtype: boolean
    """

    u = p2 - p1
    v = p3 - p2;
    perp_u = np.array([-u[1], u[0]])

    a = np.dot(perp_u,v)

    # check that a > 0 within tolerance
    return not np.allclose(a, 0.0) and np.greater(a, 0.0)

def is_flat(p1, p2, p3):
    """Calculates wheter or not triangle p1, p2, p3 is flat (neither \
    clockwise nor counter-clockwise)

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: True if flat, otherwise False
    :rtype: boolean
    """

    u = p2 - p1
    v = p3 - p2;
    perp_u = np.array([-u[1], u[0]])

    return np.allclose(np.dot(perp_u, v), 0)

def is_acute(p1, p2, p3):
    """Calculates whether or not angle p1, p2, p3 is acute, i.e. less than \
    pi / 2

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: True if acute, otherwise False
    :rtype: boolean
    """

    # calculate angle between points
    angle = angle_3p(p1, p2, p3)

    if angle is None:
        return False

    a = np.absolute(angle)
    b = np.pi / 2

    # return whether a < b within tolerance
    return not np.allclose(a, b) and np.less(a, b)

def is_obtuse(p1,p2,p3):
    """Calculates whether or not angle p1, p2, p3 is obtuse, i.e. greater than \
    pi / 2

    :param p1: first point
    :type p1: :class:`.np.ndarray`
    :param p2: second point
    :type p2: :class:`.np.ndarray`
    :param p3: third point
    :type p3: :class:`.np.ndarray`
    :returns: True if obtuse, otherwise False
    :rtype: boolean
    """

    # calculate angle between points
    angle = angle_3p(p1, p2, p3)

    if angle is None:
        return False

    a = np.absolute(angle)
    b = np.pi / 2

    # check that a > b within tolerance
    return not np.allclose(a, b) and np.greater(a, b)

def make_hcs(a, b, scale=False):
    """Build a homogeneous coordiate system from two vectors, normalised

    :param a: first vector
    :type a: :class:`.np.ndarray`
    :param b: second vector
    :type b: :class:`.np.ndarray`
    :returns: 3x3 homogeneous coordinate matrix
    :rtype: :class:`.np.ndarray`
    """

    # resultant vector
    u = b-a

    if np.allclose(linalg.norm(u), 0.0):
        # vectors are on top of each other (within tolerance)
        return None

    if not scale:
        # normalise resultant
        u = u / linalg.norm(u)

    # mirror of u
    v = np.array([-u[1], u[0]])

    # return new coordinate system
    return np.array([
        [u[0], v[0], a[0]],
        [u[1], v[1], a[1]],
        [0.0, 0.0, 1.0]
    ])

def make_hcs_scaled(*args, **kwargs):
    """Build a homogeneous coordiate system from two vectors

    :param a: first vector
    :type a: :class:`.np.ndarray`
    :param b: second vector
    :type b: :class:`.np.ndarray`
    :returns: 3x3 homogeneous coordinate matrix
    :rtype: :class:`.np.ndarray`
    """

    return make_hcs(scale=True, *args, **kwargs)

def cs_transform_matrix(from_cs, to_cs):
    """Calculate the transformation matrix from one coordinate system to another

    :param from_cs: initial coordinate system
    :type from_cs: :class:`.np.ndarray`
    :param to_cs: target coordinate system
    :type to_cs: :class:`.np.ndarray`
    :returns: transformation matrix to convert from_cs to to_cs
    :rtype: :class:`.np.ndarray`
    """

    # multiply to_cs by the inverse of from_cs
    return np.dot(to_cs, linalg.inv(from_cs))

# -------------------------test code -----------------

def test_ll_int():
    """test random line-line intersection. returns True iff succesful"""
    # generate three points A,B,C an two lines AC, BC.
    # then calculate the intersection of the two lines
    # and check that it equals C
    p_a = vector.randvec(2, 0.0, 10.0, 1.0)
    p_b = vector.randvec(2, 0.0, 10.0, 1.0)
    p_c = vector.randvec(2, 0.0, 10.0, 1.0)
    # print p_a, p_b, p_c
    if np.allclose(linalg.norm(p_c - p_a),0) or np.allclose(linalg.norm(p_c - p_b),0):
        return True # ignore this case
    v_ac = (p_c - p_a) / linalg.norm(p_c - p_a)
    v_bc = (p_c - p_b) / linalg.norm(p_c - p_b)
    s = ll_int(p_a, v_ac, p_b, v_bc)
    if np.allclose(np.absolute(np.dot(v_ac, v_bc)),1.0):
        return len(s) == 0
    else:
        if len(s) > 0:
            p_s = s[0]
            return np.allclose(p_s[0],p_c[0]) and np.allclose(p_s[1],p_c[1])
        else:
            return False

def test_rr_int():
    """test random ray-ray intersection. returns True iff succesful"""
    # generate tree points A,B,C an two rays AC, BC.
    # then calculate the intersection of the two rays
    # and check that it equals C
    p_a = vector.randvec(2, 0.0, 10.0,1.0)
    p_b = vector.randvec(2, 0.0, 10.0,1.0)
    p_c = vector.randvec(2, 0.0, 10.0,1.0)
    # print p_a, p_b, p_c
    if np.allclose(linalg.norm(p_c - p_a),0) or np.allclose(linalg.norm(p_c - p_b),0):
        return True # ignore this case
    v_ac = (p_c - p_a) / linalg.norm(p_c - p_a)
    v_bc = (p_c - p_b) / linalg.norm(p_c - p_b)
    s = rr_int(p_a, v_ac, p_b, v_bc)
    if np.allclose(np.absolute(np.dot(v_ac, v_bc)),1.0):
        return len(s) == 0
    else:
        if len(s) > 0:
            p_s = s[0]
            return np.allclose(p_s[0],p_c[0]) and np.allclose(p_s[1],p_c[1])
        else:
            return False

def test1():
    sat = True
    for i in range(0,100):
        sat = sat and test_ll_int()
        if not sat:
            print "ll_int() failed"
            return
    if sat:
        print "ll_int() passed"
    else:
        print "ll_int() failed"

    sat = True
    for i in range(0,100):
        sat = sat and test_rr_int()
        if not sat:
            print "rr_int() failed"
            return

    if sat:
        print "rr_int() passed"
    else:
        print "rr_int() failed"

    print "2D angles"
    for i in xrange(9):
        a = i * 45 * np.pi / 180
        p1 = np.array([1.0,0.0])
        p2 = np.array([0.0,0.0])
        p3 = np.array([np.cos(a),np.sin(a)])
        print p3, angle_3p(p1,p2,p3) * 180 / np.pi, "flip", angle_3p(p3,p2,p1) * 180 / np.pi

if __name__ == '__main__': test1()
