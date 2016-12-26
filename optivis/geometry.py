# -*- coding: utf-8 -*-

"""Geometry classes for representing vectors and performing geometric
transformations on sets of vectors"""

from __future__ import unicode_literals, division

import numpy as np
import numpy.linalg as la
import math
import logging
import copy

class Scalar(object):
    """Scalar value functions"""

    """Relative tolerance"""
    rel_tol = 1e-05

    """Absolute tolerance"""
    abs_tol = 1e-08

    @staticmethod
    def sign(x):
        if x > 0:
            return 1

        return -1

    @classmethod
    def tol_eq(cls, a, b, rel_tol=None, abs_tol=None):
        if rel_tol is None:
            rel_tol = cls.rel_tol

        if abs_tol is None:
            abs_tol = cls.abs_tol

        a = float(a)
        b = float(b)

        return abs(a - b) <= (abs_tol + rel_tol * abs(b))

    @classmethod
    def tol_zero(cls, a, *args, **kwargs):
        return cls.tol_eq(a, 0, *args, **kwargs)

    @classmethod
    def tol_gt(cls, a, b, *args, **kwargs):
        return a > b and not cls.tol_eq(a, b, *args, **kwargs)

    @classmethod
    def tol_lt(cls, a, b, *args, **kwargs):
        return a < b and not cls.tol_eq(a, b, *args, **kwargs)

    @classmethod
    def tol_ge(cls, a, b, *args, **kwargs):
        return a > b or cls.tol_eq(a, b, *args, **kwargs)

    @classmethod
    def tol_le(cls, a, b, *args, **kwargs):
        return a < b or cls.tol_eq(a, b, *args, **kwargs)

class Matrix(object):
    """Matrix and associated methods"""

    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        rep = ""

        return "\n".join([" ".join([unicode(element) for element in row]) \
        for row in self.elements])

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        # TODO: check if dimensions > 2, but has to be quick
        self._elements = elements

    @classmethod
    def identity(cls, size):
        if size == 2:
            return cls([[1.0, 0.0], [0.0, 1.0]])

        raise NotImplementedError("Size != 2 not available")

    @property
    def num_rows(self):
        return len(self.elements)

    @property
    def num_cols(self):
        return len(self.elements[0])

    @property
    def num_elements(self):
        return self.num_rows * self.num_cols

    @property
    def num_dim(self):
        """Number of dimensions"""

        dimensions = 1

        if (self.num_rows > 1) and (self.num_cols > 1):
            dimensions += 1

        return dimensions

    def inverse(self):
        if self.num_rows is not self.num_cols:
            raise Exception('Inverse only defined for square matrices')

        return self.solve(self.identity(self.num_rows))

    def transpose(self):
        """Transpose of matrix"""

        t_matrix = []

        for row in xrange(self.num_cols):
            t_row = []

            for col in xrange(self.num_rows):
                t_row.append(self.elements[col][row])

            t_matrix.append(t_row)

        return(self.__class__(t_matrix))

    def round(self, precision=4):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.elements[row][col] = round(self.elements[row][col], \
                precision)

    def __mul__(self, other):
        """Matrix multiplication

        :param other: other matrix
        :type other: :class:`.Matrix`
        """

        if self.num_cols is not other.num_rows:
            raise Exception('Matrix dimensions mismatch')

        return Matrix([[sum(a * b for a, b in zip(row_a, col_b)) \
        for col_b in zip(*other.elements)] for row_a in self.elements])

    def solve(self, B, *args, **kwargs):
        """Solve Ax = B for x, where A is this matrix and B is another matrix \
        or vector

        :param B: right hand side matrix or vector
        :type B: :class:`Matrix`
        :returns: solution x of Ax = B, where x has the same shape as B
        :rtype: :class:`Matrix`
        """

        # use Numpy for now
        A = np.array(self.elements)
        B = np.array(B.elements)

        # solve
        x = la.solve(A, B)

        return Matrix(x.tolist())

    @classmethod
    def identity(cls, n):
        """Generate n-by-n identity matrix

        :param n: number of rows/columns
        :type n: int
        """

        n = int(n)

        # function to generate 1 or 0 for diagonals
        def ij_elem(i, j):
            if i == j:
                return 1.0

            return 0.0

        return cls([[ij_elem(i, j) for i in xrange(n)] for j in xrange(n)])

