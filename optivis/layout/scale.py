from __future__ import unicode_literals, division
import numpy

class ScaleFunction(object):
    def __init__(self, coefficients=None):
        if coefficients is None:
            coefficients = [0, 1]

        self.coefficients = coefficients

    def getScaledLength(self, length):
        scaledLength = 0

        for i in range(0, len(self.coefficients)):
            scaledLength += self.coefficients[i] * length ** i

        return scaledLength

    def validate(self):
        roots = numpy.roots(numpy.polyder(self.coefficients))

    @property
    def coefficients(self):
        return self.__coefficients

    @coefficients.setter
    def coefficients(self, coefficients):
        if not isinstance(coefficients, (list, tuple)):
            raise Exception('Specified coefficients is not a list or tuple')

        self.__coefficients = coefficients

class LargeLengthScaleFunction(ScaleFunction):
    def __init__(self):
        return super(LargeLengthScaleFunction, self).__init__(coefficients=[0, 0.3])
