# -*- coding: utf-8 -*-

"""Clusters are generalised constraints on sets of points in 2D. Cluster
types are Rigids, Hedgehogs and Balloons."""

from __future__ import unicode_literals, division

import abc

from multimethod import MultiVariable

class Distance(object):
    """Represents a known distance"""

    def __init__(self, a, b):
        """Create a new Distance

        :param a: point variable
        :param b: point variable
        """

        # set variables
        self.vars = (a, b)

    def __unicode__(self):
        return "distance({0}, {1})".format(*self.vars)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __hash__(self):
        return hash(frozenset(self.vars))

    def __eq__(self, other):
        if isinstance(other, Distance):
        # check the variables are equal
            return frozenset(self.vars) == frozenset(other.vars)

            return False

class Angle(object):
    """Represents a known angle"""

    def __init__(self, a, b, c):
        """Create a new Angle

        :param a: point variable
        :param b: point variable
        :param c: point variable
        """

        # set variables
        self.vars = (a, b, c)

    def __eq__(self, other):
        if isinstance(other, Angle):
        # check variables are equal and that point c is the same
        # TODO: is the vars[2] check necessary?
            return self.vars[2] == other.vars[2] and \
            frozenset(self.vars) == frozenset(other.vars)

        return False

    def __unicode__(self):
        return "angle({0}, {1}, {2})".format(*self.vars)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __hash__(self):
        return hash(frozenset(self.vars))

class Cluster(MultiVariable):
    """A set of points, satisfying some constaint"""

    __metaclass__ = abc.ABCMeta

    name = "cluster"

    def __init__(self, variables, *args, **kwargs):
        """Create a new cluster

        :param vars: sequence of cluster variables
        """

        # call parent constructor
        super(Cluster, self).__init__(*args, **kwargs)

        # set variables
        self.vars = set(variables)

        # set default overconstrained value
        self.overconstrained = False

    def intersection(self, other):
        """Get intersection with another cluster

        Returns the intersection as an appropriate subclass of
        :class:`~.Cluster`. If no valid cluster exists to represent the
        intersection, None is returned.

        :param other: other :class:`~.Cluster`
        """

        # intersection between the two clusters
        shared = set(self.vars).intersection(other.vars)

        # don't return a one point cluster as it is not a valid constraint
        if len(shared) < 2:
            return None

        # get names of this and other
        this_name = self.name
        other_name = other.name

        # create a set containing the types of this cluster and the other cluster
        names = set([this_name, other_name])

        # two rigids
        if names == set([Rigid.name]):
            # if they share two or more points then the intersection is also a
            # rigid
            if len(shared) >= 2:
                return Rigid(shared)

        # two balloons
        if names == set([Balloon.name]):
            # if they share three or more points the intersection is also a
            # balloon
            if len(shared) >= 3:
                return Balloon(shared)

        # two hedgehogs
        if names == set([Hedgehog.name]):
            # if the hedgehogs share the same central value and there are at
            # least 2 shared non-central points, the intersection is a hedgehog
            if self.cvar == other.cvar and len(xvars) >= 2:
                # get intersection of non-central variables in both hedgehogs
                xvars = set(self.xvars).intersection(other.xvars)

                return Hedgehog(self.cvar, xvars)

        # a rigid and a balloon
        if names == set([Rigid.name, Balloon.name]):
            # both clusters are balloons; if they share three or more points
            # then the intersection is itself a balloon
            if len(shared) >= 3:
                return Balloon(shared)

        # a rigid or balloon and a hedgehog
        if names == set([Hedgehog.name, Rigid.name]) \
        or names == set([Hedgehog.name, Balloon.name]):
            # decide on which cluster is the hedgehog
            if other_name is Hedgehog.name:
                a = self
                b = other
            else:
                a = other
                b = self

            # if the clusters share the central variable, and there are at
            # least two additional variables, then the intersection is a
            # hedgehog
            if b.cvar in a.vars and len(xvars) >= 2:
                # get shared variables not including the central variable in the
                # hedgehog
                xvars = shared - set([b.cvar])

                return Hedgehog(b.cvar, xvars)

        # default return for non matches
        return None

    def var_intersection(self, other):
        """Returns the intersection of the variables of other :class:`~.Cluster`

        :param other: other :class:`~.Cluster`
        """

        return self.vars.intersection(other.vars)

    def over_distances(self, other):
        """Returns the overconstrained distances with the other \
        :class:`~.Cluster`

        Only :class:`~.Rigid` returns a non-empty set.

        :param other: other cluster
        """

        # return empty set by default
        return set()

    def over_angles(self, other):
        """Returns the overconstrained angles with the other :class:`~.Cluster`

        :param other: other cluster
        """

        return NotImplementedError("Only available in child classes")

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    def __unicode__(self):
        """Returns a status string for the cluster"""

        # create character string to represent whether the cluster is
        # overconstrained
        ovr_const = ""

        if self.overconstrained:
            ovr_const += "!"

        # create string variable list
        var_list = ", ".join(self._variable_list())

        return "{0}{1}#{2}({3})".format(ovr_const, self.name, id(self), \
        var_list)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def _variable_list(self):
        """Variable list for the :class:`~.Cluster`

        This is overridden by :class:`~.Hedgehog`.
        """

        return self.vars

