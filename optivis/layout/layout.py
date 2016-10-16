# -*- coding: utf-8 -*-

"""Layout classes"""

from __future__ import unicode_literals, division

import abc

from optivis.geometry import Coordinates
from optivis.layout.scale import LinearScale

class Layout(object):
    __metaclass__ = abc.ABCMeta

    # class title (for GUI)
    title = "Abstract"

    def __init__(self, scene, scale_obj=None):
        if scale_obj is None:
            scale_obj = LinearScale()

        self.scene = scene
        self.scale_obj = scale_obj

        # empty set of linked components
        self.linked_components = set([])

    @abc.abstractmethod
    def is_fixed(self, component):
        pass

    def get_scaled_link_length(self, length):
        return self.scale_obj.get_scaled_length(length)

    def get_default_reference(self):
        """Returns a reference component to act as a default"""

        # return first link's output component
        return self.scene.links[0].output_node.component

    def get_component_links(self, component, avoid=None):
        """Returns the links attached to the specified component, optionally \
        avoiding a component"""

        # empty list of links
        links = []

        # loop over all links in the scene
        for link in self.scene.links:
            if link == avoid:
                # skip this link, because it has been requested to be avoided
                continue

            # check if link contains the component
            if link.has_component(component):
                # add to list
                links.append(link)

        return links

    def normalise_positions(self):
        """Move the position of all components such that the topmost, leftmost \
        position is the origin"""

        # get offset to apply to all components
        (lower_bounds, _) = self.scene.get_bounding_box()
        offset = lower_bounds.flip()

        for link in self.scene.links:
            link.start_pos += offset
            link.end_pos += offset

        for component in self.scene.components:
            component.position += offset

    @abc.abstractmethod
    def arrange(self):
        """Arranges the components and links in the scene"""
        pass

class StandardLayout(Layout):
    title = "Standard"

    def __init__(self, *args, **kwargs):
        super(StandardLayout, self).__init__(*args, **kwargs)

    def arrange(self):
        # make sure there is a reference component
        if self.scene.reference is None:
            # use the default reference
            self.scene.reference = self.get_default_reference()

        # empty linked components list
        self.linked_components = set([])

        # layout links
        self.layout_links()

        # translate scene top left edge to origin
        self.normalise_positions()

    def layout_links(self):
        """Lays out components using the length and angles of their links"""

        # loop over links attached to reference component, and also other links
        # attached to components to which these links attach the reference
        for link in self.get_component_links(self.scene.reference):
            # recursive
            self.layout_link_chain(link, self.scene.reference)

    def layout_link_chain(self, link, reference_component):
        print "[Layout] Linking {0} with respect to {1}".format(link, \
        reference_component)

        # work out which node is the target and which is the reference
        if link.output_node.component == reference_component:
            # output node is reference
            reference_node = link.output_node
            target_node = link.input_node
        elif link.input_node.component == reference_component:
            # input node is reference
            reference_node = link.input_node
            target_node = link.output_node
        else:
            raise Exception("Reference component {0} is not part of \
{1}".format(referenceComponent, link))

        # get target component
        target_component = target_node.component

        # check if target is already laid out
        if self.is_fixed(target_component):
            print "[Layout] WARNING: target component {0} is already laid out. \
Linking with straight line.".format(target_component)

            # set link start and end positions
            link.start_pos = link.output_node.get_absolute_pos()
            link.end_pos = link.input_node.get_absolute_pos()

            # we're done
            return

        # first set target node azimuth to be opposite the reference's
        target_node.set_absolute_azimuth( \
        reference_node.get_absolute_output_azimuth() + 180)

        # then set the position of the target component
        target_node.set_absolute_node_pos(self.get_target_node_pos(link, \
        reference_node))

        # set link start and end positions
        link.start_pos = link.output_node.get_absolute_pos()
        link.end_pos = link.input_node.get_absolute_pos()

        # add components to set of constrained components
        self.linked_components.add(reference_component)
        self.linked_components.add(target_component)

        # loop over links to/from the target component, avoiding this one
        for this_link in self.get_component_links(target_component, avoid=link):
            # layout any components linked to target component
            self.layout_link_chain(this_link, target_component)

    def get_target_node_pos(self, link, reference_node):
        if link.input_node != reference_node \
        and link.output_node != reference_node:
            raise Exception("Reference node {0} is not a node of \
{1}".format(reference_node, link))

        # absolute position of pivot point
        pivot_position = reference_node.get_absolute_pos()

        # angle
        pivot_angle = reference_node.get_absolute_output_azimuth()

        # position of component with respect to pivot
        relative_position = Coordinates( \
        self.get_scaled_link_length(link.length), 0).rotate(pivot_angle)

        # absolute position of component
        return pivot_position + relative_position

    def is_fixed(self, component):
        return component in self.linked_components
