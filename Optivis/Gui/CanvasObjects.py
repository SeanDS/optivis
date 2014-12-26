from __future__ import division
import os
import abc

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

import Optivis
import Optivis.BenchObjects

class CanvasObject(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self):
    return None

  @abc.abstractmethod
  def draw(self, *args, **kwargs):
    return

class CanvasComponent(CanvasObject):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, component, azimuth=0, position=None):
    if not isinstance(component, Optivis.BenchObjects.Component):
      raise Exception('Specified component is not of type Optivis.BenchObjects.Component')
    
    if position is None:
      # No position defined, so create a default one.
      position = Optivis.Coordinates(0, 0)

    self.component = component
    self.azimuth = azimuth
    self.position = position

    super(CanvasComponent, self).__init__()

  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):
    if not isinstance(position, Optivis.Coordinates):
      raise Exception('Specified position is not of type Optivis.Coordinates')
    
    self.__position = position
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
  
  def getBoundingBox(self):
    # get nominal corner positions
    topLeft = self.size * Optivis.Coordinates(-0.5, -0.5)
    topRight = self.size * Optivis.Coordinates(0.5, -0.5)
    bottomLeft = self.size * Optivis.Coordinates(-0.5, 0.5)
    bottomRight = self.size * Optivis.Coordinates(0.5, 0.5)
    
    # rotate corners by azimuth
    topLeft = topLeft.rotate(self.azimuth)
    topRight = topRight.rotate(self.azimuth)
    bottomLeft = bottomLeft.rotate(self.azimuth)
    bottomRight = bottomRight.rotate(self.azimuth)
    
    # find min and max coordinates    
    xPositions = [topLeft.x, topRight.x, bottomLeft.x, bottomRight.x]
    yPositions = [topLeft.y, topRight.y, bottomLeft.y, bottomRight.y]
    
    minPos = Optivis.Coordinates(min(xPositions), min(yPositions))
    maxPos = Optivis.Coordinates(max(xPositions), max(yPositions))
    
    # add global position
    minPos = minPos.translate(self.position)
    maxPos = maxPos.translate(self.position)
    
    return minPos, maxPos
    
  def __str__(self):
    # return component's __str__
    return self.component.__str__()

class QtCanvasComponent(CanvasComponent):  
  def __init__(self, *args, **kwargs):
    super(QtCanvasComponent, self).__init__(*args, **kwargs)
  
  def draw(self, scene):
    # Create full system path from filename and SVG directory.
    path = os.path.join(self.component.svgDir, self.component.filename)
    
    # Create graphical representation of SVG image at path.
    svgItem = PyQt4.QtSvg.QGraphicsSvgItem(path)
    
    # Set position of top-left corner.
    # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
    svgItem.setPos(self.position.x - self.component.size.x / 2, self.position.y - self.component.size.y / 2)
    
    # Rotate clockwise.
    # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
    svgItem.translate(self.component.size.x / 2, self.component.size.y / 2)
    svgItem.rotate(self.azimuth)
    svgItem.translate(-self.component.size.x / 2, -self.component.size.y / 2)
    
    scene.addItem(svgItem)

class CanvasLink(CanvasObject):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, link, start, end, startMarker=True, endMarker=True, startMarkerRadius=3, endMarkerRadius=2, startMarkerColor="red", endMarkerColor="blue"):
    
    if start is None:
      # No start position defined, so create a default one.
      start = Optivis.Coordinates(0, 0)
    
    if end is None:
      # No end position defined, so create a default one.
      end = Optivis.Coordinates(0, 0)
    
    self.link = link
    self.start = start
    self.end = end
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    super(CanvasLink, self).__init__()

  @property
  def link(self):
    return self.__link

  @link.setter
  def link(self, link):
    if not isinstance(link, Optivis.BenchObjects.Link):
      raise Exception('Specified link is not of type Link')
    
    self.__link = link

  @property
  def start(self):
    return self.__start

  @start.setter
  def start(self, start):
    if not isinstance(start, Optivis.Coordinates):
      raise Exception('Specified start is not of type Optivis.Coordinates')
    
    self.__start = start

  @property
  def end(self):
    return self.__end

  @end.setter
  def end(self, end):
    if not isinstance(end, Optivis.Coordinates):
      raise Exception('Specified end is not of type Optivis.Coordinates')
    
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

class QtCanvasLink(CanvasLink):
  def __init__(self, *args, **kwargs):    
    super(QtCanvasLink, self).__init__(*args, **kwargs)

  def draw(self, scene):
    pen = PyQt4.QtGui.QPen(PyQt4.QtCore.Qt.red, self.link.width, PyQt4.QtCore.Qt.SolidLine)
    line = PyQt4.QtGui.QGraphicsLineItem(self.start.x, self.start.y, self.end.x, self.end.y)
    line.setPen(pen)
    
    # add line to graphics scene
    scene.addItem(line)
    
    # add markers if necessary
    if self.startMarker:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.start.x - self.startMarkerRadius, self.start.y - self.startMarkerRadius, self.startMarkerRadius * 2, self.startMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(self.startMarkerColor, 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      scene.addItem(circle)
      
    if self.endMarker:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.end.x - self.endMarkerRadius, self.end.y - self.endMarkerRadius, self.endMarkerRadius * 2, self.endMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(self.endMarkerColor, 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      scene.addItem(circle)