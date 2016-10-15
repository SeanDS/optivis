from __future__ import unicode_literals, division

import abc
import math

import optivis
import optivis.geometry
import optivis.bench.components
import optivis.bench.links
import scale

class AbstractLayout(object):
    __metaclass__ = abc.ABCMeta

    title = "Abstract"

    # set of components that are part of links
    linkedComponents = set([])

    def __init__(self, scene, scaleFunc=None):
        if scaleFunc is None:
            scaleFunc = scale.ScaleFunction()

        self.scene = scene
        self.scaleFunc = scaleFunc

    @property
    def scene(self):
        return self.__scene

    @scene.setter
    def scene(self, scene):
        if not isinstance(scene, optivis.scene.Scene):
            raise Exception('Specified scene is not of type optivis.scene.Scene')

        self.__scene = scene

    @property
    def scaleFunc(self):
        return self.__scaleFunc

    @scaleFunc.setter
    def scaleFunc(self, scaleFunc):
        if not isinstance(scaleFunc, scale.ScaleFunction):
            raise Exception('Specified scale function is not of type ScaleFunction')

        self.__scaleFunc = scaleFunc

    @abc.abstractmethod
    def isFixed(self, component):
        pass

    def arrange(self):
        # make sure there is a reference component
        if self.scene.reference is None:
            # set reference to first link's output component
            self.scene.reference = self.scene.links[0].outputNode.component

        ###
        # Layout and link everything

        # empty linked components list
        self.linkedComponents = set([])

        # layout links
        self.layoutLinks()

        # move scene positions so that left most, topmost object is at the origin
        self.normalisePositions()

    def layoutLinks(self):
        # loop over links attached to reference component, and also other links
        # attached to components to which these links attach the reference
        for link in self.getComponentLinks(self.scene.reference):
            # recursive
            self.layoutLinkChain(link, self.scene.reference)

    def layoutLinkChain(self, link, referenceComponent):
        print "[Layout] Linking {0} with respect to {1}".format(link, referenceComponent)

        referenceNode = None
        targetNode = None

        if link.inputNode.component == referenceComponent:
            referenceNode = link.inputNode
            targetNode = link.outputNode
        elif link.outputNode.component == referenceComponent:
            referenceNode = link.outputNode
            targetNode = link.inputNode
        else:
            raise Exception('Specified reference component, {0}, is not part of the specified link, {1}'.format(referenceComponent, link))

        targetComponent = targetNode.component

        # check if target is already laid out
        if self.isFixed(targetComponent):
            print "[Layout]      WARNING: target component {0} is already laid out. Linking with straight line.".format(targetComponent)

            # set link start and end positions
            link.start = link.outputNode.getAbsolutePosition()
            link.end = link.inputNode.getAbsolutePosition()

            return

        # set other node azimuth first
        targetNode.setAbsoluteAzimuth(referenceNode.getAbsoluteAzimuth())

        # then set the position of the input component
        targetNode.setAbsolutePosition(self.getTargetNodePositionRelativeToReferenceNode(link, referenceNode))

        # set link start and end positions
        link.start = link.outputNode.getAbsolutePosition()
        link.end = link.inputNode.getAbsolutePosition()

        # add components to set of constrained components
        self.linkedComponents.add(referenceComponent)
        self.linkedComponents.add(targetComponent)

        # get links to/from the target component, avoiding this one
        subLinks = self.getComponentLinks(targetComponent, avoid=link)

        # layout any components linked to target component
        for subLink in subLinks:
            self.layoutLinkChain(subLink, targetComponent)

    def getComponentLinks(self, component, avoid=None):
        links = []

        for link in self.scene.links:
            if link == avoid:
                # skip this link, because it has been requested to be avoided
                continue

            if link.hasComponent(component):
                links.append(link)

        return links

    def removeLinkFromList(self, link, links):
        for i in range(0, len(links)):
            if links[i] == link:
                del(links[i])

                return links

        raise Exception('Link {0} was not found in the list provided'.format(link))

    def getTargetNodePositionRelativeToReferenceNode(self, link, referenceNode):
        if link.inputNode != referenceNode and link.outputNode != referenceNode:
            raise Exception('Specified reference node, {0}, is not a node in the specified link, {1}'.format(referenceNode, link))

        # absolute position of pivot point
        pivotPosition = referenceNode.getAbsolutePosition()

        # angle
        pivotAngle = referenceNode.getAbsoluteAzimuth()

        # position of component with respect to pivot
        relativePosition = optivis.geometry.Coordinates(self.getScaledLinkLength(link.length), 0).rotate(pivotAngle)

        if isinstance(referenceNode, optivis.bench.nodes.InputNode):
            # flip position because we're going 'backwards' from input to output
            relativePosition = relativePosition.flip()

        # absolute position of component
        return pivotPosition.translate(relativePosition)

    def normalisePositions(self):
        """
        Move the position of all components such that the topmost, leftmost position is the origin
        """

        # get offset to apply to all components
        (lowerBounds, upperBounds) = self.scene.getBoundingBox()
        offset = lowerBounds.flip()

        for link in self.scene.links:
            link.start = link.start.translate(offset)
            link.end = link.end.translate(offset)

        for component in self.scene.getComponents():
            component.position = component.position.translate(offset)

    def getScaledLinkLength(self, length):
        return self.scaleFunc.getScaledLength(length)

class StandardLayout(AbstractLayout):
    title = "Standard"

    def __init__(self, *args, **kwargs):
        super(StandardLayout, self).__init__(*args, **kwargs)

    def isFixed(self, component):
        return component in self.linkedComponents

class ConstrainedLayout(AbstractLayout):
    title = "Constrained"

    def __init__(self, *args, **kwargs):
        super(ConstrainedLayout, self).__init__(*args, **kwargs)

    # override
    def layoutLinks(self, *args, **kwargs):
        # first constrain angles of optics
        for constraint in self.scene.constraints:
            constraint.constrain()

        super(ConstrainedLayout, self).layoutLinks(*args, **kwargs)

    def isFixed(self, component):
        if component in self.linkedComponents:
            # check if any constraints constrain this component
            for constraint in self.scene.constraints:
                if constraint.constrains(component):
                    print "{0} is fixed".format(component)
                    return True

            # check if this is attached to a constrained component
            for link in self.scene.links:
                if link.hasComponent(component):
                    # this link is attached to the component
                    # is the other side constrained?
                    for thisComponent in link.getComponents():
                        if thisComponent is not component:
                            # this is the other side of the link
                            for constraint in self.scene.constraints:
                                if constraint.constrains(thisComponent):
                                    print "{0} is fixed because it's attached to fixed component {1}".format(component, thisComponent)
                                    return True

        print "{0} is not fixed".format(component)

        return False
