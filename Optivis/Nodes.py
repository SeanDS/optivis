from __future__ import division
import BenchObjects

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
    if not isinstance(component, BenchObjects.Component):
      raise Exception('Specified component is not of type BenchObjects.Component')
    
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