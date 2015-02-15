from __future__ import unicode_literals, division

import os
import os.path
import sys

import abc

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

import optivis.view
import optivis.view.svg
import optivis.layout
import optivis.bench.components
import optivis.bench.links

class AbstractCanvas(optivis.view.AbstractDrawable):
  qApplication = None
  qMainWindow = None
  qScene = None
  qView = None
  
  def __init__(self, *args, **kwargs):
    super(AbstractCanvas, self).__init__(*args, **kwargs)

    self.create()
    self.initialise()
    
  def create(self):
    # create application
    self.qApplication = PyQt4.Qt.QApplication(sys.argv)
    self.qMainWindow = PyQt4.Qt.QMainWindow()
    
    # create drawing area
    self.qScene = PyQt4.QtGui.QGraphicsScene()
    self.qView = GraphicsView(self.qScene, self.qMainWindow)
    self.qView.setScale(self.zoom)
    
    # set view antialiasing
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing)
    
    # set window title
    self.qMainWindow.setWindowTitle(self.title)
    
    ### add menu and menu items
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
  
  @abc.abstractmethod
  def initialise(self):
    """
    Lays out the GUI after all of the main widgets have been created by create()
    """
    
    pass

  def draw(self):
    # empty the qScene
    self.qScene.clear()
    
    # draw objects
    for canvasLink in self.getDrawableLinks():
      canvasLink.draw(self.qScene, startMarkers=self.startMarkers, endMarkers=self.endMarkers, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor)
    
    for canvasComponent in self.getDrawableComponents():
      canvasComponent.draw(self.qScene)
  
  def layout(self):
    # instantiate layout manager and arrange objects
    layout = optivis.layout.SimpleLayout(self.scene)
    layout.arrange()
  
  def show(self):
    # layout scene
    self.layout()
    
    # draw scene
    self.draw()

    # show on screen
    self.qMainWindow.show()
    
    sys.exit(self.qApplication.exec_())
  
  def getDrawableComponents(self):
    drawableComponents = []
    
    for component in self.scene.components:
      # Add component to list of canvas components.
      drawableComponents.append(CanvasComponent(component))
    
    return drawableComponents
  
  def getDrawableLinks(self):
    drawableLinks = []
    
    for link in self.scene.links:
      # Add link to list of canvas links.
      drawableLinks.append(CanvasLink(link))
    
    return drawableLinks
  
  def export(self):
    # generate file path
    directory = os.path.join(os.path.expanduser('~'), 'export.svg')
    
    # default path and file format
    path = None
    fileFormat = None
    
    # get path to file to export to
    while True:    
      dialog = PyQt4.Qt.QFileDialog(parent=self.qMainWindow, caption='Export SVG', directory=directory, filter=';;'.join(optivis.view.svg.Svg._Svg__filters))
      dialog.setAcceptMode(PyQt4.Qt.QFileDialog.AcceptSave)
      dialog.setFileMode(PyQt4.Qt.QFileDialog.AnyFile)

      # show dialog
      dialog.exec_()
      
      if len(dialog.selectedFiles()) is 0:
	# no filename specified
	return

      # get file path and format
      path, extension = os.path.splitext(str(dialog.selectedFiles()[0]))
      
      try:
	# check if we can write to the path
	open(path, 'w').close()
	os.unlink(path)
	
	# get valid format
	fileFormat = extension[1:]

	if extension not in optivis.view.svg.Svg._Svg__extensions:
	  PyQt4.Qt.QMessageBox.critical(self.qMainWindow, 'File extension invalid', 'The specified file extension, \'{0}\', is invalid'.format(extension))
	  
	  continue
	
	break
      except OSError:
	PyQt4.Qt.QMessageBox.critical(self.qMainWindow, 'Filename invalid', 'The specified filename is invalid')
      except IOError:
	PyQt4.Qt.QMessageBox.critical(self.qMainWindow, 'Permission denied', 'You do not have permission to save the file to the specified location.')

    # export
    return self.exportSvg(path=path + extension, fileFormat=fileFormat)
  
  def exportSvg(self, *args, **kwargs):
    svgView = optivis.view.svg.Svg(self.scene)
    svgView.export(*args, **kwargs)

