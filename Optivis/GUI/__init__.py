from __future__ import division
import Tkinter as Tk
import Optivis
from Optivis.BenchObjects import *
from CanvasObjects import *
from Optivis.Nodes import *

class Tkinter(object):
  master = None
  canvas = None

  def __init__(self, bench, size=None, azimuth=0, zoom=1.0, startMarker=True, endMarker=True, startMarkerRadius=4, endMarkerRadius=2, startMarkerOutline="red", endMarkerOutline="blue"):
    if not isinstance(bench, Optivis.Bench):
      raise Exception('Specified bench is not of type Optivis.Bench')
    
    title = "Optivis - {0}".format(bench.title)
    
    if size is None:
      size = Optivis.Coordinates(500, 500)
    
    self.bench = bench
    self.size = size
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
    self.canvas = Tk.Canvas(self.master, width=self.size.x, height=self.size.y)

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
    
    # centre everything
    self.centre(canvasObjects)
    
    # draw objects
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
      size = component.size * self.zoom
      
      # add component to list of canvas components
      # azimuth of component is set to global azimuth - but in reality all but the first component will have its azimuth overridden based
      # on input/output node alignment
      canvasObjects.append(CanvasComponent(component=component, size=size, azimuth=self.azimuth, position=self.size / 2))
    
    ###
    # Layout and link everything
    
    for link in self.bench.links:
      canvasComponent1 = self.findCanvasComponent(link.outputNode.component, canvasObjects)
      canvasComponent2 = self.findCanvasComponent(link.inputNode.component, canvasObjects)
      
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
      linkEndPosition = Optivis.Coordinates(link.length, 0).rotate(outputAzimuth) * self.zoom
      
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
      
      # add canvas link
      canvasObjects.append(CanvasLink(start=outputNodeAbsolutePosition, end=inputNodeAbsolutePosition, width=self.zoom, fill=link.colour, startMarker=self.startMarker, endMarker=self.endMarker, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerOutline=self.startMarkerOutline, endMarkerOutline=self.endMarkerOutline))
      
      # add components to list of components
      # FIXME: don't add same component twice
      linkedComponents.append(link.inputNode.component)
      
    return canvasObjects
  
  def findCanvasComponent(self, component, canvasComponents):
    if not isinstance(component, Component):
      raise Exception('Specified canvas component is not of type Component')
    
    for thisCanvasComponent in canvasComponents:
      if thisCanvasComponent.component == component:
	return thisCanvasComponent
    
    raise Exception('Cannot find specified canvas object in buffer (this shouldn\'t happen!)')

  def centre(self, canvasObjects):
    # min and max positions
    minPos = Optivis.Coordinates(float('inf'), float('inf'))
    maxPos = Optivis.Coordinates(float('-inf'), float('-inf'))
    
    for canvasObject in canvasObjects:
      if isinstance(canvasObject, CanvasComponent):
	(thisMinPos, thisMaxPos) = canvasObject.getBoundingBox()
	
	if thisMinPos.x < minPos.x: minPos.x = thisMinPos.x
	if thisMinPos.y < minPos.y: minPos.y = thisMinPos.y
	
	if thisMaxPos.x > maxPos.x: maxPos.x = thisMaxPos.x
	if thisMaxPos.y > maxPos.y: maxPos.y = thisMaxPos.y
    
    # work out size from min and max
    size = maxPos - minPos
    
    # centre coordinates of group
    groupCentre = maxPos - size / 2
    
    # correction factor to middle of screen
    correction = self.size / 2 - groupCentre
    
    # loop over all objects, applying a translation
    for canvasObject in canvasObjects:
      if isinstance(canvasObject, CanvasComponent):
	canvasObject.position = canvasObject.position.translate(correction)
      elif isinstance(canvasObject, CanvasLink):
	canvasObject.start = canvasObject.start.translate(correction)
	canvasObject.end = canvasObject.end.translate(correction)

  def arrangeZ(self):
    """
    Arrange z-order of components using their tags
    """
    
    # send start markers to top
    self.canvas.tag_raise("startmarker")
  
    # now send end markers to top
    self.canvas.tag_raise("endmarker")

  @property
  def size(self):
    return self.__size

  @size.setter
  def size(self, size):
    if not isinstance(size, Optivis.Coordinates):
      raise Exception('Specified size is not of type Optivis.Coordinates')
    
    self.__size = size
    
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