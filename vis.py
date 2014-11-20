from __future__ import division
import os
import math
import Tkinter as Tk
import Image
import ImageTk
import rsvg
import cairo

class Optivis(object):
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
      
      # coordinates of output node for rotated component
      (xOutputRelative, yOutputRelative) = Optivis.rotate((link.outputNode.xPos, link.outputNode.yPos), canvasComponent1.azimuth)
      
      # combined output node and component position
      (xOutput, yOutput) = Optivis.translate((canvasComponent1.xPos, canvasComponent1.yPos), (xOutputRelative, yOutputRelative))
      
      outputAzimuth = canvasComponent1.azimuth + link.outputNode.azimuth
      inputAzimuth = outputAzimuth
      
      # link lengths in cartesian coordinates (well, 'Tkinter' coordinates)
      xLength = link.length * math.cos(math.radians(outputAzimuth))
      yLength = link.length * math.sin(math.radians(outputAzimuth))
      
      # coordinates of input node for rotated component input node
      (xInputRelative, yInputRelative) = Optivis.rotate((link.inputNode.xPos, link.inputNode.yPos), inputAzimuth - link.inputNode.azimuth)
      
      (xInput, yInput) = Optivis.translate((xOutput, yOutput), (xLength, yLength))
      
      # check if input component is already linked
      if link.inputNode.component in linkedComponents:
	# can't move component - already linked
	
	# get input node coordinates
	(xInputTest, yInputTest) = Optivis.translate((canvasComponent2.xPos, canvasComponent2.yPos), Optivis.rotate((link.inputNode.xPos, link.inputNode.yPos), canvasComponent2.azimuth))
	
	#if not (canvasComponent2.xPos, canvasComponent2.yPos) == (xPos2, yPos2):
	#if not (xInput, yInput) == (xInputTest, yInputTest):
	if not self.compareCoordinates((xInput, yInput), (xInputTest, yInputTest)):
	  # warn the user that they have specified a link longer/shorter or different angle than necessary to keep this component in its current position
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it. Ignoring link length and angle!".format(canvasComponent2, canvasComponent1)
	  
	  # print desired position
	  print "\tDesired position: ({0}, {1})".format(xInput, yInput)
	  
	  # print overridden position
	  print "\tOverridden position: ({0}, {1})".format(xInputTest, yInputTest)
	  
	  # override position
	  (xInput, yInput) = (xInputTest, yInputTest)
      else:
	# coordinates of second component
	(xPos2, yPos2) = Optivis.translate((xOutput, yOutput), (-xInputRelative, -yInputRelative), (xLength, yLength))
      
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

class CanvasObject(object):
  def __init__(self):
    return None

  # FIXME: make draw() an abstract class

class CanvasComponent(CanvasObject):
  def __init__(self, component, azimuth=0, xPos=0, yPos=0):
    if not isinstance(component, Component):
      raise Exception('Specified component is not of type Component')
    
    self.azimuth = azimuth
    self.image = None

    self.component = component
    self.xPos = xPos
    self.yPos = yPos

    super(CanvasComponent, self).__init__()
  
  def draw(self, canvas, svgDir):
    if not isinstance(canvas, Tk.Canvas):
      raise Exception('Specified canvas is not of type Tk.Canvas')

    canvas.create_image(self.xPos, self.yPos, image=self.getImage(svgDir=svgDir), anchor=Tk.CENTER)

  @property
  def xPos(self):
    return self.__xPos
  
  @xPos.setter
  def xPos(self, xPos):
    self.__xPos = xPos
  
  @property
  def yPos(self):
    return self.__yPos
  
  @yPos.setter
  def yPos(self, yPos):
    self.__yPos = yPos
  
  def getImage(self, svgDir):
    self.image = self.component.toImage(svgDir=svgDir, azimuth=self.azimuth)
    
    return self.image
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
    
  def __str__(self):
    # return visObject's __str__
    return self.visObject.__str__()

