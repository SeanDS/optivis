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
    
class SimpleLayout(AbstractLayout):
  def __init__(self, *args, **kwargs):
    super(SimpleLayout, self).__init__(*args, **kwargs)
  
  def arrange(self):
    linkedComponents = set([])

    # make copy of links list
    links = self.scene.links
    
    # make sure there is a reference component
    if self.scene.reference is None:
      self.scene.reference = self.scene.components[0]
      
    # add reference component to linked components set, so it is automatically constrained
    linkedComponents.add(self.scene.reference)
    
    # find link with reference, and move it to start of list
    for i in range(len(self.scene.links)):
      link = self.scene.links[i]
      
      if link.hasComponent(self.scene.reference):
	del(links[i])
	links.insert(0, link)
	
	break
    
    ###
    # Layout and link everything
    
    for link in links:
      print "[Layout] Linking {0}".format(link)
      
      outputComponent = link.outputNode.component
      inputComponent = link.inputNode.component
      
      if outputComponent in linkedComponents and inputComponent in linkedComponents:
	# both components already constrained
	print "[Layout] Link {0} properties ignored because both linked components are already constrained by other links.".format(link)
      elif outputComponent in linkedComponents:
	# output component already constrained, input component not constrained
	
	# set azimuth first
	link.inputNode.setAbsoluteAzimuth(link.outputNode.getAbsoluteAzimuth())
	
	# set the position of the input component
	link.inputNode.setAbsolutePosition(self.getInputNodePositionRelativeToOutputNode(link))
      elif inputComponent in linkedComponents:
	# input component already constrained, output component not constrained
	
	# set azimuth first	
	link.outputNode.setAbsoluteAzimuth(link.inputNode.getAbsoluteAzimuth())
	
	# set the position of the output component
	link.outputNode.setAbsolutePosition(self.getOutputNodePositionRelativeToInputNode(link))
      else:
	# neither component already constrained, so just artificially constrain the first to (0, 0) FIXME: this should check to see if these components are linked later...
	link.outputNode.setAbsolutePosition(optivis.geometry.Coordinates(0, 0))
	
	# set azimuth first
	link.inputNode.setAbsoluteAzimuth(link.outputNode.getAbsoluteAzimuth())
	
	# set the position of the input component
	link.inputNode.setAbsolutePosition(self.getInputNodePositionRelativeToOutputNode(link))
	
      link.start = link.outputNode.getAbsolutePosition()
      link.end = link.inputNode.getAbsolutePosition()
      
      # add components to set of constrained components
      linkedComponents.add(outputComponent)
      linkedComponents.add(inputComponent)
    
    # move scene positions so that left most, topmost object is at the origin
    self.normalisePositions()
      
  def getInputNodePositionRelativeToOutputNode(self, link):    
    # absolute position of pivot point
    pivotPosition = link.outputNode.getAbsolutePosition()
    
    # angle
    pivotAngle = link.outputNode.getAbsoluteAzimuth()
    
    # position of component with respect to pivot
    relativePosition = optivis.geometry.Coordinates(link.length, 0).rotate(pivotAngle)
    
    # absolute position of component
    return pivotPosition.translate(relativePosition)
  
  def getOutputNodePositionRelativeToInputNode(self, link):    
    # absolute position of pivot point
    pivotPosition = link.inputNode.getAbsolutePosition()
    
    # angle
    pivotAngle = link.inputNode.getAbsoluteAzimuth()
    
    # position of component with respect to pivot, flipped because we're going 'backwards' from input to output
    relativePosition = optivis.geometry.Coordinates(link.length, 0).rotate(pivotAngle).flip()
    
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
    
    for component in self.scene.components:
      component.position = component.position.translate(offset)