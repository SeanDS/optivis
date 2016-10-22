# -*- coding: utf-8 -*-

"""Constraint graphs

A constraint graph represents a constraint problem. A constraint defines a
number of variables, and a relation between those variables that must be
satisfied.

Note that no values are associated with variables in the constraint graph, i.e.
satisfying constraints is not considered in this module.

The constraint graph is (internally) represented by a directed bi-partite
graph; nodes are variables or constraints and edges run from variables to
constraints.

Variables are just names; any non-mutable hashable object, e.g. a string,
qualifies for a variable. Constraints must be instances of (suclasses of) class
Constraint, and must also be non-mutable, hashable objects.
"""

from __future__ import unicode_literals, division

from optivis.layout.geosolver.graph import Graph
from optivis.layout.geosolver.notify import Notifier

class Constraint(object):
    """Abstract constraint

       A constraint defines a relation between variables that should be
       satisfied.

       Subclasses must define proper __init__(), variables() and satisfied()
       methods. Constraints must be non-mutable, hashable objects.
    """

    def variables(self):
        """return a list of variables

           If an attribute '_variables' has been defined, a new list
           with the contents of that attribute will be returned.
           Subclasses may choose to initialise this variable or to
           override this function.
        """
        if hasattr(self, "_variables"):
            return list(self._variables)
        else:
            raise NotImplementedError

    def satisfied(self, mapping):
        """return true iff constraint is satisfied by given mapping
           from variables to values (dictionary)"""
        raise NotImplementedError

class ConstraintGraph(Notifier):
    """A constraint graph.

       For more information see module documentation.
    """

    def __init__(self):
        """Create a new, empty ConstraintGraph"""
        Notifier.__init__(self)
        self._variables = {}
        """A set of variables"""
        self._constraints = {}
        """A set of constraints"""
        self._graph = Graph()
        """A graph for fast navigation. The graph contains an
           edge from a var to a constraint if the constraint is imposed
           on that variable"""

    def variables(self):
        """return a list of variables"""
        return self._variables.keys()

    def constraints(self):
        """return a list of variables"""
        return self._constraints.keys()

    def add_variable(self, varname):
        """add a variable"""
        if not varname in self._variables:
            self._variables[varname] = None
            self._graph.add_vertex(varname)
            self.send_notify(("add_variable", varname))

    def rem_variable(self, varname):
        """remove a variable"""
        if varname in self._variables:
            # remove constraints on variabe
            for con in self.get_constraints_on(varname):
                self.rem_constraint(con)
            # remove variable itself
            del self._variables[varname]
            self._graph.rem_vertex(varname)
            self.send_notify(("rem_variable", varname))

    def add_constraint(self, con):
        """add a constraint"""
        if con not in self._constraints:
            self._constraints[con] = None
            for var in con.variables():
                self.add_variable(var)
                self._graph.add_edge(var, con)
            self.send_notify(("add_constraint", con))

    def rem_constraint(self, con):
        """remove a variable"""
        if con in self._constraints:
            del self._constraints[con]
            self._graph.rem_vertex(con)
            self.send_notify(("rem_constraint", con))

    def get_constraints_on(self, var):
        """get a list of all constraints on var"""
        if self._graph.has_vertex(var):
            return self._graph.outgoing_vertices(var)
        else:
            return []

    def get_constraints_on_all(self, varlist):
        """get a list of all constraints on all vars in list"""
        if len(varlist) == 0: return []
        l0 = self.get_constraints_on(varlist[0])
        l = []
        for con in l0:
            ok = True;
            for var in varlist[1:]:
                ok &= (var in con.variables())
            #for
            if ok: l.append(con)
        #for
        return l;

    def get_constraints_on_any(self, varlist):
        """get a list of all constraints on any of the vars in list"""
        if len(varlist) == 0: return []
        l = []
        for var in varlist:
            l0 = self.get_constraints_on(var)
            for con in l0:
                if con not in l: l.append(con)
            #for
        #for
        return l;

    def __unicode__(self):
        return "ConstraintGraph(variables=[{0}], constraints=[{1}])".format( \
        ", ".join([unicode(var) for var in self._variables.keys()]), \
        ", ".join([unicode(const) for const in self._constraints.keys()]))

    def __str__(self):
        return unicode(self).encode("utf-8")

# ---------- test ----------

def test():
    class PlusConstraint(Constraint):
        def __init__(self, a, b, c):
            self._variables = [a,b,c]

        def satisfied(self, mapping):
            return mapping[self._variables[0]] + mapping[self._variables[1]]\
             == mapping[self._variables[2]]

        def __str__(self):
            s = "PlusConstraint("
            s += self._variables[0]+","
            s += self._variables[1]+","
            s += self._variables[2]+")"
            return s

    problem = ConstraintGraph()
    problem.add_variable('a')
    problem.add_variable('b')
    plus = PlusConstraint('a','b','c')
    problem.add_constraint(plus)
    print str(problem)
    print "get_constraints_on(a) = ",
    print map(str, problem.get_constraints_on('a'))

if __name__ == "__main__":
    test()
