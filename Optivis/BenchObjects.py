from __future__ import division
import math

import Optivis
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
  svgDir = 'svg'
  
  def __init__(self, name, filename, size, inputNodes, outputNodes):
    self.name = name
    self.filename = filename
    self.size = size
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
  def size(self):
    return self.__size
  
  @size.setter
  def size(self, size):
    if not isinstance(size, Optivis.Coordinates):
      raise Exception('Specified size is not of type Optivis.Coordinates')
    
    self.__size = size
  
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
  
  def getInputNode(self, nodeName):
    for node in self.inputNodes:
      if node.name is nodeName:
	return node
    
    raise Exception('No input node with name {0} found'.format(nodeName))
  
  def getOutputNode(self, nodeName):
    for node in self.outputNodes:
      if node.name is nodeName:
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
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-mir.svg"
    size = Optivis.Coordinates(11, 29)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      Nodes.InputNode(name="fr", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=aoi+0),
      Nodes.InputNode(name="bk", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      Nodes.OutputNode(name="fr", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180-aoi),
      Nodes.OutputNode(name="bk", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=0-aoi)
    ]
    
    super(CavityMirror, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitter(Mirror):
  def __init__(self, aoi=-45, *args, **kwargs):
    filename = "b-bsp.svg"
    size = Optivis.Coordinates(11, 29)
    
    inputNodes = [
      Nodes.InputNode(name="frA", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=aoi),
      Nodes.InputNode(name="frB", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=-aoi),
      Nodes.InputNode(name="bkA", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=180-aoi),
      Nodes.InputNode(name="bkB", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=180+aoi)
    ]
    
    outputNodes = [
      Nodes.OutputNode(name="frA", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180-aoi),
      Nodes.OutputNode(name="frB", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180+aoi),
      Nodes.OutputNode(name="bkA", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=aoi),
      Nodes.OutputNode(name="bkB", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=-aoi)
    ]
    
    super(BeamSplitter, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitterCube(Mirror):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-bspcube.svg"
    size = Optivis.Coordinates(23, 23)
    
    inputNodes = [
      Nodes.InputNode(name="frA", component=self, position=Optivis.Coordinates(0, -0.5), azimuth=aoi+90),
      Nodes.InputNode(name="frB", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=aoi+180),
      Nodes.InputNode(name="bkA", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=aoi),
      Nodes.InputNode(name="bkB", component=self, position=Optivis.Coordinates(0, 0.5), azimuth=aoi+270)
    ]
    
    outputNodes = [
      Nodes.OutputNode(name="frA", component=self, position=Optivis.Coordinates(0.5, 0), azimuth=-aoi),
      Nodes.OutputNode(name="frB", component=self, position=Optivis.Coordinates(0, -0.5), azimuth=270-aoi),
      Nodes.OutputNode(name="bkA", component=self, position=Optivis.Coordinates(0, 0.5), azimuth=90-aoi),
      Nodes.OutputNode(name="bkB", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180-aoi)
    ]
    
    super(BeamSplitter, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Laser(Source):
  def __init__(self, *args, **kwargs):
    filename = "c-laser1.svg"
    size = Optivis.Coordinates(62, 46)
    
    outputNode = Nodes.OutputNode(name="out", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180)
    
    super(Laser, self).__init__(filename=filename, size=size, outputNode=outputNode, *args, **kwargs)