# -*- coding: utf-8 -*-

"""Geometric constraint problem and solver. Uses ClusterSolver for solving
problems incrementally."""

from __future__ import unicode_literals, division

import math
import logging

from optivis.layout.geosolver.vector import vector
from optivis.layout.geosolver.clustersolver import PrototypeMethod, \
ClusterSolver, is_information_increasing
from optivis.layout.geosolver.cluster import Rigid, Hedgehog
from optivis.layout.geosolver.configuration import Configuration
from optivis.layout.geosolver.constraint import Constraint, ConstraintGraph
from optivis.layout.geosolver.notify import Notifier, Listener
from optivis.layout.geosolver.tolerance import tol_eq
from optivis.layout.geosolver.intersections import angle_3p, distance_2p
from optivis.layout.geosolver.selconstr import SelectionConstraint

class GeometricProblem(Notifier, Listener):
    """A geometric constraint problem with a prototype.

       A problem consists of point variables (just variables for short), prototype
       points for each variable and constraints.

       Variables are just names and can be identified by any hashable object
       (recommend strings).
       Supported constraints are instances of DistanceConstraint,
       AngleConstraint, FixConstraint or SelectionConstraint.

       Prototype points are instances of the vector class.

       GeometricProblem listens for changes in constraint parameters and passes
       these changes, and changes in the system of constraints and the prototype,
       to any other listeners (e.g. GeometricSolver)

       instance attributes:
         cg         - a ConstraintGraph instance
         prototype  - a dictionary mapping variables to points
    """

    def __init__(self):
        """initialize a new problem"""

        Notifier.__init__(self)
        Listener.__init__(self)

        self.dimension = 2
        self.prototype = {}
        self.cg = ConstraintGraph()

    def add_point(self, variable, position):
        """add a point variable with a prototype position"""

        if variable not in self.prototype:
            # add point to prototype
            self.prototype[variable] = position

            # add to constraint graph
            self.cg.add_variable(variable)
        else:
            raise Exception("point already in problem")

    def set_point(self, variable, position):
        """set prototype position of point variable"""

        if variable not in self.prototype:
            raise Exception("unknown point variable")

        self.prototype[variable] = position
        self.send_notify(("set_point", (variable, position)))

    def get_point(self, variable):
        """get prototype position of point variable"""

        if variable not in self.prototype:
            raise Exception("unknown point variable")

        return self.prototype[variable]

    def has_point(self, variable):
        return variable in self.prototype

    def add_constraint(self, con):
        """add a constraint"""

        if isinstance(con, DistanceConstraint):
            for var in con.variables():
                if var not in self.prototype:
                    raise Exception("point variable not in problem")

            if self.get_distance(con.variables()[0],con.variables()[1]):
                raise Exception("distance already in problem")
            else:
                con.add_listener(self)

                self.cg.add_constraint(con)
        elif isinstance(con, AngleConstraint):
            for var in con.variables():
                if var not in self.prototype:
                    raise Exception("point variable not in problem")
            if self.get_angle(con.variables()[0], con.variables()[1], \
            con.variables()[2]):
                raise Exception("angle already in problem")
            else:
                con.add_listener(self)

                self.cg.add_constraint(con)
        elif isinstance(con, SelectionConstraint):
            for var in con.variables():
                if var not in self.prototype:
                    raise Exception("point variable not in problem")

            self.cg.add_constraint(con)
            self.send_notify(("add_selection_constraint", con))
        elif isinstance(con, FixConstraint):
            for var in con.variables():
                if var not in self.prototype:
                    raise Exception("point variable not in problem")

            if self.get_fix(con.variables()[0]):
                raise Exception("fix already in problem")

            self.cg.add_constraint(con)
        else:
            raise Exception("unsupported constraint type")

    def get_distance(self, a, b):
        """return the distance constraint on given points, or None"""

        on_a = self.cg.get_constraints_on(a)
        on_b = self.cg.get_constraints_on(b)

        on_ab = filter(lambda c: c in on_a and c in on_b, on_a)
        distances = filter(lambda c: isinstance(c, DistanceConstraint), on_ab)

        if len(distances) > 1:
            raise Exception("multiple constraints found")
        elif len(distances) == 1:
            return distances[0]

        return None

    def get_angle(self, a, b, c):
        """return the angle constraint on given points, or None"""

        on_a = self.cg.get_constraints_on(a)
        on_b = self.cg.get_constraints_on(b)
        on_c = self.cg.get_constraints_on(c)

        on_abc = filter(lambda x: x in on_a and x in on_b and x in on_c, on_a)
        angles = filter(lambda x: isinstance(x, AngleConstraint), on_abc)
        candidates = filter(lambda x: x.variables()[1] == b, angles)

        if len(candidates) > 1:
            raise Exception("multiple constraints found")
        elif len(candidates) == 1:
            return candidates[0]

        return None

    def get_fix(self, p):
        """return the fix constraint on given point, or None"""

        on_p = self.cg.get_constraints_on(p)

        fixes = filter(lambda x: isinstance(x, FixConstraint), on_p)

        if len(fixes) > 1:
            raise Exception("multiple constraints found")
        elif len(fixes) == 1:
            return fixes[0]

        return None

    def verify(self, solution):
        """returns true iff all constraints satisfied by given solution.
           solution is a dictionary mapping variables (names) to values (points)"""

        if solution == None:
            sat = False
        else:
            sat = True

            for con in self.cg.constraints():
                solved = True

                for v in con.variables():
                    if v not in solution:
                        solved = False

                        break

                if not solved:
                    logging.getLogger("geometric").debug("%s not solved", con)

                    sat = False
                elif not con.satisfied(solution):
                    logging.getLogger("geometric").debug("%s not satisfied", \
                    con)

                    sat = False

        return sat

    def rem_point(self, var):
        """remove a point variable from the constraint system"""

        if var in self.prototype:
            self.cg.rem_variable(var)

            del( self.prototype[var])
        else:
            raise Exception("variable {0} not in problem.".format(var))

    def rem_constraint(self, con):
        """remove a constraint from the constraint system"""

        if con in self.cg.constraints():
            if isinstance(con, SelectionConstraint):
                self.send_notify(("rem_selection_constraint", con))

            self.cg.rem_constraint(con)
        else:
            raise Exception("no constraint {0} in problem.".format(con))

    def receive_notify(self, obj, notify):
        """When notified of changed constraint parameters, pass on to listeners"""

        if isinstance(object, ParametricConstraint):
            (message, data) = notify

            if message == "set_parameter":
                self.send_notify(("set_parameter", (obj, data)))

    def __unicode__(self):
        # variable list on separate lines
        variables = "\n".join(["{0} = {1}".format(variable, \
        self.prototype[variable]) for variable in self.prototype])

        # constraints on separate lines
        constraints = "\n".join([unicode(constraint) for constraint \
        in self.cg.constraints()])

        return "{0}\n{1}".format(variables, constraints)

    def __str__(self):
        return unicode(self).encode("utf-8")

