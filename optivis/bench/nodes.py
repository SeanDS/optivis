from __future__ import unicode_literals, division

import abc

import optivis.geometry
import components

class Node(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, name, component, position, aoiMultiplier=1, aoiOffset=0):
    """
    position is normalised to the component's dimensions (i.e. usually between -0.5 and 0.5)
    
    aoiMultiplier is the constant to multiply the component angle of incidence by
    aoiOffset is the offset to add to the component angle of incidence
    """
    
    self.name = name
    self.component = component
    self.position = position
    self.aoiMultiplier = aoiMultiplier
    self.aoiOffset = aoiOffset
  
  def getNodeAzimuth(self):
    aoi = self.component.aoi
    
    return self.aoiMultiplier * aoi + self.aoiOffset
  
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
  def aoiMultiplier(self):
    return self.__aoiMultiplier
  
  @aoiMultiplier.setter
  def aoiMultiplier(self, aoiMultiplier):
    self.__aoiMultiplier = aoiMultiplier
    
  @property
  def aoiOffset(self):
    return self.__aoiOffset
  
  @aoiOffset.setter
  def aoiOffset(self, aoiOffset):
    self.__aoiOffset = aoiOffset

  @abc.abstractmethod
  def __str__(self):
    return
  
  def getRelativePosition(self):
    """
    Get position of node with respect to component's center
    """
    
    return (self.position * self.component.size).rotate(self.component.azimuth)
  
  def getAbsolutePosition(self):
    """
    Return position of node taking account of node's component's position
    """
    
    return self.component.position.translate(self.getRelativePosition())
  
  def getAbsoluteAzimuth(self):
    return self.component.azimuth + self.getNodeAzimuth()
  
  def setAbsolutePosition(self, nodeAbsolutePosition):
    """
    Set position of component based on position of node
    """
    
    # component position
    self.component.position = nodeAbsolutePosition.translate(self.getRelativePosition().flip())
  
  def setAbsoluteAzimuth(self, absoluteAzimuth):
    """
    Set azimuth of component based on azimuth of node
    """
    
    self.component.azimuth = absoluteAzimuth - self.getNodeAzimuth()

class InputNode(Node):
  def __init__(self, *args, **kwargs):
    super(InputNode, self).__init__(*args, **kwargs)

  def __str__(self):
    return "{0}<-{1}".format(self.component, self.name)

class OutputNode(Node):
  def __init__(self, *args, **kwargs):
    super(OutputNode, self).__init__(*args, **kwargs)

  def __str__(self):
    return "{0}->{1}".format(self.component, self.name)