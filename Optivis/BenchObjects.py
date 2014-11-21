from __future__ import division
import os
import math
import Image
import ImageTk
import rsvg
import cairo
import Nodes

class BenchObject(object):
  def __init__(self):
    # nothing to do
    return
  
  def __eq__(self, other):
    return self.__dict__ == other.__dict__
    #return self.filename == other.filename and self.width == other.width and self.height = other.height # FIXME: check also for inputNodes, etc

class Link(BenchObject):
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
    if not isinstance(outputNode, Nodes.OutputNode):
      raise Exception('Specified output node is not of type Nodes.OutputNode')
    
    self.__outputNode = outputNode
  
  @property
  def inputNode(self):
    return self.__inputNode
  
  @inputNode.setter
  def inputNode(self, inputNode):
    if not isinstance(inputNode, Nodes.InputNode):
      raise Exception('Specified input node is not of type Nodes.InputNode')
    
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

class Component(BenchObject):
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
      Nodes.InputNode(name="fr", component=self, xPos=-width/2, yPos=0, azimuth=aoi+0),
      Nodes.InputNode(name="bk", component=self, xPos=width/2, yPos=0, azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      Nodes.OutputNode(name="fr", component=self, xPos=-width/2, yPos=0, azimuth=180-aoi),
      Nodes.OutputNode(name="bk", component=self, xPos=width/2, yPos=0, azimuth=0-aoi)
    ]
    
    super(CavityMirror, self).__init__(filename=filename, width=width, height=height, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitter(Mirror):
  def __init__(self, filename="b-bsp.svg", width=23, height=23, aoi=0, *args, **kwargs):
    inputNodes = [
      Nodes.InputNode(name="frA", component=self, xPos=0, yPos=-height/2, azimuth=aoi+90),
      Nodes.InputNode(name="frB", component=self, xPos=width/2, yPos=0, azimuth=aoi+180),
      Nodes.InputNode(name="bkA", component=self, xPos=-width/2, yPos=0, azimuth=aoi),
      Nodes.InputNode(name="bkB", component=self, xPos=0, yPos=height/2, azimuth=aoi+270)
    ]
    
    outputNodes = [
      Nodes.OutputNode(name="frA", component=self, xPos=width/2, yPos=0, azimuth=-aoi),
      Nodes.OutputNode(name="frB", component=self, xPos=0, yPos=-height/2, azimuth=270-aoi),
      Nodes.OutputNode(name="bkA", component=self, xPos=0, yPos=height/2, azimuth=90-aoi),
      Nodes.OutputNode(name="bkB", component=self, xPos=-width/2, yPos=0, azimuth=180-aoi)
    ]
    
    super(BeamSplitter, self).__init__(filename=filename, width=width, height=height, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Laser(Source):
  def __init__(self, filename="c-laser1.svg", width=62, height=46, *args, **kwargs):
    outputNode = Nodes.OutputNode(name="out", component=self, xPos=-width/2, yPos=0, azimuth=180)
    
    super(Laser, self).__init__(filename=filename, width=width, height=height, outputNode=outputNode, *args, **kwargs)