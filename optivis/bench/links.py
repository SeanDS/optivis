from __future__ import unicode_literals, division

import abc
import math

import optivis.bench
import optivis.geometry
import nodes
import labels

class AbstractLink(optivis.bench.AbstractBenchItem):
  __metaclass__ = abc.ABCMeta

  def __init__(self, outputNode, inputNode, length, start=None, end=None, *args, **kwargs):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    
    if start is None:
      start = optivis.geometry.Coordinates(0, 0)
    
    if end is None:
      end = optivis.geometry.Coordinates(0, 0)
      
    self.start = start
    self.end = end
    
    super(AbstractLink, self).__init__(*args, **kwargs)

  def __str__(self):
    return "{0} --> {1}".format(self.outputNode, self.inputNode)
  
  def getLabelOrigin(self):
    return self.start + (self.end - self.start) / 2
  
  def getLabelAzimuth(self):
    size = self.end - self.start
    
    if size.y == 0:
      # avoid division by zero
      return 0
    
    return math.degrees(math.atan2(size.y, size.x))
  
  def getSize(self):
    size = self.end - self.start
    
    return optivis.geometry.Coordinates(math.sqrt(math.pow(size.x, 2) + math.pow(size.y, 2)), 0)
  
  def hasComponent(self, component):
    if self.outputNode.component is component or self.inputNode.component is component:
      return True
    
    return False
  
  @property
  def outputNode(self):
    return self.__outputNode
  
  @outputNode.setter
  def outputNode(self, outputNode):
    if not isinstance(outputNode, nodes.OutputNode):
      raise Exception('Specified output node is not of type nodes.OutputNode')
    
    self.__outputNode = outputNode
  
  @property
  def inputNode(self):
    return self.__inputNode
  
  @inputNode.setter
  def inputNode(self, inputNode):
    if not isinstance(inputNode, nodes.InputNode):
      raise Exception('Specified input node is not of type nodes.InputNode')
    
    self.__inputNode = inputNode
    
  @property
  def length(self):
    return self.__length

  @length.setter
  def length(self, length):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    length = float(length)
    
    if length < 0:
      raise Exception('Length must be greater than or equal to 0')
    
    self.__length = length
    
  @property
  def start(self):
    return self.__start
  
  @start.setter
  def start(self, start):
    if not isinstance(start, optivis.geometry.Coordinates):
      raise Exception('Specified start is not of type optivis.geometry.Coordinates')
    
    self.__start = start
    
  @property
  def end(self):
    return self.__end
  
  @end.setter
  def end(self, end):
    if not isinstance(end, optivis.geometry.Coordinates):
      raise Exception('Specified end is not of type optivis.geometry.Coordinates')
    
    self.__end = end

class Link(AbstractLink):
  def __init__(self, width=1.0, color="red", startMarker=False, endMarker=False, startMarkerRadius=3, endMarkerRadius=2, startMarkerColor="red", endMarkerColor="blue", *args, **kwargs):
    self.width = width
    self.color = color
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor

    super(Link, self).__init__(*args, **kwargs)
    
    # check we've not linked one component to itself
    if self.outputNode.component == self.inputNode.component:
      raise Exception('Cannot link component directly to itself')
    
  @property
  def width(self):
    return self.__width

  @width.setter
  def width(self, width):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    width = float(width)
    
    if width < 0:
      raise Exception('Width must be >= 0')
    
    self.__width = width
  
  @property
  def color(self):
    return self.__color
  
  @color.setter
  def color(self, color):
    if not isinstance(color, basestring):
      raise Exception('Specified color is not of type basestring')
    
    #FIXME: check for valid colors here
    self.__color = color
