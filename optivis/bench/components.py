# -*- coding: utf-8 -*-

"""Component classes"""

from __future__ import unicode_literals, division

import os
import math
import abc

from optivis.bench.items import BenchItem
from optivis.bench.nodes import Node
from optivis.geometry import Vector

class Component(BenchItem):
    # set abstract class
    __metaclass__ = abc.ABCMeta

    # SVG directory
    svg_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

    # TODO: component name should be used instead of filename
    # TODO: size should be read from SVG file
    def __init__(self, filename, size, name="", azimuth=0, aoi=None, \
    position=None, tooltip=None, *args, **kwargs):
        """Instantiates a component

        :param filename: filename for the component's SVG drawing
        :param size: :class:`~optivis.geometry.Vector` object \
        representing the size of the SVG drawing (in pixels)
        :param name: component name
        :param azimuth: angle this component has with respect to the positive \
        x direction in the global coordinate system
        :param aoi: (optional) angle of incidence of light on the component, \
        defined with respect to the positive x direction, used by nodes to \
        calculate the reflected light direction; if None then the layout \
        manager will decide what angle to use based on the context
        :param position: :class:`~optivis.geometry.Vector` representing \
        the default position
        :param tooltip: tooltip text for GUI
        """

        # set position if not specified
        if position is None:
            # use origin
            position = Vector.origin()

        # use name as tooltip if not specified
        if tooltip is None:
            tooltip = name

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
        if aoi is None:
            # set None
            self._aoi = None

            return

        # coerce azimuth between 0 and 360
        self._aoi = Component._coerce_angle(aoi)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = Vector(position)

    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, tooltip):
        if tooltip is None:
            self._tooltip = ""

            return

        self._tooltip = unicode(tooltip)

    @staticmethod
    def _coerce_angle(angle):
        """Coerces an angle between 0 and 360

        :param angle: angle to coerce
        """

        return float(angle) % 360

    def get_label_origin(self):
        """Vector labels should be placed with respect to"""

        # use the component's position
        return self.position

    def get_label_azimuth(self):
        """Azimuth labels should be placed with respect to"""

        # return the component's azimuth
        return self.azimuth

    def get_bounding_box(self):
        """Vector of item's edges closest to and furthest away from \
        origin

        :return: (lower, upper) bounds
        """

        # get nominal corner positions
        top_left = self.size * Vector(-0.5, -0.5)
        top_right = self.size * Vector(0.5, -0.5)
        bottom_left = self.size * Vector(-0.5, 0.5)
        bottom_right = self.size * Vector(0.5, 0.5)

        # rotate corners by azimuth
        top_left = top_left.rotate(self.azimuth)
        top_right = top_right.rotate(self.azimuth)
        bottom_left = bottom_left.rotate(self.azimuth)
        bottom_right = bottom_right.rotate(self.azimuth)

        # collect x and y coordinates into separate lists
        x_coords = [top_left.x, top_right.x, bottom_left.x, bottom_right.x]
        y_coords = [top_left.y, top_right.y, bottom_left.y, bottom_right.y]

        # find min and max coordinates to form bounds
        min_bound = Vector(min(x_coords), min(y_coords))
        max_bound = Vector(max(x_coords), max(y_coords))

        # return bounds with respect to global position
        return self.position + min_bound, self.position + max_bound

    def has_node(self, name):
        """Checks if the node with the given name exists as part of this \
        component

        :param name: node name to search for
        """

        for node in self.nodes:
            if node.name == name:
                return True

        return False

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

        Accepts arguments for Node.

        :return: newly added node
        """

        # create new node
        node = Node(*args, component=self, **kwargs)

        # set the node's component to this
        self.nodes.append(node)

        return node

    def get_aoi_for_constrained_node_angle(self, node1, node2, angle):
        return (angle - node1.aoi_offset - node2.aoi_offset) \
        / (node1.aoi_multiplier - node2.aoi_multiplier)

    def get_node_pos(self, node):
        """Get the position of the specified node

        This is overridden by subclasses.

        :param node: node to place
        """

        return node.nom_pos

    def aoi_is_explicit(self):
        """Whether this component's angle of incidence is explicitly defined"""

        # None represents an unconstrained aoi
        return self.aoi is not None

class Source(Component):
    """Represents a component with 1 node"""

    __metaclass__ = abc.ABCMeta

class Laser(Source):
    def __init__(self, *args, **kwargs):
        filename = "c-laser1.svg"
        size = Vector(62, 46)

        # call parent
        super(Laser, self).__init__(filename=filename, size=size, *args, \
        **kwargs)

        # add output node
        self.add_node(name="out", nom_pos=Vector(31, 0))