class GraphicsView(PyQt4.QtGui.QGraphicsView):
  def __init__(self, *args, **kwargs):
    super(GraphicsView, self).__init__(*args, **kwargs)
  
  def setScale(self, scale):
    """
    Set scale of graphics view.
    
    There is no native setScale() method for a QGraphicsView, so this must be achieved via setTransform().
    """
    
    transform = PyQt4.QtGui.QTransform()
    transform.scale(scale, scale)
    
    self.setTransform(transform)

class Simple(AbstractCanvas):
  def __init__(self, *args, **kwargs):
    super(Simple, self).__init__(*args, **kwargs)
  
  def initialise(self):
    # set central widget to be the view
    self.qMainWindow.setCentralWidget(self.qView)
    
    # resize main window to fit content
    self.qMainWindow.resize(self.size.x, self.size.y)

    return
    
class Full(AbstractCanvas):
  def __init__(self, *args, **kwargs):
    super(Full, self).__init__(*args, **kwargs)
  
  def initialise(self):
    ### create controls
    
    # add control widgets
    self.controls = ControlPanel(self)
    self.controls.setFixedWidth(200)
    
    ### create container for view and controls
    self.container = PyQt4.QtGui.QWidget()
    
    ### create and populate layout
    self.hBox = PyQt4.QtGui.QHBoxLayout()
    
    # add qView to layout
    self.hBox.addWidget(self.qView, stretch=3)
    
    # add controls to layout
    self.hBox.addWidget(self.controls, stretch=1)
    
    ### finish up
    
    # set container's layout
    self.container.setLayout(self.hBox)
    
    # add container to main window and set as central element
    self.qMainWindow.setCentralWidget(self.container)
    
    # set fixed size for view
    self.qView.setMinimumSize(self.size.x, self.size.y)
    
    #self.qMainWindow.repaint()

    return

class ControlPanel(PyQt4.QtGui.QWidget):
  zoomRange = (0.1, 10)
  zoomStep = 0.1
  
  def __init__(self, canvas, *args, **kwargs):
    super(ControlPanel, self).__init__(*args, **kwargs)
  
    self.canvas = canvas
    
    self.addControls()
  
  @property
  def canvas(self):
    return self.__canvas
  
  @canvas.setter
  def canvas(self, canvas):
    self.__canvas = canvas
  
  def addControls(self):
    ### master layout
    controlLayout = PyQt4.QtGui.QVBoxLayout()
    
    ### zoom controls
    
    # group box for slider
    zoomSliderGroupBox = PyQt4.QtGui.QGroupBox(title="Zoom")
    
    # zoom slider
    self.zoomSlider = PyQt4.QtGui.QSlider(PyQt4.QtCore.Qt.Horizontal)
    self.zoomSlider.setFocusPolicy(PyQt4.QtCore.Qt.NoFocus)
    self.zoomSlider.setRange(self.zoomRange[0] / self.zoomStep, self.zoomRange[1] / self.zoomStep)
    self.zoomSlider.setSingleStep(1)
    self.zoomSlider.setSliderPosition(self.canvas.zoom / self.zoomStep)
    self.zoomSlider.valueChanged[int].connect(self.zoomSliderChanged)
    
    # zoom spin box
    self.zoomSpinBox = PyQt4.QtGui.QDoubleSpinBox()
    self.zoomSpinBox.setDecimals(1)
    self.zoomSpinBox.setRange(*self.zoomRange)
    self.zoomSpinBox.setSingleStep(self.zoomStep)
    self.zoomSpinBox.setValue(self.canvas.zoom) # TODO: check this is a valid step
    self.zoomSpinBox.valueChanged[float].connect(self.zoomSpinBoxChanged)
    
    # add zoom controls to zoom group box
    sliderLayout = PyQt4.QtGui.QHBoxLayout()
    
    sliderLayout.addWidget(self.zoomSlider)
    sliderLayout.addWidget(self.zoomSpinBox)
    
    zoomSliderGroupBox.setLayout(sliderLayout)
    
    # add zoom group box to control box
    controlLayout.addWidget(zoomSliderGroupBox)
    
    ### marker controls
    
    # group box for marker controls
    markerCheckBoxGroupBox = PyQt4.QtGui.QGroupBox(title="Markers")
    
    # start marker checkbox
    startMarkersCheckBox = PyQt4.QtGui.QCheckBox("Start")
    startMarkersCheckBox.setChecked(self.canvas.startMarkers)
    startMarkersCheckBox.stateChanged.connect(self.startMarkersChanged)
    
    endMarkersCheckBox = PyQt4.QtGui.QCheckBox("End")
    endMarkersCheckBox.setChecked(self.canvas.endMarkers)
    endMarkersCheckBox.stateChanged.connect(self.endMarkersChanged)
    
    # add marker controls to marker group box
    markerLayout = PyQt4.QtGui.QHBoxLayout()
    markerLayout.addWidget(startMarkersCheckBox)
    markerLayout.addWidget(endMarkersCheckBox)
    
    markerCheckBoxGroupBox.setLayout(markerLayout)
    
    # add marker check box group box to control box
    controlLayout.addWidget(markerCheckBoxGroupBox)
    
    ### add layout to control widget
    self.setLayout(controlLayout)
  
  def zoomSliderChanged(self, value):
    # scale value by zoom step (sliders only support int increments)
    self.setZoom(float(value * self.zoomStep))
  
  def zoomSpinBoxChanged(self, value):
    self.setZoom(float(value))
  
  def setZoom(self, zoom):
    zoom = round(zoom / self.zoomStep) * self.zoomStep
    
    self.canvas.zoom = zoom
    self.canvas.qView.setScale(zoom)
    
    # update zoom slider
    self.zoomSlider.setSliderPosition(self.canvas.zoom / self.zoomStep)
    
    # update zoom spin box
    self.zoomSpinBox.setValue(self.canvas.zoom)
  
  def startMarkersChanged(self, value):
    if value == PyQt4.QtCore.Qt.Checked:
      self.setStartMarkers(True)
    else:
      self.setStartMarkers(False)
      
  def endMarkersChanged(self, value):
    if value == PyQt4.QtCore.Qt.Checked:
      self.setEndMarkers(True)
    else:
      self.setEndMarkers(False)
  
  def setStartMarkers(self, value):
    self.canvas.startMarkers = value
    self.canvas.draw()
    
  def setEndMarkers(self, value):
    self.canvas.endMarkers = value
    self.canvas.draw()

