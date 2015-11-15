from __future__ import unicode_literals, division

import abc

from optivis.bench import AbstractBenchItem
from optivis.bench.links import AbstractLink

class AbstractConstraint():
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, componentA, componentB):
    self.componentA = componentA
    self.componentB = componentB
    
  @property
  def componentA(self):
    return self.__componentA
  
  @componentA.setter
  def componentA(self, component):
    if not isinstance(component, AbstractBenchItem):
      raise Exception('Specified component is not of type AbstractBenchItem')
    
    self.__componentA = component

  @property
  def componentB(self):
    return self.__componentB
  
  @componentB.setter
  def componentB(self, component):
    if not isinstance(component, AbstractBenchItem):
      raise Exception('Specified component is not of type AbstractBenchItem')
    
    self.__componentB = component
  
  @abc.abstractmethod
  def constrain(self):
    pass
  
  @abc.abstractmethod
  def constrains(self, benchItem):
    """
    Does this constraint involve the specified bench item?
    """
    pass

class AbstractLinkConstraint(AbstractConstraint):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, linkA, linkB):
    if not isinstance(linkA, AbstractLink) or not isinstance(linkB, AbstractLink):
      raise Exception('A specified link is not of type AbstractLink')
    
    super(AbstractLinkConstraint, self).__init__(componentA=linkA, componentB=linkB)
  
  @property
  def linkA(self):
    return self.componentA
  
  @property
  def linkB(self):
    return self.componentB
  
  def getCommonComponent(self):
    return self.linkA.getNodesForCommonComponent(self.linkB)[0]
  
  def constrains(self, benchItem):
    """
    Does this constraint involve the specified bench item?
    """
    
    #TODO: type checking
    
    return benchItem is self.getCommonComponent()

class LinkAngularConstraint(AbstractLinkConstraint):
  def __init__(self, angle, *args, **kwargs):
    super(LinkAngularConstraint, self).__init__(*args, **kwargs)
    
    self.angle = angle
    
  @property
  def angle(self):
    return self.__angle
  
  @angle.setter
  def angle(self, angle):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    angle = float(angle) % 360
    
    self.__angle = angle
  
  def constrain(self):
    # set common component's angle of incidence
    (component, nodeA, nodeB) = self.linkA.getNodesForCommonComponent(self.linkB)
    
    # get angle of incidence required for this constraint
    aoi = component.getAoiForConstrainedNodeAngle(nodeA, nodeB, self.angle)
    
    component.aoi = aoi