class CanvasLink(CanvasObject):
  def __init__(self, (xStart, yStart), (xEnd, yEnd), fill="black"):
    self.startPos = (xStart, yStart)
    self.endPos = (xEnd, yEnd)
    self.fill = fill
    
    super(CanvasLink, self).__init__()

  def draw(self, canvas, svgDir):
    if not isinstance(canvas, Tk.Canvas):
      raise Exception('Specified canvas is not of type Tk.Canvas')

    canvas.create_line(self.startPos[0], self.startPos[1], self.endPos[0], self.endPos[1], fill=self.fill)

  @property
  def startPos(self):
    return self.__startPos

  @startPos.setter
  def startPos(self, startPos):
    self.__startPos = startPos

  @property
  def endPos(self):
    return self.__endPos

  @endPos.setter
  def endPos(self, endPos):
    self.__endPos = endPos

  @property
  def fill(self):
    return self.__fill

  @fill.setter
  def fill(self, fill):
    self.__fill = fill

class GUI(object):
  master = None
  canvas = None

  def __init__(self, width=500, height=500, title="Optivis", svgDir="svg"):
    self.width = width
    self.height = height
    self.title = title
    self.svgDir = svgDir

    # create canvas
    self.master = Tk.Tk()
    self.canvas = Tk.Canvas(self.master, width=self.width, height=self.height)

    self.initialise()

  def initialise(self):
    # set title
    # TODO: make this user-settable
    self.master.title(self.title)

    # add menu
    menuBar = Tk.Menu(self.master)
    menuBar.add_command(label="Exit", command=self.quit)

    self.master.config(menu=menuBar)

  def quit(self):
    self.master.destroy()

  def draw(self, canvasComponents):
    for canvasComponent in canvasComponents:
      canvasComponent.draw(self.canvas, self.svgDir)

    # force redraw
    self.canvas.pack()

    # run GUI loop
    self.master.mainloop()
  
  #def addMarker(self, (xPos, yPos), radius=2, *args, **kwargs):
  #  self.canvas.create_oval(xPos - radius, yPos - radius, xPos + radius, yPos + radius, *args, **kwargs)

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
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title

  @property
  def svgDir(self):
    return self.__svgDir

  @svgDir.setter
  def svgDir(self, svgDir):
    self.__svgDir = svgDir

class Node(object):  
  def __init__(self, name, component, xPos, yPos, azimuth):
    self.name = name
    self.component = component
    self.xPos = xPos
    self.yPos = yPos
    self.azimuth = azimuth
  
  @property
  def name(self):
    return self.__name
  
  @name.setter
  def name(self, name):
    self.__name = name
    
  @property
  def component(self):
    return self.__component

  @component.setter
  def component(self, component):
    if not isinstance(component, Component):
      raise Exception('Specified component is not of type Component')
    
    self.__component = component
    
  @property
  def xPos(self):
    return self.__xPos
  
  @xPos.setter
  def xPos(self, xPos):
    self.__xPos = xPos
  
  @property
  def yPos(self):
    return self.__yPos
  
  @yPos.setter
  def yPos(self, yPos):
    self.__yPos = yPos
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth

class InputNode(Node):
  def __init__(self, *args, **kwargs):
    super(InputNode, self).__init__(*args, **kwargs)

class OutputNode(Node):
  def __init__(self, *args, **kwargs):
    super(OutputNode, self).__init__(*args, **kwargs)

class VisObject(object):
  def __init__(self):
    # nothing to do
    return
  
  def __eq__(self, other):
    return self.__dict__ == other.__dict__
    #return self.filename == other.filename and self.width == other.width and self.height = other.height # FIXME: check also for inputNodes, etc

class Link(VisObject):
  def __init__(self, outputNode, inputNode, length, colour="red"):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    self.colour = colour
    
  @property
  def outputNode(self):
    return self.__outputNode
  
  @outputNode.setter
  def outputNode(self, outputNode):
    if not isinstance(outputNode, OutputNode):
      raise Exception('Specified output node is not of type OutputNode')
    
    self.__outputNode = outputNode
  
  @property
  def inputNode(self):
    return self.__inputNode
  
  @inputNode.setter
  def inputNode(self, inputNode):
    if not isinstance(inputNode, InputNode):
      raise Exception('Specified input node is not of type InputNode')
    
    self.__inputNode = inputNode
  
  @property
  def length(self):
    return self.__length
  
  @length.setter
  def length(self, length):
    self.__length = length
  
  @property
  def colour(self):
    return self.__colour
  
  @colour.setter
  def colour(self, colour):
    #FIXME: check for valid colours here
    self.__colour = colour
  
