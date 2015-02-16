from __future__ import unicode_literals, division

import os
import math
import abc

import optivis.geometry
import nodes

class AbstractComponent(object):
  __metaclass__ = abc.ABCMeta
  
  svgDir = os.path.join(os.path.dirname(__file__), '..', 'assets')
  
  def __init__(self, filename, size, inputNodes, outputNodes, azimuth=0, name=None, position=None):
    if name is None:
      # empty name
      name = ''
    
    if position is None:
      position = optivis.geometry.Coordinates(0, 0)
    
    self.name = name
    self.filename = filename
    self.size = size
    self.inputNodes = inputNodes
    self.outputNodes = outputNodes
    self.azimuth = azimuth
    self.position = position
    
  def __eq__(self, other):
    return self.__dict__ == other.__dict__
  
  def getBoundingBox(self):
    # get nominal corner positions
    topLeft = self.size * optivis.geometry.Coordinates(-0.5, -0.5)
    topRight = self.size * optivis.geometry.Coordinates(0.5, -0.5)
    bottomLeft = self.size * optivis.geometry.Coordinates(-0.5, 0.5)
    bottomRight = self.size * optivis.geometry.Coordinates(0.5, 0.5)
    
    # rotate corners by azimuth
    topLeft = topLeft.rotate(self.azimuth)
    topRight = topRight.rotate(self.azimuth)
    bottomLeft = bottomLeft.rotate(self.azimuth)
    bottomRight = bottomRight.rotate(self.azimuth)
    
    # find min and max coordinates    
    xPositions = [topLeft.x, topRight.x, bottomLeft.x, bottomRight.x]
    yPositions = [topLeft.y, topRight.y, bottomLeft.y, bottomRight.y]
    
    minPos = optivis.geometry.Coordinates(min(xPositions), min(yPositions))
    maxPos = optivis.geometry.Coordinates(max(xPositions), max(yPositions))
    
    # add global position
    minPos = minPos.translate(self.position)
    maxPos = maxPos.translate(self.position)
    
    return minPos, maxPos
  
  @property
  def name(self):
    return self.__name
  
  @name.setter
  def name(self, name):
    if not isinstance(name, basestring):
      raise Exception('Specified name is not of type basestring')
    
    self.__name = name
  
  @property
  def filename(self):
    return self.__filename
  
  @filename.setter
  def filename(self, filename):
    if not isinstance(filename, basestring):
      raise Exception('Specified filename is not of type basestring')
    
    self.__filename = filename
    
  @property
  def size(self):
    return self.__size
  
  @size.setter
  def size(self, size):
    # check size is valid object
    if not isinstance(size, optivis.geometry.Coordinates):
      raise Exception('Specified size is not of type optivis.geometry.Coordinates')
    
    # check size coordinates are positive
    if size.x < 0 or size.y < 0:
      raise Exception('Size dimensions must be positive')
    
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
    
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    azimuth = float(azimuth)
    
    self.__azimuth = azimuth
    
  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):
    if not isinstance(position, optivis.geometry.Coordinates):
      raise Exception('Specified position is not of type optivis.geometry.Coordinates')
    
    self.__position = position
  
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
  