class RefractiveMedium(Component):
    """Component with a refractive index"""

    # refractive index of vacuum around components
    vacuum_n = 1

    def __init__(self, n=1.35, *args, \
    **kwargs):
        """Instantiates a refractive medium

        :param n: refractive index of medium
        """

        super(RefractiveMedium, self).__init__(*args, **kwargs)

        self.n = n

        # default lists of shared nodes (populated once nodes are added)
        self.share_x = []
        self.share_y = []

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, n):
        n = float(n)

        if n < 0:
            raise Exception("Refractive index must be > 0")

        # check that n is >= vacuum n
        if n < self.vacuum_n:
            raise Exception("Refractive index must be > {0} \
(vacuum index)".format(self.vacuum_n))

        self._n = n

    def set_node_reference(self, target_node, reference_node, axis):
        """Adds a shared node

        :param target_node: target_node
        :param reference_node: reference node
        :param axis: axis to share
        """

        # validate axis
        if axis not in ["x", "y", "both"]:
            raise Exception("Specified axis must be either \"x\", \"y\" or \
\"both\"")

        # check nodes aren't the same
        if reference_node == target_node:
            raise Exception("Share list nodes cannot be identical")

        # check nodes share the same component
        if reference_node.component != target_node.component:
            raise Exception("Share list nodes must be attached to the same \
component")

        if axis == "x" or axis == "both":
            self.share_x.append([reference_node, target_node])

        if axis == "y" or axis == "both":
            self.share_y.append([reference_node, target_node])

    def _get_node_x_reference(self, node):
        for sequence in self.share_x:
            if sequence[1] == node:
                return sequence[0]

    def _get_node_y_reference(self, node):
        for sequence in self.share_y:
            if sequence[1] == node:
                return sequence[0]

    def get_node_pos(self, node):
        """Get the position of the specified node

        This takes into account the effect of the position of any reference \
        nodes defined for the specified node.

        :param node: node to place
        """

        # nominal position at zero aoi
        pos = super(RefractiveMedium, self).get_node_pos(node)

        # x and y references (None if not defined)
        x_ref_node = self._get_node_x_reference(node)
        y_ref_node = self._get_node_y_reference(node)

        # offset position if necessary
        if x_ref_node:
            # angle of incidence in medium
            aoi = self._snell_refraction( \
            x_ref_node.get_relative_output_azimuth())

            # distance along y-axis between nodes
            length = pos.y - x_ref_node.nom_pos.y

            # refract the node based on the length and angle of incidence
            pos.x = x_ref_node.nom_pos.x \
            + length * math.tan(math.degrees(aoi))

        # offset position if necessary
        if y_ref_node:
            # angle of incidence in medium (radians)
            aoi = self._snell_refraction( \
            y_ref_node.get_relative_output_azimuth())

            # distance along x-axis between nodes
            length = pos.x - y_ref_node.nom_pos.x

            # refract the node based on the length and angle of incidence
            pos.y = y_ref_node.nom_pos.y + length * math.tan(aoi)

        return pos

    def _snell_refraction(self, low_n_aoi):
        """Calculates the angle with respect to the normal inside the material

        :param low_n_aoi: angle of incidence of light beam in outer material \
        with respect to normal, in radians
        """

        return math.asin(self.vacuum_n * math.sin(math.radians(low_n_aoi)) \
        / self.n)

class SteeringMirror(RefractiveMedium):
    def __init__(self, *args, **kwargs):
        filename = "b-mir.svg"
        size = Vector(11, 29)

        super(SteeringMirror, self).__init__(filename=filename, size=size, \
        *args, **kwargs)

        self.add_node(name="a", nom_pos=Vector(5.5, 0))
        self.add_node(name="b", nom_pos=Vector(5.5, 0), aoi_coeff=-1)

class Mirror(RefractiveMedium):
    def __init__(self, *args, **kwargs):
        filename = "b-cav-mir.svg"
        size = Vector(11, 29)

        # call parent
        super(Mirror, self).__init__(filename=filename, size=size, \
        *args, **kwargs)

        node_a = self.add_node(name="a", nom_pos=Vector(5.5, 0))
        node_b = self.add_node(name="b", nom_pos=Vector(5.5, 0), \
        aoi_coeff=-1)
        node_c = self.add_node(name="c", nom_pos=Vector(-5.5, 0), \
        aoi_offset=180)
        node_d = self.add_node(name="d", nom_pos=Vector(-5.5, 0), \
        aoi_coeff=-1, aoi_offset=180)

        # set reference nodes
        self.set_node_reference(node_c, node_a, "y")
        self.set_node_reference(node_d, node_b, "y")

class BeamSplitter(RefractiveMedium):
    def __init__(self, aoi=45, *args, **kwargs):
        filename = "b-bsp.svg"
        size = Vector(11, 29)

        super(BeamSplitter, self).__init__(filename=filename, size=size, \
        aoi=aoi, *args, **kwargs)

        node_a = self.add_node(name="a", nom_pos=Vector(5.5, 0))
        node_b = self.add_node(name="b", nom_pos=Vector(5.5, 0), \
        aoi_coeff=-1)
        node_c = self.add_node(name="c", nom_pos=Vector(-5.5, 0), \
        aoi_offset=180)
        node_d = self.add_node(name="d", nom_pos=Vector(-5.5, 0), \
        aoi_coeff=-1, aoi_offset=180)

        # set reference nodes
        self.set_node_reference(node_c, node_a, "y")
        self.set_node_reference(node_d, node_b, "y")