class GeometricSolver(Listener):
    """The GeometricSolver monitors changes in a GeometricProblem and
       maps any changes to corresponding changes in a GeometricCluster
    """

    def __init__(self, problem):
        """Create a new GeometricSolver instance

           keyword args
            problem        - the GeometricProblem instance to be monitored for changes
        """

        # call parent constructor
        super(GeometricSolver, self).__init__()

        # init variables
        self.problem = problem
        self.dimension = problem.dimension

        # constraint graph object
        self.cg = problem.cg

        # solver
        self.dr = ClusterSolver()

        # map
        self._map = {}

        # register listeners
        self.cg.add_listener(self)
        self.dr.add_listener(self)

        # create an initial fix cluster
        self.fixvars = []
        self.fixcluster = None

        # map current constraint graph variables
        for var in self.cg.variables():
            self._add_variable(var)

        # add distances first? Nicer decomposition in Rigids
        for con in self.cg.constraints():
            if isinstance(con, DistanceConstraint):
                self._add_constraint(con)

        # add angles and other constraints first? Better performance
        for con in self.cg.constraints():
            if not isinstance(con, DistanceConstraint):
                self._add_constraint(con)

    def get_constrainedness(self):
        # get cluster solver's top level solution(s)
        toplevel = self.dr.top_level()

        if len(toplevel) > 1:
            return "under-constrained"

        elif len(toplevel) == 1:
            cluster = toplevel[0]

            if isinstance(cluster, Rigid):
                configurations = self.dr.get(cluster)

                if configurations == None:
                    return "unsolved"
                elif len(configurations) > 0:
                    return "well-constrained"
                else:
                    return "over-constrained"
            else:
                return "under-constrained"
        elif len(toplevel) == 0:
            return "error"

    def get_result(self):
        """Computes the solution(s) to the geometric problem"""

        # empty dict
        map = {}

        # get cluster solver object's rigid clusters
        # at this point, the solver may already have a solution, if the solver
        # has been run before
        for drcluster in self.dr.rigids():
            # create empty geometric cluster
            geocluster = GeometricCluster()

            # create map from geometric cluster to drcluster (and vice versa)
            map[drcluster] = geocluster
            map[geocluster] = drcluster

            # determine variables
            for var in drcluster.vars:
                geocluster.variables.append(var)

            # determine solutions
            solutions = self.dr.get(drcluster)

            underconstrained = False

            if solutions != None:
                for solution in solutions:
                    geocluster.solutions.append(solution.mapping)

                    if solution.underconstrained:
                        underconstrained = True

            # determine flag
            if drcluster.overconstrained:
                geocluster.flag = GeometricCluster.S_OVER
            elif len(geocluster.solutions) == 0:
                geocluster.flag = GeometricCluster.I_OVER
            elif underconstrained:
                geocluster.flag = GeometricCluster.I_UNDER
            else:
                geocluster.flag = GeometricCluster.OK

        # determine subclusters
        for method in self.dr.methods():
            for out in method.outputs:
                if isinstance(out, Rigid):
                    parent = map[out]

                    for inp in method.inputs:
                        if isinstance(inp, Rigid):
                            parent.subs.append(map[inp])

        # combine clusters due to selection
        for method in self.dr.methods():
            if isinstance(method, PrototypeMethod):
                incluster = method.inputs[0]
                outcluster = method.outputs[0]
                geoin = map[incluster]
                geoout = map[outcluster]
                geoout.subs = list(geoin.subs)

        # determine top-level result
        rigids = filter(lambda c: isinstance(c, Rigid), self.dr.top_level())

        if len(rigids) == 0:
            # no variables in problem?
            result = GeometricCluster()

            result.variables = []
            result.subs = []
            result.solutions = []
            result.flags = GeometricCluster.UNSOLVED
        elif len(rigids) == 1:
            # structurally well constrained
            result = map[rigids[0]]
        else:
            # structurally underconstrained cluster
            result = GeometricCluster()
            result.flag = GeometricCluster.S_UNDER

            for rigid in rigids:
                result.subs.append(map[rigid])

        return result

    def receive_notify(self, obj, message):
        """Take notice of changes in constraint graph"""

        if obj == self.cg:
            (dtype, data) = message
            if dtype == "add_constraint":
                self._add_constraint(data)
            elif dtype == "rem_constraint":
                self._rem_constraint(data)
            elif dtype == "add_variable":
                self._add_variable(data)
            elif dtype == "rem_variable":
                self._rem_variable(data)
            else:
                raise Exception("unknown message type {0}".format(dtype))
        elif obj == self.problem:
            (dtype, data) = message

            if dtype == "set_point":
                (variable, point) = data

                self._update_variable(variable)
            elif dtype == "set_parameter":
                (constraint, value) = data

                self._update_constraint(constraint)
            else:
                raise Exception("unknown message type {0}".format(dtype))
        elif obj == self.dr:
            pass
        else:
            raise Exception("message from unknown source {0} {1}".format(obj, message))

    def _add_variable(self, var):
        if var not in self._map:
            rigid = Rigid([var])

            self._map[var] = rigid
            self._map[rigid] = var

            self.dr.add(rigid)

            self._update_variable(var)

    def _rem_variable(self, var):
        logging.getLogger("geometric").debug("GeometricSolver._rem_variable")

        if var in self._map:
            self.dr.remove(self._map[var])

            del(self._map[var])

    def _add_constraint(self, con):
        if isinstance(con, AngleConstraint):
            # map to hedgehog
            vars = list(con.variables())

            # hedgehog with 2nd point of constraint as the main point, and the
            # other points specified w.r.t. it
            hog = Hedgehog(vars[1], [vars[0], vars[2]])

            self._map[con] = hog
            self._map[hog] = con

            self.dr.add(hog)

            # set configuration
            self._update_constraint(con)
        elif isinstance(con, DistanceConstraint):
            # map to rigid
            vars = list(con.variables())

            rig = Rigid([vars[0], vars[1]])

            self._map[con] = rig
            self._map[rig] = con

            self.dr.add(rig)

            # set configuration
            self._update_constraint(con)
        elif isinstance(con, FixConstraint):
            if self.fixcluster != None:
                self.dr.remove(self.fixcluster)

            self.fixvars.append(con.variables()[0])

            if len(self.fixvars) >= self.problem.dimension:
                self.fixcluster = Cluster(self.fixvars)
                self.dr.add(self.fixcluster)
                self.dr.set_root(fixcluster)

            self._update_fix()
        else:
            pass

    def _rem_constraint(self, con):
        logging.getLogger("geometric").debug("GeometricSolver._rem_constraint")

        if isinstance(con,FixConstraint):
            if self.fixcluster != None:
                self.dr.remove(self.fixcluster)

            var = self.get(con.variables()[0])

            if var in self.fixvars:
                self.fixvars.remove(var)

            if len(self.fixvars) < self.problem.dimension:
                self.fixcluster = None
            else:
                self.fixcluster = Cluster(self.fixvars)
                self.dr.add(self.fixcluster)
                self.dr.set_root(self.fixcluster)
        elif con in self._map:
            self.dr.remove(self._map[con])
            del(self._map[con])

    def _update_constraint(self, con):
        if isinstance(con, AngleConstraint):
            # set configuration

            # the hog was added to the map for this constraint by _add_constraint,
            # which calls this method
            hog = self._map[con]

            # get variables associated with constraint
            variables = list(con.variables())

            v0 = variables[0]
            v1 = variables[1]
            v2 = variables[2]

            # get the constraint's specified angle
            angle = con.get_parameter()

            # create points representing the constraint
            p0 = vector([1.0, 0.0])
            p1 = vector([0.0, 0.0])
            p2 = vector([math.cos(angle), math.sin(angle)])

            # create configuration
            conf = Configuration({v0: p0, v1: p1, v2: p2})

            # set the hedgehog's configuration in the solver
            self.dr.set(hog, [conf])

            assert con.satisfied(conf.mapping)
        elif isinstance(con, DistanceConstraint):
            # set configuration
            rig = self._map[con]

            variables = list(con.variables())

            v0 = variables[0]
            v1 = variables[1]

            dist = con.get_parameter()

            p0 = vector([0.0, 0.0])
            p1 = vector([dist, 0.0])

            conf = Configuration({v0: p0, v1: p1})

            self.dr.set(rig, [conf])

            assert con.satisfied(conf.mapping)
        elif isinstance(con, FixConstraint):
            self._update_fix()
        else:
            raise Exception("unknown constraint type")

    def _update_variable(self, variable):
        cluster = self._map[variable]
        proto = self.problem.get_point(variable)

        conf = Configuration({variable: proto})

        self.dr.set(cluster, [conf])

    def _update_fix(self):
        if self.fixcluster:
            variables = fixcluster.vars

            map = {}

            for var in variables:
                map[var] = self.problem.get_fix(var).get_parameter()

            conf = Configuration(map)

            self.dr.set(fixcluster, [conf])
        else:
            logging.getLogger("geometric").warning("No fix cluster to update")