class CanvasComponent(optivis.bench.components.AbstractDrawableComponent):  
  def __init__(self, component, *args, **kwargs):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type AbstractComponent')
    
    self.component = component
    
    super(CanvasComponent, self).__init__(*args, **kwargs)
  
  def draw(self, qScene):
    print "[GUI] Drawing component {0} at {1}".format(self.component, self.component.position)
    
    # Create full system path from filename and SVG directory.
    path = os.path.join(self.component.svgDir, self.component.filename)
    
    # Create graphical representation of SVG image at path.
    svgItem = PyQt4.QtSvg.QGraphicsSvgItem(path)
    
    # Set position of top-left corner.
    # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
    svgItem.setPos(self.component.position.x - self.component.size.x / 2, self.component.position.y - self.component.size.y / 2)
    
    # Rotate clockwise.
    # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
    svgItem.translate(self.component.size.x / 2, self.component.size.y / 2)
    svgItem.rotate(self.component.azimuth)
    svgItem.translate(-self.component.size.x / 2, -self.component.size.y / 2)
    
    qScene.addItem(svgItem)

class CanvasLink(optivis.bench.links.AbstractDrawableLink):
  def __init__(self, link, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.link = link
    
    super(CanvasLink, self).__init__(*args, **kwargs)

  def draw(self, qScene, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    print "[GUI] Drawing link {0}".format(self.link)
    
    pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.link.color), self.link.width, PyQt4.QtCore.Qt.SolidLine)
    line = PyQt4.QtGui.QGraphicsLineItem(self.link.start.x, self.link.start.y, self.link.end.x, self.link.end.y)
    line.setPen(pen)
    
    # add line to graphics scene
    qScene.addItem(line)
    
    # add markers if necessary
    if startMarkers:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.link.start.x - startMarkerRadius, self.link.start.y - startMarkerRadius, startMarkerRadius * 2, startMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(startMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)
      
    if endMarkers:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.link.end.x - endMarkerRadius, self.link.end.y - endMarkerRadius, endMarkerRadius * 2, endMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(endMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)