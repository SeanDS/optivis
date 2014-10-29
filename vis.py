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
      
      self.canvasObjects.append(CanvasComponent(component=component, azimuth=45, xPos=250, yPos=250))
    
    for link in self.links:
      canvasComponent1 = self.getCanvasObject(link.outputNode.component)
      canvasComponent2 = self.getCanvasObject(link.inputNode.component)
      
      xPos1 = canvasComponent1.xPos + link.outputNode.xPos
      yPos1 = canvasComponent1.yPos + link.outputNode.yPos
      
      print xPos1
      print yPos1
      
      # rotate xPos1 and yPos1
      (xPos1, yPos1) = Optivis.rotateCoordinates(xPos1, yPos1, canvasComponent1.visObject.width, canvasComponent1.visObject.height, canvasComponent1.azimuth)
      
      print xPos1
      print yPos1
      
      # link lengths in cartesian coordinates
      xLength = link.length * math.cos(math.radians(link.outputNode.azimuth))
      yLength = link.length * math.sin(math.radians(link.outputNode.azimuth))
      
      xPos2 = xPos1 + xLength
      yPos2 = yPos1 + yLength
      
      # update second component position FIXME: map this to the input node azimuth
      canvasComponent2.xPos = xPos2 - link.inputNode.xPos
      canvasComponent2.yPos = yPos2 - link.inputNode.yPos
      
      canvas.create_line(xPos1, yPos1, xPos2, yPos2)
    
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
  def rotateCoordinates(xPos, yPos, xWidth, yWidth, azimuth):
    # apply rotation matrix to xPos and yPos
    xPosRotated = xPos + xWidth * math.cos(math.radians(azimuth)) - yWidth * math.sin(math.radians(azimuth))
    yPosRotated = yPos + xWidth * math.sin(math.radians(azimuth)) + yWidth * math.cos(math.radians(azimuth))
    
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
  def __init__(self, outputNode, inputNode, length):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    
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
  
class Component(VisObject):
  def __init__(self, filename, width, height, inputNodes, outputNodes):
    self.filename = filename
    self.width = width
    self.height = height
    self.inputNodes = inputNodes
    self.outputNodes = outputNodes
  
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
    
    print azimuth
    
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
    image = image.rotate(azimuth, expand=True)
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

class Source(Component):
  def __init__(self, outputNode, *args, **kwargs):    
    inputNodes = []
    outputNodes = [outputNode]
    
    super(Source, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Mirror(Component):
  def __init__(self, *args, **kwargs):
    super(Mirror, self).__init__(*args, **kwargs)

class CavityMirror(Mirror):
  def __init__(self, filename="b-mir.svg", width=11, height=29):
    inputNodes = [InputNode(name="fr", component=self, xPos=0, yPos=height/2, azimuth=180)]
    outputNodes = [OutputNode(name="bk", component=self, xPos=11, yPos=height/2, azimuth=0)]
    
    super(CavityMirror, self).__init__(filename=filename, width=width, height=height, inputNodes=inputNodes, outputNodes=outputNodes)

class Laser(Source):
  def __init__(self, filename="c-laser1.svg", width=62, height=46):
    outputNode = OutputNode(name="out", component=self, xPos=0, yPos=height/2, azimuth=180)
    
    super(Laser, self).__init__(filename=filename, width=width, height=height, outputNode=outputNode)

if __name__ == '__main__':
  master = Tk.Tk()
  
  canvas = Tk.Canvas(master, width=500, height=500)
  
  table = Optivis()
  
  l = Laser()
  m = CavityMirror()
  
  table.addComponent(l)
  table.addComponent(m)
  table.addLink(Link(l.outputNodes[0], m.inputNodes[0], 50))
  
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