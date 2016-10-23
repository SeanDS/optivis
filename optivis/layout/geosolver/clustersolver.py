# -*- coding: utf-8 -*-

"""A generic 2D geometric constraint solver.

The solver finds a generic solution for problems formulated by Clusters. The
generic solution is a directed acyclic graph of Clusters and Methods. Particilar
problems and solutions are represented by a Configuration for each cluster.
"""

from __future__ import unicode_literals, division

import abc

from optivis.layout.geosolver.graph import Graph
from optivis.layout.geosolver.method import Method, MethodGraph
from optivis.layout.geosolver.notify import Notifier
from optivis.layout.geosolver.multimethod import MultiVariable, \
MultiMethod
from optivis.layout.geosolver.cluster import *
from optivis.layout.geosolver.configuration import Configuration
from optivis.layout.geosolver.selconstr import NotCounterClockwiseConstraint, \
NotClockwiseConstraint, NotAcuteConstraint, NotObtuseConstraint
from optivis.layout.geosolver.intersections import *

class ClusterMethod(MultiMethod):
    __metaclass__ = abc.ABCMeta

    def prototype_constraints(self):
        return []

class PrototypeMethod(MultiMethod):
    """A PrototypeMethod selects those solutions of a cluster for which the \
    protoype and the solution satisfy the same constraints."""

    def __init__(self, incluster, selclusters, outcluster, constraints):
        # call parent constructor
        super(PrototypeMethod, self).__init__(name="PrototypeMethod", \
        inputs=[incluster]+selclusters, outputs=[outcluster])

        # set constraints
        self.constraints = list(constraints)

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug( \
"PrototypeMethod.multi_execute called")

        incluster = self.inputs[0]
        selclusters = []

        for i in range(1, len(self.inputs)):
            selclusters.append(self.inputs[i])

        logging.getLogger("clustersolver").debug("input clusters %s", incluster)
        logging.getLogger("clustersolver").debug("selection clusters %s", \
        selclusters)

        # get confs
        inconf = inmap[incluster]
        selmap = {}

        for cluster in selclusters:
            conf = inmap[cluster]

            assert len(conf.vars()) == 1

            var = conf.vars()[0]
            selmap[var] = conf.map[var]

        selconf = Configuration(selmap)
        sat = True

        logging.getLogger("clustersolver").debug("input configuration = \
%s", inconf)
        logging.getLogger("clustersolver").debug("selection configuration = \
%s", selconf)

        for con in self.constraints:
            satcon = con.satisfied(inconf.map) != con.satisfied(selconf.map)

            logging.getLogger("clustersolver").debug("constraint = %s", con)
            logging.getLogger("clustersolver").debug("constraint satisfied? \
%s", satcon)
            sat = sat and satcon

        logging.getLogger("clustersolver").debug("prototype satisfied? %s", \
sat)

        if sat:
            return [inconf]

        return []