class Rigid(Cluster):
    """Represents a cluster of points variables that forms a rigid body"""

    def __init__(self, *args, **kwargs):
        return super(Rigid, self).__init__(name="rigid", *args, **kwargs)

    def over_distances(self, other):
        """Returns the overconstrained distances with the other \
        :class:`~.Cluster`

        Overrides :class:`~.Cluster`.

        :param other: other cluster
        """

        # return empty set if the other cluster is not also a Rigid
        if other.name != Rigid.name:
            return set()

        # get list of shared variables between clusters
        shared = list(self.var_intersection(other))

        # empty overdistance set
        overdistances = set()

        # add overdistance on all combinations of shared variables
        for i in range(len(shared)):
            for j in range(i):
                overdistances.add(Distance(shared[i], shared[j]))

        return overdistances

    def over_angles(self, other):
        """Returns the overconstrained angles with the other :class:`~.Cluster`

        Overrides :class:`~.Cluster`.

        :param other: other cluster
        """

        if other.name == Rigid.name:
            return Rigid.over_angles_bb(self, other)
        elif other.name == Balloon.name:
            return Rigid.over_angles_cb(self, other)
        elif other.name == Hedgehog.name:
            return Rigid.over_angles_ch(self, other)

    def copy(self):
        return Rigid(self.vars)

class Balloon(Cluster):
    """Represents a set of points that are invariant to rotation, translation \
    and scaling"""

    def __init__(self, *args, **kwargs):
        """Create a new balloon"""

        # call parent
        super(Balloon, self).__init__(name="balloon", *args, **kwargs)

        # check there are enough variables for a balloon
        if len(self.vars) < 3:
            raise Exception("Balloon must have at least three variables")

    def over_angles(self, other):
        """Returns the overconstrained angles with the other :class:`~.Cluster`

        Overrides :class:`~.Cluster`.

        :param other: other cluster
        """

        if other.name == Rigid.name:
            return Balloon.over_angles_cb(self, other)
        elif other.name == Balloon.name:
            return Balloon.over_angles_bb(self, other)
        elif other.name == Hedgehog.name:
            return Balloon.over_angles_bh(self, other)

    def copy(self):
        return Balloon(self.vars)

class Hedgehog(Cluster):
    """An Hedgehog represents a set of points (M,X1...XN) where all angles
    a(Xi,M,Xj) are known"""

    def __init__(self, cvar, xvars, *args, **kwargs):
        """Create a new hedgehog

        :param cvar: central variable
        :param xvars: other variables
        """

        # set central value
        self.cvar = cvar

        # make sure there are at least 2 other variables
        if len(xvars) < 2:
            raise Exception("A hedgehog must have at least three variables")

        # set other variables
        self.xvars = set(xvars)

        # call parent constructor with all variables
        super(Hedgehog, self).__init__(self.xvars.union([self.cvar]), \
        name="hedgehog", *args, **kwargs)

    def over_angles(self, other):
        """Returns the overconstrained angles with the other :class:`~.Cluster`

        Overrides :class:`~.Cluster`.

        :param other: other cluster
        """

        if other.name == Rigid.name:
            return Hedgehog.over_angles_ch(self, other)
        elif other.name == Balloon.name:
            return Hedgehog.over_angles_bh(self, other)
        elif other.name == Hedgehog.name:
            return Hedgehog.over_angles_hh(self, other)

    def _variable_list(self):
        """Variable list for the :class:`~.Hedgehog`

        Overrides :class:`~.Cluster`.
        """

        # central value followed by other variables
        return [self.cvar].extend(self.xvars)

    def copy(self):
        return Hedgehog(self.cvar, self.xvars)

def over_constraints(cstr_a, cstr_b):
    """Returns the overconstrained distances and angles for a pair of clusters

    :param cstr_a: first cluster
    :param cstr_b: second cluster
    """

    # return union of sets of overconstrained distances and angles
    return over_distances(cstr_a, cstr_b).union(over_angles(cstr_a, cstr_b))

def over_distances(cstr_a, cstr_b):
    """Returns the overconstrained distances for a pair of clusters

    :param cstr_a: first cluster
    :param cstr_b: second cluster
    """

    return cstr_a.over_distances(cstr_b)

def over_angles(cstr_a, cstr_b):
    """Returns the overconstrained angles for a pair of clusters

    :param cstr_a: first cluster
    :param cstr_b: second cluster
    """

    return cstr_a.over_angles(cstr_b)

def binomial(n, k):
    p = 1

    for j in range(k):
        p = p * (n - j) // (j + 1)

    return p

def num_constraints(cluster):
    return num_distances(cluster) + num_angles(cluster)

def num_distances(cluster):
    if isinstance(cluster, Rigid):
        n = len(cluster.vars)
        return binomial(n, 2)
    else:
        return 0

def num_angles(cluster):
    if isinstance(cluster, Balloon) or isinstance(cluster, Rigid):
        n = len(cluster.vars)
        return binomial(n, 3) * 3
    elif isinstance(cluster, Hedgehog):
        n = len(cluster.xvars)
        return binomial(n, 2)
    else:
        return 0
