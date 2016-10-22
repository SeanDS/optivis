# -*- coding: utf-8 -*-

"""Base classes for multi-valued assignments in methodgraphs"""

from __future__ import unicode_literals, division

from method import Method, MethodGraph

class MultiVariable(object):
    """Represents multi-valued variables"""

    def __init__(self, name=None):
        self.name = name

    def __unicode__(self):
        if self.name is None:
            return "MultiVariable#{0}".format(id(self))

        return "MultiVariable({0})".format(self.name)

    def __str__(self):
        return self.encode('utf-8')

    def __repr__(self):
        return unicode(self)

class MultiMethod(Method):
    """A :class:`~Method` that is executed for multiple alternative inputs, \
    resulting in multiple output values.

    Input may optionally contain MultiVariable instances.
    There must be a single MultiVariable output variable.

    Subclasses should implement the 'multi_execute' method, not overide the \
    'execute' method. This method is called for every permutation of values of \
    multi-valued input variables.

    Any input variables that are instances of :class:`~.MultiVariable` will be \
    replaced by their shadowed counterpart in the input map for multi_execute.

    The 'multi_execute' method must return a list of possible values for the \
    output variable. The output values returned by subsequent calls \
    multi-execute are collected and stored in the output \
    :class:`~.MultiVariable`.
    """

    def __init__(self):
        """Instantiate a MultiMethod

        Call this after _inputs and _outputs has been set.
        """

        self._multi_inputs = []

        for variable in self._inputs:
            if isinstance(variable, MultiVariable):
                self._multi_inputs.append(variable)

        if len(self._outputs) != 1:
            raise Exception("MultiMethod requires exactly one output")

        if not isinstance(self._outputs[0], MultiVariable):
            raise Exception("MultiMethod requires a MultiVariable output")

    def execute(self, inmap):
        """Calls multi_execute for each permutation of multi-valued input \
        variables and collects result in multi-valued ouput variables

        Subclasses should implement multi_execute.
        """

        base_inmap = {}

        for variable in self._inputs:
            if variable not in self._multi_inputs:
                value = inmap[variable]
                base_inmap[variable] = value

        outvar = self._outputs[0]
        values = self._recurse_execute(inmap, base_inmap, self._multi_inputs)

        return {outvar: values}

    def _recurse_execute(self, inmap, base_inmap, multi_inputs):
        if len(multi_inputs) > 0:
            mvar = multi_inputs[0]
            values = inmap[mvar]
            output = set()

            for value in values:
                base_inmap[mvar] = value
                output.union_update(self._recurse_execute(inmap, base_inmap, \
                multi_inputs[1:]))

            return output
        else:
            return self.multi_execute(base_inmap)
