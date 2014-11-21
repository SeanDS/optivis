from __future__ import division
import math
import Tkinter as Tk

from BenchObjects import *
from CanvasObjects import *
from Gui import *
from Nodes import *

class Bench(object):
  ###
  # GUI
  gui = None

  ###
  # Optivis canvas components

  components = []
  links = []
  
  # This holds objects drawn on the canvas. This acts as a buffer for the canvas - deleting its contents will eventually delete the equivalent representation from the canvas!
  canvasObjects = []
  
  def __init__(self, width=500, height=500, azimuth=0):
    self.azimuth = azimuth
    self.gui = GUI(width=width, height=height)

  def draw(self):
    # create canvas objects
    self.vis()

    # draw them
    self.gui.draw(self.canvasObjects)
    
  def addComponent(self, component):
    if not isinstance(component, Component):    
      raise Exception('Specified component is not of type Component')
    
    self.components.append(component)
  
  def addLink(self, link):
    if not isinstance(link, Link):
      raise Exception('Specified link is not of type Link')
    
    if not link.inputNode.component in self.components:
      raise Exception('Input node component has not been added to table')
    
    if not link.outputNode.component in self.components:
      raise Exception('Output node component has not been added to table')
    
    self.links.append(link)

  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
  
  def createCanvasObjects(self):    
    # clear image buffer
    del self.canvasObjects[:]
    
    for component in self.components:
      width = component.width
      height = component.height
      
      # add component to list of canvas objects
      # azimuth of component is set to global azimuth - but in reality all but the first component will have its azimuth overridden based
      # on input/output node alignment
      self.canvasObjects.append(CanvasComponent(component=component, azimuth=self.azimuth, xPos=self.gui.width / 2, yPos=self.gui.height / 2))

  def vis(self):
    # convert optical components to canvas objects
    self.createCanvasObjects()
    
    # list of componets already linked
    linkedComponents = []
    
    for link in self.links:
      canvasComponent1 = self.getCanvasComponent(link.outputNode.component)
      canvasComponent2 = self.getCanvasComponent(link.inputNode.component)
      
      outputAzimuth = canvasComponent1.azimuth + link.outputNode.azimuth
      inputAzimuth = outputAzimuth
      
      # coordinates of output node for rotated component
      (xOutputRelative, yOutputRelative) = Bench.rotate((link.outputNode.xPos, link.outputNode.yPos), canvasComponent1.azimuth)
      
      # combined output node and component position
      (xOutput, yOutput) = Bench.translate((canvasComponent1.xPos, canvasComponent1.yPos), (xOutputRelative, yOutputRelative))
      
      # link lengths in cartesian coordinates (well, 'Tkinter' coordinates)
      xLength = link.length * math.cos(math.radians(outputAzimuth))
      yLength = link.length * math.sin(math.radians(outputAzimuth))
      
      # coordinates of input node for rotated component input node
      (xInputRelative, yInputRelative) = Bench.rotate((link.inputNode.xPos, link.inputNode.yPos), canvasComponent2.azimuth)
      
      (xInput, yInput) = Bench.translate((xOutput, yOutput), (xLength, yLength))
      
      # check if input component is already linked
      if link.inputNode.component in linkedComponents:
	# can't move component - already linked
	
	# get input node coordinates
	(xInputTest, yInputTest) = Bench.translate((canvasComponent2.xPos, canvasComponent2.yPos), Bench.rotate((link.inputNode.xPos, link.inputNode.yPos), canvasComponent2.azimuth + link.inputNode.azimuth))
	
	#if not (canvasComponent2.xPos, canvasComponent2.yPos) == (xPos2, yPos2):
	#if not (xInput, yInput) == (xInputTest, yInputTest):
	if not self.compareCoordinates((xInput, yInput), (xInputTest, yInputTest)):# and not inputAzimuth is (canvasComponent2.azimuth + link.inputNode.azimuth):
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it. Ignoring link length and angle!".format(canvasComponent2, canvasComponent1)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(xInput, yInput)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(xInputTest, yInputTest)
	  
	  # override position and azimuth
	  (xInput, yInput) = (xInputTest, yInputTest)
	  #inputAzimuth = canvasComponent2.azimuth + link.inputNode.azimuth
      else:
	# coordinates of second component
	(xPos2, yPos2) = Bench.translate((xOutput, yOutput), (-xInputRelative, -yInputRelative), (xLength, yLength))
      
	# update second component position
	canvasComponent2.xPos = xPos2
	canvasComponent2.yPos = yPos2
      
	# update second component azimuth to be the link azimuth minus the input azimuth
	canvasComponent2.azimuth = inputAzimuth - link.inputNode.azimuth
      
      # add canvas link
      self.canvasObjects.append(CanvasLink((xOutput, yOutput), (xInput, yInput), fill=link.colour))

      # marker for start and end lines
      #self.addMarker((xOutput, yOutput), fill="red") # start (output)
      #self.addMarker((xInput, yInput), fill="blue")  # end (input)
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(link.inputNode.component)

  def compareCoordinates(self, XY1, XY2, tol=1e-18, rel=1e-7):
    """
    Compare coordinate floats without precision errors. Based on http://code.activestate.com/recipes/577124-approximately-equal/.
    """
    
    if tol is rel is None:
        raise TypeError('Cannot specify both absolute and relative errors are None')
    
    xTests = []
    yTests = []
    
    if tol is not None:
      xTests.append(tol)
      yTests.append(tol)
      
    if rel is not None:
      xTests.append(rel * abs(XY1[0]))
      yTests.append(rel * abs(XY1[1]))
    
    assert xTests
    assert yTests
    
    return (abs(XY1[0] - XY2[0]) <= max(xTests)) and (abs(XY1[1] - XY2[1]) <= max(yTests))
  
  def getCanvasComponent(self, component):
    if not isinstance(component, Component):
      raise Exception('Specified canvas component is not of type Component')
    
    for thisCanvasComponent in self.getCanvasComponents():
      if thisCanvasComponent.component == component:
	return thisCanvasComponent
    
    raise Exception('Cannot find specified canvas object in buffer (this shouldn\'t happen!)')
  
  def getCanvasComponents(self):
    canvasComponents = []
    
    for thisObject in self.canvasObjects:
      if isinstance(thisObject, CanvasComponent):
	canvasComponents.append(thisObject)
    
    return canvasComponents
  
  @staticmethod
  def translate(*args):
    return map(sum, zip(*args))
  
  @staticmethod
  def rotate((xPos, yPos), azimuth):
    """
    Rotation applied for the left-handed coordinate system used by Tkinter.
    Azimuth is the angle in degrees to rotate in a clockwise direction.
    """
    
    # apply rotation matrix to xPos and yPos
    xPosRotated = xPos * math.cos(math.radians(azimuth)) - yPos * math.sin(math.radians(azimuth))
    yPosRotated = xPos * math.sin(math.radians(azimuth)) + yPos * math.cos(math.radians(azimuth))
    
    return (xPosRotated, yPosRotated)