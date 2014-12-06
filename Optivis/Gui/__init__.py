from __future__ import division

import sys
import abc

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui

import Optivis
from Optivis.BenchObjects import *
from CanvasObjects import *
from Optivis.Nodes import *
import Optivis.Layout

class AbstractGui(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, bench, size=None, azimuth=0, zoom=1.0, startMarker=False, endMarker=False, startMarkerRadius=4, endMarkerRadius=2, startMarkerOutline="red", endMarkerOutline="blue"):
    if not isinstance(bench, Optivis.Bench):
      raise Exception('Specified bench is not of type Optivis.Bench')
    
    title = "Optivis - {0}".format(bench.title)
    
    if size is None:
      size = Optivis.Coordinates(500, 500)
    
    self.bench = bench
    self.size = size
    self.azimuth = azimuth
    self.zoom = zoom
    self.title = title
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerOutline = startMarkerOutline
    self.endMarkerOutline = endMarkerOutline
    
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
    
    # set title
    #self.master.title(self.title)

    # make root menu
    #menuBar = Tkinter.Menu(self.master)
    
    # make and add file menu
    #fileMenu = Tkinter.Menu(menuBar, tearoff=0)
    #fileMenu.add_command(label="Exit", command=self.quit)
    #menuBar.add_cascade(label="File", menu=fileMenu)

    #self.master.config(menu=menuBar)
    return

  def quit(self):
    #self.master.destroy()
    return

  def createCanvasObjectLists(self):
    canvasComponents = []
    canvasLinks = []
    
    for component in self.bench.components:
      size = component.size * self.zoom
      
      # add component to list of canvas components
      # azimuth of component is set to global azimuth - but in reality all but the first component will have its azimuth overridden based
      # on input/output node alignment
      canvasComponents.append(QtCanvasComponent(component=component, size=size, azimuth=self.azimuth, position=self.size / 2))
    
    for link in self.bench.links:
      canvasLinks.append(QtCanvasLink(link=link, start=Optivis.Coordinates(0, 0), end=Optivis.Coordinates(0, 0), startMarker=self.startMarker, endMarker=self.endMarker, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerOutline=self.startMarkerOutline, endMarkerOutline=self.endMarkerOutline))
    
    return (canvasComponents, canvasLinks)

  def show(self):
    (canvasComponents, canvasLinks) = self.createCanvasObjectLists()
    
    layout = Optivis.Layout.SimpleLayout(self, canvasComponents, canvasLinks)
    
    layout.arrange()
    layout.centre()
    
    # draw objects
    for canvasLink in canvasLinks:
      canvasLink.draw(self.scene)
    
    for canvasComponent in canvasComponents:
      canvasComponent.draw(self.scene)

    self.view.show()
    
    sys.exit(self.application.exec_())