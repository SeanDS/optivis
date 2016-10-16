# -*- coding: utf-8 -*-

"""Component classes"""

from __future__ import unicode_literals, division

import os
import math
import abc

from optivis.bench.items import BenchItem
from optivis.bench.nodes import Node
from optivis.geometry import Coordinates

class Component(BenchItem):
    # set abstract class
    __metaclass__ = abc.ABCMeta

    # SVG directory
    svg_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

    # TODO: component name should be used instead of filename
    # TODO: size should be read from SVG file
    def __init__(self, filename, size, name="", azimuth=0, aoi=0, \
    position=None, tooltip=None, *args, **kwargs):
        """Instantiates a component

        :param azimuth: the angle this component has with respect to the \
        positive x direction in the global coordinate system
        :param aoi: angle of incidence of light on the component, defined with \
        respect to the positive x direction, used by nodes to calculate the \
        reflected light direction
        """

        # set position if not specified
        if position is None:
            # use origin
            position = Coordinates.origin()

        # set properties
        self.filename = filename
        self.size = size
        self.name = name
        self.azimuth = azimuth
        self.aoi = aoi
        self.position = position
        self.tooltip = tooltip

        # create node list
        self.nodes = []

        # call parent constructor
        super(Component, self).__init__(*args, **kwargs)

    def __unicode__(self):
        """String representation of the component"""

        # use component name
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of the component"""

        return unicode(self)

    def __eq__(self, other):
        """Check if the specified other component is equal to this one"""

        # compare properties
        return self.__dict__ == other.__dict__

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = unicode(filename)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        # check size coordinates are positive
        if not size.is_positive():
            raise Exception("Size dimensions must be positive")

        self._size = size

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = unicode(name)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        # coerce azimuth between 0 and 360
        self._azimuth = Component._coerce_angle(azimuth)

    @property
    def aoi(self):
        return self._aoi

    @aoi.setter
    def aoi(self, aoi):
        # coerce azimuth between 0 and 360
        self._aoi = Component._coerce_angle(aoi)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = Coordinates(position)

    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, tooltip):
        self._tooltip = unicode(tooltip)

    @staticmethod
    def _coerce_angle(angle):
        """Coerces an angle between 0 and 360

        :param angle: angle to coerce
        """

        return float(angle) % 360

    def get_label_origin(self):
        """Coordinates labels should be placed with respect to"""

        # use the component's position
        return self.position

    def get_label_azimuth(self):
        """Azimuth labels should be placed with respect to"""

        # return the component's azimuth
        return self.azimuth

    def get_bounding_box(self):
        """Coordinates of item's edges closest to and furthest away from \
        origin

        :return: (lower, upper) bounds
        """

        # get nominal corner positions
        top_left = self.size * Coordinates(-0.5, -0.5)
        top_right = self.size * Coordinates(0.5, -0.5)
        bottom_left = self.size * Coordinates(-0.5, 0.5)
        bottom_right = self.size * Coordinates(0.5, 0.5)

        # rotate corners by azimuth
        top_left = top_left.rotate(self.azimuth)
        top_right = top_right.rotate(self.azimuth)
        bottom_left = bottom_left.rotate(self.azimuth)
        bottom_right = bottom_right.rotate(self.azimuth)

        # collect x and y coordinates into separate lists
        x_coords = [top_left.x, top_right.x, bottom_left.x, bottom_right.x]
        y_coords = [top_left.y, top_right.y, bottom_left.y, bottom_right.y]

        # find min and max coordinates to form bounds
        min_bound = Coordinates(min(x_coords), min(y_coords))
        max_bound = Coordinates(max(x_coords), max(y_coords))

        # return bounds with respect to global position
        return self.position + min_bound, self.position + max_bound

    def get_node(self, name):
        """Gets the node with the given name

        :param name: name to search for
        """

        for node in self.nodes:
            if node.name == name:
                return node

        raise Exception("No node with name {0} found".format(name))

    def add_node(self, *args, **kwargs):
        """Adds a node to the component

        Accepts arguments for Node
        """

        # add new node, setting the node's component to this
        self.nodes.append(Node(*args, component=self, **kwargs))

    def get_aoi_for_constrained_node_angle(self, node1, node2, angle):
        return (angle - node1.aoi_offset - node2.aoi_offset) \
        / (node1.aoi_multiplier - node2.aoi_multiplier)

class Source(Component):
    """Represents a component with 1 node"""

    __metaclass__ = abc.ABCMeta

class Laser(Source):
    def __init__(self, *args, **kwargs):
        filename = "c-laser1.svg"
        size = Coordinates(62, 46)

        # call parent
        super(Laser, self).__init__(filename=filename, size=size, *args, \
        **kwargs)

        # add output node
        self.add_node(name="out", position=Coordinates(31, 0))

class SteeringMirror(Component):
    def __init__(self, *args, **kwargs):
        filename = "b-mir.svg"
        size = Coordinates(11, 29)

        super(SteeringMirror, self).__init__(filename=filename, size=size, \
        *args, **kwargs)

        self.add_node(name="a", position=Coordinates(5.5, 0))
        self.add_node(name="b", position=Coordinates(5.5, 0))

class Mirror(Component):
    def __init__(self, *args, **kwargs):
        filename = "b-cav-mir.svg"
        size = Coordinates(11, 29)

        # call parent
        super(Mirror, self).__init__(filename=filename, size=size, \
        *args, **kwargs)

        self.add_node(name="a", position=Coordinates(5.5, 0))
        self.add_node(name="b", position=Coordinates(5.5, 0))
        self.add_node(name="c", position=Coordinates(-5.5, 0), aoi_offset=180)
        self.add_node(name="d", position=Coordinates(-5.5, 0), aoi_offset=180)

class BeamSplitter(Component):
    def __init__(self, aoi=45, *args, **kwargs):
        filename = "b-bsp.svg"
        size = Coordinates(11, 29)

        super(BeamSplitter, self).__init__(filename=filename, size=size, \
        aoi=aoi, *args, **kwargs)

        self.add_node(name="a", position=Coordinates(5.5, 0))
        self.add_node(name="b", position=Coordinates(5.5, 0))
        self.add_node(name="c", position=Coordinates(-5.5, 0), aoi_offset=180)
        self.add_node(name="d", position=Coordinates(-5.5, 0), aoi_offset=180)
