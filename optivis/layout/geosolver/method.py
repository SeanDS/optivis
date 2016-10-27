# -*- coding: utf-8 -*-

"""Module for method graphs.

A method graph contains variables and methods. Methods are objects that specify
input and output variables and an 'execute' method. Whenever the value of a
variable is changed, one or more methods are executed to update the value of
'upstream' variables."""

from __future__ import unicode_literals, division

import abc

from optivis.layout.geosolver.graph import Graph

class Method(object):
    """Defines input variables, output variables and an execute method

    Instances must be immutable, hashable objects.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, inputs, outputs):
        """Instantiates a new Method"""

        self.name = unicode(name)
        self.inputs = list(inputs)
        self.outputs = list(outputs)

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
        # comma separated list of inputs
        input_str = " + ".join([unicode(_input) for _input in self.inputs])

        # comma separated list of outputs
        output_str = " + ".join([unicode(output) for output in self.outputs])

        # combined string
        return "{0}({1} -> {2})".format(self.name, input_str, \
        output_str)

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

        # call parent to set appropriate inputs and outputs
        super(AddMethod, self).__init__("AddMethod", inputs=[a, b], outputs=[c])

    def execute(self, in_map):
        """Execute method"""

        # map of outputs to input values
        out_map = {}

        # get variables from lists of inputs and outputs
        a = self.inputs[0]
        b = self.inputs[1]
        c = self.outputs[0]

        # calculate c = a + b if the variables exist in the input map
        if a in in_map and b in in_map \
        and in_map[a] != None and in_map[b] != None:
            # set the value in the output map
            out_map[c] = in_map[a] + in_map[b]

        return out_map

class SubMethod(Method):
    """Method representing subtraction of two variables"""

    def __init__(self, a, b, c):
        """Instantiates a new SubMethod

        :param a: first input
        :param b: second input
        :param c: output
        """

        # call parent to set appropriate inputs and outputs
        super(SubMethod, self).__init__("SubMethod", inputs=[a, b], outputs=[c])

    def execute(self, in_map):
        """Execute method"""

        # map of outputs to input values
        out_map = {}

        # get variables from lists of inputs and outputs
        a = self.inputs[0]
        b = self.inputs[1]
        c = self.outputs[0]

        # calculate c = a - b if the variables exist in the input map
        if a in in_map and b in in_map \
        and in_map[a] != None and in_map[b] != None:
            # set the value in the output map
            out_map[c] = in_map[a] - in_map[b]

        return out_map

class SetMethod(Method):
    """Method representing the setting of a variable's value"""

    def __init__(self, variable, value):
        """Instantiates a new SetMethod

        :param variable: variable name
        :param value: any object to be associated with var
        """

        # call parent to set appropriate inputs and outputs
        super(SetMethod, self).__init__("SetMethod", inputs=[], \
        outputs=[variable])

        # make a record of the value to be set
        self._value = value

    def execute(self, in_map):
        """Execute method"""

        # return a dict with the output set to the value
        return {self._outputs[0]: self._value}

    def __unicode__(self):
        """Unicode representation of the method

        Overrides :class:`~.Method`
        """

        # show the output's set value in the string representation
        return "{0}({1}={2})".format(self.name, self._outputs[0], self._value)

