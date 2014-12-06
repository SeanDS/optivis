from __future__ import division

import abc

import Optivis
import Optivis.Gui

class AbstractLayout(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, gui, canvasComponents, canvasLinks):
    self.gui = gui
    self.canvasComponents = canvasComponents
    self.canvasLinks = canvasLinks
  
  @abc.abstractmethod
  def arrange(self):
    return
  
  def getCanvasComponent(self, component):
    if not isinstance(component, Optivis.Component):
      raise Exception('Specified component is not of type Component')
    
    for thisCanvasComponent in self.canvasComponents:
      if thisCanvasComponent.component == component:
	return thisCanvasComponent
    
    raise Exception('Cannot find specified canvas component in list!')
  
  def getCanvasLink(self, link):
    if not isinstance(link, Optivis.Link):
      raise Exception('Specified link is not of type Link')
    
    for thisCanvasLink in self.canvasLinks:
      if thisCanvasLink.link == link:
	return thisCanvasLink
    
    raise Exception('Cannot find specified canvas link in list!')
  
  @property
  def gui(self):
    return self.__gui
  
  @gui.setter
  def gui(self, gui):
    if not isinstance(gui, Optivis.Gui.AbstractGui):
      raise Exception('Specified gui is not of type Optivis.Gui.AbstractGui')
    
    self.__gui = gui
  
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
    
    for link in self.gui.bench.links:
      canvasLink = self.getCanvasLink(link)
      canvasComponent1 = self.getCanvasComponent(link.outputNode.component)
      canvasComponent2 = self.getCanvasComponent(link.inputNode.component)
      
      # absolute angle of output beam
      outputAzimuth = canvasComponent1.azimuth + link.outputNode.azimuth
      
      # absolute input angle the same as output angle (light travels in a straight line!)
      inputAzimuth = outputAzimuth
      
      # node positions relative to components' centers
      outputNodeRelativePosition = link.outputNode.position * canvasComponent1.size
      inputNodeRelativePosition = link.inputNode.position * canvasComponent2.size
      
      # coordinates of output node for rotated component
      outputNodeRelativeRotatedPosition = outputNodeRelativePosition.rotate(canvasComponent1.azimuth)
      
      # combined output node and component position
      outputNodeAbsolutePosition = canvasComponent1.position.translate(outputNodeRelativeRotatedPosition)
      
      # create link end position (unrotated)
      linkEndPosition = Optivis.Coordinates(link.length, 0).rotate(outputAzimuth)
      
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

  def centre(self):
    # min and max positions
    minPos = Optivis.Coordinates(float('inf'), float('inf'))
    maxPos = Optivis.Coordinates(float('-inf'), float('-inf'))
    
    for canvasComponent in self.canvasComponents:
      (thisMinPos, thisMaxPos) = canvasComponent.getBoundingBox()
      
      if thisMinPos.x < minPos.x: minPos.x = thisMinPos.x
      if thisMinPos.y < minPos.y: minPos.y = thisMinPos.y
      
      if thisMaxPos.x > maxPos.x: maxPos.x = thisMaxPos.x
      if thisMaxPos.y > maxPos.y: maxPos.y = thisMaxPos.y
    
    # work out size from min and max
    size = maxPos - minPos
    
    # centre coordinates of group
    groupCentre = maxPos - size / 2
    
    # correction factor to middle of screen
    correction = self.gui.size / 2 - groupCentre
    
    # loop over all objects, applying a translation
    for canvasComponent in self.canvasComponents:
      canvasComponent.position = canvasComponent.position.translate(correction)
    
    for canvasLink in self.canvasLinks:
      canvasLink.start = canvasLink.start.translate(correction)
      canvasLink.end = canvasLink.end.translate(correction)