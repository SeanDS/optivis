from __future__ import unicode_literals, division

import datetime

import geometry
import bench.components
import bench.links
import layout.constraints

class Scene(object):
  links = []
  constraints = []
  
  def __init__(self, title=None, reference=None, constraints=[]):
    if title is None:
      title = datetime.datetime.now().strftime('%Y-%M-%d %H:%M')
    
    self.title = title
    self.reference = reference
    self.constraints = constraints
  
  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    if not isinstance(title, basestring):
      raise Exception('Specified title is not of type basestring')
    
    self.__title = title
  
  @property
  def reference(self):
    """
    Reference component for layout. The azimuth of this component
    is used as the absolute reference when laying out scenes.
    """
    
    return self.__reference
  
  @reference.setter
  def reference(self, component):    
    if component is not None:
      # check component is valid object
      if not isinstance(component, bench.components.AbstractComponent):
	raise Exception('Specified component is not of type AbstractComponent')
    
    self.__reference = component
    
  @property
  def constraints(self):
    return self.__constraints

  @constraints.setter
  def constraints(self, constraints):
    if isinstance(constraints, layout.constraints.AbstractConstraint):
      self.__constraints = [constraints]
    elif isinstance(constraints, (list, tuple)):
      if not all(isinstance(constraint, layout.constraints.AbstractConstraint) for constraint in constraints):
        raise Exception('A specified constraint is not of type AbstractConstraint')

      self.__constraints = constraints
    else:
      raise Exception('Specified constraints are not an AbstractConstraint or a list of AbstractConstraint objects')
  
  def link(self, *args, **kwargs):
    # create Link object
    link = bench.links.Link(*args, **kwargs)
    
    # add to scene
    self.addLink(link)
    
    # constrain length if specified
    if 'length' in kwargs:
      self.addConstraint(layout.constraints.LinkLengthConstraint(kwargs['length'], nodeA=link.outputNode, nodeB=link.inputNode))
  
  def addLink(self, link):
    if not isinstance(link, bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.links.append(link)
  
  def addConstraint(self, constraint):
    if not isinstance(constraint, layout.constraints.AbstractConstraint):
      raise Exception('Specified constraint is not of type AbstractConstraint')
    
    self.constraints.append(constraint)
  
  def getComponents(self):
    components = []
    # FIXME: change to use sets
    
    for link in self.links:
      if link.inputNode.component not in components:
	components.append(link.inputNode.component)
      
      if link.outputNode.component not in components:
	components.append(link.outputNode.component)

    return components
  
  def getBoundingBox(self):
    # set initial bounds to infinity
    lowerBound = geometry.Coordinates(float('inf'), float('inf'))
    upperBound = geometry.Coordinates(float('-inf'), float('-inf'))
    
    # loop over components to find actual bounds
    for component in self.getComponents():
      (thisLowerBound, thisUpperBound) = component.getBoundingBox()
      
      if thisLowerBound.x < lowerBound.x: lowerBound.x = thisLowerBound.x
      if thisLowerBound.y < lowerBound.y: lowerBound.y = thisLowerBound.y
      if thisUpperBound.x > upperBound.x: upperBound.x = thisUpperBound.x
      if thisUpperBound.y > upperBound.y: upperBound.y = thisUpperBound.y
    
    return (lowerBound, upperBound)
  
  def getSize(self):
    (lowerBound, upperBound) = self.getBoundingBox()
    
    return upperBound.translate(lowerBound.flip())

  def getLinkFromNodes(self, nodeA, nodeB):
    for link in self.links:
      if link.hasNodes(nodeA, nodeB):
        return link
    
    raise Exception('Specified nodes are not present in any link in this scene')