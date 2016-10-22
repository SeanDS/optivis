# -*- coding: utf-8 -*-

"""Geometry classes"""

from __future__ import unicode_literals, division

import numpy as np
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
