import os
import os.path
import sys

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

import optivis.gui
import optivis.layout

class Simple(optivis.gui.AbstractGui):
  qApplication = None
  qMainWindow = None
  qScene = None
  qView = None

  def __init__(self, *args, **kwargs):
    super(Simple, self).__init__(*args, **kwargs)

    self.initialise()
  
  def initialise(self):
    # create application
    self.qApplication = PyQt4.Qt.QApplication(sys.argv)
    self.qMainWindow = PyQt4.Qt.QMainWindow()
    
    # create drawing area
    self.qScene = PyQt4.QtGui.QGraphicsScene()
    self.qView = PyQt4.QtGui.QGraphicsView(self.qScene, self.qMainWindow)
    
    # set view antialiasing
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing)
    
    # scale view by zoom level
    self.qView.scale(self.zoom, self.zoom)
    
    # set application's central widget
    self.qMainWindow.setCentralWidget(self.qView)
    
    # set window title
    self.qMainWindow.setWindowTitle(self.title)
    
    # resize to fit content
    self.qMainWindow.resize(self.size.x, self.size.y)
    
    # add menu and menu items
    menubar = self.qMainWindow.menuBar()
    fileMenu = menubar.addMenu('&File')
    
    exportAction = PyQt4.QtGui.QAction('Export', self.qMainWindow)
    exportAction.setShortcut('Ctrl+E')
    exportAction.triggered.connect(self.export)
    fileMenu.addAction(exportAction)
    
    exitAction = PyQt4.QtGui.QAction('Exit', self.qMainWindow)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.triggered.connect(self.qApplication.quit)
    fileMenu.addAction(exitAction)

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
    self.qMainWindow.show()
    
    sys.exit(self.qApplication.exec_())
  
  def export(self):
    # generate file path
    directory = os.path.join(os.path.expanduser('~'), 'export.svg')
    
    # get path to file to export to
    while True:    
      dialog = PyQt4.Qt.QFileDialog(parent=self.qMainWindow, caption='Export SVG', directory=directory, filter='SVG files (*.svg)')
      dialog.setAcceptMode(PyQt4.Qt.QFileDialog.AcceptSave)
      dialog.setFileMode(PyQt4.Qt.QFileDialog.AnyFile)

      # show dialog
      dialog.exec_()
      
      if len(dialog.selectedFiles()) is 0:
	# no filename specified
	return

      # get path
      path = dialog.selectedFiles()[0]
      
      try:
	open(path, 'w').close()
	os.unlink(path)
	
	break;
      except OSError:
	PyQt4.Qt.QMessageBox.critical(self.qMainWindow, 'Filename invalid', 'The specified filename is invalid')
      except IOError:
	PyQt4.Qt.QMessageBox.critical(self.qMainWindow, 'Permission denied', 'You do not have permission to save the file to the specified location.')

    # export SVG
    return self.exportSvg(path)
  
  def exportSvg(self, path):
    # get bounding rectangle for graphics scene
    sceneRect = self.qScene.itemsBoundingRect()
    
    generator = PyQt4.QtSvg.QSvgGenerator()
    generator.setFileName(path)
    generator.setSize(PyQt4.Qt.QSize(sceneRect.width(), sceneRect.height()))
    generator.setTitle(self.title)
    
    # create painter
    painter = PyQt4.Qt.QPainter()
    painter.begin(generator)
    
    # convert scene to SVG image
    self.qScene.render(painter)
    
    # finish painting
    painter.end()
    
    return True

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