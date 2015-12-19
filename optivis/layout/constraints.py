from __future__ import unicode_literals, division

import abc

from optivis.bench import AbstractBenchItem
from optivis.layout import AbstractLayout
from optivis.bench.nodes import Node

class AbstractConstraint():
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    self.constrainedNodes = set([])
  
  @abc.abstractmethod
  def constrain(self, layout):    
    self.layout = layout
  
  @property
  def layout(self):
    return self.__layout
  
  @layout.setter
  def layout(self, layout):
    if not isinstance(layout, AbstractLayout):
      raise Exception('Specified layout is not of type AbstractLayout')
    
    self.__layout = layout
  
  @property
  def constrainedNodes(self):
    return self.__constrainedNodes
  
  @constrainedNodes.setter
  def constrainedNodes(self, constrainedNodes):
    if not isinstance(constrainedNodes, set):
      raise Exception('Specified constrained nodes set is not a set')
    
    for node in constrainedNodes:
      if not isinstance(node, Node):
        raise Exception('A node in constrained nodes set is not of type Node')
    
    self.__constrainedNodes = constrainedNodes
  
  def addConstrainedNode(self, node):
    if not isinstance(node, Node):
      raise Exception('Specified node is not of type Node')
    
    self.__constrainedNodes.add(node)

class AbstractLinkConstraint(AbstractConstraint):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, nodeA, nodeB, *args, **kwargs):    
    super(AbstractLinkConstraint, self).__init__(*args, **kwargs)
    
    self.nodeA = nodeA
    self.nodeB = nodeB
  
  @property
  def nodeA(self):
    return self.__nodeA
  
  @nodeA.setter
  def nodeA(self, nodeA):
    if not isinstance(nodeA, Node):
      raise Exception('Specified node is not of type Node')
    
    self.__nodeA = nodeA
    
  @property
  def nodeB(self):
    return self.__nodeB
  
  @nodeB.setter
  def nodeB(self, nodeB):
    if not isinstance(nodeB, Node):
      raise Exception('Specified node is not of type Node')
    
    self.__nodeB = nodeB
    
  def updateConstrainedNodes(self):
    self.addConstrainedNode(self.nodeA)
    self.addConstrainedNode(self.nodeB)

class LinkLengthConstraint(AbstractLinkConstraint):
  def __init__(self, length, *args, **kwargs):
    super(LinkLengthConstraint, self).__init__(*args, **kwargs)
    
    self.length = length
  
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
  
  def constrain(self, *args, **kwargs):
    super(LinkLengthConstraint, self).constrain(*args, **kwargs)
    
    # get Link object between nodes
    # TODO: wrap this in try/catch
    link = self.layout.scene.getLinkFromNodes(self.nodeA, self.nodeB)
    
    # set link length
    link.length = self.length
    
    self.updateConstrainedNodes()

class LinkAngleConstraint(AbstractLinkConstraint):
  def __init__(self, length, *args, **kwargs):
    super(LinkLengthConstraint, self).__init__(*args, **kwargs)
    
    self.angle = angle
  
  @property
  def angle(self):
    return self.__angle
  
  @angle.setter
  def angle(self, angle):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    angle = float(angle) % 360
    
    self.__angle = angle
  
  def constrain(self, *args, **kwargs):
    super(LinkAngleConstraint, self).constrain(*args, **kwargs)
    
    # get Link object between nodes
    # TODO: wrap this in try/catch
    link = self.layout.scene.getLinkFromNodes(self.nodeA, self.nodeB)
    
    # set link angle
    link.angle = self.angle
    
    self.updateConstrainedNodes()