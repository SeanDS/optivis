# -*- coding: utf-8 -*-

"""Node classes"""

from __future__ import unicode_literals, division

from optivis.geometry import Coordinates

class Node(object):
    def __init__(self, name, component, position, aoi_offset=0):
        """Instantiates a Node

        :param name: name of the node
        :param component: component this node is associated with
        :param position: position of node, defined with respect to the \
        component's center
        :param aoi_offset: azimuthal offset this node's outgoing light has \
        with respect to the component's angle of incidence
        """

        # set properties
        self.name = name
        self.component = component
        self.position = position
        self.aoi_offset = aoi_offset

    def __unicode__(self):
        """String representation of this node"""

        return "{0}::{1}".format(self.component, self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of this node"""

        return unicode(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = unicode(name)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = Coordinates(position)

    @property
    def aoi_offset(self):
        return self._aoi_offset

    @aoi_offset.setter
    def aoi_offset(self, aoi_offset):
        self._aoi_offset = float(aoi_offset)

    def get_relative_output_azimuth(self):
        """Get azimuth of node in the output direction with respect to the \
        component"""

        return self.component.aoi + self.aoi_offset

    def get_absolute_output_azimuth(self):
        """Get azimuth of node in the output direction with respect to the \
        global coordinate system"""

        return self.component.azimuth + self.get_relative_output_azimuth()

    def get_relative_pos(self):
        """Get position of node with respect to component's center"""

        return self.position.rotate(self.component.azimuth)

    def get_absolute_pos(self):
        """Get position of node in global coordinate system"""

        return self.component.position + self.get_relative_pos()

    def set_absolute_node_pos(self, absolute_pos):
        """Set position of the component based on the specified position of \
        the node

        :param absolute_pos: absolute position of the node
        """

        # component position
        self.component.position = absolute_pos - self.get_relative_pos()

    def set_absolute_azimuth(self, absolute_azimuth):
        """Set azimuth of the component based on the specified azimuth of \
        the node"""

        self.component.azimuth = absolute_azimuth \
        - self.get_relative_output_azimuth()