class ClusterSolver(Notifier):
    """A generic 2D geometric constraint solver

    Finds a generic solution for problems formulated by cluster constraints.

    Constraints are Clusters: Rigids, Hedgehogs and Balloons.
    Cluster are added and removed using the add and remove methods.
    After adding each Cluster, the solver tries to merge it with
    other clusters, resulting in new Clusters and Methods.

    For each Cluster a set of Configurations can be set using the
    set method. Configurations are propagated via Methods and can
    be retrieved with the get method."""

    def __init__(self, *args, **kwargs):
        """Create a new empty solver"""

        super(ClusterSolver, self).__init__(*args, **kwargs)

        self._graph = Graph()
        self._graph.add_vertex("_root")
        self._graph.add_vertex("_toplevel")
        self._graph.add_vertex("_variables")
        self._graph.add_vertex("_distances")
        self._graph.add_vertex("_angles")
        self._graph.add_vertex("_rigids")
        self._graph.add_vertex("_hedgehogs")
        self._graph.add_vertex("_balloons")
        self._graph.add_vertex("_methods")

        # queue of new objects to process
        self._new = []

        # methodgraph
        self._mg = MethodGraph()

    def variables(self):
        """get list of variables"""
        return self._graph.outgoing_vertices("_variables")

    def distances(self):
        """get list of distances"""
        return self._graph.outgoing_vertices("_distances")

    def angles(self):
        """get list of angles"""
        return self._graph.outgoing_vertices("_angles")

    def rigids(self):
        """get list of rigids"""
        return self._graph.outgoing_vertices("_rigids")

    def hedgehogs(self):
        """get list of hedgehogs"""
        return self._graph.outgoing_vertices("_hedgehogs")

    def balloons(self):
        """get list of balloons"""
        return self._graph.outgoing_vertices("_balloons")

    def methods(self):
        """get list of methods"""
        return self._graph.outgoing_vertices("_methods")

    def top_level(self):
        """get top-level objects"""
        return self._graph.outgoing_vertices("_toplevel")

    def is_top_level(self, object):
        return self._graph.has_edge("_toplevel",object)

    def add(self, cluster):
        """Add a cluster.

           arguments:
              cluster: A Rigid
           """

        logging.getLogger("clustersolver").debug("add_cluster %s", cluster)

        self._add_cluster(cluster)
        self._process_new()

    def remove(self, cluster):
        """Remove a cluster.
           All dependend objects are also removed.
        """

        self._remove(cluster)
        self._process_new()

    def set(self, cluster, configurations):
        """Associate a list of configurations with a cluster"""
        self._mg.set(cluster, configurations)

    def get(self, cluster):
        """Return a set of configurations associated with a cluster"""
        return self._mg.get(cluster)

    def set_root(self, rigid):
        """Make given rigid cluster the root cluster

           arguments:
              cluster: A Rigid
           """
        self._graph.rem_vertex("_root")
        self._graph.add_edge("_root", rigid)

    def find_dependent(self, obj):
        """Return a list of objects that depend on given object directly."""
        l = self._graph.outgoing_vertices(obj)
        return filter(lambda x: self._graph.get(obj, x) == "dependency", l)

    def find_depends(self, obj):
        """Return a list of objects that the given object depends on directly"""
        l = self._graph.ingoing_vertices(obj)
        return filter(lambda x: self._graph.get(x, obj) == "dependency", l)

    def contains(self, obj):
        return self._graph.has_vertex(obj)

    def _add_dependency(self, on, dependend):
        """Add a dependence for second object on first object"""
        self._graph.add_edge(on, dependend, "dependency")

    def _add_to_group(self, group, obj):
        """Add object to group"""
        self._graph.add_edge(group, obj, "contains")

    def _add_needed_by(self, needed, by):
        """Add relation 'needed' object is needed 'by'"""
        self._graph.add_edge(needed, by, "needed_by")

    def _objects_that_need(self, needed):
        """Return objects needed by given object"""
        return filter(lambda x: self._graph.get(needed,x) == "needed_by", \
        self._graph.outgoing_vertices(needed))

    def _objects_needed_by(self, needer):
        """Return objects needed by given object"""
        return filter(lambda x: self._graph.get(x,needer) == "needed_by", \
        self._graph.ingoing_vertices(needer))

    def _add_top_level(self, obj):
        self._graph.add_edge("_toplevel", obj)
        self._new.append(obj)

    def _rem_top_level(self, obj):
        self._graph.rem_edge("_toplevel", obj)

        if obj in self._new:
            self._new.remove(obj)

    def _remove(self, obj):
        # find all indirectly dependend objects
        to_delete = [obj] + self._find_descendent(obj)

        to_restore = set()

        # remove all objects
        for item in to_delete:
            # if merge removed items from toplevel then add them back to top level
            if hasattr(item, "restore_toplevel"):
                for cluster in item.restore_toplevel:
                    to_restore.add(cluster)

            # delete it from graph
            logging.getLogger("clustersolver").debug("deleting %s", item)
            self._graph.rem_vertex(item)

            # remove from _new list
            if item in self._new:
                self._new.remove(item)

            # remove from methodgraph
            if isinstance(item, Method):
                # note: method may have been removed because variable removed
                try:
                    self._mg.rem_method(item)
                except:
                    pass
            elif isinstance(item, MultiVariable):
                self._mg.rem_variable(item)

            # notify listeners
            self.send_notify(("remove", item))

        # restore top level (also added to _new)
        map(lambda x: self._add_top_level(x), [cluster for cluster \
        in to_restore if self._graph.has_vertex(cluster)])

        # re-solve
        self._process_new()

    def _find_descendent(self,v):
        """find all descendend objects of v (directly or indirectly \
        dependent)"""

        front = [v]
        result = {}

        while len(front) > 0:
            x = front.pop()

            if x not in result:
                result[x] = 1
                front += self.find_dependent(x)

        del(result[v])

        return list(result)

    def _add_variable(self, var):
        """Add a variable if not already in system

           arguments:
              var: any hashable object
        """

        if not self._graph.has_vertex(var):
            logging.getLogger("clustersolver").debug("_add_variable %s", var)

            self._add_to_group("_variables", var)

    def _add_cluster(self, cluster):
        if isinstance(cluster, Rigid):
            self._add_rigid(cluster)
        elif isinstance(cluster, Hedgehog):
            self._add_hog(cluster)
        elif isinstance(cluster, Balloon):
            self._add_balloon(cluster)
        else:
            raise Exception("unsupported type {0}".format(type(cluster)))

    def _add_rigid(self, newcluster):
        """add a rigid cluster if not already in system"""

        logging.getLogger("clustersolver").debug("_add_rigid %s", newcluster)

        # check if not already exists
        if self._graph.has_vertex(newcluster):
            raise Exception("rigid already in clsolver")

        # update graph
        self._add_to_group("_rigids", newcluster)

        for var in newcluster.vars:
            self._add_variable(var)
            self._add_dependency(var, newcluster)

        # if there is no root cluster, this one will be it
        if len(self._graph.outgoing_vertices("_root")) == 0:
            self._graph.add_edge("_root", newcluster)

        # add to top level
        self._add_top_level(newcluster)

        # add to methodgraph
        self._mg.add_variable(newcluster)

        # notify
        self.send_notify(("add", newcluster))

    def _add_hog(self, hog):
        logging.getLogger("clustersolver").debug("_add_hog: %s", hog)

        # check if not already exists
        if self._graph.has_vertex(hog):
            raise Exception("hedgehog already in clsolver")

        # update graph
        self._add_to_group("_hedgehogs",hog)

        for var in list(hog.xvars) + [hog.cvar]:
            self._add_variable(var)
            self._add_dependency(var, hog)

        # add to top level
        self._add_top_level(hog)

        # add to methodgraph
        self._mg.add_variable(hog)

        # notify
        self.send_notify(("add", hog))

    def _add_balloon(self, newballoon):
        """add a cluster if not already in system"""
        logging.getLogger("clustersolver").debug("_add_balloon %s", newballoon)

        # check if not already exists
        if self._graph.has_vertex(newballoon):
            raise Exception("balloon already in clsolver")

        # update graph
        self._add_to_group("_balloons", newballoon)

        for var in newballoon.vars:
            self._add_variable(var)
            self._add_dependency(var, newballoon)

        # add to top level
        self._add_top_level(newballoon)

         # add to methodgraph
        self._mg.add_variable(newballoon)

        # notify
        self.send_notify(("add", newballoon))

    def _add_merge(self, merge):
        # structural check that method has one output
        if len(merge.outputs) != 1:
            raise Exception("merge number of outputs != 1")

        # get only output of merge
        output = merge.outputs[0]

        # consistent merge?
        consistent = True

        # check if all combinations of the inputs are consistent
        for i1 in range(len(merge.inputs)):
            for i2 in range(i1 + 1, len(merge.inputs)):
                c1 = merge.inputs[i1]
                c2 = merge.inputs[i2]

                consistent = consistent and self._is_consistent_pair(c1, c2)

        # set merge consistency
        merge.consistent = consistent

        # merge is overconstrained if all of the inputs are overconstrained and
        # the merge is not consistent
        output.overconstrained = reduce(lambda x, y: x and y, merge.inputs) \
        and not consistent

        # add to graph
        self._add_cluster(output)
        self._add_method(merge)

        # remove inputs from toplevel
        map(lambda x: self._rem_top_level(x), merge.inputs)

        # add prototype selection method
        self._add_prototype_selector(merge)

        # add solution selection method
        self._add_solution_selector(merge)

    def _add_prototype_selector(self, merge):
        incluster = merge.outputs[0]
        constraints = merge.prototype_constraints()

        if len(constraints) == 0:
            return

        variables = set()

        map(lambda x: variables.update(x.variables()), constraints)

        selclusters = []

        for var in variables:
            clusters = self._graph.outgoing_vertices(var)
            clusters = filter(lambda c: isinstance(c, Rigid), clusters)
            clusters = filter(lambda c: len(c.vars) == 1, clusters)

            if len(clusters) != 1:
                raise Exception("no prototype cluster for variable \
{0}".format(v))

            selclusters.append(clusters[0])

        outcluster = incluster.copy()

        # Rick 20090519 - copy does not copy structural overconstrained flag?
        outcluster.overconstrained = incluster.overconstrained

        selector = PrototypeMethod(incluster, selclusters, outcluster, \
        constraints)

        self._add_cluster(outcluster)
        self._add_method(selector)
        self._rem_top_level(incluster)

    def _add_solution_selector(self, merge):
        return

    def _add_method(self, method):
        logging.getLogger("clustersolver").debug("new %s", method)

        self._add_to_group("_methods", method)

        for obj in method.inputs:
            self._add_dependency(obj, method)

        for obj in method.outputs:
            self._add_dependency(method, obj)
            self._add_dependency(obj, method)

        self._mg.add_method(method)
        self.send_notify(("add", method))

    def _process_new(self):
        while len(self._new) > 0:
            new_obj = self._new.pop()
            logging.getLogger("clustersolver").debug("search from %s", \
            new_obj)

            # do search
            search = self._search(new_obj)

            if search and self.is_top_level(new_obj):
                # maybe more rules applicable.... push back on stack
                self._new.append(new_obj)

    def _search(self, new_cluster):
        if isinstance(new_cluster, Rigid):
            self._search_from_rigid(new_cluster)
        elif isinstance(new_cluster, Hedgehog):
            self._search_from_hog(new_cluster)
        elif isinstance(new_cluster, Balloon):
            self._search_from_balloon(new_cluster)
        else:
            raise Exception("don't know how to search from {0}".format(new_cluster))

    def _search_from_balloon(self, balloon):
        if self._search_absorb_from_balloon(balloon):
            return
        if self._search_balloon_from_balloon(balloon):
            return
        if self._search_cluster_from_balloon(balloon):
            return
        self._search_hogs_from_balloon(balloon)

    def _search_from_hog(self, hog):
        if self._search_absorb_from_hog(hog):
            return
        if self._search_merge_from_hog(hog):
            return
        if self._search_balloon_from_hog(hog):
            return
        self._search_hogs_from_hog(hog)

    def _search_from_rigid(self, cluster):
        if self._search_absorb_from_cluster(cluster):
            return
        if self._search_balloonclustermerge_from_cluster(cluster):
            return
        if self._search_merge_from_cluster(cluster):
            return
        self._search_hogs_from_cluster(cluster)

    def _search_absorb_from_balloon(self, balloon):
        for cvar in balloon.vars:
            # find all incident hedgehogs
            hogs = self._find_hogs(cvar)

            # determine shared vertices per hedgehog
            for hog in hogs:
                shared = set(hog.xvars).intersection(balloon.vars)

                if len(shared) == len(hog.xvars):
                    return self._merge_balloon_hog(balloon, hog)

    def _search_absorb_from_cluster(self, cluster):
        for cvar in cluster.vars:
            # find all incident hedgehogs
            hogs = self._find_hogs(cvar)

            # determine shared vertices per hedgehog
            for hog in hogs:
                shared = set(hog.xvars).intersection(cluster.vars)

                if len(shared) == len(hog.xvars):
                    return self._merge_cluster_hog(cluster, hog)

    def _search_absorb_from_hog(self, hog):
        dep = self.find_dependent(hog.cvar)

        # case BH (overconstrained):
        balloons = filter(lambda x: isinstance(x, Balloon) \
        and self.is_top_level(x), dep)
        sharecx = filter(lambda x: len(set(hog.xvars).intersection(x.vars)) \
        >= 1, balloons)

        for balloon in sharecx:
            sharedcx = set(balloon.vars).intersection(hog.xvars)

            if len(sharedcx) == len(hog.xvars):
                return self._merge_balloon_hog(balloon, hog)

        # case CH (overconstrained)
        clusters = filter(lambda x: isinstance(x, Rigid) \
        and self.is_top_level(x), dep)
        sharecx = filter(lambda x: len(set(hog.xvars).intersection(x.vars)) \
        >= 1, clusters)

        for cluster in sharecx:
            sharedcx = set(cluster.vars).intersection(hog.xvars)

            if len(sharedcx) == len(hog.xvars):
                return self._merge_cluster_hog(cluster, hog)

    def _find_balloons(self, variables):
        balloons = set()

        for var in variables:
            deps = self.find_dependent(var)
            balls = filter(lambda x: isinstance(x, Balloon), deps)
            balloons = balloons.intersection(balls)

        return balloons

    def _make_balloon(self, var1, var2, var3, hog1, hog2):
        logging.getLogger("clustersolver").debug("_make_balloon %s, %s, %s", \
        var1, var2, var3)

        # derive sub-hogs if necessary
        variables = set([var1, var2, var3])

        if len(hog1.xvars) > 2:
            hog1 = self._derive_subhog(hog1, variables.intersection(hog1.xvars))

        if len(hog2.xvars) > 2:
            hog2 = self._derive_subhog(hog2, variables.intersection(hog2.xvars))

        # create balloon
        balloon = Balloon([var1, var2, var3])

        # create balloon method
        balloon_method = BalloonFromHogs(hog1, hog2, balloon)

        # add the new merge
        self._add_merge(balloon_method)

        return balloon

    def _search_balloon_from_hog(self, hog):
        new_balloons = []

        var1 = hog.cvar

        for var2 in hog.xvars:
            hogs = self._find_hogs(var2)

            for hog2 in hogs:
                if var1 in hog2.xvars:
                    for var3 in hog2.xvars:
                        if var3 != var2 and var3 in hog.xvars:
                            if not self._known_angle(var1, var3, var2):
                                new_balloons.append(self._make_balloon(var1, \
                                var2, var3, hog, hog2))

        if len(new_balloons) > 0:
            return new_balloons

        return None

    def _search_balloon_from_balloon(self, balloon):
        # map from adjacent balloons to variables shared with input balloon
        mapping = {}

        for var in balloon.vars:
            deps = self.find_dependent(var)

            balloons = filter(lambda x: isinstance(x, Balloon), deps)
            balloons = filter(lambda x: self.is_top_level(x), balloons)

            for bal2 in balloons:
                if bal2 != balloon:
                    if bal2 in mapping:
                        mapping[bal2].update([var])
                    else:
                        mapping[bal2] = set([var])

        for bal2 in mapping:
            if len(mapping[bal2]) >= 2:
                return self._merge_balloons(balloon, bal2)

        return None

    def _search_cluster_from_balloon(self, balloon):
        logging.getLogger("clustersolver").debug("_search_cluster_from_balloon")

        # map from adjacent clusters to variables shared with input balloon
        mapping = {}

        for var in balloon.vars:
            deps = self.find_dependent(var)

            clusters = filter(lambda x: isinstance(x, Rigid) \
            or isinstance(x, Distance), deps)
            clusters = filter(lambda x: self.is_top_level(x), clusters)

            for c in clusters:
                if c in mapping:
                    mapping[c].update([var])
                else:
                    mapping[c] = set([var])

        for cluster in mapping:
            if len(mapping[cluster]) >= 2:
                return self._merge_balloon_cluster(balloon, cluster)

        return None

    def _search_balloonclustermerge_from_cluster(self, rigid):
        logging.getLogger("clustersolver").debug( \
        "_search_balloonclustermerge_from_cluster")

        # map from adjacent clusters to variables shared with input balloon
        mapping = {}

        for var in rigid.vars:
            deps = self.find_dependent(var)

            balloons = filter(lambda x: isinstance(x, Balloon), deps)
            balloons = filter(lambda x: self.is_top_level(x), balloons)

            for b in balloons:
                if b in mapping:
                    mapping[b].update([var])
                else:
                    mapping[b] = set([var])

        for balloon in mapping:
            if len(mapping[balloon]) >= 2:
                return self._merge_balloon_cluster(balloon, rigid)

        return None

    def _merge_balloons(self, balloon_a, balloon_b):
        # create new balloon and merge method

        # get variables in both balloons
        variables = set(balloon_a.vars).union(balloon_b.vars)

        # create new balloon cluster
        new_balloon = Balloon(variables)

        # add new balloon merge
        self._add_merge(BalloonMerge(balloon_a, balloon_b, new_balloon))

        return new_balloon

    def _merge_balloon_cluster(self, balloon, cluster):
        # create new cluster and method

        # get variables in both the balloon and the cluster
        variables = set(balloon.vars).union(cluster.vars)

        # create new rigid cluster
        new_cluster = Rigid(list(variables))

        # add new balloon-rigid merge
        self._add_merge(BalloonRigidMerge(balloon, cluster, new_cluster))

        return new_cluster

    def _find_hogs(self, cvar):
        deps = self.find_dependent(cvar)

        hogs = filter(lambda x: isinstance(x, Hedgehog), deps)
        hogs = filter(lambda x: x.cvar == cvar, hogs)
        hogs = filter(lambda x: self.is_top_level(x), hogs)

        return hogs

    def _make_hog_from_cluster(self, cvar, cluster):
        # outer variables of hedgehog are the rigid's variables
        xvars = set(cluster.vars)

        # remove the central value of the hedgehog from the list
        xvars.remove(cvar)

        # create the new hedgehog from the central and outer variables
        hog = Hedgehog(cvar, xvars)

        # add the hedgehog
        self._add_hog(hog)

        # add new rigid-to-hedgehog method
        self._add_method(Rigid2Hog(cluster, hog))

        return hog

    def _make_hog_from_balloon(self, cvar, balloon):
        xvars = set(balloon.vars)

        xvars.remove(cvar)

        hog = Hedgehog(cvar, xvars)

        self._add_hog(hog)

        method = Balloon2Hog(balloon, hog)

        self._add_method(method)

        return hog

    def _search_hogs_from_balloon(self, newballoon):
        if len(newballoon.vars) <= 2:
            return None

        # create/merge hogs
        for cvar in newballoon.vars:
            # potential new hog
            xvars = set(newballoon.vars)

            xvars.remove(cvar)

            # find all incident hogs
            hogs = self._find_hogs(cvar)

            # determine shared vertices per hog
            for hog in hogs:
                shared = set(hog.xvars).intersection(xvars)
                if len(shared) >= 1 and len(shared) \
                < len(hog.xvars) and len(shared) < len(xvars):
                    tmphog = Hedgehog(cvar, xvars)
                    if not self._graph.has_vertex(tmphog):
                        newhog = self._make_hog_from_balloon(cvar, newballoon)
                        self._merge_hogs(hog, newhog)

    def _search_hogs_from_cluster(self, newcluster):
        if len(newcluster.vars) <= 2:
            return None

        # create/merge hogs
        for cvar in newcluster.vars:
            # potential new hog
            xvars = set(newcluster.vars)
            xvars.remove(cvar)

            # find all incident hogs
            hogs = self._find_hogs(cvar)

            # determine shared vertices per hog
            for hog in hogs:
                shared = set(hog.xvars).intersection(xvars)

                if len(shared) >= 1 and len(shared) \
                < len(hog.xvars) and len(shared) < len(xvars):
                    tmphog = Hedgehog(cvar, xvars)
                    if not self._graph.has_vertex(tmphog):
                        newhog = self._make_hog_from_cluster(cvar, newcluster)
                        self._merge_hogs(hog, newhog)

    def _search_hogs_from_hog(self, newhog):
        # find adjacent clusters
        dep = self.find_dependent(newhog.cvar)

        top = filter(lambda c: self.is_top_level(c), dep)
        clusters = filter(lambda x: isinstance(x,Rigid), top)
        balloons = filter(lambda x: isinstance(x,Balloon), top)
        hogs = self._find_hogs(newhog.cvar)

        tomerge = []

        for cluster in clusters:
            if len(cluster.vars) < 3:
                continue

            # determine shared vars
            xvars = set(cluster.vars)
            xvars.remove(newhog.cvar)

            shared = set(newhog.xvars).intersection(xvars)

            if len(shared) >= 1 and len(shared) < len(xvars) \
            and len(shared) < len(newhog.xvars):
                tmphog = Hedgehog(newhog.cvar, xvars)

                if not self._graph.has_vertex(tmphog):
                    newnewhog = self._make_hog_from_cluster(newhog.cvar, \
                    cluster)

                    tomerge.append(newnewhog)

        for balloon in balloons:
            # determine shared vars
            xvars = set(balloon.vars)
            xvars.remove(newhog.cvar)

            shared = set(newhog.xvars).intersection(xvars)

            if len(shared) >= 1 and len(shared) \
            < len(xvars) and len(shared) < len(newhog.xvars):
                tmphog = Hedgehog(newhog.cvar, xvars)

                if not self._graph.has_vertex(tmphog):
                    newnewhog = self._make_hog_from_balloon(newhog.cvar, \
                    balloon)

                    tomerge.append(newnewhog)

        for hog in hogs:
            if hog == newhog:
                continue

            # determine shared vars
            shared = set(newhog.xvars).intersection(hog.xvars)

            if len(shared) >= 1 and len(shared) \
            < len(hog.xvars) and len(shared) < len(newhog.xvars):
                # if mergeable, then create new hog
                tomerge.append(hog)

        if len(tomerge) == 0:
            return None
        else:
            lasthog = newhog

            for hog in tomerge:
                lasthog = self._merge_hogs(lasthog, hog)

            return lasthog

    def _merge_hogs(self, hog1, hog2):
        logging.getLogger("clustersolver").debug("merging %s + %s", hog1, hog2)

        # create new hog and method
        xvars = set(hog1.xvars).union(hog2.xvars)

        mergedhog = Hedgehog(hog1.cvar, xvars)

        method = MergeHogs(hog1, hog2, mergedhog)

        self._add_merge(method)

        return mergedhog

    def _search_merge_from_hog(self, hog):
        # case CH (overconstrained)
        dep = self.find_dependent(hog.cvar)

        clusters = filter(lambda x: isinstance(x,Rigid) and self.is_top_level(x), dep)
        sharecx = filter(lambda x: len(set(hog.xvars).intersection(x.vars)) >=1, clusters)

        for cluster in sharecx:
            sharedcx = set(cluster.vars).intersection(hog.xvars)

            if len(sharedcx) == len(hog.xvars):
                return self._merge_cluster_hog(cluster, hog)

        # case CHC
        for i in range(len(sharecx)):
            c1 = sharecx[i]

            for j in range(i + 1, len(sharecx)):
                c2 = sharecx[j]

                return self._merge_cluster_hog_cluster(c1, hog, c2)

        # case CCH
        sharex = set()

        for var in hog.xvars:
            dep = self.find_dependent(var)

            sharex.update(filter(lambda x: isinstance(x,Rigid) \
            and self.is_top_level(x), dep))

        for c1 in sharecx:
            for c2 in sharex:
                if c1 == c2: continue

                shared12 = set(c1.vars).intersection(c2.vars)
                sharedh2 = set(hog.xvars).intersection(c2.vars)
                shared2 = shared12.union(sharedh2)

                if len(shared12) >= 1 and len(sharedh2) >= 1 \
                and len(shared2) == 2:
                    return self._merge_cluster_cluster_hog(c1, c2, hog)

        return None

    def _search_merge_from_cluster(self, newcluster):
        logging.getLogger("clustersolver").debug("_search_merge %s", newcluster)

        # find clusters overlapping with new cluster
        overlap = {}
        for var in newcluster.vars:
            # get dependent objects
            dep = self._graph.outgoing_vertices(var)

            # only clusters
            dep = filter(lambda c: self._graph.has_edge("_rigids",c), dep)

            # only top level
            dep = filter(lambda c: self.is_top_level(c), dep)

            # remove newcluster
            if newcluster in dep:
                dep.remove(newcluster)

            for cluster in dep:
                if cluster in overlap:
                    overlap[cluster].append(var)
                else:
                    overlap[cluster] = [var]

        # point-cluster merge
        for cluster in overlap:
            if len(overlap[cluster]) == 1:
                if len(cluster.vars) == 1:
                    return self._merge_point_cluster(cluster, newcluster)
                elif len(newcluster.vars) == 1:
                    return self._merge_point_cluster(newcluster, cluster)

        # two cluster merge (overconstrained)
        for cluster in overlap:
            if len(overlap[cluster]) >= 2:
                return self._merge_cluster_pair(cluster, newcluster)

        # three cluster merge
        clusterlist = overlap.keys()

        for i in range(len(clusterlist)):
            c1 = clusterlist[i]
            for j in range(i + 1, len(clusterlist)):
                c2 = clusterlist[j]

                shared12 = set(c1.vars).intersection(c2.vars)
                shared13 = set(c1.vars).intersection(newcluster.vars)
                shared23 = set(c2.vars).intersection(newcluster.vars)
                shared1 = shared12.union(shared13)
                shared2 = shared12.union(shared23)
                shared3 = shared13.union(shared23)

                if len(shared1) == 2 and len(shared1) == 2 and \
                   len(shared2) == 2:
                    return self._merge_cluster_triple(c1, c2, newcluster)

        # merge with an angle, case 1
        for cluster in overlap:
            ovars = overlap[cluster]

            if len(ovars) == 1:
                cvar = ovars[0]
            else:
                raise Exception("unexpected case")

            hogs = self._find_hogs(cvar)

            for hog in hogs:
                sharedch = set(cluster.vars).intersection(hog.xvars)
                sharednh = set(newcluster.vars).intersection(hog.xvars)
                sharedh = sharedch.union(sharednh)

                if len(sharedch) >= 1 and len(sharednh) >= 1 \
                and len(sharedh) >= 2:
                    return self._merge_cluster_hog_cluster(cluster, hog, \
                    newcluster)

        # merge with an angle, case 2
        for var in newcluster.vars:
            hogs = self._find_hogs(var)

            for hog in hogs:
                sharednh = set(newcluster.vars).intersection(hog.xvars)

                if len(sharednh) < 1:
                    continue

                for cluster in overlap:
                    sharednc = set(newcluster.vars).intersection(cluster.vars)

                    if len(sharednc) != 1:
                        raise Exception("unexpected case")

                    if hog.cvar in cluster.vars:
                        continue

                    sharedch = set(cluster.vars).intersection(hog.xvars)
                    sharedc = sharedch.union(sharednc)

                    if len(sharedch) >= 1 and len(sharedc) >= 2:
                        return self._merge_cluster_cluster_hog(newcluster, \
                        cluster, hog)

        # merge with an angle, case 3
        for cluster in overlap:
            sharednc = set(newcluster.vars).intersection(cluster.vars)

            if len(sharednc) != 1:
                raise Exception("unexpected case")

            for var in cluster.vars:
                hogs = self._find_hogs(var)

                for hog in hogs:
                    if hog.cvar in newcluster.vars:
                        continue

                    sharedhc = set(newcluster.vars).intersection(hog.xvars)
                    sharedhn = set(cluster.vars).intersection(hog.xvars)
                    sharedh = sharedhn.union(sharedhc)
                    sharedc = sharedhc.union(sharednc)

                    if len(sharedhc) >= 1 and len(sharedhn) >= 1 \
                    and len(sharedh) >= 2 and len(sharedc) == 2:
                        return self._merge_cluster_cluster_hog(cluster, \
                        newcluster, hog)

    def _merge_point_cluster(self, point, cluster):
        logging.getLogger("clustersolver").debug("_merge_point_cluster %s, \
%s", point, cluster)

        # get variables from point and rigid
        variables = set(point.vars).union(cluster.vars)

        # create new rigid from variables
        new_cluster = Rigid(variables)

        # add new point-to-rigid merge
        self._add_merge(Merge1C(point, cluster, new_cluster))

        return new_cluster

    def _merge_cluster_pair(self, c1, c2):
        """Merge a pair of clusters, structurally overconstrained.
           Rigid which contains root is used as origin.
           Returns resulting cluster.
        """

        logging.getLogger("clustersolver").debug("_merge_cluster_pair %s, %s", \
        c1, c2)

        # always use root cluster as first cluster, swap if needed
        if not self._contains_root(c1) and not self._contains_root(c2):
            pass
        elif self._contains_root(c1) and self._contains_root(c2):
            raise Exception("two root clusters")
        elif self._contains_root(c2):
            logging.getLogger("clustersolver").debug("swap cluster order")

            return self._merge_cluster_pair(c2, c1)

        # create new cluster and merge
        variables = set(c1.vars).union(c2.vars)

        # create new rigid cluster from variables
        new_cluster = Rigid(variables)

        # add new two-rigid merge
        self._add_merge(Merge2C(c1, c2, new_cluster))

        return new_cluster

    def _merge_cluster_hog(self, cluster, hog):
        """merge rigid and hog (absorb hog, overconstrained)"""

        logging.getLogger("clustersolver").debug("_merge_cluster_hog %s, %s", \
        cluster, hog)

        # create new rigid from variables
        new_cluster = Rigid(cluster.vars)

        # add new rigid-hedgehog merge
        self._add_merge(MergeCH(cluster, hog, new_cluster))

        return new_cluster

    def _merge_balloon_hog(self, balloon, hog):
        """merge balloon and hog (absorb hog, overconstrained)"""

        logging.getLogger("clustersolver").debug("_merge_balloon_hog %s, %s", \
        balloon, hog)

        # create new balloon and merge
        newballoon = Balloon(balloon.vars)

        merge = MergeBH(balloon, hog, newballoon)

        self._add_merge(merge)

        return newballoon

    def _merge_cluster_triple(self, c1, c2, c3):
        """Merge a triple of clusters.
           Rigid which contains root is used as origin.
           Returns resulting cluster.
        """

        logging.getLogger("clustersolver").debug("_merge_cluster_triple %s, \
%s, %s", c1, c2, c3)

        # always use root cluster as first cluster, swap if needed
        if self._contains_root(c2):
            logging.getLogger("clustersolver").debug("swap cluster order")

            return self._merge_cluster_triple(c2, c1, c3)
        elif self._contains_root(c3):
            logging.getLogger("clustersolver").debug("swap cluster order")

            return self._merge_cluster_triple(c3, c1, c2)

        # create new cluster and method
        allvars = set(c1.vars).union(c2.vars).union(c3.vars)

        newcluster = Rigid(allvars)

        merge = Merge3C(c1,c2,c3,newcluster)

        self._add_merge(merge)

        return newcluster

    def _merge_cluster_hog_cluster(self, c1, hog, c2):
        """merge c1 and c2 with a hog, with hog center in c1 and c2"""
        logging.getLogger("clustersolver").debug("_merge_cluster_hog_cluster \
%s, %s, %s", c1, hog, c2)

        # always use root cluster as first cluster, swap if needed
        if self._contains_root(c2):
            logging.getLogger("clustersolver").debug("swap cluster order")

            return self._merge_cluster_hog_cluster(c2, hog, c1)

        # derive sub-hog if nessecairy
        allvars = set(c1.vars).union(c2.vars)
        xvars = set(hog.xvars).intersection(allvars)

        if len(xvars) < len(hog.xvars):
            logging.getLogger("clustersolver").debug("deriving sub-hog")

            hog = self._derive_subhog(hog, xvars)

        #create new cluster and merge
        allvars = set(c1.vars).union(c2.vars)

        newcluster = Rigid(allvars)

        merge = MergeCHC(c1,hog,c2,newcluster)

        self._add_merge(merge)

        return newcluster

    def _derive_subhog(self, hog, xvars):
        subvars = set(hog.xvars).intersection(xvars)

        assert len(subvars) == len(xvars)

        subhog = Hedgehog(hog.cvar, xvars)
        method = SubHog(hog, subhog)

        self._add_hog(subhog)
        self._add_method(method)

        return subhog

    def _merge_cluster_cluster_hog(self, c1, c2, hog):
        """merge c1 and c2 with a hog, with hog center only in c1"""

        logging.getLogger("clustersolver").debug("_merge_cluster_cluster_hog \
%s, %s, %s", c1, c2, hog)

        # always use root cluster as first cluster, swap if needed
        if self._contains_root(c1) and self._contains_root(c2):
            raise Exception("two root clusters!")
        elif not self._contains_root(c1) and not self._contains_root(c2):
            pass
        elif self._contains_root(c2):
            return self._merge_cluster_cluster_hog(c2, c1, hog)

        # derive subhog if necessary
        allvars = set(c1.vars).union(c2.vars)
        xvars = set(hog.xvars).intersection(allvars)

        if len(xvars) < len(hog.xvars):
            logging.getLogger("clustersolver").debug("deriving sub-hog")

            hog = self._derive_subhog(hog, xvars)

        # create new cluster and method
        newcluster = Rigid(allvars)

        merge = MergeCCH(c1,c2,hog,newcluster)

        self._add_merge(merge)

        return newcluster

    def _contains_root(self, input_cluster):
        """returns True iff input_cluster is root cluster or was determined by
        merging with the root cluster."""

        # start from root cluster. Follow merges upwards until:
        #  - input cluster found -> True
        #  - no more merges -> False

        if len(self._graph.outgoing_vertices("_root")) > 1:
            raise Exception("more than one root cluster")
        if len(self._graph.outgoing_vertices("_root")) == 1:
            cluster = self._graph.outgoing_vertices("_root")[0]
        else:
            cluster = None

        while (cluster != None):
            if cluster is input_cluster:
                return True

            fr = self._graph.outgoing_vertices(cluster)

            me = filter(lambda x: isinstance(x, Merge), fr)
            me = filter(lambda x: cluster in x.outputs, me)

            if len(me) > 1:
                raise Exception("root cluster merged more than once")
            elif len(me) == 0:
                cluster = None
            elif len(me[0].outputs) != 1:
                raise Exception("a merge with number of outputs != 1")
            else:
                cluster = me[0].outputs[0]

        return False

    def _is_consistent_pair(self, object1, object2):
        logging.getLogger("clustersolver").debug("in is_consistent_pair %s, \
%s", object1, object2)

        oc = over_constraints(object1, object2)

        logging.getLogger("clustersolver").debug("over_constraints: %s", \
        map(unicode, oc))

        # calculate consistency (True if no overconstraints)
        consistent = reduce(lambda x, y: x and y, \
        [self._consistent_overconstraint_in_pair(con, object1, object2) \
        for con in oc], True)

        logging.getLogger("clustersolver").debug("global consistent? %s", \
        consistent)

        return consistent

    def _consistent_overconstraint_in_pair(self, overconstraint, object1, \
    object2):
        logging.getLogger("clustersolver").debug("consistent %s in %s and \
%s?", overconstraint, object1, object2)

        # get sources for constraint in given clusters
        s1 = self._source_constraint_in_cluster(overconstraint, object1)
        s2 = self._source_constraint_in_cluster(overconstraint, object2)

        if s1 == None:
            consistent = False
        elif s2 == None:
            consistent = False
        elif s1 == s2:
            consistent = True
        else:
            if self._is_atomic(s1) and not self._is_atomic(s2):
                consistent = False
            elif self._is_atomic(s2) and not self._is_atomic(s1):
                consistent = False
            else:
                consistent = True

        logging.getLogger("clustersolver").debug("consistent? %s", consistent)

        return consistent

    def _source_constraint_in_cluster(self, constraint, cluster):
        if not self._contains_constraint(cluster, constraint):
            raise Exception("constraint not in cluster")
        elif self._is_atomic(cluster):
            return cluster
        else:
            method = self._determining_method(cluster)
            inputs = method.inputs
            down = filter(lambda x: self._contains_constraint(x, constraint), \
            inputs)

            if len(down) == 0:
                return cluster
            elif len(down) > 1:
                if method.consistent == True:
                    return self._source_constraint_in_cluster(constraint, \
                    down[0])
                else:
                    logging.getLogger("clustersolver").warning("Source is \
inconsistent")
                    return None
            else:
                return self._source_constraint_in_cluster(constraint, down[0])

    def _is_atomic(self, object):
        return self._determining_method(object) is None

    def _determining_method(self, object):
        depends = self.find_depends(object)
        methods = filter(lambda x: isinstance(x, Method), depends)

        if len(methods) == 0:
            return None
        elif len(methods) > 1:
            raise Exception("object determined by more than one method")
        else:
            return methods[0]

    def _contains_constraint(self, object, constraint):
        if isinstance(constraint, Distance):
            return self._contains_distance(object, constraint)
        elif isinstance(constraint, Angle):
            return self._contains_angle(object, constraint)
        else:
            raise Exception("unexpected case")

    def _contains_distance(self,object, distance):
        if isinstance(object, Rigid):
            return (distance.vars[0] in object.vars and distance.vars[1] \
            in object.vars)
        elif isinstance(object, Distance):
            return (distance.vars[0] in object.vars and distance.vars[1] \
            in object.vars)
        else:
            return False

    def _contains_angle(self, object, angle):
        if isinstance(object, Rigid) or isinstance(object, Balloon):
            return (angle.vars[0] in object.vars
            and angle.vars[1] in object.vars
            and angle.vars[2] in object.vars)
        elif isinstance(object, Hedgehog):
            return (angle.vars[1] == object.cvar and
            angle.vars[0] in object.xvars and
            angle.vars[2] in object.xvars)
        elif isinstance(object, Angle):
            return (angle.vars[1] == object.vars[1] and
            angle.vars[0] in object.vars and
            angle.vars[2] in object.vars)
        else:
            return False

    def __unicode__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(\
        [unicode(x) for x in self.distances()], \
        [unicode(x) for x in self.angles()], \
        [unicode(x) for x in self.rigids()], \
        [unicode(x) for x in self.hedgehogs()], \
        [unicode(x) for x in self.balloons()], \
        [unicode(x) for x in self.methods()])

    def __str__(self):
        return unicode(self).encode("utf-8")

    def _known_angle(self, a, b, c):
        """returns Balloon, Rigid or Hedgehog that contains angle(a, b, c)"""

        if a == b or a == c or b == c:
            raise Exception("all vars in angle must be different")

        # get objects dependend on a, b and c
        dep_a = self._graph.outgoing_vertices(a)
        dep_b = self._graph.outgoing_vertices(b)
        dep_c = self._graph.outgoing_vertices(c)

        dependend = []

        for obj in dep_a:
            if obj in dep_b and obj in dep_c:
                dependend.append(obj)

        # find a hedgehog
        hogs = filter(lambda x: isinstance(x,Hedgehog), dependend)
        hogs = filter(lambda hog: hog.cvar == b, hogs)
        hogs = filter(lambda x: self.is_top_level(x), hogs)

        if len(hogs) == 1: return hogs[0]
        if len(hogs) > 1: raise Exception("angle in more than one hedgehog")

        # or find a cluster
        clusters = filter(lambda x: isinstance(x,Rigid), dependend)
        clusters = filter(lambda x: self.is_top_level(x), clusters)

        if len(clusters) == 1: return clusters[0]
        if len(clusters) > 1: raise Exception("angle in more than one Rigid")

        # or find a balloon
        balloons = filter(lambda x: isinstance(x,Balloon), dependend)
        balloons = filter(lambda x: self.is_top_level(x), balloons)

        if len(balloons) == 1: return balloons[0]
        if len(balloons) > 1: raise Exception("angle in more than one Balloon")

        return None

