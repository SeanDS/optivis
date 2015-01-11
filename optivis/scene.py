import datetime
from xml.etree import ElementTree as et

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
  
  def exportSvg(self, path, width, height):
    return
  
  def getSvgElementTree(self, width, height):
    # create document
    document = et.Element('svg', width=width, height=height, version='1.1', xmlns='http://www.w3.org/2000/svg')