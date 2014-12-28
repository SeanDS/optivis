from __future__ import division

import abc

import optivis.geometry
import optivis.scene
import optivis.bench.components
import optivis.bench.links

class AbstractGui(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, scene, size=None, azimuth=0, zoom=1.0, startMarker=False, endMarker=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    title = "Optivis - {0}".format(scene.title)
    
    if size is None:
      size = optivis.geometry.Coordinates(500, 500)
      
    if startMarkerColor is None:
      startMarkerColor = "red"
    
    if endMarkerColor is None:
      endMarkerColor = "blue"
    
    self.scene = scene
    self.size = size
    self.azimuth = azimuth
    self.zoom = zoom
    self.title = title
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    return
  
  @abc.abstractmethod
  def createCanvasObjectLists(self):
    return

  @property
  def scene(self):
    return self.__scene

  @scene.setter
  def scene(self, scene):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    self.__scene = scene
  
  @property
  def size(self):
    return self.__size

  @size.setter
  def size(self, size):
    if not isinstance(size, optivis.geometry.Coordinates):
      raise Exception('Specified size is not of type optivis.geometry.Coordinates')
    
    self.__size = size
    
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
    
  @property
  def zoom(self):
    return self.__zoom
  
  @zoom.setter
  def zoom(self, zoom):
    self.__zoom = zoom
    
  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title
    
  @property
  def startMarker(self):
    return self.__startMarker
  
  @startMarker.setter
  def startMarker(self, startMarker):
    self.__startMarker = startMarker
    
  @property
  def endMarker(self):
    return self.__endMarker
  
  @endMarker.setter
  def endMarker(self, endMarker):
    self.__endMarker = endMarker
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerColor(self):
    return self.__startMarkerColor
  
  @startMarkerColor.setter
  def startMarkerColor(self, startMarkerColor):
    self.__startMarkerColor = startMarkerColor
    
  @property
  def endMarkerColor(self):
    return self.__endMarkerColor
  
  @endMarkerColor.setter
  def endMarkerColor(self, endMarkerColor):
    self.__endMarkerColor = endMarkerColor

class AbstractCanvasObject(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    return None

  @abc.abstractmethod
  def draw(self, *args, **kwargs):
    return
  
class AbstractCanvasLink(AbstractCanvasObject):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, link, start, end, startMarker=True, endMarker=True, startMarkerRadius=3, endMarkerRadius=2, startMarkerColor="red", endMarkerColor="blue"):
    
    if start is None:
      # No start position defined, so create a default one.
      start = optivis.geometry.Coordinates(0, 0)
    
    if end is None:
      # No end position defined, so create a default one.
      end = optivis.geometry.Coordinates(0, 0)
    
    self.link = link
    self.start = start
    self.end = end
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    super(AbstractCanvasLink, self).__init__()

  @property
  def link(self):
    return self.__link

  @link.setter
  def link(self, link):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type optivis.bench.links.AbstractLink')
    
    self.__link = link

  @property
  def start(self):
    return self.__start

  @start.setter
  def start(self, start):
    if not isinstance(start, optivis.geometry.Coordinates):
      raise Exception('Specified start is not of type optivis.geometry.Coordinates')
    
    self.__start = start

  @property
  def end(self):
    return self.__end

  @end.setter
  def end(self, end):
    if not isinstance(end, optivis.geometry.Coordinates):
      raise Exception('Specified end is not of type optivis.geometry.Coordinates')
    
    self.__end = end

  @property
  def fill(self):
    return self.__fill

  @fill.setter
  def fill(self, fill):
    self.__fill = fill
    
  @property
  def startMarker(self):
    return self.__startMarker
  
  @startMarker.setter
  def startMarker(self, startMarker):
    self.__startMarker = startMarker
    
  @property
  def endMarker(self):
    return self.__endMarker
  
  @endMarker.setter
  def endMarker(self, endMarker):
    self.__endMarker = endMarker
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerColor(self):
    return self.__startMarkerColor
  
  @startMarkerColor.setter
  def startMarkerColor(self, startMarkerColor):
    self.__startMarkerColor = startMarkerColor
    
  @property
  def endMarkerColor(self):
    return self.__endMarkerColor
  
  @endMarkerColor.setter
  def endMarkerColor(self, endMarkerColor):
    self.__endMarkerColor = endMarkerColor
    
class AbstractCanvasComponent(AbstractCanvasObject):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, component, azimuth=0, position=None):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type optivis.bench.components.AbstractComponent')
    
    if position is None:
      # No position defined, so create a default one.
      position = optivis.geometry.Coordinates(0, 0)

    self.component = component
    self.azimuth = azimuth
    self.position = position

    super(AbstractCanvasComponent, self).__init__()

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
  
  def getBoundingBox(self):
    # get nominal corner positions
    topLeft = self.size * optivis.geometry.Coordinates(-0.5, -0.5)
    topRight = self.size * optivis.geometry.Coordinates(0.5, -0.5)
    bottomLeft = self.size * optivis.geometry.Coordinates(-0.5, 0.5)
    bottomRight = self.size * optivis.geometry.Coordinates(0.5, 0.5)
    
    # rotate corners by azimuth
    topLeft = topLeft.rotate(self.azimuth)
    topRight = topRight.rotate(self.azimuth)
    bottomLeft = bottomLeft.rotate(self.azimuth)
    bottomRight = bottomRight.rotate(self.azimuth)
    
    # find min and max coordinates    
    xPositions = [topLeft.x, topRight.x, bottomLeft.x, bottomRight.x]
    yPositions = [topLeft.y, topRight.y, bottomLeft.y, bottomRight.y]
    
    minPos = optivis.geometry.Coordinates(min(xPositions), min(yPositions))
    maxPos = optivis.geometry.Coordinates(max(xPositions), max(yPositions))
    
    # add global position
    minPos = minPos.translate(self.position)
    maxPos = maxPos.translate(self.position)
    
    return minPos, maxPos
    
  def __str__(self):
    # return component's __str__
    return self.component.__str__()