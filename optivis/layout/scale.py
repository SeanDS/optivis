# -*- coding: utf-8 -*-

"""Link length scale classes"""

from __future__ import unicode_literals, division

import abc

class Scale(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, coefficients):
        self.coefficients = coefficients

    def get_scaled_length(self, length):
        # default scaled length
        scaled_length = 0

        # return the sum of the higher order lengths scaled by the coefficients
        return sum([coefficient * length ** i \
        for (i, coefficient) in enumerate(self.coefficients)])

    @property
    def coefficients(self):
        return self._coefficients

    @coefficients.setter
    def coefficients(self, coefficients):
        self._coefficients = list(coefficients)

class LinearScale(Scale):
    def __init__(self):
        super(LinearScale, self).__init__([0, 1])

class LargeLengthScale(Scale):
    def __init__(self):
        super(LargeLengthScale, self).__init__(coefficients=[0, 0.3])
