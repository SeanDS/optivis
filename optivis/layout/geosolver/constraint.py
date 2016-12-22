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

import abc
import logging

from optivis.layout.geosolver.graph import Graph
from optivis.layout.geosolver.notify import Notifier

class Constraint(object):
    """Abstract constraint

    A constraint defines a relation between variables that should be satisfied.

    Subclasses must define proper __init__(), variables() and satisfied()
    methods.

    Constraints must be immutable, hashable objects.
    """

    __metaclass__ = abc.ABCMeta

    def variables(self):
        """Returns a list of variables in this constraint

        If an attribute '_variables' has been defined, a new list with the
        contents of that attribute will be returned.

        Subclasses may choose to initialise this variable or to override this
        function.
        """

        # check if there are explicit variables defined
        if hasattr(self, "_variables"):
            # return list of variables
            return list(self._variables)
        else:
            # subclass hasn't set _variables or overridden this function
            raise NotImplementedError

    @abc.abstractmethod
    def satisfied(self, mapping):
        """Returns true if this constraint is satisfied by the specified \
        mapping from variables to values

        :param mapping: dict containing mapping
        """

        pass

    @abc.abstractmethod
    def __unicode__(self):
        raise NotImplementedError

    def __str__(self):
        return unicode(self).encode("utf-8")

class ConstraintGraph(Notifier):
    """A constraint graph"""

    def __init__(self, *args, **kwargs):
        """Creates a new, empty ConstraintGraph

        Defines relation between variables and constraints using a graph. If a
        constraint is imposed upon a variable, an edge is defined between them
        in the graph."""

        # initialise Notifier
        super(ConstraintGraph, self).__init__(*args, **kwargs)

        # empty dict of variables
        self._variables = {}

        # empty dict of constraints
        self._constraints = {}

        # empty graph
        self._graph = Graph()

    def variables(self):
        """Returns a list of this graph's variables"""

        return self._variables.keys()

    def constraints(self):
        """Returns a list of this graph's constraints"""

        return self._constraints.keys()

    def add_variable(self, var_name):
        """Adds the specified variable to the graph

        :param var_name: name of the variable to add
        """

        # only add if it doesn't already exist
        if var_name in self._variables:
            return

        # create entry in variables dict
        self._variables[var_name] = None

        # create a vertex in the graph for the variable
        self._graph.add_vertex(var_name)

        # notify listeners that a new variable has been added
        self.send_notify(("add_variable", var_name))

    def rem_variable(self, var_name):
        """Removes the specified variable from the graph

        :param var_name: name of the variable to remove
        """

        # only remove if it already exists
        if var_name not in self._variables:
            logging.getLogger("constraint").warning("Trying to remove variable \
that isn't in graph")

            return

        # remove variable's constraints
        map(lambda x: self.rem_constraint(x), self.get_constraints_on(var_name))

        # remove variable from dict
        del(self._variables[var_name])

        # remove graph vertex associated with the variable
        self._graph.rem_vertex(var_name)

        # notify listeners that a variable has been removed
        self.send_notify(("rem_variable", var_name))

    def add_constraint(self, constraint):
        """Adds the specified constraint to the graph

        :param constraint: constraint to add
        """

        # only add constraint if it isn't already in the graph
        if constraint in self._constraints:
            return

        # create entry in constraints dict
        self._constraints[constraint] = None

        # process the constraint's variables
        for var in constraint.variables():
            # add the variable to the graph
            self.add_variable(var)

            # create edge in the graph for the variable
            self._graph.add_edge(var, constraint)

        # notify listeners that a constraint has been added
        self.send_notify(("add_constraint", constraint))

    def rem_constraint(self, constraint):
        """Removes the specified constraint from the graph

        :param constraint: constraint to remove
        """

        # only remove constraint if it already exists in the graph
        if constraint not in self._constraints:
            logging.getLogger("constraint").warning("Trying to remove \
constraint that isn't in graph")

            return

        # remove constraint from dict
        del(self._constraints[constraint])

        # remove graph vertex associated with the constraint
        self._graph.rem_vertex(constraint)

        # notify listeners that a constraint was removed
        self.send_notify(("rem_constraint", constraint))

    def get_constraints_on(self, variable):
        """Returns a list of all constraints on the specified variable

        :param variable: variable to get constraints for
        """

        # check if variable is in the graph
        if not self._graph.has_vertex(variable):
            # default to empty list
            return []

        # return the variable's outgoing vertices
        return self._graph.outgoing_vertices(variable)

    def get_constraints_on_all(self, variables):
        """Gets a list of the constraints shared by all of the variables \
        specified in the sequence

        :param variables: variables to find constraints for"""

        # if no variables were specified, there are no shared constraints
        if len(variables) == 0:
            # return  an empty list
            return []

        # empty list of shared constraints
        shared_constraints = []

        # loop over the constraints of the first variable in the list
        for constraint in self.get_constraints_on(variables[0]):
            # default flag
            shared_constraint = True

            # loop over the variables in the rest of the list
            for var in variables[1:]:
                # is this variable constrained by this constraint?
                if var not in constraint.variables():
                    # this variable doesn't share the constraint
                    shared_constraint = False

                    # no point checking the others
                    break

            if shared_constraint:
                # add constraint to list of shared constraints
                shared_constraints.append(constraint)

        return shared_constraints

    def get_constraints_on_any(self, variables):
        """Gets a list of the constraints on any of the specified variables

        :param variables: variables to get constraints for"""

        # if no variables were specified, there are no constraints
        if len(variables) == 0:
            # return  an empty list
            return []

        # empty set of constraints
        constraints = set([])

        map(lambda x: constraints.update(x), \
        [set(self.get_constraints_on(variable)) for variable in variables])

        # return constraints set as a list
        return list(constraints)

    def __unicode__(self):
        return "ConstraintGraph(variables=[{0}], constraints=[{1}])".format( \
        ", ".join([unicode(var) for var in self._variables.keys()]), \
        ", ".join([unicode(const) for const in self._constraints.keys()]))

    def __str__(self):
        return unicode(self).encode("utf-8")

class PlusConstraint(Constraint):
    """Constraint for testing purposes"""

    def __init__(self, a, b, c):
        self._variables = [a, b, c]

    def __unicode__(self):
        return "PlusConstraint({0})".format(", ".join(self.variables))

    def satisfied(self, mapping):
        return mapping[self._variables[0]] + mapping[self._variables[1]] \
         == mapping[self._variables[2]]
