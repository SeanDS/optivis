import abc

import nodes

class AbstractLink(object):
  __metaclass__ = abc.ABCMeta

class Link(AbstractLink):
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
