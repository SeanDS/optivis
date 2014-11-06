from __future__ import division
import os
import math
import Tkinter as Tk
import Image
import ImageTk
import rsvg
import cairo

class Optivis(object):
  components = []
  links = []
  
  # This holds objects drawn on the canvas. This acts as a buffer for the canvas - deleting its contents will eventually delete the equivalent representation from the canvas!
  canvasObjects = []
  
  def __init__(self, svgDir="svg"):
    self.svgDir = svgDir
    
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
  def svgDir(self):
    return self.__svgDir
  
  @svgDir.setter
  def svgDir(self, svgDir):
    self.__svgDir = svgDir
  
  def vis(self, canvas, scale=1):
    if not isinstance(canvas, Tk.Canvas):
      raise Exception('Specified canvas is not of type Tkinter.Canvas')
    
    # clear image buffer
    del self.canvasObjects[:]
    
    for component in self.components:
      width = component.width * scale
      height = component.height * scale
      
      self.canvasObjects.append(CanvasComponent(component=component, azimuth=0, xPos=250, yPos=250))
    
    # list of nodes already linked
    linkedNodes = []
    
    for link in self.links:
      canvasComponent1 = self.getCanvasObject(link.outputNode.component)
      canvasComponent2 = self.getCanvasObject(link.inputNode.component)
      
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
      
      # candidate position of second component
      (xPos2, yPos2) = Optivis.translate((xOutput, yOutput), (-xInputRelative, -yInputRelative), (xLength, yLength))
      
      # FIXME: potential bug with components linked across 180 degrees in a loop (i.e. position of component the same, but angle different) - do a similar check to the one below for angles      
      if link.inputNode in linkedNodes:
	# can't move component - already linked	
	# check if linking it would require moving it
	if not (canvasComponent2.xPos, canvasComponent2.yPos) == (xPos2, yPos2):
	  print "WARNING: component {0} already constrained by a link, and linking it to component {1} would require moving it. Ignoring link length and angle!".format(canvasComponent2, canvasComponent1)
	  
	  # update input position
	  (xInput, yInput) = Optivis.translate((canvasComponent2.xPos, canvasComponent2.yPos), Optivis.rotate((link.inputNode.xPos, link.inputNode.yPos), canvasComponent2.azimuth))
      else:
	# coordinates of second component
	(xPos2, yPos2) = Optivis.translate((xOutput, yOutput), (-xInputRelative, -yInputRelative), (xLength, yLength))
      
	# update second component position
	canvasComponent2.xPos = xPos2
	canvasComponent2.yPos = yPos2
      
      # update second component azimuth to be the link azimuth minus the input azimuth
      canvasComponent2.azimuth = inputAzimuth - link.inputNode.azimuth
      
      # draw link
      canvas.create_line(xOutput, yOutput, xInput, yInput, fill=link.colour)
      
      # marker for start line
      canvas.create_oval(xOutput - 5, yOutput - 5, xOutput + 5, yOutput + 5, fill="red")
      
      # marker for end line
      canvas.create_oval(xInput - 5, yInput - 5, xInput + 5, yInput + 5, fill="blue")
      
      # add link to list of links
      linkedNodes.append(link.inputNode)
    
    # loop over components again, adding them
    for canvasComponent in self.getCanvasComponents():
      canvas.create_image(canvasComponent.xPos, canvasComponent.yPos, image=canvasComponent.getImage(svgDir=self.svgDir), anchor=Tk.CENTER)
    
    canvas.pack()
  
  def getCanvasObject(self, visObject):
    if not isinstance(visObject, VisObject):
      raise Exception('Specified canvas object is not of type VisObject')
    
    for thisObject in self.canvasObjects:
      if thisObject.visObject == visObject:
	return thisObject
    
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
  def __init__(self, visObject, xPos=0, yPos=0):
    self.visObject = visObject
    self.xPos = xPos
    self.yPos = yPos

  @property
  def visObject(self):
    return self.__visObject

  @visObject.setter
  def visObject(self, visObject):
    if not isinstance(visObject, VisObject):
      raise Exception('Specified canvas object is not of type VisObject')
    
    self.__visObject = visObject
    
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

class CanvasComponent(CanvasObject):
  def __init__(self, component, azimuth=0, *args, **kwargs):
    if not isinstance(component, Component):
      raise Exception('Specified component is not of type Component')
    
    self.azimuth = azimuth
    self.image = None
    
    super(CanvasComponent, self).__init__(visObject=component, *args, **kwargs)
  
  def getImage(self, svgDir):
    self.image = self.visObject.toImage(svgDir=svgDir, azimuth=self.azimuth)
    
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

class Laser(Source):
  def __init__(self, filename="c-laser1.svg", width=62, height=46, *args, **kwargs):
    outputNode = OutputNode(name="out", component=self, xPos=-width/2, yPos=0, azimuth=180)
    
    super(Laser, self).__init__(filename=filename, width=width, height=height, outputNode=outputNode, *args, **kwargs)

if __name__ == '__main__':
  master = Tk.Tk()
  
  canvas = Tk.Canvas(master, width=500, height=500)
  #canvas.create_line(0, 100, 400, 500)
  #canvas.create_line(0, 80, 420, 500)
  #canvas.create_line(0, 60, 440, 500)
  #canvas.create_line(0, 40, 460, 500)
  #canvas.create_line(0, 20, 480, 500)
  #canvas.create_line(0, 0, 500, 500)
  #canvas.create_line(20, 0, 500, 480)
  #canvas.create_line(40, 0, 500, 460)
  #canvas.create_line(60, 0, 500, 440)
  #canvas.create_line(80, 0, 500, 420)
  #canvas.create_line(100, 0, 500, 400)
  
  table = Optivis()
  
  l1 = Laser(name="L1")
  m1 = CavityMirror(name="M1", aoi=30)
  m2 = CavityMirror(name="M2", aoi=15)
  m3 = CavityMirror(name="M3", aoi=0)
  
  table.addComponent(l1)
  table.addComponent(m1)
  table.addComponent(m2)
  table.addComponent(m3)
  
  table.addLink(Link(l1.outputNodes[0], m1.inputNodes[0], 100))
  table.addLink(Link(m1.outputNodes[0], m2.inputNodes[0], 100))
  table.addLink(Link(m2.outputNodes[0], m3.inputNodes[0], 150))
  
  #table.addComponent(m1)
  #table.addComponent(m2)
  #table.addComponent(m3)
  
  #table.addLink(Link(m1.outputNodes[0], m2.inputNodes[0], 100))
  #table.addLink(Link(m2.outputNodes[0], m3.inputNodes[0], 100))
  #table.addLink(Link(m3.outputNodes[0], m1.inputNodes[0], 100))
  
  table.vis(canvas)

"""
master = vis.Tk()

canvas = vis.Canvas(master, width=200, height=100)
canvas.pack()

canvas.create_line(0, 0, 200, 100)
canvas.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
canvas.create_rectangle(50, 25, 150, 75, fill="blue")

tkImage = svnToPhotoImage("svg/c-laser1.svg")

canvas.create_image(100, 100, image=tkImage)

vis.mainloop()
"""