class Component(VisObject):
  def __init__(self, name, filename, width, height, inputNodes, outputNodes):
    self.name = name
    self.filename = filename
    self.width = width
    self.height = height
    self.inputNodes = inputNodes
    self.outputNodes = outputNodes
  
  @property
  def name(self):
    return self.__name
  
  @name.setter
  def name(self, name):
    self.__name = name
  
  @property
  def filename(self):
    return self.__filename
  
  @filename.setter
  def filename(self, filename):
    self.__filename = filename
  
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
  def inputNodes(self):
    return self.__inputNodes
  
  @inputNodes.setter
  def inputNodes(self, inputNodes):
    self.__inputNodes = inputNodes
  
  @property
  def outputNodes(self):
    return self.__outputNodes
  
  @outputNodes.setter
  def outputNodes(self, outputNodes):
    self.__outputNodes = outputNodes
  
  def toImage(self, svgDir, width=-1, height=-1, azimuth=0):
    """
    Returns a ImageTk.PhotoImage object represeting the svg file
    """
    
    filepath = os.path.join(svgDir, self.filename)
    
    svg = rsvg.Handle(file=filepath)
    
    if width < 0:
      width = svg.get_dimension_data()[0]
    
    if height < 0:
      height = svg.get_dimension_data()[1]
    
    height = int(height)
    width = int(width)
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    
    svg.render_cairo(context)
    
    tkImage = ImageTk.PhotoImage('RGBA')
    image = Image.frombuffer('RGBA', (width, height), surface.get_data(), 'raw', 'BGRA', 0, 1)
    image = image.rotate(-azimuth, expand=True) # -azimuth used because we have a left handed coordinate system
    tkImage.paste(image)
    
    return(tkImage)
  
  def getInputNode(self, nodeName):
    for node in self.inputNodes:
      if node.name == nodeName:
	return node
    
    raise Exception('No input node with name {0} found'.format(nodeName))
  
  def getOutputNode(self, nodeName):
    for node in self.outputNodes:
      if node.name == nodeName:
	return node
    
    raise Exception('No output node with name {0} found'.format(nodeName))
  
  def __str__(self):
    return self.name

class Source(Component):
  def __init__(self, outputNode, *args, **kwargs):    
    inputNodes = []
    outputNodes = [outputNode]
    
    super(Source, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Mirror(Component):
  def __init__(self, *args, **kwargs):
    super(Mirror, self).__init__(*args, **kwargs)

class CavityMirror(Mirror):
  def __init__(self, filename="b-mir.svg", width=11, height=29, aoi=0, *args, **kwargs):
    inputNodes = [
      # input node azimuth defined WRT input light direction
      InputNode(name="fr", component=self, xPos=-width/2, yPos=0, azimuth=aoi+0),
      InputNode(name="bk", component=self, xPos=width/2, yPos=0, azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      OutputNode(name="fr", component=self, xPos=-width/2, yPos=0, azimuth=180-aoi),
      OutputNode(name="bk", component=self, xPos=width/2, yPos=0, azimuth=0-aoi)
    ]
    
    super(CavityMirror, self).__init__(filename=filename, width=width, height=height, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitter(Mirror):
  def __init__(self, filename="b-bsp.svg", width=23, height=23, aoi=0, *args, **kwargs):
    inputNodes = [
      InputNode(name="frA", component=self, xPos=0, yPos=-height/2, azimuth=aoi+90),
      InputNode(name="frB", component=self, xPos=width/2, yPos=0, azimuth=aoi+180),
      InputNode(name="bkA", component=self, xPos=-width/2, yPos=0, azimuth=aoi),
      InputNode(name="bkB", component=self, xPos=0, yPos=height/2, azimuth=aoi+270)
    ]
    
    outputNodes = [
      OutputNode(name="frA", component=self, xPos=width/2, yPos=0, azimuth=-aoi),
      OutputNode(name="frB", component=self, xPos=0, yPos=-height/2, azimuth=270-aoi),
      OutputNode(name="bkA", component=self, xPos=0, yPos=height/2, azimuth=90-aoi),
      OutputNode(name="bkB", component=self, xPos=-width/2, yPos=0, azimuth=180-aoi)
    ]
    
    super(BeamSplitter, self).__init__(filename=filename, width=width, height=height, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Laser(Source):
  def __init__(self, filename="c-laser1.svg", width=62, height=46, *args, **kwargs):
    outputNode = OutputNode(name="out", component=self, xPos=-width/2, yPos=0, azimuth=180)
    
    super(Laser, self).__init__(filename=filename, width=width, height=height, outputNode=outputNode, *args, **kwargs)
