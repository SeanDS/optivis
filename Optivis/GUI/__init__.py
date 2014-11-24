from __future__ import division
import Tkinter as Tk
import math
from Optivis import Bench
from Optivis.BenchObjects import *
from CanvasObjects import *
from Optivis.Nodes import *

class Tkinter(object):
  master = None
  canvas = None

  def __init__(self, bench, width=500, height=500, azimuth=0, zoom=1.0, startMarker=True, endMarker=True, startMarkerRadius=4, endMarkerRadius=2, startMarkerOutline="red", endMarkerOutline="blue"):
    if not isinstance(bench, Bench):
      raise Exception('Specified bench is not of type Bench')
    
    title = "Optivis - {0}".format(bench.title)
    
    self.bench = bench
    self.width = width
    self.height = height
    self.azimuth = azimuth
    self.zoom = zoom
    self.title = title
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerOutline = startMarkerOutline
    self.endMarkerOutline = endMarkerOutline

    # create canvas
    self.master = Tk.Tk()
    self.canvas = Tk.Canvas(self.master, width=self.width, height=self.height)

    self.initialise()
  
  def initialise(self):
    # set title
    self.master.title(self.title)

    # make root menu
    menuBar = Tk.Menu(self.master)
    
    # make and add file menu
    fileMenu = Tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="Exit", command=self.quit)
    menuBar.add_cascade(label="File", menu=fileMenu)

    self.master.config(menu=menuBar)

  def quit(self):
    self.master.destroy()

  def show(self):    
    # get canvas objects
    canvasObjects = self.layout()
    
    for canvasObject in canvasObjects:
      canvasObject.draw(self.canvas)

    # arrange z-order
    self.arrangeZ()

    # force redraw
    self.canvas.pack()

    # run GUI loop
    self.master.mainloop()

  def layout(self):
    
    # list of componets already linked
    linkedComponents = []

    ###
    # Create list for canvas objects and add canvas components to it
    canvasObjects = []
    
    for component in self.bench.components:
      width = int(component.refWidth * self.zoom)
      height = int(component.refHeight * self.zoom)
      
      # add component to list of canvas components
      # azimuth of component is set to global azimuth - but in reality all but the first component will have its azimuth overridden based
      # on input/output node alignment
      canvasObjects.append(CanvasComponent(component=component, width=width, height=height, azimuth=self.azimuth, xPos=self.width / 2, yPos=self.height / 2))
    
    ###
    # Layout and link everything
    
    for link in self.bench.links:
      canvasComponent1 = self.findCanvasComponent(link.outputNode.component, canvasObjects)
      canvasComponent2 = self.findCanvasComponent(link.inputNode.component, canvasObjects)
      
      outputAzimuth = canvasComponent1.azimuth + link.outputNode.azimuth
      inputAzimuth = outputAzimuth
      
      # node positions relative to components' centers
      outputNodeX = link.outputNode.xPos * canvasComponent1.width
      outputNodeY = link.outputNode.yPos * canvasComponent1.height
      inputNodeX = link.inputNode.xPos * canvasComponent2.width
      inputNodeY = link.inputNode.yPos * canvasComponent2.height
      
      # coordinates of output node for rotated component
      (xOutputRelative, yOutputRelative) = Tkinter.rotate((outputNodeX, outputNodeY), canvasComponent1.azimuth)
      
      # combined output node and component position
      (xOutput, yOutput) = Tkinter.translate((canvasComponent1.xPos, canvasComponent1.yPos), (xOutputRelative, yOutputRelative))
      
      # link lengths in cartesian coordinates (well, 'Tkinter' coordinates)
      xLength = link.length * math.cos(math.radians(outputAzimuth)) * self.zoom
      yLength = link.length * math.sin(math.radians(outputAzimuth)) * self.zoom
      
      # coordinates of input node for rotated component input node
      (xInputRelative, yInputRelative) = Tkinter.rotate((inputNodeX, inputNodeY), inputAzimuth - link.inputNode.azimuth)
      
      (xInput, yInput) = Tkinter.translate((xOutput, yOutput), (xLength, yLength))
      
      # check if input component is already linked
      if link.inputNode.component in linkedComponents:
	# can't move component - already linked
	
	# test input node coordinates
	(xInputTest, yInputTest) = Tkinter.translate((canvasComponent2.xPos, canvasComponent2.yPos), Tkinter.rotate((inputNodeX, inputNodeY), canvasComponent2.azimuth))
	
	if not self.compareCoordinates((xInput, yInput), (xInputTest, yInputTest)):
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it or using a different angle of incidence. Ignoring link length and angle!".format(canvasComponent2, canvasComponent1)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(xInput, yInput)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(xInputTest, yInputTest)
	  
	  # override position and azimuth
	  (xInput, yInput) = (xInputTest, yInputTest)
      else:
	# coordinates of second component
	(xPos2, yPos2) = Tkinter.translate((xOutput, yOutput), (-xInputRelative, -yInputRelative), (xLength, yLength))
      
	# update second component position
	canvasComponent2.xPos = xPos2
	canvasComponent2.yPos = yPos2
      
	# update second component azimuth to be the link azimuth minus the input's azimuth
	canvasComponent2.azimuth = inputAzimuth - link.inputNode.azimuth
      
      # add canvas link
      canvasObjects.append(CanvasLink((xOutput, yOutput), (xInput, yInput), width=self.zoom, fill=link.colour, startMarker=self.startMarker, endMarker=self.endMarker, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerOutline=self.startMarkerOutline, endMarkerOutline=self.endMarkerOutline))
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(link.inputNode.component)
      
    return canvasObjects

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
  
  def findCanvasComponent(self, component, canvasComponents):
    if not isinstance(component, Component):
      raise Exception('Specified canvas component is not of type Component')
    
    for thisCanvasComponent in canvasComponents:
      if thisCanvasComponent.component == component:
	return thisCanvasComponent
    
    raise Exception('Cannot find specified canvas object in buffer (this shouldn\'t happen!)')
  
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

  def arrangeZ(self):
    """
    Arrange z-order of components using their tags
    """
    
    # send start markers to top
    self.canvas.tag_raise("startmarker")
  
    # now send end markers to top
    self.canvas.tag_raise("endmarker")

  @property
  def width(self):
    return self.__width

  @width.setter
  def width(self, width):
    self.__width = width

  @property
  def height(self):
    return self.__height

  @height.setter
  def height(self, height):
    self.__height = height
    
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
    
  @property
  def zoom(self):
    return self.__zoom
  
  @zoom.setter
  def zoom(self, zoom):
    self.__zoom = zoom
    
  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title
    
  @property
  def startMarker(self):
    return self.__startMarker
  
  @startMarker.setter
  def startMarker(self, startMarker):
    self.__startMarker = startMarker
    
  @property
  def endMarker(self):
    return self.__endMarker
  
  @endMarker.setter
  def endMarker(self, endMarker):
    self.__endMarker = endMarker
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerOutline(self):
    return self.__startMarkerOutline
  
  @startMarkerOutline.setter
  def startMarkerOutline(self, startMarkerOutline):
    self.__startMarkerOutline = startMarkerOutline
    
  @property
  def endMarkerOutline(self):
    return self.__endMarkerOutline
  
  @endMarkerOutline.setter
  def endMarkerOutline(self, endMarkerOutline):
    self.__endMarkerOutline = endMarkerOutline