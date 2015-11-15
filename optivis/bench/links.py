from __future__ import unicode_literals, division

import abc
import math

import optivis.bench
import optivis.geometry
import nodes
import labels

class AbstractLink(optivis.bench.AbstractBenchItem):
  __metaclass__ = abc.ABCMeta

  def __init__(self, outputNode, inputNode, length=None, start=None, end=None, specs=None, *args, **kwargs):
    self.outputNode = outputNode
    self.inputNode = inputNode
    self.length = length
    
    if start is None:
      start = optivis.geometry.Coordinates(0, 0)
    
    if end is None:
      end = optivis.geometry.Coordinates(0, 0)

    if specs is None:
      # default link spec
      specs = LinkSpec()

    self.start = start
    self.end = end
    self.specs = specs

    # check we've not linked one component to itself
    if self.outputNode.component == self.inputNode.component:
      raise Exception('Cannot link component directly to itself')
    
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
    if component in self.getComponents():
      return True
    
    return False
  
  def getComponents(self):
    return [self.outputNode.component, self.inputNode.component]

  def getNodesForCommonComponent(self, otherLink):
    thisOutputComponent = self.outputNode.component
    thisInputComponent = self.inputNode.component
    
    otherOutputComponent = otherLink.outputNode.component
    otherInputComponent = otherLink.inputNode.component
    
    # gets common component shared with other link
    if thisOutputComponent is otherOutputComponent:
      return (thisOutputComponent, self.outputNode, otherLink.outputNode)
    elif thisOutputComponent is otherInputComponent:
      return (thisOutputComponent, self.outputNode, otherLink.inputNode)
    elif thisInputComponent is otherOutputComponent:
      return (thisInputComponent, self.inputNode, otherLink.outputNode)
    elif thisInputComponent is otherInputComponent:
      return (thisInputComponent, self.inputNode, otherLink.inputNode)
    else:
      raise Exception('Specified other link does not share a common component with this link')
  
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
    if length is not None:
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

  @property
  def specs(self):
    return self.__specs

  @specs.setter
  def specs(self, specs):
    if isinstance(specs, LinkSpec):
      self.__specs = [specs]
    elif isinstance(specs, (list, tuple)):
      if not all(isinstance(spec, LinkSpec) for spec in specs):
        raise Exception('A specified spec is not of type LinkSpec')

      self.__specs = specs
    else:
      raise Exception('Specified specs is not a LinkSpec or a list of LinkSpec objects')

class Link(AbstractLink):
  def __init__(self, *args, **kwargs):
    super(Link, self).__init__(*args, **kwargs)

class LinkSpec(object):
  def __init__(self, width=1.0, color="red", pattern=None, offset=0, startMarker=False, endMarker=False, startMarkerRadius=3, endMarkerRadius=2, startMarkerColor="red", endMarkerColor="blue", *args, **kwargs):
    self.width = width
    self.color = color
    self.pattern = pattern
    self.offset = offset
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor

    super(LinkSpec, self).__init__(*args, **kwargs)
    
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
  def pattern(self):
    return self.__pattern
  
  @pattern.setter
  def pattern(self, pattern):
    if pattern is None:
      pattern = []
    else:
      # check that input is a list
      if not isinstance(pattern, list):
        raise Exception('Specified pattern is not a list')
  
      # check that list is an even number (a pattern must be a series of dash-space pairs)
      if len(pattern) % 2 is not 0:
        raise Exception('Specified pattern list must contain an even number of elements')
    
      # check elements are integers
      if not all(isinstance(item, float) or isinstance(item, int) for item in pattern):
        raise Exception('Specified pattern list must only contain elements of type int or float')
    
    self.__pattern = pattern

  @property
  def offset(self):
    return self.__offset

  @offset.setter
  def offset(self, offset):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    offset = float(offset)
    
    self.__offset = offset