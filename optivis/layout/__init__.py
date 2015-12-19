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

  positionConstrainedComponents = set([])
  
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

  def arrange(self):
    # make sure there is a reference component
    if self.scene.reference is None:
      # set reference to first link's output component
      self.scene.reference = self.scene.links[0].outputNode.component
    
    ###
    # Layout and link everything
    
    # empty position-constrained components list
    self.positionConstrainedComponents = set([])
    
    # laid out links
    self.laidOutLinks = set([])
    
    # process constraints
    self.constrain()
    
    # layout constrained links
    self.layoutLinks()
    
    # now that we've constrained the positions of items, now layout unconstrained links
    self.layoutLinks()
    
    # move scene positions so that left most, topmost object is at the origin
    self.normalisePositions()
  
  def constrain(self):
    """
    Constrains bench items and checks for conflicts
    """
    
    # list of nodes already constrained
    constrainedNodes = set([])
    
    for constraint in self.scene.constraints:
      constraint.constrain(self)
      
      if len(constrainedNodes.intersection(constraint.constrainedNodes)) > 0:
        raise Exception('A constraint has constrained an already-constrained node')
      
      constrainedNodes.update(constraint.constrainedNodes)
  
  def layoutLinks(self):
    # loop over links attached to reference component, and also other links
    # attached to components to which these links attach the reference
    while len(self.laidOutLinks) < len(self.scene.links):
      for link in self.getComponentLinks(self.scene.reference):
        # recursive
        self.layoutLinkChain(link, self.scene.reference)
      
  def layoutLinkChain(self, link, referenceComponent):      
    referenceNode = None
    targetNode = None
    
    if link.inputNode.component is referenceComponent:
      referenceNode = link.inputNode
      targetNode = link.outputNode
    elif link.outputNode.component is referenceComponent:
      referenceNode = link.outputNode
      targetNode = link.inputNode
    else:
      raise Exception('Specified reference component, {0}, is not part of the specified link, {1}'.format(referenceComponent, link))
    
    targetComponent = targetNode.component
    
    if referenceComponent in self.positionConstrainedComponents and targetComponent in self.positionConstrainedComponents:
      # both component positions already constrained
      print "[Layout] Linking {0}".format(link)
      
      # TODO: check for angular constraints

      # set link start and end positions
      link.start = link.outputNode.getAbsolutePosition()
      link.end = link.inputNode.getAbsolutePosition()
      
      # set link length
      link.length = link.getSize().x
      
      # set angle from positions
      angle = (link.end - link.start).getAzimuth()
      
      # set node azimuths
      referenceNode.setAbsoluteAzimuth(angle)
      targetNode.setAbsoluteAzimuth(angle)
      
      self.laidOutLinks.add(link)
    elif targetComponent not in self.positionConstrainedComponents and link.length is not None:
      # only target component not yet positioned
      print "[Layout] Linking {0} with respect to {1}".format(link, referenceComponent)
      
      # check if target is already laid out
      if self.isFixed(targetComponent):
        print "[Layout]      WARNING: target component {0} is already laid out. Linking with straight line.".format(targetComponent)
        
        # set link start and end positions
        link.start = link.outputNode.getAbsolutePosition()
        link.end = link.inputNode.getAbsolutePosition()
        
        return
      
      # set other node azimuth first
      targetNode.setAbsoluteAzimuth(referenceNode.getAbsoluteAzimuth())
      
      # set the position of the input component
      targetNode.setAbsolutePosition(self.getTargetNodePositionRelativeToReferenceNode(link, referenceNode))
      
      # set link start and end positions
      link.start = link.outputNode.getAbsolutePosition()
      link.end = link.inputNode.getAbsolutePosition()
      
      # add components to set of constrained components
      self.positionConstrainedComponents.add(referenceComponent)
      self.positionConstrainedComponents.add(targetComponent)
      
      self.laidOutLinks.add(link)
      
      # get links to/from the target component, avoiding this one, and layout any
      # components linked to target component
      for subLink in self.getComponentLinks(targetComponent, avoid=link):
        self.layoutLinkChain(subLink, targetComponent)
    else:
      # This link is zero-length and we are attempting to link a not-yet-position-constrained
      # component. We just do nothing for now, and the recursion will automatically link this
      # component when the first condition is matched, i.e. that both components are position-
      # constrained.
      return
    
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
      if links[i] is link:
	del(links[i])
	
	return links
    
    raise Exception('Link {0} was not found in the list provided'.format(link))
  
  def getTargetNodePositionRelativeToReferenceNode(self, link, referenceNode):    
    if link.inputNode is not referenceNode and link.outputNode is not referenceNode:
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
  
  def isFixed(self, component):
    return component in self.positionConstrainedComponents

class StandardLayout(AbstractLayout):
  title = "Standard"

  def __init__(self, *args, **kwargs):    
    super(StandardLayout, self).__init__(*args, **kwargs)