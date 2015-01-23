from __future__ import unicode_literals, division

import abc

import optivis
import optivis.geometry
import optivis.bench.components
import optivis.bench.links

class AbstractLayout(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, scene):
    self.scene = scene
  
  @abc.abstractmethod
  def arrange(self):
    return
  
  @property
  def scene(self):
    return self.__scene
  
  @scene.setter
  def scene(self, scene):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    self.__scene = scene
    
class AltLayout(AbstractLayout):
  def __init__(self, *args, **kwargs):
    super(AltLayout, self).__init__(*args, **kwargs)
  
  def arrange(self):
    linkedComponents = []
    
    # explicitly set first component's azimuth as per user instruction
    self.scene.components[0].azimuth = self.scene.azimuth
    
    ###
    # Layout and link everything
    
    for link in self.scene.links:
      component1 = link.outputNode.component
      component2 = link.inputNode.component
      
      # absolute angle of output beam
      outputAzimuth = component1.azimuth + link.outputNode.azimuth
      
      # absolute input angle the same as output angle (light travels in a straight line!)
      inputAzimuth = outputAzimuth
      
      # node positions relative to components' centers
      outputNodeRelativePosition = link.outputNode.position * component1.size
      inputNodeRelativePosition = link.inputNode.position * component2.size
      
      # coordinates of output node for rotated component
      outputNodeRelativeRotatedPosition = outputNodeRelativePosition.rotate(component1.azimuth)
      
      # combined output node and component position
      outputNodeAbsolutePosition = component1.position.translate(outputNodeRelativeRotatedPosition)
      
      # create link end position
      linkEndPosition = optivis.geometry.Coordinates(link.length, 0).rotate(outputAzimuth)
      
      # absolute input node position
      inputNodeAbsolutePosition = outputNodeAbsolutePosition.translate(linkEndPosition)
      
      # check if either component is already linked
      if link.inputNode.component in linkedComponents and link.outputNode.component in linkedComponents:
	# Both components already linked to something else! Just link them together as-is, and warn the user if this violates the angles of incidence.
	
	# TODO
	print "both components linked!"
	
      elif link.inputNode.component in linkedComponents:
	# can't move input component - already linked
	
	# input node position as previously defined by loop
	inputNodeClampedPosition = component2.position.translate(inputNodeRelativePosition.rotate(component2.azimuth))
	
	if not inputNodeClampedPosition == inputNodeAbsolutePosition:
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it or using a different angle of incidence. Ignoring link length and angle!".format(component2, component1)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(inputNodeAbsolutePosition.x, inputNodeAbsolutePosition.y)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(inputNodeClampedPosition.x, inputNodeClampedPosition.y)
	  
	  # override position and azimuth
	  inputNodeAbsolutePosition = inputNodeClampedPosition
      elif link.outputNode.component in linkedComponents:
	# can't move output component - already linked
	
	# output node position as previously defined by loop
	outputNodeClampedPosition = component1.position.translate(outputNodeRelativePosition.rotate(component1.azimuth))
	
	if not outputNodeClampedPosition == outputNodeAbsolutePosition:
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it or using a different angle of incidence. Ignoring link length and angle!".format(component1, component2)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(outputNodeAbsolutePosition.x, outputNodeAbsolutePosition.y)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(outputNodeClampedPosition.x, outputNodeClampedPosition.y)
	  
	  # override position and azimuth
	  outputNodeAbsolutePosition = outputNodeClampedPosition
      else:
	# neither input nor output linked - we can do what we want
	
	# coordinates of input node for rotated component input node
	inputNodeRelativeRotatedPosition = inputNodeRelativePosition.rotate(inputAzimuth - link.inputNode.azimuth)
	
	# coordinates of second component
	component2.position = inputNodeAbsolutePosition.translate(inputNodeRelativeRotatedPosition.flip())
      
	# update second component azimuth to be the link azimuth minus the input's azimuth
	component2.azimuth = inputAzimuth - link.inputNode.azimuth
      
      # set link nodes
      link.start = outputNodeAbsolutePosition
      link.end = inputNodeAbsolutePosition
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(component2)
      
class SimpleLayout(AbstractLayout):
  def __init__(self, *args, **kwargs):
    super(SimpleLayout, self).__init__(*args, **kwargs)
  
  def arrange(self):
    linkedComponents = []
    
    # explicitly set first component's azimuth as per user instruction
    self.scene.links[0].outputNode.component.azimuth = self.scene.azimuth
    
    ###
    # Layout and link everything
    
    for link in self.scene.links:
      print "Linking {0} to {1}".format(link.outputNode, link.inputNode)
      
      outputComponent = link.outputNode.component
      inputComponent = link.inputNode.component
      
      if outputComponent in linkedComponents and inputComponent in linkedComponents:
	# both components already constrained
	# TODO
	print "constrained!"
      elif outputComponent in linkedComponents:
	# output component already constrained, input component not constrained
	
	# set azimuth first
	link.inputNode.setAbsoluteAzimuth(link.outputNode.getAbsoluteAzimuth())
	
	# set the position of the input component
	link.inputNode.setAbsolutePosition(self.positionNodeRelativeToAnother(link.inputNode, link.outputNode, link.length))
      elif inputComponent in linkedComponents:
	# input component already constrained, output component not constrained
	
	# set azimuth first
	link.outputNode.setAbsoluteAzimuth(link.inputNode.getAbsoluteAzimuth())
	
	# set the position of the output component
	link.outputNode.setAbsolutePosition(self.positionNodeRelativeToAnother(link.outputNode, link.inputNode, link.length))
      else:
	# neither component already constrained, so just artificially constrain the first to (0, 0)
	link.outputNode.setAbsolutePosition(optivis.geometry.Coordinates(0, 0))
	
	# set azimuth first
	link.inputNode.setAbsoluteAzimuth(link.outputNode.getAbsoluteAzimuth())
	
	# set the position of the input component
	link.inputNode.setAbsolutePosition(self.positionNodeRelativeToAnother(link.inputNode, link.outputNode, link.length))
      
      link.start = link.outputNode.getAbsolutePosition()
      link.end = link.inputNode.getAbsolutePosition()
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(outputComponent)
      linkedComponents.append(inputComponent)
      
  def positionNodeRelativeToAnother(self, nodeToMove, nodeWithRespectTo, length):
    # absolute position of pivot point
    pivotPosition = nodeWithRespectTo.getAbsolutePosition()
    
    # angle
    pivotAngle = nodeWithRespectTo.getAbsoluteAzimuth()
    
    # position of component with respect to pivot
    relativePosition = optivis.geometry.Coordinates(length, 0).rotate(pivotAngle)
    
    # absolute position of component
    return pivotPosition.translate(relativePosition)