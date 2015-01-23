from __future__ import unicode_literals, division

import abc

import optivis.geometry
import nodes

class AbstractLink(object):
  __metaclass__ = abc.ABCMeta
  
  def __str__(self):
    return "{0} --> {1}".format(self.outputNode, self.inputNode)
  
  def hasComponent(self, component):
    if self.outputNode.component is component or self.inputNode.component is component:
      return True
    
    return False
  
class AbstractDrawableLink(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    return None

  @abc.abstractmethod
  def draw(self, *args, **kwargs):
    return

class Link(AbstractLink):
  def __init__(self, outputNode, inputNode, length, width=1.0, color="red", startMarker=False, endMarker=False, startMarkerRadius=3, endMarkerRadius=2, startMarkerColor="red", endMarkerColor="blue"):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    self.width = width
    self.color = color
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    # check we've not linked one component to itself
    if self.outputNode.component == self.inputNode.component:
      raise Exception('Cannot link component directly to itself')
    
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
    
  @property
  def startMarker(self):
    return self.__startMarker
  
  @startMarker.setter
  def startMarker(self, startMarker):
    self.__startMarker = bool(startMarker)
    
  @property
  def endMarker(self):
    return self.__endMarker
  
  @endMarker.setter
  def endMarker(self, endMarker):
    self.__endMarker = bool(endMarker)
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    startMarkerRadius = float(startMarkerRadius)
    
    if startMarkerRadius < 0:
      raise Exception('Start marker radius must be >= 0')
    
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    endMarkerRadius = float(endMarkerRadius)
    
    if endMarkerRadius < 0:
      raise Exception('Start marker radius must be >= 0')
    
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerColor(self):
    return self.__startMarkerColor
  
  @startMarkerColor.setter
  def startMarkerColor(self, startMarkerColor):
    if not isinstance(startMarkerColor, basestring):
      raise Exception('Specified start marker color is not of type basestring')
    
    #FIXME: check for valid colors here
    self.__startMarkerColor = startMarkerColor
    
  @property
  def endMarkerColor(self):
    return self.__endMarkerColor
  
  @endMarkerColor.setter
  def endMarkerColor(self, endMarkerColor):
    if not isinstance(endMarkerColor, basestring):
      raise Exception('Specified end marker color is not of type basestring')
    
    #FIXME: check for valid colors here
    self.__endMarkerColor = endMarkerColor