class GeometricCluster(object):
    """Represents the result of solving a GeometricProblem. A cluster is a list of
       point variable names and a list of solutions for
       those variables. A solution is a dictionary mapping variable names to
       points. The cluster also keeps a list of sub-clusters (GeometricCluster)
       and a set of flags, indicating incidental/structural
       under/overconstrained

       instance attributes:
            variables       - a list of point variable names
            solutions       - a list of solutions. Each solution is a dictionary
                              mapping variable names to vectors.
            subs            - a list of sub-clusters
            flag            - value                 meaning
                              OK                    well constrained
                              I_OVER                incicental over-constrained
                              I_UNDER               incidental under-constrained
                              S_OVER                structural overconstrained
                              S_UNDER               structural underconstrained
                              UNSOLVED              unsolved
       """

    OK = "well constrained"
    I_OVER = "incidental over-constrained"
    I_UNDER = "incidental under-constrained"
    S_OVER = "structral over-constrained"
    S_UNDER = "structural under-constrained"
    UNSOLVED = "unsolved"

    def __init__(self):
        """initialise an empty new cluster"""

        self.variables = []
        self.solutions = []
        self.subs = []
        self.flag = GeometricCluster.OK

    def __str__(self):
        return self._str_recursive()

    def _str_recursive(result, depth=0, done=None):
        # create indent
        spaces = ""

        for i in range(depth):
            spaces = spaces + "|"

        # make done
        if done == None:
            done = set()

        # recurse
        s = ""

        if result not in done:
            # this one is done...
            done.add(result)

            # recurse
            for sub in result.subs:
                s = s + sub._str_recursive(depth+1, done)

        elif len(result.subs) > 0:
            s = s + spaces + "|...\n"

        # print cluster
        s = spaces + "cluster " + str(result.variables) + " " + str(result.flag) + " " + str(len(result.solutions)) + " solutions\n" + s

        return s

