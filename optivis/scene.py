import datetime

import geometry
import bench.components
import bench.links

class Scene(object):
  components = []
  links = []
  
  def __init__(self, title=None, azimuth=0):
    if title is None:
      title = datetime.datetime.now().strftime('%Y-%M-%d %H:%M')
    
    self.title = title
    self.azimuth = azimuth
    
    return
  
  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title
    
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
    
  def addComponent(self, component):
    if not isinstance(component, bench.components.AbstractComponent):
      raise Exception('Specified component is not of type bench.components.AbstractComponent')
    
    self.components.append(component)
  
  def link(self, *args, **kwargs):
    link = bench.links.Link(*args, **kwargs)
    
    self.addLink(link)
  
  def addLink(self, link):
    if not isinstance(link, bench.links.AbstractLink):
      raise Exception('Specified link is not of type bench.links.AbstractLink')
    
    if not link.inputNode.component in self.components:
      raise Exception('Input node component has not been added to table')
    
    if not link.outputNode.component in self.components:
      raise Exception('Output node component has not been added to table')
    
    self.links.append(link)
  
  def getBoundingBox(self):
    # set initial bounds to infinity
    lowerBound = geometry.Coordinates(float('inf'), float('inf'))
    upperBound = geometry.Coordinates(float('-inf'), float('-inf'))
    
    # loop over components to find actual bounds
    for component in self.components:
      (thisLowerBound, thisUpperBound) = component.getBoundingBox()
      
      if thisLowerBound.x < lowerBound.x: lowerBound.x = thisLowerBound.x
      if thisLowerBound.y < lowerBound.y: lowerBound.y = thisLowerBound.y
      if thisUpperBound.x > upperBound.x: upperBound.x = thisUpperBound.x
      if thisUpperBound.y > upperBound.y: upperBound.y = thisUpperBound.y
    
    return (lowerBound, upperBound)