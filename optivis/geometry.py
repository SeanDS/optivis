# -*- coding: utf-8 -*-

"""Geometry classes"""

from __future__ import unicode_literals, division

import math
import logging

class Coordinates(object):
    """Cartesian coordinates"""

    # absolute and relative tolerances for comparing coordinates
    tol = 1e-18
    rel = 1e-7

    def __init__(self, *args):
        """Instantiates Cartesian coordinates

        :param *args: sequence of x and y coordinates, or Coordinates object
        """

        # extract arguments
        (x, y) = Coordinates._extract(*args)

        # set coordinates
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        """String representation of the coordinates"""

        return "({0:.3f}, {1:.3f})".format(self.x, self.y)

    def __repr__(self):
        """Representation of the coordinates"""

        return self.__str__()

    def rotate(self, azimuth):
        """Rotation of coordinates about the origin using a left-handed \
        coordinate system

        :param azimuth: the angle in degrees to rotate in a clockwise direction
        """

        # apply rotation matrix to x and y
        x = self.x * math.cos(math.radians(azimuth)) \
        - self.y * math.sin(math.radians(azimuth))
        y = self.x * math.sin(math.radians(azimuth)) \
        + self.y * math.cos(math.radians(azimuth))

        # return new coordinates
        return Coordinates(x, y)

    @property
    def azimuth(self):
        """Azimuth defined by the coordinate with respect to the origin"""

        return math.degrees(math.atan2(self.y, self.x))

    def flip(self):
        """Flips the coordinates

        Doing "-y" doesn't work because the operation becomes -1 * y, which is
        why we need this.
        """

        return Coordinates(-self.x, -self.y)

    def __eq__(self, other):
        """Compare coordinates to this one

        Works without precision errors, based on
        http://code.activestate.com/recipes/577124-approximately-equal/.

        :param other: other coordinates to compare
        """

        # check if other is a Coordinates object
        if not isinstance(other, Coordinates):
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

        :param *args: factor(s) or Coordinates to multiply this by
        """

        # coerce inputs to Coordinates object
        other = Coordinates(*args)

        # multiply each dimension and return as a new Coordinates object
        return Coordinates(self.x * other.x, self.y * other.y)

    def __div__(self, *args):
        """Division operator

        Pass-through to true division operator.
        """

        return self.__truediv__(*args)

    def __truediv__(self, *args):
        """Performs true (non-integer) division on the coordinate

        :param *args: factor(s) or Coordinates to divide this by
        """

        # coerce inputs to Coordinates object
        other = Coordinates(*args)

        # divide each dimension and return as a new Coordinates object
        return Coordinates(self.x / other.x, self.y / other.y)

    def __add__(self, *args):
        """Adds other coordinates to this one

        :param *args: factor(s) or Coordinates to add to this
        """

        # coerce inputs to Coordinates object
        other = Coordinates(*args)

        # add each dimension and return as a new Coordinates object
        return Coordinates(self.x + other.x, self.y + other.y)

    def __sub__(self, *args):
        """Subtracts other coordinates from this one

        :param *args: factor(s) or Coordinates to subtract from this
        """

        # coerce inputs to Coordinates object
        other = Coordinates(*args)

        # subtract each dimension and return as a new Coordinates object
        return Coordinates(self.x - other.x, self.y - other.y)

    @staticmethod
    def _extract(*sequence):
        """Extracts coordinates from input

        :param sequence: sequence (e.g. list) to extract coordinates from
        """

        # check number of inputs
        if len(sequence) < 1:
            raise ValueError('There must be at least one input')
        elif len(sequence) == 1:
            # check if the input is already Coordinates type
            if isinstance(sequence[0], Coordinates):
                # return coordinates
                return (sequence[0].x, sequence[0].y)

            # make second coordinate zero
            y = 0
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
