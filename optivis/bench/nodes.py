from __future__ import unicode_literals, division

import optivis.geometry
import components

class Node(object):  
  def __init__(self, name, component, position, azimuth):
    """
    position is normalised to the component's dimensions (i.e. usually between -0.5 and 0.5)
    """
    
    self.name = name
    self.component = component
    self.position = position
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
    if not isinstance(component, components.AbstractComponent):
      raise Exception('Specified component is not of type components.AbstractComponent')
    
    self.__component = component
    
  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):
    if not isinstance(position, optivis.geometry.Coordinates):
      raise Exception('Specified position is not of type optivis.geometry.Coordinates')
    
    self.__position = position
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth

  def __str__(self):
    return "{0}->{1}".format(self.component, self.name)

class InputNode(Node):
  def __init__(self, *args, **kwargs):
    super(InputNode, self).__init__(*args, **kwargs)

class OutputNode(Node):
  def __init__(self, *args, **kwargs):
    super(OutputNode, self).__init__(*args, **kwargs)