class Vector(Matrix):
    """Two-dimensional column vector in Cartesian coordinates"""

    def __init__(self, x, y=None):
        if y is None:
            # check if x is a Matrix
            if isinstance(x, Matrix):
                # check if the matrix is a column matrix
                if x.num_cols > 1:
                    raise Exception('Matrix must be a single column')

                # check that the matrix has 2 elements
                if x.num_rows is not 2:
                    raise Exception('Matrix must have two rows')

                y = x.elements[1][0]
                x = x.elements[0][0]
            else:
                # copy constructor
                y = x.y
                x = x.x

        # create column matrix
        super(Vector, self).__init__([[float(x)], [float(y)]])

    @property
    def x(self):
        return self.elements[0][0]

    @x.setter
    def x(self, x):
        self.elements[0][0] = float(x)

    @property
    def y(self):
        return self.elements[1][0]

    @y.setter
    def y(self, y):
        self.elements[1][0] = float(y)

    def append_row(self, row):
        raise NotImplementedError('Append operations not available in vectors')

    def append_col(self, col):
        raise NotImplementedError('Append operations not available in vectors')

    def __unicode__(self):
        """String representation of the vector's coordinates"""

        return "({0:.3f}, {1:.3f})".format(self.x, self.y)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of the coordinates"""

        return unicode(self)

    def dot(self, other):
        """Dot product

        :param other: other vector
        :type other: :class:`Vector`
        """

        return self.x * other.x + self.y * other.y

    @classmethod
    def origin(cls):
        """The coordinates of the origin"""

        return cls(0, 0)

    def rotate(self, azimuth):
        """Rotation of coordinates about the origin using a left-handed \
        coordinate system

        :param azimuth: the angle in degrees to rotate in a clockwise direction
        """

        # validate azimuth
        azimuth = float(azimuth)

        # apply rotation matrix to x and y
        x = self.x * math.cos(math.radians(azimuth)) \
        - self.y * math.sin(math.radians(azimuth))
        y = self.x * math.sin(math.radians(azimuth)) \
        + self.y * math.cos(math.radians(azimuth))

        # return new coordinates
        return self.__class__(x, y)

    @property
    def azimuth(self):
        """Azimuth defined by the coordinate with respect to the origin"""

        return math.degrees(math.atan2(self.y, self.x))

    @property
    def length(self):
        """Length between point defined by coordinates and the origin"""

        return math.sqrt(self.x * self.x + self.y * self.y)

    def is_positive(self):
        """Checks if the coordinates are all positive

        Assumes 0 is positive.
        """

        return self.x >= 0 and self.y >= 0

    def is_negative(self):
        """Checks if the coordinates are all negative

        Assumes 0 is positive
        """

        return not self.is_positive()

    def tol_eq(self, other, *args, **kwargs):
        return Scalar.tol_eq(self.x, other.x, *args, **kwargs) \
        and Scalar.tol_eq(self.y, other.y, *args, **kwargs)

    def tol_gt(self, other, *args, **kwargs):
        return self > other and not self.tol_eq(other, *args, **kwargs)

    def tol_lt(self, other, *args, **kwargs):
        return self < other and not self.tol_eq(other, *args, **kwargs)

    def tol_ge(self, other, *args, **kwargs):
        return self > other or self.tol_eq(other, *args, **kwargs)

    def tol_le(self, other, *args, **kwargs):
        return self < other or self.tol_eq(other, *args, **kwargs)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y

    def __add__(self, other):
        try:
            other_x = other.x
            other_y = other.y
        except AttributeError:
            other_x = other
            other_y = other

        return self.__class__(self.x + other_x, self.y + other_y)

    def __sub__(self, other):
        try:
            other_x = other.x
            other_y = other.y
        except AttributeError:
            other_x = other
            other_y = other

        return self.__class__(self.x - other_x, self.y - other_y)

    def __mul__(self, other):
        try:
            other_x = other.x
            other_y = other.y
        except AttributeError:
            other_x = other
            other_y = other

        return self.__class__(self.x * other_x, self.y * other_y)

    def __truediv__(self, other):
        try:
            other_x = other.x
            other_y = other.y
        except AttributeError:
            other_x = other
            other_y = other

        return self.__class__(self.x / other_x, self.y / other_y)

    def __neg__(self):
        """Negate operator"""

        return self.__class__(-self.x, -self.y)

def cc_int(p1, r1, p2, r2):
    """Intersect circle (p1, r1) with circle (p2, r2)

    :param p1: vector representing centre of first circle
    :type p1: :class:`Vector`
    :param r1: scalar representing the radius of first circle
    :type r1: float
    :param p2: vector representing centre of second circle
    :type p2: :class:`Vector`
    :param r2: scalar representing the radius of first circle
    :type r2: float
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cc_int %s %s %s %s", p1, r1, p2, \
    r2)

    # distance between circle centres
    d = (p2-p1).length

    # check if d <= 0 within tolerance
    if Scalar.tol_le(d, 0):
        # no solutions
        return []

    u = ((r1*r1 - r2*r2) / d + d) / 2

    a = r1*r1
    b = u*u

    # check that a < b within tolerance
    # FIXME: what's going on here?  elif block seems to repeat earlier check
    if Scalar.tol_lt(a, b):
        return []
    elif a < b:
        v = 0.0
    else:
        v = math.sqrt(a-b)

    s = (p2 - p1) * u / d

    if Scalar.tol_zero(s.length):
        p3a = p1 + Vector(p2.y - p1.y, p1.x - p2.x) * r1/d

        if Scalar.tol_zero(r1 / d):
            return [p3a]
        else:
            p3b = p1 + Vector(p1.y - p2.y, p2.x - p1.x) * r1/d

            return [p3a, p3b]
    else:
        p3a = p1 + s + Vector(s.y, -s.x) * v / s.length

        if Scalar.tol_zero(v / s.length):
            return [p3a]
        else:
            p3b = p1 + s + Vector(-s.y, s.x) * v / s.length

            return [p3a, p3b]