class AbstractDrawableComponent(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    return None

  @abc.abstractmethod
  def draw(self, *args, **kwargs):
    return

class Source(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, outputNode, *args, **kwargs):
    inputNodes = []
    outputNodes = [outputNode]
    
    super(Source, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Laser(Source):
  def __init__(self, *args, **kwargs):
    filename = "c-laser1.svg"
    size = optivis.geometry.Coordinates(62, 46)
    
    outputNode = nodes.OutputNode(name="out", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0)
    
    super(Laser, self).__init__(filename=filename, size=size, outputNode=outputNode, *args, **kwargs)

class Mirror(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Mirror, self).__init__(*args, **kwargs)

class CavityMirror(Mirror):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-cav-mir.svg"
    size = optivis.geometry.Coordinates(11, 29)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=180-aoi),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=-aoi)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180+aoi)
    ]
    
    super(CavityMirror, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class SteeringMirror(Mirror):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-mir.svg"
    size = optivis.geometry.Coordinates(11, 29)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi)
    ]
    
    super(SteeringMirror, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitter(Mirror):
  def __init__(self, aoi=45, *args, **kwargs):
    filename = "b-bsp.svg"
    size = optivis.geometry.Coordinates(11, 29)
    
    inputNodes = [
      nodes.InputNode(name="frA", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=180-aoi),
      nodes.InputNode(name="frB", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=180+aoi),
      nodes.InputNode(name="bkA", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi),
      nodes.InputNode(name="bkB", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=-aoi)
    ]
    
    outputNodes = [
      nodes.OutputNode(name="frA", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi),
      nodes.OutputNode(name="frB", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=-aoi),
      nodes.OutputNode(name="bkA", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bkB", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180+aoi)
    ]
    
    super(BeamSplitter, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class BeamSplitterCube(Mirror):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-bspcube.svg"
    size = optivis.geometry.Coordinates(23, 23)
    
    inputNodes = [
      nodes.InputNode(name="frA", component=self, position=optivis.geometry.Coordinates(0, -0.5), azimuth=aoi+90),
      nodes.InputNode(name="frB", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180),
      nodes.InputNode(name="bkA", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi),
      nodes.InputNode(name="bkB", component=self, position=optivis.geometry.Coordinates(0, 0.5), azimuth=aoi+270)
    ]
    
    outputNodes = [
      nodes.OutputNode(name="frA", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=-aoi),
      nodes.OutputNode(name="frB", component=self, position=optivis.geometry.Coordinates(0, -0.5), azimuth=270-aoi),
      nodes.OutputNode(name="bkA", component=self, position=optivis.geometry.Coordinates(0, 0.5), azimuth=90-aoi),
      nodes.OutputNode(name="bkB", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi)
    ]
    
    super(BeamSplitterCube, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Lens(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Lens, self).__init__(*args, **kwargs)

class ConvexLens(Lens):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-lens2.svg"
    size = optivis.geometry.Coordinates(9, 23)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0-aoi)
    ]
    
    super(ConvexLens, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class ConcaveLens(Lens):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-lens3.svg"
    size = optivis.geometry.Coordinates(9, 23)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.35, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.35, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.35, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.35, 0), azimuth=0-aoi)
    ]
    
    super(ConcaveLens, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Plate(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Plate, self).__init__(*args, **kwargs)

class QuarterWavePlate(Plate):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-wpred.svg" # FIXME: is this the 'standard' colour for a QWP?
    size = optivis.geometry.Coordinates(5, 23)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0-aoi)
    ]
    
    super(QuarterWavePlate, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class HalfWavePlate(Plate):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "b-wpgn.svg" # FIXME: is this the 'standard' colour for a HWP?
    size = optivis.geometry.Coordinates(5, 23)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0-aoi)
    ]
    
    super(HalfWavePlate, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
    
class Modulator(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, *args, **kwargs):
    super(Modulator, self).__init__(*args, **kwargs)
    
class ElectroopticModulator(Modulator):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "c-eom2.svg"
    size = optivis.geometry.Coordinates(32, 32)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0-aoi)
    ]
    
    super(ElectroopticModulator, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class AcoustoopticModulator(Modulator):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "c-aom.svg"
    size = optivis.geometry.Coordinates(43, 27)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0.1), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0.1), azimuth=aoi+180)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0.1), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0.1), azimuth=0-aoi)
    ]
    
    super(AcoustoopticModulator, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class FaradayIsolator(AbstractComponent):
  def __init__(self, aoi=0, *args, **kwargs):
    filename = "c-isolator.svg"
    size = optivis.geometry.Coordinates(52, 23)
    
    inputNodes = [
      # input node azimuth defined WRT input light direction
      nodes.InputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=aoi+0),
      nodes.InputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=aoi+180),
      nodes.InputNode(name="frPoA", component=self, position=optivis.geometry.Coordinates(-0.35, -0.1), azimuth=90+aoi),
      nodes.InputNode(name="frPoB", component=self, position=optivis.geometry.Coordinates(-0.35, 0.1), azimuth=-90-aoi),
      nodes.InputNode(name="bkPoA", component=self, position=optivis.geometry.Coordinates(0.35, -0.1), azimuth=-90-aoi),
      nodes.InputNode(name="bkPoB", component=self, position=optivis.geometry.Coordinates(0.35, 0.1), azimuth=-90+aoi)
    ]
    
    outputNodes = [
      # output node azimuth defined WRT output light direction
      nodes.OutputNode(name="fr", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=180-aoi),
      nodes.OutputNode(name="bk", component=self, position=optivis.geometry.Coordinates(0.5, 0), azimuth=0-aoi),
      nodes.OutputNode(name="frPoA", component=self, position=optivis.geometry.Coordinates(-0.35, -0.1), azimuth=90-aoi),
      nodes.OutputNode(name="frPoB", component=self, position=optivis.geometry.Coordinates(-0.35, 0.1), azimuth=270+aoi),
      nodes.OutputNode(name="bkPoA", component=self, position=optivis.geometry.Coordinates(0.35, -0.1), azimuth=270+aoi),
      nodes.OutputNode(name="bkPoB", component=self, position=optivis.geometry.Coordinates(0.35, 0.1), azimuth=90-aoi)
    ]
    
    super(FaradayIsolator, self).__init__(filename=filename, size=size, inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)

class Sink(AbstractComponent):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, inputNode, *args, **kwargs):    
    outputNodes = []
    inputNodes = [inputNode]
    
    super(Sink, self).__init__(inputNodes=inputNodes, outputNodes=outputNodes, *args, **kwargs)
 
class Photodiode(Sink):
  def __init__(self, *args, **kwargs):
    filename = "e-pd1.svg"
    size = optivis.geometry.Coordinates(16, 23)
    
    inputNode = nodes.InputNode(name="in", component=self, position=optivis.geometry.Coordinates(-0.5, 0), azimuth=0)
    
    super(Photodiode, self).__init__(filename=filename, size=size, inputNode=inputNode, *args, **kwargs)