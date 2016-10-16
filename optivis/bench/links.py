from __future__ import unicode_literals, division

import math

from optivis.bench.items import BenchItem
from optivis.geometry import Coordinates

class Link(BenchItem):
    def __init__(self, output_node, input_node, length=None, specs=None, \
    *args, **kwargs):
        self.output_node = output_node
        self.input_node = input_node
        self.length = length

        if specs is None:
            # default link spec
            specs = LinkSpec()

        self.specs = specs

        # check we've not linked one component to itself
        if self.output_node.component == self.input_node.component:
            raise Exception("Cannot link component directly to itself")

        # start and end position defaults (layout manager sets this properly)
        self.start_pos = Coordinates.origin()
        self.end_pos = Coordinates.origin()

        super(Link, self).__init__(*args, **kwargs)

    def __unicode__(self):
        """String representation of this link"""

        return "{0} --> {1}".format(self.output_node, self.input_node)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of this link"""

        return unicode(self)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = float(length)

    @property
    def start_pos(self):
        return self._start_pos

    @start_pos.setter
    def start_pos(self, start_pos):
        self._start_pos = Coordinates(start_pos)

    @property
    def end_pos(self):
        return self._end_pos

    @end_pos.setter
    def end_pos(self, end_pos):
        self._end_pos = Coordinates(end_pos)

    def get_bounding_box(self):
        """Coordinates of item's edges closest to and furthest away from \
        origin

        :return: (lower, upper) bounds
        """

        # swap if start is further from end
        if self.start_pos.length() < self.end_pos.length():
            return (self.start_pos, self.end_pos)
        else:
            return (self.end_pos, self.start_pos)

    def get_label_origin(self):        
        return self.start_pos + (self.end_pos - self.start_pos) / 2

    def get_label_azimuth(self):
        mid_point = self.end_pos - self.start_pos

        if mid_point.y == 0:
            # avoid division by zero
            return 0

        return math.degrees(math.atan2(mid_point.y, mid_point.x))

    def has_component(self, component):
        return component in self.get_components()

    def get_components(self):
        return [self.output_node.component, self.input_node.component]

#    def getNodesForCommonComponent(self, otherLink):
#        thisOutputComponent = self.outputNode.component
#        thisInputComponent = self.inputNode.component
#
#        otherOutputComponent = otherLink.outputNode.component
#        otherInputComponent = otherLink.inputNode.component
#
#        # gets common component shared with other link
#        if thisOutputComponent is otherOutputComponent:
#            return (thisOutputComponent, self.outputNode, otherLink.outputNode)
#        elif thisOutputComponent is otherInputComponent:
#            return (thisOutputComponent, self.outputNode, otherLink.inputNode)
#        elif thisInputComponent is otherOutputComponent:
#            return (thisInputComponent, self.inputNode, otherLink.outputNode)
#        elif thisInputComponent is otherInputComponent:
#            return (thisInputComponent, self.inputNode, otherLink.inputNode)
#        else:
#            raise Exception("Specified other link does not share a common component with this link")

class LinkSpec(object):
    def __init__(self, width=1.0, color="red", pattern=None, offset=0, \
    start_marker=False, end_marker=False, start_marker_radius=3, \
    end_marker_radius=2, start_marker_color="red", end_marker_color="blue"):
        self.width = width
        self.color = color
        self.pattern = pattern
        self.offset = offset
        self.start_marker = start_marker
        self.end_marker = end_marker
        self.start_marker_radius = start_marker_radius
        self.end_marker_radius = end_marker_radius
        self.start_marker_color = start_marker_color
        self.end_marker_color = end_marker_color

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        width = float(width)

        if width < 0:
            raise ValueError('Width must be >= 0')

        self._width = width

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        #FIXME: check for valid colors here
        self._color = color

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        if pattern is None:
            pattern = []
        else:
            pattern = list(pattern)

            # check that list is an even number (a pattern must be a series of dash-space pairs)
            if len(pattern) % 2 is not 0:
                raise Exception("Specified pattern list must contain an even number of elements")

        self._pattern = pattern

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        self._offset = float(offset)
