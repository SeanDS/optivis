from __future__ import division

import abc

import optivis
import optivis.geometry
import optivis.bench.components
import optivis.bench.links

class AbstractLayout(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, scene, canvasComponents, canvasLinks):
    self.scene = scene
    self.canvasComponents = canvasComponents
    self.canvasLinks = canvasLinks
  
  @abc.abstractmethod
  def arrange(self):
    return
  
  def getCanvasComponent(self, component):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type optivis.bench.components.AbstractComponent')
    
    for thisCanvasComponent in self.canvasComponents:
      if thisCanvasComponent.component == component:
	return thisCanvasComponent
    
    raise Exception('Cannot find specified canvas component in list!')
  
  def getCanvasLink(self, link):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type optivis.bench.links.AbstractLink')
    
    for thisCanvasLink in self.canvasLinks:
      if thisCanvasLink.link == link:
	return thisCanvasLink
    
    raise Exception('Cannot find specified canvas link in list!')
  
  @property
  def scene(self):
    return self.__scene
  
  @scene.setter
  def scene(self, scene):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    self.__scene = scene
  
  @property
  def canvasComponents(self):
    return self.__canvasComponents
  
  @canvasComponents.setter
  def canvasComponents(self, canvasComponents):
    self.__canvasComponents = canvasComponents
    
  @property
  def canvasLinks(self):
    return self.__canvasLinks
  
  @canvasLinks.setter
  def canvasLinks(self, canvasLinks):
    self.__canvasLinks = canvasLinks
    
class SimpleLayout(AbstractLayout):
  def __init__(self, *args, **kwargs):
    super(SimpleLayout, self).__init__(*args, **kwargs)
  
  def arrange(self):
    linkedComponents = []
    
    ###
    # Layout and link everything
    
    for link in self.scene.links:
      canvasLink = self.getCanvasLink(link)
      canvasComponent1 = self.getCanvasComponent(link.outputNode.component)
      canvasComponent2 = self.getCanvasComponent(link.inputNode.component)
      
      # absolute angle of output beam
      outputAzimuth = canvasComponent1.azimuth + link.outputNode.azimuth
      
      # absolute input angle the same as output angle (light travels in a straight line!)
      inputAzimuth = outputAzimuth
      
      # node positions relative to components' centers
      outputNodeRelativePosition = link.outputNode.position * canvasComponent1.component.size
      inputNodeRelativePosition = link.inputNode.position * canvasComponent2.component.size
      
      # coordinates of output node for rotated component
      outputNodeRelativeRotatedPosition = outputNodeRelativePosition.rotate(canvasComponent1.azimuth)
      
      # combined output node and component position
      outputNodeAbsolutePosition = canvasComponent1.position.translate(outputNodeRelativeRotatedPosition)
      
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
	inputNodeClampedPosition = canvasComponent2.position.translate(inputNodeRelativePosition.rotate(canvasComponent2.azimuth))
	
	if not inputNodeClampedPosition == inputNodeAbsolutePosition:
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it or using a different angle of incidence. Ignoring link length and angle!".format(canvasComponent2, canvasComponent1)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(inputNodeAbsolutePosition.x, inputNodeAbsolutePosition.y)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(inputNodeClampedPosition.x, inputNodeClampedPosition.y)
	  
	  # override position and azimuth
	  inputNodeAbsolutePosition = inputNodeClampedPosition
      else:
	# coordinates of second component
	canvasComponent2.position = inputNodeAbsolutePosition.translate(inputNodeRelativeRotatedPosition.flip())#outputNodeAbsolutePosition.translate(inputNodeRelativeRotatedPosition, linkEndPosition)
      
	# update second component azimuth to be the link azimuth minus the input's azimuth
	canvasComponent2.azimuth = inputAzimuth - link.inputNode.azimuth
      
      # set link nodes
      canvasLink.start = outputNodeAbsolutePosition
      canvasLink.end = inputNodeAbsolutePosition
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(link.inputNode.component)