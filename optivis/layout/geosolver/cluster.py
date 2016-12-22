# -*- coding: utf-8 -*-

"""Clusters are generalised constraints on sets of points in
:math:`\mathbb{R}^2`. Cluster types are :class:`Rigid`, :class:`Hedgehog` and
:class:`Balloon`."""

from __future__ import unicode_literals, division

import abc

from multimethod import MultiVariable

class PointRelation(object):
    """Represents a relation between a set of points"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, points):
        """Creates a new point relation

        :param name: name of relation
        :param points: list of points
        :type name: unicode
        :type points: list
        """

        self.name = unicode(name)
        self.points = list(points)

    def __unicode__(self):
        # comma separated points
        points = ", ".join(self.points)

        return "{0}({1})".format(self.name, points)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __hash__(self):
        return hash(frozenset(self.points))

class Distance(PointRelation):
    """Represents a known distance between two points"""

    def __init__(self, a, b):
        """Creates a new known distance

        The distance is defined between points *a* and *b*

        :param a: first point
        :param b: second point
        :type a: :class:`~.np.ndarray`
        :type b: :class:`~.np.ndarray`
        """

        # call parent constructor
        super(Distance, self).__init__("dist", [a, b])

    def __eq__(self, other):
        # check other object is a Distance
        if isinstance(other, Distance):
            # check points are the same
            return frozenset(self.points) == frozenset(other.points)

        return False

class Angle(PointRelation):
    """Represents a known angle between three points"""

    def __init__(self, a, b, c):
        """Creates a new known angle

        The angle is defined at the *b* edge between *a* and *c*.

        :param a: first point
        :param b: second point
        :param c: third point
        :type a: :class:`~.np.ndarray`
        :type b: :class:`~.np.ndarray`
        :type c: :class:`~.np.ndarray`
        """

        # call parent constructor
        super(Angle, self).__init__("ang", [a, b, c])

    def __eq__(self, other):
        # check other object is an Angle
        if isinstance(other, Angle):
            # check the middle point is identical, and that the other points are
            # the included
            return self.points[2] == other.points[2] \
            and frozenset(self.points) == frozenset(other.points)

        return False

class Cluster(MultiVariable):
    """A set of points, satisfying some constaint"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, variables, *args, **kwargs):
        """Create a new cluster

        Specified variables should be hashable.

        :param variables: cluster variables
        :type variables: list
        """

        # call parent constructor
        super(Cluster, self).__init__(*args, **kwargs)

        # set variables
        self.vars = set(variables)

        # set default overconstrained value
        self.overconstrained = False

    def __unicode__(self):
        # create character string to represent whether the cluster is
        # overconstrained
        ovr_const = ""

        if self.overconstrained:
            ovr_const += "!"

        # create string variable list
        var_list = ", ".join([unicode(var) for var in self._variable_list()])

        return "{0}{1}#{2}({3})".format(ovr_const, self.name, id(self), \
        var_list)

    def _variable_list(self):
        """Variable list for the cluster

        :returns: variables
        :rtype: list
        """

        return list(self.vars)

    def intersection(self, other):
        """Get the intersection between this cluster and the specified cluster

        :param other: other cluster
        :type other: :class:`Cluster`
        :returns: new cluster with intersection of input clusters' variables
        :rtype: :class:`Cluster`
        :raises TypeError: if cluster types are unknown
        """

        # get shared points between this cluster and the other cluster
        shared = set(self.vars).intersection(other.vars)

        # note, a one point cluster is never returned
        # because it is not a constraint
        if len(shared) < 2:
            return None

        if isinstance(self, Rigid):
            if isinstance(other, Rigid):
                if len(shared) >= 2:
                    return Rigid(shared)
                else:
                    return None
            elif isinstance(other, Balloon):
                if len(shared) >= 3:
                    return Balloon(shared)
                else:
                    return None
            elif isinstance(other, Hedgehog):
                xvars = set(shared) - set([other.cvar])
                if other.cvar in self.vars and len(xvars) >= 2:
                    return Hedgehog(other.cvar,xvars)
                else:
                    return None
        elif isinstance(self, Balloon):
            if isinstance(other, Rigid) or isinstance(other, Balloon):
                if len(shared) >= 3:
                    return Balloon(shared)
                else:
                    return None
            elif isinstance(other, Hedgehog):
                xvars = set(shared) - set([other.cvar])
                if other.cvar in self.vars and len(xvars) >= 2:
                    return Hedgehog(other.cvar,xvars)
                else:
                    return None
        elif isinstance(self, Hedgehog):
            if isinstance(other, Rigid) or isinstance(other, Balloon):
                xvars = set(shared) - set([self.cvar])
                if self.cvar in other.vars and len(xvars) >= 2:
                    return Hedgehog(self.cvar,xvars)
                else:
                    return None
            elif isinstance(other, Hedgehog):
                xvars = set(self.xvars).intersection(other.xvars)
                if self.cvar == other.cvar and len(xvars) >= 2:
                    return Hedgehog(self.cvar,xvars)
                else:
                    return None

        # if all fails
        raise TypeError("Intersection of unknown cluster types")

