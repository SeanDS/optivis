# -*- coding: utf-8 -*-

"""Clusters are generalised constraints on sets of points in R^n. Cluster
types are Rigids, Hedgehogs and Balloons."""

from __future__ import unicode_literals, division

from multimethod import MultiVariable

class Distance(object):
    """Represents a known distance between two points"""

    def __init__(self, a, b):
        """Create a new Distance

        :param a: first :class:`~Vector`
        :param b: second :class:`~Vector`
        """

        # set variables to the provided points
        self.vars = (a, b)

    def __unicode__(self):
        return "dist({0}, {1})".format(*self.vars)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __hash__(self):
        return hash(frozenset(self.vars))

    def __eq__(self, other):
        # check other object is a Distance
        if isinstance(other, Distance):
            # check variables are the same
            return frozenset(self.vars) == frozenset(other.vars)

        return False

class Angle(object):
    """Represents a known angle between three points"""

    def __init__(self, a, b, c):
        """Create a new Angle

        The angle is defined at the b edge between a and c.

        :param a: first :class:`~Vector`
        :param b: second :class:`~Vector`
        :param c: third :class:`~Vector`
        """

        # set variables to the provided points
        self.vars = (a, b, c)

    def __eq__(self, other):
        # check other object is an Angle
        if isinstance(other, Angle):
            # check the middle point is identical, and that the variables are
            # the same
            return self.vars[2] == other.vars[2] \
            and frozenset(self.vars) == frozenset(other.vars)
        else:
            return False

    def __hash__(self):
        return hash(frozenset(self.vars))

    def __unicode__(self):
        return "ang({0}, {1}, {2})".format(*self.vars)

    def __str__(self):
        return unicode(self).encode("utf-8")

class Cluster(MultiVariable):
    """A set of points, satisfying some constaint"""

    cluster_type = "cluster"

    def __init__(self, variables, *args, **kwargs):
        """Create a new cluster

        :param vars: sequence of cluster variables
        """

        # call parent constructor
        super(Cluster, self).__init__(name=self.cluster_type, *args, **kwargs)

        # set variables
        self.vars = set(variables)

        # set default overconstrained value
        self.overconstrained = False

    def __unicode__(self):
        """Returns a status string for the cluster"""

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
        """Variable list for the :class:`~.Cluster`

        This is overridden by :class:`~.Hedgehog`.
        """

        return list(self.vars)

    def intersection(self, other):
        """Get the intersection between this cluster and the specified cluster

        :param other: other :class:`~.Cluster`
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
        raise Exception("intersection of unknown Cluster types")

class Rigid(Cluster):
    """Represents a cluster of points variables that form a rigid body"""

    cluster_type = "rigid"

    def copy(self):
        return Rigid(self.vars)

class Hedgehog(Cluster):
    """Represents a set of points (M,X1...XN) where all angles a(Xi,M,Xj) are
    known"""

    cluster_type = "hedgehog"

    def __init__(self, cvar, xvars):
        """Create a new hedgehog

        :param cvar: center variable
        :param xvars: sequence of other variables
        """

        # set central variable
        self.cvar = cvar

        # check there are enough other variables
        if len(xvars) < 2:
            raise Exception("hedgehog must have at least three variables")

        # set other variables
        self.xvars = set(xvars)

        # call parent constructor with all variables
        super(Hedgehog, self).__init__(self.xvars.union([self.cvar]))

    def _variable_list(self):
        """Variable list for the :class:`~.Hedgehog`

        Overrides :class:`~.Cluster`.
        """

        # central value followed by other variables
        return [self.cvar] + list(self.xvars)

    def copy(self):
        return Hedgehog(self.cvar, self.xvars)

class Balloon(Cluster):
    """A Balloon (or ScalableCluster) is set of points that is
       invariant to rotation, translation and scaling.
    """
    cluster_type = "balloon"

    def __init__(self, *args, **kwargs):
        """Create a new balloon"""

        # call parent
        super(Balloon, self).__init__(*args, **kwargs)

        # check there are enough variables for a balloon
        if len(self.vars) < 3:
            raise Exception("Balloon must have at least three variables")

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
