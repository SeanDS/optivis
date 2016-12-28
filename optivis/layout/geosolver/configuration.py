# -*- coding: utf-8 -*-

"""Provides a Configuration class representing a set of named points with
coordinates"""

from __future__ import unicode_literals, division

import logging

from optivis.geometry import Scalar, Vector, Matrix, distance_2p, make_hcs, \
make_hcs_scaled, cs_transform_matrix

class Configuration(object):
    """A set of named points with coordinates of a specified dimension.

    Immutable. Defines equality and a hash function.
    """

    def __init__(self, mapping):
        """Instantiate a configuration

        :param mapping: dictionary mapping between variables and points, e.g. \
        {v0: p0, v1: p1, v2: p2}, note that points are objects of class \
        :class:`Vector`
        """

        # dictionary mapping variable names to point values
        self.mapping = dict(mapping)

        # flag indicating an underconstrained merge (i.e. not a unique solution)
        self.underconstrained = False

        self.dimension = 2
        self.makehash()

    def copy(self):
        """returns a shallow copy"""
        new = Configuration(self.mapping)
        new.underconstrained = self.underconstrained
        return new

    def vars(self):
        """return list of variables"""
        return self.mapping.keys()

    def get(self, var):
        """return position of point var"""
        return self.mapping[var]

    def transform(self, t):
        """returns a new configuration, which is this one transformed by matrix t"""
        newmap = {}
        for v in self.mapping:
            ph = (t * Matrix([[self.mapping[v].x, self.mapping[v].y, 1.0]]).transpose()).elements

            newmap[v] = Vector(ph[0][0] / ph[2][0], ph[1][0] / ph[2][0])
        return Configuration(newmap)

    def add(self, c):
        """return a new configuration which is this configuration extended with all points in c not in this configuration"""
        newmap = {}
        for v in self.mapping:
            newmap[v] = self.mapping[v]
        for v in c.mapping:
            if v not in newmap:
                newmap[v] = c.mapping[v]
        return Configuration(newmap)

    def select(self, vars):
        """return a new configuration that is a subconfiguration of this configuration, containing only the selected variables"""
        newmap = {}
        for v in vars:
            newmap[v] = self.mapping[v]
        return Configuration(newmap)

    def merge(self, other):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""

        logging.getLogger("configuration").debug("Merging %s with %s", self, other)
        t, underconstrained = self.merge_transform(other)
        othertransformed = other.transform(t)
        result = self.add(othertransformed)
        return result, underconstrained

    def merge_transform(self,other):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""

        if other.dimension != self.dimension:
            raise Exception("cannot merge configurations of different dimensions")

        shared = set(self.vars()).intersection(other.vars())
        underconstrained = self.underconstrained or other.underconstrained
        if len(shared) == 0:
            underconstrained = True
            cs1 = make_hcs(Vector.origin(), Vector(1.0, 0.0))
            cs2 = make_hcs(Vector.origin(), Vector(1.0, 0.0))
        elif len(shared) == 1:
            if len(self.vars()) > 1 and len(other.vars()) > 1:
                underconstrained = True
            v1 = list(shared)[0]
            p11 = self.mapping[v1]
            p21 = other.mapping[v1]
            cs1 = make_hcs(p11, p11 + Vector(1.0, 0.0))
            cs2 = make_hcs(p21, p21 + Vector(1.0, 0.0))
        else:   # len(shared) >= 2:
            v1 = list(shared)[0]
            v2 = list(shared)[1]
            p11 = self.mapping[v1]
            p12 = self.mapping[v2]
            if Scalar.tol_zero((p12 - p11).length):
                underconstrained = True
                cs1 = make_hcs(p11, p11 + Vector(1.0, 0.0))
            else:
                cs1 = make_hcs(p11, p12)
            p21 = other.mapping[v1]
            p22 = other.mapping[v2]
            if Scalar.tol_zero((p22 - p21).length):
                underconstrained = True
                cs2 = make_hcs(p21, p21 + Vector(1.0, 0.0))
            else:
                cs2 = make_hcs(p21, p22)
        # in any case
        t = cs_transform_matrix(cs2, cs1)
        return t, underconstrained

    def merge_scale(self, other, vars=[]):
        """returns a new configurations which is this one plus the given other configuration transformed, such that common points will overlap (if possible)."""
        if len(vars) == 0:
            shared = set(self.vars()).intersection(other.vars())
        else:
            shared = vars
        underconstrained = self.underconstrained or other.underconstrained
        if len(shared) < 2:
            raise StandardError, "must have >=2 shared point vars"

        v1 = list(shared)[0]
        v2 = list(shared)[1]
        p11 = self.mapping[v1]
        p12 = self.mapping[v2]
        if Scalar.tol_zero((p12 - p11).length):
            underconstrained = True
            cs1 = make_hcs_scaled(p11, p11 + Vector(1.0, 0.0))
        else:
            cs1 = make_hcs_scaled(p11, p12)
        p21 = other.mapping[v1]
        p22 = other.mapping[v2]
        if Scalar.tol_zero((p22 - p21).length):
            underconstrained = True
            cs2 = make_hcs_scaled(p21, p21 + Vector(1.0, 0.0))
        else:
            cs2 = make_hcs_scaled(p21, p22)
        print cs1, cs2
        t = cs_transform_matrix(cs2, cs1)
        othert = other.transform(t)
        result = self.add(othert)
        return result, underconstrained

    def __eq__(self, other):
        """two configurations are equal if they map onto eachother modulo rotation and translation"""
        if hash(self) != hash(other):
            return False
        elif len(self.mapping) != len(other.mapping):
            return False
        else:
            if not isinstance(other, Configuration):
                return False
            for var in self.mapping:
                if var not in other.mapping:
                    return False
            # determine a rotation-translation transformation
            # to transform other onto self
            t, _ = self.merge_transform(other)
            othertransformed = other.transform(t)
            # test if point map onto eachother (distance metric tolerance)
            for var in self.mapping:
                d = distance_2p(othertransformed.get(var), self.get(var))
                # check that d is greater than 0 within tolerance
                if not np.allclose(d, 0.0) and np.greater(d, 0.0):
                    return False
            return True

    def makehash(self):
        """the hash is based only on variable names (not values)"""
        val = 0
        for var in self.mapping:
            val = val + hash(var)
        self.hashvalue = hash(val)

    def __hash__(self):
        return self.hashvalue

    def __unicode__(self):
        return "Configuration({0})".format(self.mapping)

    def __str__(self):
        return unicode(self).encode("utf-8")


def test():
    p1 = np.array([0.0,0.0,0.0])
    p2 = np.array([1.0,0.0,0.0])
    p3 = np.array([0.0,1.0,0.0])
    c1 = Configuration({1:p1,2:p2})
    q1 = np.array([0.0,0.0,0.0])
    q2 = np.array([1.0,0.0,0.0])
    q3 = np.array([0.0,-1.0,0.0])
    c2 = Configuration({1:q1,2:q2})
    print c1 == c2

if __name__ == "__main__": test()