class Rigid(Cluster):
    """Represents a set of points that form a rigid body"""

    def __init__(self, *args, **kwargs):
        """Creates a new rigid cluster"""

        # call parent
        super(Rigid, self).__init__(name="rigid", *args, **kwargs)

    def copy(self):
        return Rigid(self.vars)

class Hedgehog(Cluster):
    """Represents a set of points (C, X1...XN) where all angles a(Xi, C, Xj) are
    known"""

    def __init__(self, cvar, xvars):
        """Creates a new hedgehog cluster

        :param cvar: center variable
        :param xvars: other variables
        :type cvar: object
        :type xvars: list
        :raises ValueError: if less than three variables are specified between \
        *cvar* and *xvars*
        """

        # set central variable
        self.cvar = cvar

        # check there are enough other variables
        if len(xvars) < 2:
            raise ValueError("Hedgehog must have at least three variables")

        # set other variables
        self.xvars = set(xvars)

        # call parent constructor with all variables
        super(Hedgehog, self).__init__(self.xvars.union([self.cvar]), \
        name="hedgehog")

    def _variable_list(self):
        """Gets list of variables associated with this hedgehog

        Overrides :class:`Cluster`.

        :returns: variables
        :rtype: list
        """

        # central value followed by other variables
        return [self.cvar] + list(self.xvars)

    def copy(self):
        return Hedgehog(self.cvar, self.xvars)

class Balloon(Cluster):
    """Represents a set of points that is invariant to rotation, translation and
    scaling"""

    def __init__(self, *args, **kwargs):
        """Create a new balloon

        :raises ValueError: if less than three variables are specified
        """

        # call parent
        super(Balloon, self).__init__(name="balloon", *args, **kwargs)

        # check there are enough variables for a balloon
        if len(self.vars) < 3:
            raise ValueError("Balloon must have at least three variables")

    def copy(self):
        return Balloon(self.vars)

def over_constraints(c1, c2):
    """returns the over-constraints (duplicate distances and angles) for
       a pair of clusters (rigid, angle or scalable)."""
    return over_distances(c1,c2).union(over_angles(c1,c2))

def over_angles(c1, c2):
    if isinstance(c1,Rigid) and isinstance(c2,Rigid):
        return over_angles_bb(c1,c2)
    if isinstance(c1,Rigid) and isinstance(c2,Hedgehog):
        return over_angles_ch(c1,c2)
    elif isinstance(c1,Hedgehog) and isinstance(c2,Rigid):
        return over_angles_ch(c2,c1)
    elif isinstance(c1,Hedgehog) and isinstance(c2,Hedgehog):
        return over_angles_hh(c1,c2)
    elif isinstance(c1,Rigid) and isinstance(c2,Balloon):
        return over_angles_cb(c1,c2)
    elif isinstance(c1,Balloon) and isinstance(c2,Rigid):
        return over_angles_cb(c1,c2)
    elif isinstance(c1,Balloon) and isinstance(c2,Balloon):
        return over_angles_bb(c1,c2)
    elif isinstance(c1,Balloon) and isinstance(c2,Hedgehog):
        return over_angles_bh(c1,c2)
    elif isinstance(c1,Hedgehog) and isinstance(c2,Balloon):
        return over_angles_bh(c2,c1)
    else:
        raise StandardError, "unexpected case"

