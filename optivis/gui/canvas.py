import os
import sys

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

import optivis.gui
import optivis.layout

class Simple(optivis.gui.AbstractGui):
  qApplication = None
  qScene = None
  qView = None

  def __init__(self, *args, **kwargs):
    super(Simple, self).__init__(*args, **kwargs)

    # create application and canvas
    self.qApplication = PyQt4.Qt.QApplication(sys.argv)
    self.qScene = PyQt4.QtGui.QGraphicsScene()
    self.qView = PyQt4.QtGui.QGraphicsView(self.qScene)

    self.initialise()
  
  def initialise(self):
    # set view antialiasing
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing)
    
    # scale window
    self.qView.resize(self.size.x, self.size.y)
    self.qView.scale(self.zoom, self.zoom)
    
    # set window title
    self.qView.setWindowTitle(self.title)

    return

  def quit(self):
    #self.master.destroy()
    return

  def createCanvasObjectLists(self):
    canvasComponents = []
    canvasLinks = []
    
    for component in self.scene.components:
      # Add component to list of canvas components.
      # All but the first component's azimuth will be overridden by the layout manager.
      canvasComponents.append(CanvasComponent(component=component, azimuth=self.azimuth, position=None))
    
    for link in self.scene.links:
      # Add link to list of canvas links.
      canvasLinks.append(CanvasLink(link=link, start=None, end=None, startMarker=self.startMarker, endMarker=self.endMarker, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor))
    
    return (canvasComponents, canvasLinks)

  def show(self):
    # get bench objects as separate lists of components and links
    (canvasComponents, canvasLinks) = self.createCanvasObjectLists()
    
    # instantiate layout manager and arrange objects
    layout = optivis.layout.SimpleLayout(self, canvasComponents, canvasLinks)
    layout.arrange()
    
    # draw objects
    for canvasLink in canvasLinks:
      canvasLink.draw(self.qScene)
    
    for canvasComponent in canvasComponents:
      canvasComponent.draw(self.qScene)

    # show on screen
    self.qView.show()
    
    sys.exit(self.qApplication.exec_())

class CanvasComponent(optivis.gui.AbstractCanvasComponent):  
  def __init__(self, *args, **kwargs):
    super(CanvasComponent, self).__init__(*args, **kwargs)
  
  def draw(self, qScene):
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
    
    qScene.addItem(svgItem)

class CanvasLink(optivis.gui.AbstractCanvasLink):
  def __init__(self, *args, **kwargs):    
    super(CanvasLink, self).__init__(*args, **kwargs)

  def draw(self, qScene):
    pen = PyQt4.QtGui.QPen(PyQt4.QtCore.Qt.red, self.link.width, PyQt4.QtCore.Qt.SolidLine)
    line = PyQt4.QtGui.QGraphicsLineItem(self.start.x, self.start.y, self.end.x, self.end.y)
    line.setPen(pen)
    
    # add line to graphics scene
    qScene.addItem(line)
    
    # add markers if necessary
    if self.startMarker:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.start.x - self.startMarkerRadius, self.start.y - self.startMarkerRadius, self.startMarkerRadius * 2, self.startMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.startMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)
      
    if self.endMarker:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.end.x - self.endMarkerRadius, self.end.y - self.endMarkerRadius, self.endMarkerRadius * 2, self.endMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.endMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)