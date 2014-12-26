from __future__ import division

import sys
import abc

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui

import Optivis
import Optivis.Layout
import CanvasObjects

class AbstractGui(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, bench, size=None, azimuth=0, zoom=1.0, startMarker=False, endMarker=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    if not isinstance(bench, Optivis.Bench):
      raise Exception('Specified bench is not of type Optivis.Bench')
    
    title = "Optivis - {0}".format(bench.title)
    
    if size is None:
      size = Optivis.Coordinates(500, 500)
      
    if startMarkerColor is None:
      startMarkerColor = PyQt4.QtCore.Qt.red
    
    if endMarkerColor is None:
      endMarkerColor = PyQt4.QtCore.Qt.blue
    
    self.bench = bench
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
  def size(self):
    return self.__size

  @size.setter
  def size(self, size):
    if not isinstance(size, Optivis.Coordinates):
      raise Exception('Specified size is not of type Optivis.Coordinates')
    
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

class Qt(AbstractGui):
  application = None
  scene = None
  view = None

  def __init__(self, *args, **kwargs):
    super(Qt, self).__init__(*args, **kwargs)

    # create application and canvas
    self.application = PyQt4.Qt.QApplication(sys.argv)
    self.scene = PyQt4.QtGui.QGraphicsScene()
    self.view = PyQt4.QtGui.QGraphicsView(self.scene)

    self.initialise()
  
  def initialise(self):
    # set view antialiasing
    self.view.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing)
    
    # scale window
    self.view.resize(self.size.x, self.size.y)
    self.view.scale(self.zoom, self.zoom)
    
    # set window title
    self.view.setWindowTitle(self.title)

    return

  def quit(self):
    #self.master.destroy()
    return

  def createCanvasObjectLists(self):
    canvasComponents = []
    canvasLinks = []
    
    for component in self.bench.components:
      # Add component to list of canvas components.
      # All but the first component's azimuth will be overridden by the layout manager.
      canvasComponents.append(CanvasObjects.QtCanvasComponent(component=component, azimuth=self.azimuth, position=None))
    
    for link in self.bench.links:
      # Add link to list of canvas links.
      canvasLinks.append(CanvasObjects.QtCanvasLink(link=link, start=None, end=None, startMarker=self.startMarker, endMarker=self.endMarker, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor))
    
    return (canvasComponents, canvasLinks)

  def show(self):
    # get bench objects as separate lists of components and links
    (canvasComponents, canvasLinks) = self.createCanvasObjectLists()
    
    # instantiate layout manager and arrange objects
    layout = Optivis.Layout.SimpleLayout(self, canvasComponents, canvasLinks)
    layout.arrange()
    
    # draw objects
    for canvasLink in canvasLinks:
      canvasLink.draw(self.scene)
    
    for canvasComponent in canvasComponents:
      canvasComponent.draw(self.scene)

    # show on screen
    self.view.show()
    
    sys.exit(self.application.exec_())