def over_distances(c1, c2):
    """determine set of distances in c1 and c2"""
    if not (isinstance(c1, Rigid) and isinstance(c2, Rigid)):
        return set()
    else:
        shared = list(set(c1.vars).intersection(c2.vars))
        overdists = set()
        for i in range(len(shared)):
            for j in range(i):
                v1 = shared[i]
                v2 = shared[j]
                overdists.add(Distance(v1,v2))
        return overdists

def over_angles_hh(hog1, hog2):
    # determine duplicate angles
    shared = list(set(hog1.xvars).intersection(hog2.xvars))
    if not hog1.cvar == hog2.cvar:
        return set()
    overangles = set()
    for i in range(len(shared)):
        for j in range(i):
            v1 = shared[i]
            v2 = shared[j]
            overangles.add(Angle(v1,hog1.cvar,v2))
    return overangles

def over_angles_bb(b1, b2):
    # determine duplicate angles
    shared = list(set(b1.vars).intersection(b2.vars))
    overangles = set()
    for i in range(len(shared)):
        for j in range(i+1, len(shared)):
            for k in range(j+1, len(shared)):
                v1 = shared[i]
                v2 = shared[j]
                v3 = shared[k]
                overangles.add(Angle(v1,v2,v3))
                overangles.add(Angle(v2,v3,v1))
                overangles.add(Angle(v3,v1,v2))
    return overangles

def over_angles_cb(cluster, balloon):
    # determine duplicate angles
    # note: identical to over_angles_bb and (non-existent) over_angles_cc
    shared = list(set(cluster.vars).intersection(balloon.vars))
    overangles = set()
    for i in range(len(shared)):
        for j in range(i+1, len(shared)):
            for k in range(j+1, len(shared)):
                v1 = shared[i]
                v2 = shared[j]
                v3 = shared[k]
                overangles.add(Angle(v1,v2,v3))
                overangles.add(Angle(v2,v3,v1))
                overangles.add(Angle(v3,v1,v2))
    return overangles

def over_angles_bh(balloon, hog):
    # determine duplicate angles
    shared = list(set(balloon.vars).intersection(hog.xvars))
    if hog.cvar not in balloon.vars:
        return set()
    overangles = set()
    for i in range(len(shared)):
        for j in range(i+1,len(shared)):
            v1 = shared[i]
            v2 = shared[j]
            overangles.add(Angle(v1,hog.cvar,v2))
    return overangles

def over_angles_ch(cluster, hog):
    # determine duplicate angles
    shared = list(set(cluster.vars).intersection(hog.xvars))
    if hog.cvar not in cluster.vars:
        return set()
    overangles = set()
    for i in range(len(shared)):
        for j in range(i+1,len(shared)):
            v1 = shared[i]
            v2 = shared[j]
            overangles.add(Angle(v1,hog.cvar,v2))
    return overangles

def binomial(n,k):
    p = 1
    for j in range(0,k):
        p = p*(n - j)/(j + 1)
    return p

def num_constraints(cluster):
    return num_distances(cluster)+num_angles(cluster)

def num_distances(cluster):
    if isinstance(cluster, Rigid):
        n = len(cluster.vars)
        return binomial(n,2)
    else:
        return 0

def num_angles(cluster):
    if isinstance(cluster, Balloon) or isinstance(cluster, Rigid):
        n = len(cluster.vars)
        return binomial(n,3) * 3
    elif isinstance(cluster, Hedgehog):
        n = len(cluster.xvars)
        return binomial(n,2)

    return 0