def cl_int(p1, r, p2, v):
    """Intersect circle (p1, r) with line (p2, v)

    :param p1: vector representing centre of circle
    :type p1: :class:`Vector`
    :param r: scalar representing the radius of circle
    :type r1: float
    :param p2: vector representing a point on the line
    :type p2: :class:`Vector`
    :param v: vector representing the direction of the line
    :type v: :class:`Vector`
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cl_int %s %s %s %s", p1, r, p2, \
    v)

    # distance between centre of circle and start of line
    p = p2 - p1

    # squared length of line
    d2 = v.x * v.x + v.y * v.y

    D = p.x * v.y - v.x * p.y
    E = r * r * d2 - D * D

    # check that d2 and E are both > 0 within tolerance
    if Scalar.tol_gt(d2, 0) and Scalar.tol_gt(E, 0):
        sE = math.sqrt(E)
        x1 = p1.x + (D * v.y + Scalar.sign(v.y) * v.x * sE) / d2
        x2 = p1.x + (D * v.y - Scalar.sign(v.y) * v.x * sE) / d2
        y1 = p1.y + (-D * v.x + math.abs(v.y) * sE) / d2
        y2 = p1.y + (-D * v.x - math.abs(v.y) * sE) / d2

        return [Vector(x1, y1), Vector(x2, y2)]
    elif Scalar.tol_zero(E):
        x1 = p1.x + D * v.y / d2
        y1 = p1.y + -D * v.x / d2

        return [Vector(x1, y1)]
    else:
        return []

def cr_int(p1, r, p2, v):
    """Intersect a circle (p1, r) with ray (p2, v) (a half-line)

    :param p1: vector representing centre of circle
    :type p1: :class:`Vector`
    :param r: scalar representing the radius of circle
    :type r1: float
    :param p2: vector representing a point on the ray
    :type p2: :class:`Vector`
    :param v: vector representing the direction of the ray
    :type v: :class:`Vector`
    :returns: list of zero, one or two solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("cr_int %s %s %s %s", p1, r, p2, \
    v)

    solutions = []

    # loop over solutions of the circle and line intercept
    for s in cl_int(p1, r, p2, v):
        # check if a is >= 0 within tolerance
        if Scalar.tol_ge((s - p2).dot(v), 0):
            solutions.append(s)

    return solutions

