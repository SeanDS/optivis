# -*- coding: utf-8 -*-

"""Module for method graphs.

A method graph contains variables and methods. Methods are objects that specify
input and output variables and an 'execute' method. Whenever the value of a
variable is changed, one or more methods are executed to update the value of
'upstream' variables."""

from __future__ import unicode_literals, division

import abc

from graph import Graph

class MethodGraph(object):
    """A method graph

    A method graph is represented by a directed bi-partite graph: nodes are
    either varables or methods. Edges run from input variables to methods and
    from methods to output variables.

    A method graph must not contain cycles. Every variable must be determined by
    at most one constraint.

    Methods must be instances of :class:`~.Method`. Variables are basically just
    names, and may be any immutable, hashable object, e.g. strings. Values
    associated with variables may be of any type.

    If no value is explicitly associated with a variable, it defaults to None.
    """

    def __init__(self):
        # the graph structure
        self._graph = Graph()

        # map from variable names (the keys) to values
        self._map = {}

        # collection of methods (keys)
        self._methods = {}

        # collection of changed variables since last propagation
        self._changed = {}

    def variables(self):
        """Returns a list of variables in the method graph"""

        return self._map.keys()

    def methods(self):
        """Returns a list of methods associated with the graph"""

        return self._methods.keys()

    def add_variable(self, varname, value=None):
        """Adds a variable, optionally with a value"""

        if not varname in self._map:
            self._map[varname] = value
            self._graph.add_vertex(varname)

    def rem_variable(self, varname):
        """Remove a variable and all methods on that variable"""

        if varname in self._map:
            del(self._map[varname])

            if varname in self._changed:
                del(self._changed[varname])

            # delete all methods on it
            map(self.rem_method, self._graph.ingoing_vertices(varname))
            map(self.rem_method, self._graph.outgoing_vertices(varname))

            # remove it from graph
            self._graph.rem_vertex(varname)
        else:
            raise Exception("Variable not in graph")

    def get(self, key):
        """Gets the value of a variable"""

        return self._map[key]

    def set(self, varname, value, prop=True):
        """Sets the value of a variable.

        :param prop: whether to propagate changes
        """

        self._map[varname] = value
        self._changed[varname] = 1

        if prop:
            self.propagate()

    def add_method(self, met, prop=True):
        """Adds a method.

        :param prop: whether to propagate changes
        """

        if met in self._methods:
            return

        self._methods[met] = 1

        # update graph
        for var in met.inputs():
            self.add_variable(var)
            self._graph.add_edge(var, met)

        for var in met.outputs():
            self.add_variable(var)
            self._graph.add_edge(met, var)

        # check validity of graph
        for var in met.outputs():
            if len(self._graph.ingoing_vertices(var)) > 1:
                self.rem_method(met)

                raise MethodGraphValidityException("Variable {0} determined by multiple methods".format(var))
            elif len(self._graph.path(var, var)) != 0:
                self.rem_method(met)

                raise MethodGraphValidityException("Cycle in graph not allowed (variable {0})".format(var))

        if prop:
            self._execute(met)
            self.propagate()

    def rem_method(self, met):
        """Removes a method"""

        if met in self._methods:
            del(self._methods[met])
            self._graph.rem_vertex(met)
        else:
            raise Exception("Method not in graph")

    def propagate(self):
        """Propagates any pending changes

        Changes are propagated until no changes are left or until no more
        changes can be propagated. This method is called from set() and
        add_method() by default. However, if the user so chooses, the methods
        will not call propagate, and the user should call this fucntion at a
        convenient time.
        """

        while len(self._changed) != 0:
            pick = self._changed.keys()[0]
            methods = self._graph.outgoing_vertices(pick)

            for met in methods:
                self._execute(met)

            if pick in self._changed:
                del(self._changed[pick])

    def clear(self):
        """Clears the method graph by removing all its variables"""

        while (len(self._map) > 0):
            self.rem_variable(self._map.keys()[0])

    def execute(self, met):
        """Executes a method and propagates changes

        Method must be in MethodGraph
        """

        if met in self._methods:
            self._execute(met)
            self.propagate()
        else:
            raise Exception("Method not in graph")

    def _execute(self, met):
        """Executes a method

        Method is executed only if all input variable values are not None.
        Updates mapping and change flags.
        """

        # create input map and check for None values
        inmap = {}
        has_nones = False

        for var in met.inputs():
            value = self._map[var]

            if value == None:
                has_nones = True

            inmap[var] = value
        for var in met.outputs():
            inmap[var] = self._map[var]

        # call method.execute
        if has_nones:
            outmap = {}
        else:
            outmap = met.execute(inmap)

        # update values in self._map
        # set output variables changed
        for var in met.outputs():
            if var in outmap:
                self._map[var] = outmap[var]
                self._changed[var] = 1
            else:
                if self._map[var] != None:
                    self._changed[var] = 1
                    self._map[var] = None

        # clear change flag on input variables
        for var in met.inputs():
            if var in self._changed:
                del(self._changed[var])

    def __unicode__(self):
        variables = ", ".join([str(el) for el in self._map.keys()])
        methods = ", ".join([str(el) for el in self._methods.keys()])

        return "MethodGraph(variables=[{0}], methods=[{1}])".format(variables, \
        methods)

    def __str__(self):
        return unicode(self).encode("utf-8")

