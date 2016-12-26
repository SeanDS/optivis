# -*- coding: utf-8 -*-

"""Layout classes"""

from __future__ import unicode_literals, division

import abc
import logging

from optivis.geometry import Vector
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
    def _position_is_constrained(self, component):
        pass

    def get_scaled_link_length(self, length):
        return self.scale_obj.get_scaled_length(length)

    def get_default_reference(self):
        """Returns a reference component to act as a default"""

        # return first link's output component
        return self.scene.links[0].output_node.component

    def get_component_links(self, component, avoid=None):
        """Returns the links attached to the specified component, optionally \
        avoiding a link"""

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

    def get_linked_components(self, component):
        components = []

        for link in self.get_component_links(component):
            components.append(link.get_other_component(component))

        return components

    def _get_cyclic_links(self):
        """Returns a list of links in the system that are cyclic"""

        return [link for link in self.scene.links if self._link_is_cyclic(link)]

    def _get_cyclic_nodes(self, link):
        """Gets a list of nodes that are part of a cycle

        :param link: link in a cycle to get nodes for
        """

        # get cyclic test and its path
        (is_cyclic, path) = self._link_cycle(link)

        if not is_cyclic:
            raise Exception("Specified link is not cyclic")

        nodes = set([])

        for link in path:
            nodes.add(link.output_node)
            nodes.add(link.input_node)

        return list(nodes)

    def _link_is_cyclic(self, link):
        """Checks if the specified link is part of a cycle (it is connected \
        back to itself via some other links)

        :param link: link to check
        """

        (is_cyclic, _) = self._link_cycle(link)

        return is_cyclic

    def _link_cycle(self, link):
        """Returns whether the specified link is cyclic, and the path taken in
        arriving at that conclusion

        Based on https://codereview.stackexchange.com/questions/86021/check-if-a-directed-graph-contains-a-cycle.

        :param link: link to check
        """

        # set for links visited by the recursion
        path = set()

        # set for visited links
        visited = set()

        def visit(this_link):
            if this_link in visited:
                return False

            visited.add(this_link)
            path.add(this_link)

            for neighbour_link in self.get_component_links( \
            this_link.output_node.component, this_link):
                if neighbour_link in path or visit(neighbour_link):
                    return True

            path.remove(this_link)

            return False

        return visit(link), path

    def normalise_positions(self):
        """Move the position of all components such that the topmost, leftmost \
        position is the origin"""

        # get offset to apply to all components
        (lower_bounds, _) = self.scene.get_bounding_box()
        offset = -lower_bounds

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
        """Arrange the scene

        The arrangement algorithm is complicated. Components can have specified
        angles of incidence and links can have specified lengths, meaning that
        some components can be laid out using this information. After that,
        though, some components cannot be individually laid out. If there are
        cyclic component connections, such as a beam splitter connected back to
        itself via some mirrors, then at least one of those connections will
        have to be made between two already constrained components. The second
        part of the algorithm therefore looks for sets of cyclic nodes and
        identifies their type from the lack of certain constraints. With this
        information it is possible to assign link lengths and component angles
        of incidence. This process is iteratively applied to the cyclic
        connections until the scene is fully laid out with every component
        having a defined angle of incidence and every link having a defined
        length.
        """

        # make sure there is a reference component
        if self.scene.reference is None:
            # use the default reference
            self.scene.reference = self.get_default_reference()

        # empty linked components set
        self.linked_components = set([])

        # layout links
        self._layout_links()

        # translate scene top left edge to origin
        self.normalise_positions()

    def _layout_links(self):
        """Layout links in the scene

        The first pass recursively lays out links that have explicitly defined
        lengths so that component positions are constrained. The second pass
        then lays out links that have no defined length, since there are now
        constrained component positions.
        """

        # loop over links attached to reference component, and also other links
        # attached to components to which these links attach the reference
        for link in self._get_defined_length_links():
            # recursive
            self._layout_explicit_link_chain(link, self.scene.reference)

        # find cyclic links
        for link in self._get_cyclic_links():
            # get nodes that are part of a cycle
            nodes = self._get_cyclic_nodes(link)

            print "Cyclic link {0} contains nodes: {1}".format(link, ", ".join([unicode(node) for node in nodes]))

        # loop over the undefined length links
        for link in self._get_undefined_length_links():
            # recursive
            self._layout_implicit_link(link)

    def _get_defined_length_links(self):
        """Returns a list of links that have a defined length"""

        return [link for link in self.get_component_links(self.scene.reference) \
        if link.length is not None]

    def _get_undefined_length_links(self):
        """Returns a list of links that have no defined length"""

        return [link for link in self.scene.links if link.length is None]

    def _layout_explicit_link_chain(self, link, reference_component):
        """Lays out the specified link, and links of the target component, \
        skipping links with no defined length

        :param link: link to start with
        """

        if link.length is None:
            logging.getLogger("layout").debug("Skipping link with undefined \
length %s", link)

            return

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
{1}".format(reference_component, link))

        # get target component
        target_component = target_node.component

        # check if target is already laid out
        if self._position_is_constrained(target_component):
            logging.getLogger("layout").info("Skipping link as the target \
component %s is already positionally constrained", target_component)

            return

        # first set target node azimuth to be opposite the reference's
        target_node.set_absolute_azimuth( \
        reference_node.get_absolute_output_azimuth() + 180)

        # then set the position of the target component
        target_node.set_absolute_node_pos(self._get_target_node_pos(link, \
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
            self._layout_explicit_link_chain(this_link, target_component)

    def _layout_implicit_link(self, link):
        """Lays out the specified link, and links of the target component, \
        specifying undefined link lengths if necessary

        :param link: link to start with
        """

        if link.length is not None:
            logging.getLogger("layout").debug("Skipping link with defined \
length %s", link)

            return

        print "[Layout] Linking {0}".format(link)

        # choose the reference to be the output component
        reference_node = link.output_node
        target_node = link.input_node

        # get reference and target components
        reference_component = reference_node.component
        target_component = target_node.component

        # check if target is already laid out
        if self._position_is_constrained(target_component):
            logging.getLogger("layout").info("Target component %s is already \
positionally constrained", target_component)

            # if the link length and component angles of incidence aren't
            # constrained, we can still lay it out
            if not target_component.aoi_is_explicit():
                # target can be rotated, but can the reference?
                if not reference_component.aoi_is_explicit():
                    # both target and reference can be rotated, so set the link
                    # length
                    logging.getLogger("layout").info("Both target and \
reference can be rotated; setting link length and component azimuths")

                    # calculate the vector between the two nodes
                    link_vector = link.input_node.get_absolute_pos() \
                    - link.output_node.get_absolute_pos()

                    # set the length between the target and reference
                    link.length = link_vector.length
                else:
                    raise Exception("uuuh")
            else:
                # link with a straight line
                logging.getLogger("layout").error("Target cannot be rotated \
and/or the link length cannot be changed to allow this link; link violates \
physics!")

                # set link start and end positions regardless of aoi
                link.start_pos = link.output_node.get_absolute_pos()
                link.end_pos = link.input_node.get_absolute_pos()

                # we're done
                return

        # set link start and end positions
        link.start_pos = link.output_node.get_absolute_pos()
        link.end_pos = link.input_node.get_absolute_pos()

        # add components to set of constrained components
        self.linked_components.add(reference_component)
        self.linked_components.add(target_component)

    def _get_target_node_pos(self, link, reference_node):
        if link.input_node != reference_node \
        and link.output_node != reference_node:
            raise Exception("Reference node {0} is not a node of \
{1}".format(reference_node, link))

        # absolute position of pivot point
        pivot_position = reference_node.get_absolute_pos()

        # angle
        pivot_angle = reference_node.get_absolute_output_azimuth()

        # position of component with respect to pivot
        relative_position = Vector( \
        self.get_scaled_link_length(link.length), 0).rotate(pivot_angle)

        # absolute position of component
        return pivot_position + relative_position

    def _position_is_constrained(self, component):
        return component in self.linked_components
