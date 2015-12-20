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
  
  # laid out links
  laidOutLinks = set([])

  distanceConstrainedNodes = set([])
  angleConstrainedComponents = set([])
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
    
    # constrain the reference component
    self.positionConstrainedComponents.add(self.scene.reference)
    self.angleConstrainedComponents.add(self.scene.reference)
    
    # set zero position
    # FIXME: make reference a node
    self.scene.reference.outputNodes[0].setAbsolutePosition(optivis.geometry.Coordinates(0, 0))
    
    ###
    # Layout and link everything
    
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
    
    for constraint in self.scene.constraints:
      constraint.constrain(self)
      
      if len(self.distanceConstrainedNodes.intersection(constraint.distanceConstrainedNodes)) > 0:
        raise Exception('A constraint has position-constrained an already-position-constrained node')
      
      if len(self.angleConstrainedComponents.intersection(constraint.angleConstrainedComponents)) > 0:
        raise Exception('A constraint has angle-constrained an already-angle-constrained component')
      
      self.distanceConstrainedNodes.update(constraint.distanceConstrainedNodes)
      self.angleConstrainedComponents.update(constraint.angleConstrainedComponents)
  
  def layoutLinks(self):
    # solve constraints
    while len(self.positionConstrainedComponents) < len(self.scene.getComponents()):
      for link in self.scene.links:
        self.solveConstraints(link)
    
    # set link positions
    self.setLinkPositions()
  
  def setLinkPositions(self):
    for link in self.scene.links:      
      link.start = link.inputNode.getAbsolutePosition()
      link.end = link.outputNode.getAbsolutePosition()
    
  def solveConstraints(self, link):
    outputNode = link.outputNode
    inputNode = link.inputNode
    
    outputComponent = outputNode.component
    inputComponent = inputNode.component
    
    outNodeSet = outputNode in self.distanceConstrainedNodes
    outCompSet = outputComponent in self.angleConstrainedComponents
    inNodeSet = inputNode in self.distanceConstrainedNodes
    inCompSet = inputComponent in self.angleConstrainedComponents
    
    if link.length is not None:
      if outNodeSet and outCompSet and inNodeSet and inCompSet:
        # fully constrained link
        
        # check that we're not going to move an already-constrained component
        if inputComponent in self.positionConstrainedComponents:
          #raise Exception("{0} overconstrained".format(inputComponent))
          pass
        
        # link vector
        linkVector = optivis.geometry.Coordinates(link.length, 0).rotate(outputNode.getAbsoluteAzimuth())
        
        # set input component proper position
        inputNode.setAbsoluteAzimuth(outputNode.getAbsoluteAzimuth())
        inputNode.setAbsolutePosition(outputNode.getAbsolutePosition().translate(linkVector))
        
        self.positionConstrainedComponents.add(inputComponent)
        self.positionConstrainedComponents.add(outputComponent)
        
        return
      elif not outNodeSet and outCompSet and inNodeSet and inCompSet:
        # output node NOT distance constrained
        # output component angle constrained
        # input node distance constrained
        # input component angle constrained
        
        print "[Layout] Constraining position of {0} using position and angle of {1} and link length".format(outputNode, inputNode)
          
        # set output node's absolute position using link
        outputNode.setAbsolutePosition(self.targetPosFromRefAndLink(inputNode, link))
          
        # we can now constrain the distance of the output node
        self.distanceConstrainedNodes.add(outputNode)
      elif outNodeSet and not outCompSet and inNodeSet and inCompSet:
        # output node distance constrained
        # output component NOT angle constrained
        # input node distance constrained
        # input component angle constrained
        
        print "[Layout] Constraining angle of {0} using angle of {1} ({2})".format(outputNode, inputNode, inputNode.getAbsoluteAzimuth())
        
        # set output node angle
        outputNode.setAbsoluteAzimuth(inputNode.getAbsoluteAzimuth())
        
        # set input node proper position
        linkVector = optivis.geometry.Coordinates(link.length, 0).rotate(outputNode.getAbsoluteAzimuth())
        inputNode.setAbsolutePosition(outputNode.getAbsolutePosition().translate(linkVector))
        
        # we can now constrain the angle of the output component
        self.angleConstrainedComponents.add(outputComponent)
      elif outNodeSet and outCompSet and not inNodeSet and inCompSet:
        # output node distance constrained
        # output component angle constrained
        # input node NOT distance constrained
        # input component angle constrained
        
        print "[Layout] Constraining position of {0} using position and angle of {1} and link length".format(inputNode, outputNode)
          
        # set input node's absolute position using link
        inputNode.setAbsolutePosition(self.targetPosFromRefAndLink(outputNode, link))
          
        # we can now constrain the distance of the input node
        self.distanceConstrainedNodes.add(inputNode)
      elif outNodeSet and outCompSet and inNodeSet and not inCompSet:
        # output node distance constrained
        # output component angle constrained
        # input node distance constrained
        # input component NOT angle constrained
        
        print "[Layout] Constraining angle of {0} using angle of {1} ({2})".format(inputNode, outputNode, outputNode.getAbsoluteAzimuth())
        
        # set input node angle
        inputNode.setAbsoluteAzimuth(outputNode.getAbsoluteAzimuth())
        
        # set input node proper position
        linkVector = optivis.geometry.Coordinates(link.length, 0).rotate(outputNode.getAbsoluteAzimuth())
        inputNode.setAbsolutePosition(outputNode.getAbsolutePosition().translate(linkVector))
        
        # we can now constrain the angle of the input component
        self.angleConstrainedComponents.add(inputComponent)
      else:
        print "[Layout] Skipping {0} until it is sufficiently constrained".format(link)
      
  def getComponentLinks(self, component, avoid=None):
    if avoid is not None:
      if not isinstance(avoid, set):
        raise Exception('Specified avoid set is not a set')
    
    links = []
    
    for link in self.scene.links:
      if avoid is not None:
        if link in avoid:
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
  
  def targetPosFromRefAndLink(self, referenceNode, link):
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