def ll_int(p1, v1, p2, v2):
    """Intersect two lines

    :param p1: vector representing a point on the first line
    :type p1: :class:`Vector`
    :param v1: vector represting the direction of the first line
    :type v1: :class:`Vector`
    :param p2: vector representing a point on the second line
    :type p2: :class:`Vector`
    :param v2: vector represting the direction of the second line
    :type v2: :class:`Vector`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("ll_int %s %s %s %s", p1, v1, p2, \
    v2)

    if Scalar.tol_zero(v1.x * v2.y - v1.y * v2.x):
        # lines don't intersect
        return []
    elif not Scalar.tol_zero(v2.y):
        d = p2 - p1
        r2 = -v2.x / v2.y
        f = v1.x + v1.y * r2
        t1 = (d.x + d.y * r2) / f
    else:
        d = p2-p1
        t1 = d.y / v1.y

    return [p1 + v1 * t1]

def lr_int(p1, v1, p2, v2):
    """Intersect line with ray

    :param p1: vector representing a point on the line
    :type p1: :class:`Vector`
    :param v1: vector represting the direction of the line
    :type v1: :class:`Vector`
    :param p2: vector representing a point on the ray
    :type p2: :class:`Vector`
    :param v2: vector represting the direction of the ray
    :type v2: :class:`Vector`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("lr_int %s %s %s %s", p1, v1, p2, \
    v2)

    # assume ray is a line and get intersection with line
    s = ll_int(p1, v1, p2, v2)

    # check if s > 0 and a >= 0 within tolerance
    if len(s) > 0 and Scalar.tol_ge((s[0] - p2).dot(v2), 0):
        return s
    else:
        # lines intersect behind ray
        return []