class ParametricConstraint(Constraint, Notifier):
    """A constraint with a parameter and notification when parameter changes"""

    def __init__(self):
        """initialize ParametricConstraint"""

        Notifier.__init__(self)

        self._value = None

    def get_parameter(self):
        """get parameter value"""

        return self._value

    def set_parameter(self,value):
        """set parameter value and notify any listeners"""

        self._value = value
        self.send_notify(("set_parameter", value))

class FixConstraint(ParametricConstraint):
    """A constraint to fix a point relative to the coordinate system"""

    def __init__(self, var, pos):
        """Create a new DistanceConstraint instance

           keyword args:
            var    - a point variable name
            pos    - the position parameter
        """

        super(FixConstraint, self).__init__()

        self._variables = [var]
        self.set_parameter(pos)

    def satisfied(self, mapping):
        """return True iff mapping from variable names to points satisfies constraint"""

        a = mapping[self._variables[0]]

        result = tol_eq(a[0], self._value[0]) and tol_eq(a[1], self._value[1])

        return result

    def __str__(self):
        return "FixConstraint("\
            +str(self._variables[0])+","\
            +str(self._value)+")"

class DistanceConstraint(ParametricConstraint):
    """A constraint on the Euclidean distance between two points"""

    def __init__(self, a, b, dist):
        """Create a new DistanceConstraint instance

           keyword args:
            a    - a point variable name
            b    - a point variable name
            dist - the distance parameter value
        """
        super(DistanceConstraint, self).__init__()

        self._variables = [a, b]
        self.set_parameter(dist)

    def satisfied(self, mapping):
        """return True iff mapping from variable names to points satisfies constraint"""

        a = mapping[self._variables[0]]
        b = mapping[self._variables[1]]

        result = tol_eq(distance_2p(a,b), self._value)

        return result

    def __str__(self):
        return "DistanceConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._value)+")"

class AngleConstraint(ParametricConstraint):
    """A constraint on the angle in point B of a triangle ABC"""

    def __init__(self, a, b, c, ang):
        """Create a new AngleConstraint instance.

           keyword args:
            a    - a point variable name
            b    - a point variable name
            c    - a point variable name
            ang  - the angle parameter value
        """

        super(AngleConstraint, self).__init__()

        self._variables = [a,b,c]
        self.set_parameter(ang)

    def satisfied(self, mapping):
        """return True iff mapping from variable names to points satisfies constraint"""

        a = mapping[self._variables[0]]
        b = mapping[self._variables[1]]
        c = mapping[self._variables[2]]

        ang = angle_3p(a,b,c)

        if ang == None:
            result = False
            cmp = self._value
        else:
            if len(a) >= 3:
                cmp = abs(self._value)
            else:
                cmp = self._value

            result = tol_eq(ang, cmp)

        if result == False:
            logging.getLogger("geometric").debug("measured angle = %s, parameter value = %s, geometric", ang, cmp)

        return result

    def __str__(self):
        return "AngleConstraint("\
            +str(self._variables[0])+","\
            +str(self._variables[1])+","\
            +str(self._variables[2])+","\
            +str(self._value)+")"