class Method(object):
    """Defines input variables, output variables and an execute method

    Instances must be immutable, hashable objects.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, inputs, outputs):
        """Instantiates a new Method"""

        self.name = unicode(name)
        self._inputs = list(inputs)
        self._outputs = list(outputs)

    @abc.abstractmethod
    def execute(self, inmap):
        """Execute method

        Returns a mapping (dict) of output variables to values, given an input
        map that maps input variables to values (dict). The previous value of
        the output variable should also be in inmap. If the method cannot be
        executed, it should return an empty map.
        """

        raise NotImplementedError()

    def __unicode__(self):
        input_str = ", ".join(self._inputs)
        output_str = ", ".join(self._outputs)

        return "{0}(in=[{1}], out=[{2}])".format(self.name, input_str, output_str)

    def __str__(self):
        return unicode(self).encode("utf-8")

class AddMethod(Method):
    """Method representing addition of two variables"""

    def __init__(self, a, b, c):
        """Instantiates a new AddMethod

        :param a: first input
        :param b: second input
        :param c: output
        """

        super(AddMethod, self).__init__("AddMethod", inputs=[a, b], outputs=[c])

    def execute(self, inmap):
        """Execute method"""

        outmap = {}

        a = self._inputs[0]
        b = self._inputs[1]
        c = self._outputs[0]

        if a in inmap and b in inmap and inmap[a] != None and inmap[b] != None:
            outmap[c] = inmap[a] + inmap[b]

        return outmap

class SubMethod(Method):
    """Method representing subtraction of two variables"""

    def __init__(self, a, b, c):
        """Instantiates a new SubMethod

        :param a: first input
        :param b: second input
        :param c: output
        """

        super(SubMethod, self).__init__("SubMethod", inputs=[a, b], outputs=[c])

    def execute(self, inmap):
        """Execute method"""

        outmap = {}

        a = self._inputs[0]
        b = self._inputs[1]
        c = self._outputs[0]

        if a in inmap and b in inmap and inmap[a] != None and inmap[b] != None:
            outmap[c] = inmap[a] - inmap[b]

        return outmap

class SetMethod(Method):
    """Method representing the setting of a variable's value"""

    def __init__(self, var, value):
        """Instantiates a new SetMethod

        :param var: variable name
        :param value: any object to be associated with var
        """

        super(SetMethod, self).__init__("SetMethod", inputs=[], outputs=[var])

        # set value
        self._value = value

    def execute(self, inmap):
        """Execute method"""

        return {self._outputs[0]: self._value}

    def __unicode__(self):
        return "{0}({1}={2})".format(self.name, self._outputs[0], self._value)

class AssignMethod(Method):
    """Method representing the assignment of a value to a variable"""

    def __init__(self, a, b):
        """Instantiates a new AssignMethod

        :param a: first input
        :param b: second input
        """

        self._inputs = [b]
        self._outputs = [a]

    def execute(self, inmap):
        if self._inputs[0] in inmap:
            return {self._outputs[0]: inmap(self._inputs[0])}

        return {}

    def __unicode__(self):
        return "{0}({1}={2})".format(self.name, self._inputs[0], self._value)

class MethodGraphValidityException(Exception):
    """Error indicating operation violated MethodGraph validity"""

    def __unicode__(self):
        return unicode(repr(self))

    def __str__(self):
        return unicode(self).encode("utf-8")