class Merge(ClusterMethod):
    """A merge is a method such that a single output cluster satisfies
    all constraints in several input clusters. The output cluster
    replaces the input clusters in the constriant problem"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, consistent, overconstrained, *args, **kwargs):
        super(Merge, self).__init__(*args, **kwargs)

        self.consistent = consistent
        self.overconstrained = overconstrained

    def __unicode__(self):
        # get parent unicode
        string = super(Merge, self).__unicode__()

        # add status and return
        return string + "[{0}]".format(self.status_str())

    def status_str(self):
        if self.consistent:
            consistent_status = "consistent"
        else:
            consistent_status = "inconsistent"

        if self.overconstrained:
            constrained_status = "overconstrained"
        else:
            constrained_status = "well constrained"

        return "{0}, {1}".format(consistent_status, constrained_status)

class Merge1C(Merge):
    """Represents a merging of a one-point cluster with any other cluster
       The first cluster determines the orientation of the resulting
       cluster
    """

    def __init__(self, in1, in2, out):
        super(Merge1C, self).__init__(name="Merge1C", inputs=[in1, in2], \
        outputs=[out], overconstrained=False, consistent=True)

    def __unicode__(self):
        s =  "merge1C("+str(self.inputs[0])+"+"+str(self.inputs[1])+"->"+str(self.outputs[0])+")"
        s += "[" + self.status_str()+"]"

        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("Merge1C.multi_execute called")

        c1 = self.inputs[0]
        c2 = self.inputs[1]

        conf1 = inmap[c1]
        conf2 = inmap[c2]

        if len(c1.vars) == 1:
            return [conf2.copy()]
        else:
            return [conf1.copy()]

class Merge2C(Merge):
    """Represents a merging of two clusters (overconstrained)
       The first cluster determines the orientation of the resulting
       cluster"""

    def __init__(self, in1, in2, out):
        super(Merge2C, self).__init__(name="Merge2C", inputs=[in1, in2], \
        outputs=[out], overconstrained=True, consistent=True)

        self.input1 = in1
        self.input2 = in2
        self.output = out

    def __str__(self):
        s =  "merge2C("+str(self.input1)+"+"+str(self.input2)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"

        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("Merge2C.multi_execute called")

        c1 = self.inputs[0]
        c2 = self.inputs[1]

        conf1 = inmap[c1]
        conf2 = inmap[c2]

        return [conf1.merge(conf2)]

class MergeCH(Merge):
    """Represents a merging of a cluster and a hog (where
       the hog is absorbed by the cluster). Overconstrained."""

    def __init__(self, cluster, hog, out):
        super(MergeCH, self).__init__(name="MergeCH", inputs=[cluster, hog], \
        outputs=[out], overconstrained=True, consistent=True)

        self.cluster = cluster
        self.hog = hog
        self.output = out

    def __str__(self):
        s =  "mergeCH("+str(self.cluster)+"+"+str(self.hog)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("MergeCH.multi_execute called")

        conf1 = inmap[self.cluster]

        return [conf1.copy()]

class MergeBH(Merge):
    """Represents a merging of a balloon and a hog (where
       the hog is absorbed by the balloon). Overconstrained.
    """

    def __init__(self, balloon, hog, out):
        super(MergeBH, self).__init__(name="MergeBH", inputs=[balloon, hog], \
        outputs=[out], overconstrained=True, consistent=True)

        self.balloon = balloon
        self.hog = hog
        self.output = out

    def __str__(self):
        s =  "mergeBH("+str(self.balloon)+"+"+str(self.hog)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("MergeBH.multi_execute called")

        conf1 = inmap[self.balloon]

        return [conf1.copy()]

class Merge3C(Merge):
    """Represents a merging of three clusters
       The first cluster determines the orientation of the resulting
       cluster
    """

    def __init__(self, c1, c2, c3, out):
        super(Merge3C, self).__init__(name="Merge3C", inputs=[c1, c2, c3], \
        outputs=[out], overconstrained=False, consistent=True)

        self.input1 = c1
        self.input2 = c2
        self.input3 = c3
        self.output = out

        # check coincidence
        shared12 = set(c1.vars).intersection(c2.vars)
        shared13 = set(c1.vars).intersection(c3.vars)
        shared23 = set(c2.vars).intersection(c3.vars)
        shared1 = shared12.union(shared13)
        shared2 = shared12.union(shared23)
        shared3 = shared13.union(shared23)

        if len(shared12) < 1:
            raise Exception("underconstrained c1 and c2")
        elif len(shared12) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c1 \
and c2")

            self.overconstrained = True
        if len(shared13) < 1:
            raise Exception("underconstrained c1 and c3")
        elif len(shared13) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c1 \
and c3")

            self.overconstrained = True
        if len(shared23) < 1:
            raise Exception("underconstrained c2 and c3")
        elif len(shared23) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c2 \
and c3", "clmethods")

            self.overconstrained = True
        if len(shared1) < 2:
            raise Exception("underconstrained c1")
        elif len(shared1) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c1")

            self.overconstrained = True
        if len(shared2) < 2:
            raise Exception("underconstrained c2")
        elif len(shared2) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c2")

            self.overconstrained = True
        if len(shared3) < 2:
            raise Exception("underconstrained c3")
        elif len(shared3) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCC - c3")

            self.overconstrained = True

    def __str__(self):
        s = "merge3C("+str(self.input1)+"+"+str(self.input2)+"+"+str(self.input3)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("Merge3C.multi_execute called")

        c1 = inmap[self.inputs[0]]
        c2 = inmap[self.inputs[1]]
        c3 = inmap[self.inputs[2]]

        shared12 = set(c1.vars()).intersection(c2.vars()).difference(c3.vars())
        shared13 = set(c1.vars()).intersection(c3.vars()).difference(c2.vars())
        shared23 = set(c2.vars()).intersection(c3.vars()).difference(c1.vars())

        v1 = list(shared12)[0]
        v2 = list(shared13)[0]
        v3 = list(shared23)[0]

        assert v1 != v2
        assert v1 != v3
        assert v2 != v3

        p11 = c1.get(v1)
        p21 = c1.get(v2)
        d12 = vector.norm(p11 - p21)
        p23 = c3.get(v2)
        p33 = c3.get(v3)
        d23 = vector.norm(p23 - p33)
        p32 = c2.get(v3)
        p12 = c2.get(v1)
        d31 = vector.norm(p32 - p12)

        ddds = solve_ddd(v1, v2, v3, d12, d23, d31)

        solutions = []

        for s in ddds:
            solution = c1.merge(s).merge(c2).merge(c3)

            solutions.append(solution)

        return solutions

    def prototype_constraints(self):
        c1 = self.inputs[0]
        c2 = self.inputs[1]
        c3 = self.inputs[2]

        shared12 = set(c1.vars).intersection(c2.vars).difference(c3.vars)
        shared13 = set(c1.vars).intersection(c3.vars).difference(c2.vars)
        shared23 = set(c2.vars).intersection(c3.vars).difference(c1.vars)

        v1 = list(shared12)[0]
        v2 = list(shared13)[0]
        v3 = list(shared23)[0]

        assert v1 != v2
        assert v1 != v3
        assert v2 != v3

        constraints = []

        constraints.append(NotCounterClockwiseConstraint(v1, v2, v3))
        constraints.append(NotClockwiseConstraint(v1, v2, v3))

        return constraints

def solve_ddd(v1, v2, v3, d12, d23, d31):
    logging.getLogger("clustersolver").debug("solve_ddd: %s %s %s %f %f %f", \
    v1, v2, v3, d12, d23, d31)

    p1 = vector.vector([0.0, 0.0])
    p2 = vector.vector([d12, 0.0])
    p3s = cc_int(p1, d31, p2, d23)

    solutions = []

    for p3 in p3s:
        solution = Configuration({v1:p1, v2:p2, v3:p3})

        solutions.append(solution)

    return solutions

class MergeCHC(Merge):
    """Represents a merging of two clusters and a hedgehog
       The first cluster determines the orientation of the resulting
       cluster
    """

    def __init__(self, c1, hog, c2, out):
        super(MergeCHC, self).__init__(name="MergeCHC", inputs=[c1, hog, c2], \
        outputs=[out], overconstrained=False, consistent=True)

        self.c1 = c1
        self.hog = hog
        self.c2 = c2
        self.output = out

        # check coincidence
        if not (hog.cvar in c1.vars and hog.cvar in c2.vars):
            raise Exception("hog.cvar not in c1.vars and c2.vars")

        shared12 = set(c1.vars).intersection(c2.vars)
        shared1h = set(c1.vars).intersection(hog.xvars)
        shared2h = set(c2.vars).intersection(hog.xvars)

        shared1 = shared12.union(shared1h)
        shared2 = shared12.union(shared2h)
        sharedh = shared1h.union(shared2h)

        if len(shared12) < 1:
            raise Exception("underconstrained c1 and c2")
        elif len(shared12) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CHC - c1 \
and c2")

            self.overconstrained = True
        if len(shared1h) < 1:
            raise Exception("underconstrained c1 and hog")
        elif len(shared1h) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CHC - c1 \
and hog")

            self.overconstrained = True
        if len(shared2h) < 1:
            raise Exception("underconstrained c2 and hog")
        elif len(shared2h) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CHC - c2 \
and hog")

            self.overconstrained = True
        if len(shared1) < 2:
            raise Exception("underconstrained c1")
        elif len(shared1) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CHC - c1")

            self.overconstrained = True
        if len(shared2) < 2:
            raise Exception("underconstrained c2")
        elif len(shared2) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CHC - c2")

            self.overconstrained = True
        if len(sharedh) < 2:
            raise Exception("underconstrained hog")
        elif len(shared1) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CHC - \
hog")

            self.overconstrained = True

    def __str__(self):
        s = "mergeCHC("+str(self.c1)+"+"+str(self.hog)+"+"+str(self.c2)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("MergeCHC.multi_execute called")

        # determine vars
        shared1 = set(self.hog.xvars).intersection(self.c1.vars)
        shared2 = set(self.hog.xvars).intersection(self.c2.vars)

        v1 = list(shared1)[0]
        v2 = self.hog.cvar
        v3 = list(shared2)[0]

        # get configs
        conf1 = inmap[self.c1]
        confh = inmap[self.hog]
        conf2 = inmap[self.c2]

        # determine angle
        p1h = confh.get(v1)
        p2h = confh.get(v2)
        p3h = confh.get(v3)
        a123 = angle_3p(p1h, p2h, p3h)

        # d1c
        p11 = conf1.get(v1)
        p21 = conf1.get(v2)
        d12 = distance_2p(p11,p21)

        # d2c
        p32 = conf2.get(v3)
        p22 = conf2.get(v2)
        d23 = distance_2p(p32,p22)

        # solve
        dads = solve_dad(v1, v2, v3, d12, a123, d23)
        solutions = []

        for s in dads:
            solution = conf1.merge(s).merge(conf2)
            solutions.append(solution)

        return solutions

def solve_dad(v1, v2, v3, d12, a123, d23):
    logging.getLogger("clustersolver").debug("solve_dad: %s %s %s %f %f %f", \
    v1, v2, v3, d12, a123, d23)

    p2 = vector.vector([0.0, 0.0])
    p1 = vector.vector([d12, 0.0])
    p3s = [vector.vector([d23 * math.cos(a123), d23 * math.sin(a123)])]

    solutions = []

    for p3 in p3s:
        solution = Configuration({v1: p1, v2: p2, v3: p3})
        solutions.append(solution)

    return solutions

class MergeCCH(Merge):
    """Represents a merging of two clusters and a hedgehog
       The first cluster determines the orientation of the resulting
       cluster
    """
    def __init__(self, c1, c2, hog, out):
        super(MergeCCH, self).__init__(name="MergeCCH", inputs=[c1, c2, hog], \
        outputs=[out], overconstrained=False, consistent=True)

        self.c1 = c1
        self.c2 = c2
        self.hog = hog
        self.output = out

        # check coincidence
        if hog.cvar not in c1.vars:
            raise Exception("hog.cvar not in c1.vars")
        if hog.cvar in c2.vars:
            raise Exception("hog.cvar in c2.vars")

        shared12 = set(c1.vars).intersection(c2.vars)
        shared1h = set(c1.vars).intersection(hog.xvars)
        shared2h = set(c2.vars).intersection(hog.xvars)

        shared1 = shared12.union(shared1h)
        shared2 = shared12.union(shared2h)
        sharedh = shared1h.union(shared2h)

        if len(shared12) < 1:
            raise Exception("underconstrained c1 and c2")
        elif len(shared12) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCH - c1 \
and c2")

            self.overconstrained = True
        if len(shared1h) < 1:
            raise Exception("underconstrained c1 and hog")
        elif len(shared1h) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCH - c1 \
and hog")

            self.overconstrained = True
        if len(shared2h) < 1:
            raise Exception("underconstrained c2 and hog")
        elif len(shared2h) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCH - c2 \
and hog")

            self.overconstrained = True
        if len(shared1) < 1:
            raise Exception("underconstrained c1")
        elif len(shared1) > 1:
            logging.getLogger("clustersolver").debug("overconstrained CCH - c1")

            self.overconstrained = True
        if len(shared2) < 2:
            raise Exception("underconstrained c2")
        elif len(shared2) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCH - c2")

            self.overconstrained = True
        if len(sharedh) < 2:
            raise Exception("underconstrained hog")
        elif len(sharedh) > 2:
            logging.getLogger("clustersolver").debug("overconstrained CCH - \
hog")

            self.overconstrained = True

    def __str__(self):
        s = "mergeCCH("+str(self.c1)+"+"+str(self.c2)+"+"+str(self.hog)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("MergeCCH.multi_execute called")

        # assert hog.cvar in c1
        if self.hog.cvar in self.c1.vars:
            c1 = self.c1
            c2 = self.c2
        else:
            c1 = self.c2
            c2 = self.c1

        # get v1
        v1 = self.hog.cvar

        # get v2
        candidates2 = set(self.hog.xvars).intersection(c1.vars).intersection(c2.vars)

        assert len(candidates2) >= 1

        v2 = list(candidates2)[0]

        # get v3
        candidates3 = set(self.hog.xvars).intersection(c2.vars).difference([v1, v2])

        assert len(candidates3) >= 1

        v3 = list(candidates3)[0]

        # check
        assert v1 != v2
        assert v1 != v3
        assert v2 != v3

        # get configs
        confh = inmap[self.hog]
        conf1 = inmap[c1]
        conf2 = inmap[c2]

        # get angle
        p1h = confh.get(v1)
        p2h = confh.get(v2)
        p3h = confh.get(v3)
        a312 = angle_3p(p3h, p1h, p2h)

        # get distance d12
        p11 = conf1.get(v1)
        p21 = conf1.get(v2)
        d12 = distance_2p(p11, p21)

        # get distance d23
        p22 = conf2.get(v2)
        p32 = conf2.get(v3)
        d23 = distance_2p(p22, p32)
        adds = solve_add(v1, v2, v3, a312, d12, d23)

        solutions = []

        # do merge (note, order c1 c2 restored)
        conf1 = inmap[self.c1]
        conf2 = inmap[self.c2]

        for s in adds:
            solution = conf1.merge(s).merge(conf2)
            solutions.append(solution)

        return solutions

    def prototype_constraints(self):
        # assert hog.cvar in c1
        if self.hog.cvar in self.c1.vars:
            c1 = self.c1
            c2 = self.c2
        else:
            c1 = self.c2
            c2 = self.c1

        shared1h = set(self.hog.xvars).intersection(c1.vars).difference([self.hog.cvar])
        shared2h = set(self.hog.xvars).intersection(c2.vars).difference(shared1h)

        # get vars
        v1 = self.hog.cvar
        v2 = list(shared1h)[0]
        v3 = list(shared2h)[0]

        assert v1 != v2
        assert v1 != v3
        assert v2 != v3

        constraints = []

        constraints.append(NotAcuteConstraint(v2, v3, v1))
        constraints.append(NotObtuseConstraint(v2, v3, v1))

        return constraints

def solve_add(a,b,c, a_cab, d_ab, d_bc):
    logging.getLogger("clustersolver").debug("solve_dad: %s %s %s %f %f %f", \
    a, b, c, a_cab, d_ab, d_bc)

    p_a = vector.vector([0.0, 0.0])
    p_b = vector.vector([d_ab, 0.0])

    dir = vector.vector([math.cos(-a_cab), math.sin(-a_cab)])

    solutions = cr_int(p_b, d_bc, p_a, dir)

    rval = []

    for s in solutions:
        p_c = s
        map = {a: p_a, b: p_b, c: p_c}

        rval.append(Configuration(map))

    return rval

class BalloonFromHogs(Merge):
    """Represent a balloon merged from two hogs"""
    def __init__(self, hog1, hog2, balloon):
        """Create a new balloon from two angles

           keyword args:
            hog1 - a Hedghog
            hog2 - a Hedehog
            balloon - a Balloon instance
        """

        super(BalloonFromHogs, self).__init__(name="BalloonFromHogs", \
        inputs=[hog1, hog2], outputs=[balloon], overconstrained=False, \
        consistent=True)

        self.hog1 = hog1
        self.hog2 = hog2
        self.balloon = balloon

        # check coincidence
        if hog1.cvar == hog2.cvar:
            raise Exception("hog1.cvar is hog2.cvar")

        shared12 = set(hog1.xvars).intersection(hog2.xvars)

        if len(shared12) < 1:
            raise Exception("underconstrained")

    def __str__(self):
        s = "hog2balloon("+str(self.hog1)+"+"+str(self.hog2)+"->"+str(self.balloon)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug( \
        "BalloonFromHogs.multi_execute called")

        v1 = self.hog1.cvar
        v2 = self.hog2.cvar

        shared = set(self.hog1.xvars).intersection(self.hog2.xvars).difference([v1,v2])

        v3 = list(shared)[0]

        assert v1 != v2
        assert v1 != v3
        assert v2 != v3

        # determine angle312
        conf1 = inmap[self.hog1]

        p31 = conf1.get(v3)
        p11 = conf1.get(v1)
        p21 = conf1.get(v2)
        a312 = angle_3p(p31,p11,p21)

        # determine distance d12
        d12 = 1.0

        # determine angle123
        conf2 = inmap[self.hog2]
        p12 = conf2.get(v1)
        p22 = conf2.get(v2)
        p32 = conf2.get(v3)
        a123 = angle_3p(p12,p22,p32)

        # solve
        return solve_ada(v1, v2, v3, a312, d12, a123)

def solve_ada(a, b, c, a_cab, d_ab, a_abc):
    logging.getLogger("clustersolver").debug("solve_ada: %s %s %s %f %f %f", \
    a, b, c, a_cab, d_ab, a_abc)

    p_a = vector.vector([0.0, 0.0])
    p_b = vector.vector([d_ab, 0.0])

    dir_ac = vector.vector([math.cos(-a_cab), math.sin(-a_cab)])
    dir_bc = vector.vector([-math.cos(-a_abc), math.sin(-a_abc)])

    if tol_eq(math.sin(a_cab), 0.0) and tol_eq(math.sin(a_abc),0.0):
        m = d_ab / 2 + math.cos(-a_cab) * d_ab - math.cos(-a_abc) * d_ab

        p_c = vector.vector([m, 0.0])

        map = {a: p_a, b: p_b, c: p_c}

        cluster = Configuration(map)
        cluster.underconstrained = True

        rval = [cluster]
    else:
        solutions = rr_int(p_a, dir_ac, p_b, dir_bc)

        rval = []

        for s in solutions:
            p_c = s
            map = {a: p_a, b: p_b, c: p_c}

            rval.append(Configuration(map))

    return rval

class BalloonMerge(Merge):
    """Represents a merging of two balloons"""

    def __init__(self, in1, in2, out):
        super(BalloonMerge, self).__init__(name="BalloonMerge", \
        inputs=[in1, in2], outputs=[out], overconstrained=False, \
        consistent=True)

        self.input1 = in1
        self.input2 = in2
        self.output = out
        self.shared = list(set(self.input1.vars).intersection(self.input2.vars))

        shared = set(in1.vars).intersection(in2.vars)

        if len(shared) < 2:
            raise Exception("underconstrained")
        elif len(shared) > 2:
            logging.getLogger("clustersolver").debug("overconstrained balloon \
merge")

            self.overconstrained = True

    def __str__(self):
        s = "balloonmerge("+str(self.input1)+"+"+str(self.input2)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("BalloonMerge.multi_execute \
called")

        c1 = self.inputs[0]
        c2 = self.inputs[1]

        conf1 = inmap[c1]
        conf2 = inmap[c2]

        return [conf1.merge_scale_2D(conf2)]

class BalloonRigidMerge(Merge):
    """Represents a merging of a balloon and a cluster"""

    def __init__(self, balloon, cluster, output):
        super(BalloonRigidMerge, self).__init__(name="BalloonRigidMerge", \
        inputs=[balloon, cluster], outputs=[output], overconstrained=False, \
        consistent=True)

        self.balloon = balloon
        self.cluster= cluster
        self.output = output
        self.shared = list(set(self.balloon.vars).intersection(self.cluster.vars))

        # check coincidence
        shared = set(balloon.vars).intersection(cluster.vars)

        if len(shared) < 2:
            raise Exception("underconstrained balloon-cluster merge")
        elif len(shared) > 2:
            logging.getLogger("clustersolver").debug("overconstrained merge %s \
+ %s", balloon, cluster)

            self.overconstrained = True

    def __str__(self):
        s = "balloonclustermerge("+str(self.balloon)+"+"+str(self.cluster)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug( \
"BalloonRigidMerge.multi_execute called")

        rigid = inmap[self.cluster]
        balloon = inmap[self.balloon]

        return [rigid.merge_scale_2D(balloon)]

class MergeHogs(Merge):
    """Represents a merging of two hogs to form a new hog"""

    def __init__(self, hog1, hog2, output):
        super(MergeHogs, self).__init__(name="MergeHogs", inputs=[hog1, hog2], \
        outputs=[output], overconstrained=False, consistent=True)

        self.hog1 = hog1
        self.hog2 = hog2
        self.output = output

        if hog1.cvar != hog2.cvar:
            raise Exception("hog1.cvar != hog2.cvar")

        shared = set(hog1.xvars).intersection(hog2.xvars)

        if len(shared) < 1:
            raise Exception("underconstrained balloon-cluster merge")
        elif len(shared) > 1:
            logging.getLogger("clustersolver").debug("overconstrained merge \
%s + %s", hog1, hog2)

            self.overconstrained = True

    def __str__(self):
        s = "mergeHH("+str(self.hog1)+"+"+str(self.hog2)+"->"+str(self.output)+")"
        s += "[" + self.status_str()+"]"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("MergeHogs.multi_execute \
called")

        conf1 = inmap[self.inputs[0]]
        conf2 = inmap[self.inputs[1]]

        shared = set(self.hog1.xvars).intersection(self.hog2.xvars)

        conf12 = conf1.merge_scale_2D(conf2, [self.hog1.cvar, list(shared)[0]])

        return [conf12]

class Derive(ClusterMethod):
    """A derive is a method such that a single output cluster is a
    subconstraint of a single input cluster."""

    __metaclass__ = abc.ABCMeta

class Rigid2Hog(Derive):
    """Represents a derivation of a hog from a cluster"""

    def __init__(self, cluster, hog):
        super(Rigid2Hog, self).__init__(name="Rigid2Hog", inputs=[cluster], \
        outputs=[hog])

        self.cluster = cluster
        self.hog = hog

    def __str__(self):
        s = "rigid2hog("+str(self.cluster)+"->"+str(self.hog)+")"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("Rigid2Hog.multi_execute \
called")

        conf1 = inmap[self.inputs[0]]
        vars = list(self.outputs[0].xvars) + [self.outputs[0].cvar]
        conf = conf1.select(vars)

        return [conf]

class Balloon2Hog(Derive):
    """Represents a derivation of a hog from a balloon
    """
    def __init__(self, balloon, hog):
        super(Balloon2Hog, self).__init__(name="Balloon2Hog", \
        inputs=[balloon], outputs=[hog])

        self.balloon = balloon
        self.hog = hog

    def __str__(self):
        s = "balloon2hog("+str(self.balloon)+"->"+str(self.hog)+")"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("Balloon2Hog.multi_execute \
called")

        conf1 = inmap[self.inputs[0]]
        vars = list(self.outputs[0].xvars) + [self.outputs[0].cvar]
        conf = conf1.select(vars)

        return [conf]

class SubHog(Derive):
    def __init__(self, hog, sub):
        super(SubHog, self).__init__(name="SubHog", inputs=[hog], outputs=[sub])

        self.hog = hog
        self.sub = sub

    def __str__(self):
        s = "subhog("+str(self.hog)+"->"+str(self.sub)+")"
        return s

    def multi_execute(self, inmap):
        logging.getLogger("clustersolver").debug("SubHog.multi_execute called")

        conf1 = inmap[self.inputs[0]]
        vars = list(self.outputs[0].xvars) + [self.outputs[0].cvar]
        conf = conf1.select(vars)

        return [conf]

def is_information_increasing(method):
    output = method.outputs[0]

    for cluster in method.inputs:
        if num_constraints(cluster.intersection(output)) >= num_constraints(output):
            # method's output doesn't remove a constraint from an input
            return False

    return True
