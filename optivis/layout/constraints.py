from __future__ import unicode_literals, division

import abc

from optivis.bench import AbstractBenchItem
from optivis.bench.components import AbstractComponent
from optivis.layout import AbstractLayout
from optivis.bench.nodes import Node

class AbstractConstraint():
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    self.distanceConstrainedNodes = set([])
    self.angleConstrainedComponents = set([])
  
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
  def distanceConstrainedNodes(self):
    return self.__distanceConstrainedNodes
  
  @distanceConstrainedNodes.setter
  def distanceConstrainedNodes(self, distanceConstrainedNodes):
    if not isinstance(distanceConstrainedNodes, set):
      raise Exception('Specified distance constrained nodes set is not a set')
    
    for node in distanceConstrainedNodes:
      if not isinstance(node, Node):
        raise Exception('A node in distance constrained nodes set is not of type Node')
    
    self.__distanceConstrainedNodes = distanceConstrainedNodes
  
  def addDistanceConstrainedNode(self, node):
    if not isinstance(node, Node):
      raise Exception('Specified node is not of type Node')
    
    self.__distanceConstrainedNodes.add(node)
    
  @property
  def angleConstrainedComponents(self):
    return self.__angleConstrainedComponents
  
  @angleConstrainedComponents.setter
  def angleConstrainedComponents(self, angleConstrainedComponents):
    if not isinstance(angleConstrainedComponents, set):
      raise Exception('Specified angle constrained components set is not a set')
    
    for component in angleConstrainedComponents:
      if not isinstance(node, AbstractComponent):
        raise Exception('A component in angle constrained components set is not of type AbstractComponent')
    
    self.__angleConstrainedComponents = angleConstrainedComponents
  
  def addAngleConstrainedComponent(self, component):
    if not isinstance(component, AbstractComponent):
      raise Exception('Component is not of type AbstractComponent')
    
    self.__angleConstrainedComponents.add(component)

class AbstractNodePairConstraint(AbstractConstraint):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, nodeA, nodeB, *args, **kwargs):    
    super(AbstractNodePairConstraint, self).__init__(*args, **kwargs)
    
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

class LinkLengthConstraint(AbstractNodePairConstraint):
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

  def __str__(self):
    return "Length({0}, {1}) = {2}".format(self.nodeA, self.nodeB, self.length)
  
  def constrain(self, *args, **kwargs):
    super(LinkLengthConstraint, self).constrain(*args, **kwargs)
    
    # get Link object between nodes
    # TODO: wrap this in try/catch
    link = self.layout.scene.getLinkFromNodes(self.nodeA, self.nodeB)
    
    # set link length
    link.length = self.length
    
    self.updateConstrainedNodes()
    
  def updateConstrainedNodes(self):
    self.addDistanceConstrainedNode(self.nodeA)
    self.addDistanceConstrainedNode(self.nodeB)

class NodeAngleConstraint(AbstractNodePairConstraint):
  def __init__(self, angle, *args, **kwargs):    
    super(NodeAngleConstraint, self).__init__(*args, **kwargs)
    
    # check that the specified nodes are for the same component
    if self.nodeA.component is not self.nodeB.component:
      raise Exception('Specified nodes are not for the same component')
    
    self.angle = angle
    
    # check whether the constraint is possible
    try:
      self.getComponentAoi()
    except Exception as e:
      # for now we just throw it again
      raise e
  
  @property
  def angle(self):
    return self.__angle
  
  @angle.setter
  def angle(self, angle):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    angle = float(angle) % 360
    
    self.__angle = angle
  
  @property
  def component(self):
    return self.nodeA.component
  
  def __str__(self):
    return "Angle({0}, {1}) = {2}".format(self.nodeA, self.nodeB, self.angle)
  
  def constrain(self, *args, **kwargs):
    super(NodeAngleConstraint, self).constrain(*args, **kwargs)
    
    self.component.aoi = self.getComponentAoi()
    
    self.updateConstrainedNodes()
  
  def getComponentAoi(self):
    # TODO: make this a more descriptive error (e.g. the offsets are 180 degrees apart, or the multipliers are equal and opposite)
    
    try:
      aoi = (self.angle - self.nodeA.aoiOffset + self.nodeB.aoiOffset) / (self.nodeA.aoiMultiplier - self.nodeB.aoiMultiplier)
    except ZeroDivisionError:
      raise Exception('Specified constraint is impossible')
    
    return aoi

  def updateConstrainedNodes(self):
    self.addAngleConstrainedComponent(self.component)