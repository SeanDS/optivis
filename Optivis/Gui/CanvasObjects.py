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
  
  def __init__(self, component, size, azimuth=0, position=None):
    if not isinstance(component, Optivis.BenchObjects.Component):
      raise Exception('Specified component is not of type Optivis.BenchObjects.Component')
    
    if position is None:
      position = Optivis.Coordinates(0, 0)

    self.component = component
    self.size = size
    self.azimuth = azimuth
    self.position = position

    super(CanvasComponent, self).__init__()

  @property
  def size(self):
    return self.__size
  
  @size.setter
  def size(self, size):
    self.__size = size

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
    path = os.path.join(self.component.svgDir, self.component.filename)
    
    svgItem = PyQt4.QtSvg.QGraphicsSvgItem(path)
    svgItem.setPos(self.position.x + self.component.size.x / 2, self.position.y + self.component.size.y / 2)
    #svgItem.setPos(self.position.x, self.position.y)
    svgItem.setTransformOriginPoint(self.component.size.x / 2, self.component.size.y / 2)
    
    transform = PyQt4.QtGui.QTransform()
    transform.rotate(self.azimuth)
    
    # rotate about the centre
    svgItem.setTransform(transform)
    
    scene.addItem(svgItem)

class CanvasLink(CanvasObject):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, link, start, end, startMarker=True, endMarker=True, startMarkerRadius=3, endMarkerRadius=2, startMarkerOutline="red", endMarkerOutline="blue"):    
    self.link = link
    self.start = start
    self.end = end
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerOutline = startMarkerOutline
    self.endMarkerOutline = endMarkerOutline
    
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
  def startMarkerOutline(self):
    return self.__startMarkerOutline
  
  @startMarkerOutline.setter
  def startMarkerOutline(self, startMarkerOutline):
    self.__startMarkerOutline = startMarkerOutline
    
  @property
  def endMarkerOutline(self):
    return self.__endMarkerOutline
  
  @endMarkerOutline.setter
  def endMarkerOutline(self, endMarkerOutline):
    self.__endMarkerOutline = endMarkerOutline

class QtCanvasLink(CanvasLink):  
  def __init__(self, *args, **kwargs):    
    super(QtCanvasLink, self).__init__(*args, **kwargs)

  def draw(self, scene):
    pen = PyQt4.QtGui.QPen(PyQt4.QtCore.Qt.red, self.link.width, PyQt4.QtCore.Qt.SolidLine)
    line = PyQt4.QtGui.QGraphicsLineItem(self.start.x, self.start.y, self.end.x, self.end.y)
    line.setPen(pen)
    
    scene.addItem(line)
    
    # add markers if necessary
    #if self.startMarker:
      #painter.setPen(PyQt4.QtGui.QPen(PyQt4.QtCore.Qt.red, 1, PyQt4.QtCore.Qt.SolidLine))      
      #painter.drawEllipse(int(self.start.x - self.startMarkerRadius), int(self.start.y - self.startMarkerRadius), int(self.start.x + self.startMarkerRadius), int(self.start.y + self.startMarkerRadius))
      
    #if self.endMarker:
      #painter.setPen(PyQt4.QtGui.QPen(PyQt4.QtCore.Qt.blue, 2, PyQt4.QtCore.Qt.SolidLine))      
      #painter.drawEllipse(int(self.end.x - self.endMarkerRadius), int(self.end.y - self.endMarkerRadius), int(self.end.x + self.endMarkerRadius), int(self.end.y + self.endMarkerRadius))