def rr_int(p1, v1, p2, v2):
    """Intersect ray with ray

    :param p1: vector representing a point on the first ray
    :type p1: :class:`Vector`
    :param v1: vector represting the direction of the first ray
    :type v1: :class:`Vector`
    :param p2: vector representing a point on the second ray
    :type p2: :class:`Vector`
    :param v2: vector represting the direction of the second ray
    :type v2: :class:`Vector`
    :returns: list of zero or one solution points
    :rtype: list
    """

    logging.getLogger("geometry").debug("rr_int %s %s %s %s", p1, v1, p2, \
    v2)

    # assume rays are lines and get intersection
    s = ll_int(p1, v1, p2, v2)

    a1 = (s[0] - p1).dot(v1)
    a2 = (s[0] - p2).dot(v2)

    # check len(s) > 0 and a1 >= 0 and a2 >= 0 within tolerance
    if len(s) > 0 and Scalar.tol_ge((s[0] - p1).dot(v1), 0) \
    and Scalar.tol_ge((s[0] - p1).dot(v1), 0):
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
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: angle in radians, or None
    :rtype: float
    """

    # distances between points
    d21 = (p2 - p1).length
    d23 = (p3 - p2).length

    if Scalar.tol_zero(d21) or Scalar.tol_zero(d23):
        # degenerate angle
        return None

    # vectors between points
    v21 = (p1 - p2) / d21
    v23 = (p3 - p2) / d23

    # calculate vector rotating v21 to v23
    t = v21.dot(v23)

    # clip to +/-1.0 to fix floating point errors
    if t > 1.0:
        t = 1.0
    elif t < -1.0:
        t = -1.0

    # calculate angle from rotation vector
    angle = math.acos(t)

    if is_counterclockwise(p1, p2, p3):
        # flip angle
        angle = -angle

    return angle

def distance_2p(p1, p2):
    """Calculates the Euclidean distance between two points

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :returns: distance between the points
    :rtype: float
    """

    return (p2 - p1).length

def is_clockwise(p1, p2, p3):
    """Calculates whether or not triangle p1, p2, p3 is orientated clockwise

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: True if clockwise, otherwise False
    :rtype: boolean
    """

    u = p2 - p1
    v = p3 - p2;
    perp_u = Vector(-u.y, u.x)

    # check a < 0 within tolerance
    return Scalar.tol_lt(perp_u.dot(v), 0)

def is_counterclockwise(p1, p2, p3):
    """Calculates whether or not triangle p1, p2, p3 is orientated \
    counter-clockwise

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: True if counter-clockwise, otherwise False
    :rtype: boolean
    """

    u = p2 - p1
    v = p3 - p2;
    perp_u = Vector(-u.y, u.x)

    # check that a > 0 within tolerance
    return Scalar.tol_gt(perp_u.dot(v), 0)

def is_flat(p1, p2, p3):
    """Calculates wheter or not triangle p1, p2, p3 is flat (neither \
    clockwise nor counter-clockwise)

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: True if flat, otherwise False
    :rtype: boolean
    """

    u = p2 - p1
    v = p3 - p2;
    perp_u = Vector(-u.y, u.x)

    return Scalar.tol_zero(perp_u.dot(v), 0)

def is_acute(p1, p2, p3):
    """Calculates whether or not angle p1, p2, p3 is acute, i.e. less than \
    pi / 2

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: True if acute, otherwise False
    :rtype: boolean
    """

    # calculate angle between points
    angle = angle_3p(p1, p2, p3)

    if angle is None:
        return False

    return Scalar.tol_lt(math.abs(angle), math.pi / 2)

def is_obtuse(p1,p2,p3):
    """Calculates whether or not angle p1, p2, p3 is obtuse, i.e. greater than \
    pi / 2

    :param p1: first point
    :type p1: :class:`Vector`
    :param p2: second point
    :type p2: :class:`Vector`
    :param p3: third point
    :type p3: :class:`Vector`
    :returns: True if obtuse, otherwise False
    :rtype: boolean
    """

    # calculate angle between points
    angle = angle_3p(p1, p2, p3)

    if angle is None:
        return False

    return Scalar.tol_gt(math.abs(angle), math.pi / 2)

def make_hcs(a, b, scale=False):
    """Build a homogeneous coordiate system from two vectors, normalised

    :param a: first vector
    :type a: :class:`Vector`
    :param b: second vector
    :type b: :class:`Vector`
    :returns: 3x3 homogeneous coordinate matrix
    :rtype: :class:`Vector`
    """

    # resultant vector
    u = b - a

    if Scalar.tol_zero(u.length):
        # vectors are on top of each other (within tolerance)
        return None

    if not scale:
        # normalise resultant
        u /= u.length

    # mirror of u
    v = Vector(-u.y, u.x)

    # return new coordinate system
    return Matrix([
        [u.x, v.x, a.x],
        [u.y, v.y, a.y],
        [0.0, 0.0, 1.0]
    ])

def make_hcs_scaled(*args, **kwargs):
    """Build a homogeneous coordiate system from two vectors

    :param a: first vector
    :type a: :class:`Vector`
    :param b: second vector
    :type b: :class:`Vector`
    :returns: 3x3 homogeneous coordinate matrix
    :rtype: :class:`Vector`
    """

    return make_hcs(scale=True, *args, **kwargs)

def cs_transform_matrix(from_cs, to_cs):
    """Calculate the transformation matrix from one coordinate system to another

    :param from_cs: initial coordinate system
    :type from_cs: :class:`Vector`
    :param to_cs: target coordinate system
    :type to_cs: :class:`Vector`
    :returns: transformation matrix to convert from_cs to to_cs
    :rtype: :class:`Vector`
    """

    return to_cs * from_cs.inverse()

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