class AssignMethod(Method):
    """Method representing the assignment of a value to a variable"""

    def __init__(self, a, b):
        """Instantiates a new AssignMethod

        :param a: first input
        :param b: second input
        """

        # call parent to set appropriate inputs and outputs
        super(AssignMethod, self).__init__("AssignMethod", inputs=[b], \
        outputs=[a])

    def execute(self, in_map):
        """Execute method"""

        # return empty dict of the only input is not in the map
        if self._inputs[0] not in in_map:
            return {}

        # set the relevant output to the mapping and return
        return {self._outputs[0]: in_map(self._inputs[0])}

    def __unicode__(self):
        # show the input's assigned value in the string representation
        return "{0}({1}={2})".format(self.name, self._inputs[0], self._value)

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

        if varname not in self._map:
            self._map[varname] = value
            self._graph.add_vertex(varname)

    def rem_variable(self, varname):
        """Remove a variable and all methods on that variable"""

        if varname not in self._map:
            raise Exception("Variable not in graph")

        del(self._map[varname])

        if varname in self._changed:
            del(self._changed[varname])

        # delete all methods on it
        map(self.rem_method, self._graph.ingoing_vertices(varname))
        map(self.rem_method, self._graph.outgoing_vertices(varname))

        # remove it from graph
        self._graph.rem_vertex(varname)

    def get(self, variable):
        """Gets the value of a variable"""

        return self._map[variable]

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
        for var in met.inputs:
            self.add_variable(var)
            self._graph.add_edge(var, met)

        for var in met.outputs:
            self.add_variable(var)
            self._graph.add_edge(met, var)

        # check validity of graph
        for var in met.outputs:
            if len(self._graph.ingoing_vertices(var)) > 1:
                self.rem_method(met)

                raise MethodGraphDetermineException("Variable {0} determined \
by multiple methods".format(var))
            elif len(self._graph.path(var, var)) != 0:
                self.rem_method(met)

                raise MethodGraphCycleException("Cycle in graph not allowed \
(variable {0})".format(var))

        if prop:
            # execute includes propagation
            self.execute(met)

    def rem_method(self, met):
        """Removes a method"""

        if met not in self._methods:
            raise Exception("Method not in graph")

        del(self._methods[met])
        self._graph.rem_vertex(met)

    def propagate(self):
        """Propagates any pending changes

        Changes are propagated until no changes are left or until no more
        changes can be propagated. This method is called from set() and
        add_method() by default. However, if the user so chooses, the methods
        will not call propagate, and the user should call this function at a
        convenient time.
        """

        while len(self._changed) != 0:
            pick = self._changed.keys()[0]
            methods = self._graph.outgoing_vertices(pick)

            map(lambda method: self._do_execute(method), methods)

            if pick in self._changed:
                del(self._changed[pick])

    def clear(self):
        """Clears the method graph by removing all its variables"""

        while (len(self._map) > 0):
            self.rem_variable(self._map.keys()[0])

    def execute(self, method):
        """Executes a method and propagates changes

        Method must be in MethodGraph
        """

        if method not in self._methods:
            raise Exception("Method not in graph")

        self._do_execute(method)
        self.propagate()

    def _do_execute(self, method):
        """Executes a method

        Method is executed only if all input variable values are not None.
        Updates mapping and change flags.
        """

        # create input map and check for None values
        inmap = {}
        has_nones = False

        for var in method.inputs:
            value = self._map[var]

            if value == None:
                has_nones = True

            inmap[var] = value

        for var in method.outputs:
            inmap[var] = self._map[var]

        # call method.execute
        if has_nones:
            outmap = {}
        else:
            outmap = method.execute(inmap)

        # update values in self._map
        # set output variables changed
        for var in method.outputs:
            if var in outmap:
                self._map[var] = outmap[var]
                self._changed[var] = 1
            else:
                if self._map[var] != None:
                    self._changed[var] = 1
                    self._map[var] = None

        # clear change flag on input variables
        for var in method.inputs:
            if var in self._changed:
                del(self._changed[var])

    def __unicode__(self):
        variables = ", ".join([unicode(element) \
        for element in self._map.keys()])
        methods = ", ".join([unicode(element) \
        for element in self._methods.keys()])

        return "MethodGraph(variables=[{0}], methods=[{1}])".format(variables, \
        methods)

    def __str__(self):
        return unicode(self).encode("utf-8")

class MethodGraphCycleException(Exception):
    """Error indicating a cyclic connection in a MethodGraph"""
    pass

class MethodGraphDetermineException(Exception):
    """Error indicating a variable is determined by more than one method in a
    MethodGraph"""
    pass
