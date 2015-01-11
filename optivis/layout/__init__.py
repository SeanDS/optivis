from __future__ import division

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
    
class SimpleLayout(AbstractLayout):
  def __init__(self, *args, **kwargs):
    super(SimpleLayout, self).__init__(*args, **kwargs)
  
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
      
      # coordinates of input node for rotated component input node
      inputNodeRelativeRotatedPosition = inputNodeRelativePosition.rotate(inputAzimuth - link.inputNode.azimuth)
      
      # absolute input node position
      inputNodeAbsolutePosition = outputNodeAbsolutePosition.translate(linkEndPosition)
      
      # check if input component is already linked
      if link.inputNode.component in linkedComponents:
	# can't move component - already linked
	
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
      else:
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