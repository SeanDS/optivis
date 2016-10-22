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
        return unicode(self).encode('utf-8')

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

    def __init__(self, *args, **kwargs):
        """Instantiate a MultiMethod"""

        # call parent constructor
        super(MultiMethod, self).__init__(*args, **kwargs)

        # empty list of multi inputs
        self.multi_inputs = []

        for variable in self.inputs:
            if isinstance(variable, MultiVariable):
                self.multi_inputs.append(variable)

        if len(self.outputs) != 1:
            raise Exception("MultiMethod requires exactly one output")

        if not isinstance(self.outputs[0], MultiVariable):
            raise Exception("MultiMethod requires a MultiVariable output")

    def execute(self, inmap):
        """Calls multi_execute for each permutation of multi-valued input \
        variables and collects result in multi-valued ouput variables

        Subclasses should implement multi_execute.
        """

        base_inmap = {}

        for variable in self.inputs:
            if variable not in self.multi_inputs:
                value = inmap[variable]
                base_inmap[variable] = value

        outvar = self.outputs[0]
        values = self._recurse_execute(inmap, base_inmap, self.multi_inputs)

        return {outvar: values}

    def _recurse_execute(self, inmap, base_inmap, multi_inputs):
        if len(multi_inputs) > 0:
            mvar = multi_inputs[0]
            values = inmap[mvar]
            output = set()

            for value in values:
                base_inmap[mvar] = value
                output.update(self._recurse_execute(inmap, base_inmap, \
                multi_inputs[1:]))

            return output
        else:
            return self.multi_execute(base_inmap)

class SumProdMethod(MultiMethod):
    """A MultiMethod that assigns the sum and product of its input to its output
    MultiVariable"""

    def __init__(self, a, b, c):
        super(SumProdMethod, self).__init__("SumProdMethod", [a, b], [c])

    def multi_execute(self, inmap):
        a = inmap[self.inputs[0]]
        b = inmap[self.inputs[1]]

        return [a + b, a * b]
