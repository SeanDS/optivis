from __future__ import division
import math
import abc

import Optivis
import Nodes

class BenchObject(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    # nothing to do
    return
  
  def __eq__(self, other):
    return self.__dict__ == other.__dict__
    #return self.filename == other.filename and self.width == other.width and self.height = other.height # FIXME: check also for inputNodes, etc

class Link(BenchObject):
  def __init__(self, outputNode, inputNode, length, width=1.0, colour="red"):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    self.width = width
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
  def width(self):
    return self.__width

  @width.setter
  def width(self, width):
    if width < 0:
      raise Exception('Specified width is invalid')
    
    self.__width = width
  
  @property
  def colour(self):
    return self.__colour
  
  @colour.setter
  def colour(self, colour):
    #FIXME: check for valid colours here
    self.__colour = colour

class Component(BenchObject):
  __metaclass__ = abc.ABCMeta
  
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
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, outputNode, *args, **kwargs):    
    inputNodes = []
    outputNodes = [outputNode]
    
    super(Source, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Laser(Source):
  def __init__(self, *args, **kwargs):
    filename = "c-laser1.svg"
    size = Optivis.Coordinates(62, 46)
    
    outputNode = Nodes.OutputNode(name="out", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=180)
    
    super(Laser, self).__init__(filename=filename, size=size, outputNode=outputNode, *args, **kwargs)

class Mirror(Component):
  __metaclass__ = abc.ABCMeta
  
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

class Lens(Component):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Lens, self).__init__(*args, **kwargs)

class ConvexLens(Lens):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-lens2.svg"
    size = Optivis.Coordinates(9, 23)
    
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
    
    super(ConvexLens, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class ConcaveLens(Lens):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-lens3.svg"
    size = Optivis.Coordinates(9, 23)
    
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
    
    super(ConcaveLens, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Plate(Component):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Plate, self).__init__(*args, **kwargs)

class QuarterWavePlate(Plate):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-wpred.svg" # FIXME: is this the 'standard' colour for a QWP?
    size = Optivis.Coordinates(5, 23)
    
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
    
    super(QuarterWavePlate, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class HalfWavePlate(Plate):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-wpgn.svg" # FIXME: is this the 'standard' colour for a HWP?
    size = Optivis.Coordinates(5, 23)
    
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
    
    super(HalfWavePlate, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Modulator(Component):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Modulator, self).__init__(*args, **kwargs)
    
class ElectroopticModulator(Modulator):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "c-eom2.svg"
    size = Optivis.Coordinates(32, 32)
    
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
    
    super(ElectroopticModulator, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class FaradayIsolator(Component):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "c-isolator.svg"
    size = Optivis.Coordinates(52, 23)
    
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
    
    super(FaradayIsolator, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Sink(Component):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, inputNode, *args, **kwargs):    
    outputNodes = []
    inputNodes = [inputNode]
    
    super(Sink, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
 
class Photodiode(Sink):
  def __init__(self, *args, **kwargs):
    filename = "e-pd1.svg"
    size = Optivis.Coordinates(16, 23)
    
    inputNode = Nodes.InputNode(name="in", component=self, position=Optivis.Coordinates(-0.5, 0), azimuth=0)
    
    super(Photodiode, self).__init__(filename=filename, size=size, inputNode=inputNode, *args, **kwargs)