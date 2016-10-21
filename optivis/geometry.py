# -*- coding: utf-8 -*-

"""Geometry classes"""

from __future__ import unicode_literals, division

import math
import logging

class Vector(object):
    """Vector in Cartesian coordinates"""

    # absolute and relative tolerances for comparing coordinates
    tol = 1e-10 # good enough for most applications
    rel = 1e-7

    def __init__(self, *args):
        """Instantiates vector

        :param *args: sequence of x and y coordinates, or Vector object
        """

        # extract arguments
        (x, y) = Vector._extract(*args)

        # set coordinates
        self.x = float(x)
        self.y = float(y)

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
        return Vector(x, y)

    @property
    def azimuth(self):
        """Azimuth defined by the coordinate with respect to the origin"""

        return math.degrees(math.atan2(self.y, self.x))

    def length(self):
        """Length between point defined by coordinates and the origin"""

        return math.hypot(self.x, self.y)

    def flip(self):
        """Flips the coordinates

        Doing "-y" doesn't work because the operation becomes -1 * y, which is
        why we need this.
        """

        return Vector(-self.x, -self.y)

    def is_positive(self):
        """Checks if the coordinates are all positive

        Assumes 0 is positive.
        """

        return self.x >= 0 and self.y >= 0

    def __eq__(self, other):
        """Compare coordinates to this one

        Works without precision errors, based on
        http://code.activestate.com/recipes/577124-approximately-equal/.

        :param other: other coordinates to compare
        """

        # check if other is a Vector object
        if not isinstance(other, Vector):
            # other object is not equal to this one
            return False

        # tolerance tests lists for each coordinate
        x_tests = []
        y_tests = []

        if self.tol is not None:
            # add absolute tolerance tests for each coordinate
            x_tests.append(self.tol)
            y_tests.append(self.tol)

        if self.rel is not None:
            # add relative tolerance tests for each coordinate
            x_tests.append(self.rel * abs(self.x))
            y_tests.append(self.rel * abs(self.y))

        # return equality based on most stringent tolerance
        return (abs(self.x - other.x) <= max(x_tests)) \
        and (abs(self.y - other.y) <= max(y_tests))

    def __ne__(self, other):
        """Compares whether other coordinate differs from this one

        :param other: other coordinate to compare
        """

        return not self == other

    def __mul__(self, *args):
        """Multiplies the coordinates by the specified factor

        :param *args: factor(s) or Vector to multiply this by
        """

        # coerce inputs to Vector object
        other = Vector(*args)

        # multiply each dimension and return as a new Vector object
        return Vector(self.x * other.x, self.y * other.y)

    def __div__(self, *args):
        """Division operator

        Pass-through to true division operator.
        """

        return self.__truediv__(*args)

    def __truediv__(self, *args):
        """Performs true (non-integer) division on the coordinate

        :param *args: factor(s) or Vector to divide this by
        """

        # coerce inputs to Vector object
        other = Vector(*args)

        # divide each dimension and return as a new Vector object
        return Vector(self.x / other.x, self.y / other.y)

    def __add__(self, *args):
        """Adds other coordinates to this one

        :param *args: factor(s) or Vector to add to this
        """

        # coerce inputs to Vector object
        other = Vector(*args)

        # add each dimension and return as a new Vector object
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, *args):
        """Subtracts other coordinates from this one

        :param *args: factor(s) or Vector to subtract from this
        """

        # coerce inputs to Vector object
        other = Vector(*args)

        # subtract each dimension and return as a new Vector object
        return Vector(self.x - other.x, self.y - other.y)

    @staticmethod
    def _extract(*sequence):
        """Extracts coordinates from input

        :param sequence: sequence (e.g. list) to extract coordinates from
        """

        # check number of inputs
        if len(sequence) < 1:
            raise ValueError("There must be at least one input")
        elif len(sequence) == 1:
            # check if the input is already Vector type
            if isinstance(sequence[0], Vector):
                # return coordinates
                return (sequence[0].x, sequence[0].y)

            # make second coordinate equal to first (essential for
            # multiplication and division by single values)
            y = float(sequence[0])
        else:
            # use explicit y definition
            y = float(sequence[1])

        # warn if more arguments are specified
        if len(sequence) > 2:
            logging.getLogger("geometry").warning("Extra coordinates ignored")

        # set x from first argument
        x = float(sequence[0])

        # create and return new coordinates as a tuple
        return (x, y)
