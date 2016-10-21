# -*- coding: utf-8 -*-

"""Node classes"""

from __future__ import unicode_literals, division

import math
import logging

from optivis.geometry import Vector

class Node(object):
    def __init__(self, name, component, aoi_coeff=1, aoi_offset=0, \
    nom_pos=None):
        """Instantiates a Node

        :param name: name of the node
        :param component: component this node is associated with
        :param aoi_coeff: coefficient to apply to angle of incidence when \
        calculating reflection
        :param aoi_offset: azimuthal offset this node's outgoing light has \
        with respect to the component's angle of incidence
        :param nom_pos: nominal position of node, defined with respect to the \
        component's center
        """

        # set properties
        self.name = name
        self.component = component
        self.aoi_coeff = aoi_coeff
        self.aoi_offset = aoi_offset
        self.nom_pos = nom_pos

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
    def nom_pos(self):
        return self._nom_pos

    @nom_pos.setter
    def nom_pos(self, nom_pos):
        self._nom_pos = Vector(nom_pos)

    @property
    def aoi_coeff(self):
        return self._aoi_coeff

    @aoi_coeff.setter
    def aoi_coeff(self, aoi_coeff):
        self._aoi_coeff = float(aoi_coeff)

    @property
    def aoi_offset(self):
        return self._aoi_offset

    @aoi_offset.setter
    def aoi_offset(self, aoi_offset):
        self._aoi_offset = float(aoi_offset)

    def get_position(self):
        """Get the position of the node, adjusted due to linked nodes if \
        necessary"""

        # get the position of the node as dictated by the component
        return self.component.get_node_pos(self)

    def get_relative_output_azimuth(self):
        """Get azimuth of node in the output direction with respect to the \
        component"""

        # get component aoi
        aoi = self.component.aoi

        # default value for aoi
        if aoi is None:
            logging.getLogger("nodes").info("The aoi for %s is undefined, so \
tentatively using 0", self.component)

            aoi = 0

        return self.aoi_coeff * aoi + self.aoi_offset

    def get_absolute_output_azimuth(self):
        """Get azimuth of node in the output direction with respect to the \
        global coordinate system"""

        return self.component.azimuth + self.get_relative_output_azimuth()

    def get_relative_pos(self):
        """Get position of node with respect to component's center"""

        return self.get_position().rotate(self.component.azimuth)

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
