from __future__ import unicode_literals, division

import os
import os.path
import sys

import abc
import math

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

import optivis.view
import optivis.view.svg
import optivis.layout
import optivis.bench.components
import optivis.bench.links
import optivis.geometry

class AbstractCanvas(optivis.view.AbstractView):
  __metaclass__ = abc.ABCMeta
  
  qApplication = None
  qMainWindow = None
  qScene = None
  qView = None

  SHOW_COMPONENTS = 1 << 0
  SHOW_LINKS = 1 << 1
  SHOW_LABELS = 1 << 2

  # 'show all', 2^(n+1)-1 where n is the number of significant bits above
  SHOW_MAX = (1 << 3) - 1
  
  def __init__(self, showFlags=None, showLabelFlags=0, *args, **kwargs):
    super(AbstractCanvas, self).__init__(*args, **kwargs)

    if showFlags is None:
      showFlags = AbstractCanvas.SHOW_MAX

    self.showFlags = showFlags
    self.showLabelFlags = showLabelFlags

    self.create()
    self.initialise()

  @property
  def showFlags(self):
    return self.__showFlags

  @showFlags.setter
  def showFlags(self, showFlags):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    showFlags = int(showFlags)

    if showFlags < 0 or showFlags > AbstractCanvas.SHOW_MAX:
      raise Exception('Specified show flags are not valid. Show flags value must be between 0 and {0}'.format(AbstractCanvas.SHOW_MAX))

    self.__showFlags = showFlags

  @property
  def showLabelFlags(self):
    return self.__showLabelFlags

  @showLabelFlags.setter
  def showLabelFlags(self, showLabelFlags):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    showLabelFlags = int(showLabelFlags)

    if showLabelFlags < 0:
      raise Exception('Specified show label flags are not valid. Show flags value must be > 0 and {0}')

    self.__showLabelFlags = showLabelFlags
    
  def create(self):
    # create application
    self.qApplication = PyQt4.Qt.QApplication(sys.argv)
    self.qMainWindow = MainWindow()
    
    # create drawing area
    self.qScene = GraphicsScene()
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
    
    # get canvas links and components
    canvasLinks = self.getCanvasLinks()
    canvasComponents = self.getCanvasComponents()
    canvasLabels = []
    
    # draw links
    if self.showFlags & AbstractCanvas.SHOW_LINKS:
      for canvasLink in canvasLinks:
        canvasLink.draw(self.qScene, startMarkers=self.startMarkers, endMarkers=self.endMarkers, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor)
        
	if canvasLink.item.label is not None:
	  # Add label to list of canvas labels.
	  canvasLabels.append(CanvasLabel(canvasLink))

    # draw components
    if self.showFlags & AbstractCanvas.SHOW_COMPONENTS:
      for canvasComponent in canvasComponents:
        canvasComponent.draw(self.qScene)
        
        if canvasComponent.item.label is not None:
	  # Add label to list
	  canvasLabels.append(CanvasLabel(canvasComponent))

    # draw labels
    if self.showFlags & AbstractCanvas.SHOW_LABELS:
      for canvasLabel in canvasLabels:
	canvasLabel.draw(self.qScene)
  
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
  
  def getCanvasComponents(self):
    canvasComponents = []
    
    for component in self.scene.getComponents():
      # Add component to list of canvas components.
      canvasComponents.append(CanvasComponent(component, clickedCallback=self.qMainWindow.clickHandler))
    
    return canvasComponents
  
  def getCanvasLinks(self):
    canvasLinks = []
    
    for link in self.scene.links:
      # Add link to list of canvas links.
      canvasLinks.append(CanvasLink(link))
    
    return canvasLinks
  
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

class MainWindow(PyQt4.Qt.QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)
  
  def clickHandler(self, *args, **kwargs):
    print self.sender()

class GraphicsScene(PyQt4.QtGui.QGraphicsScene):
  def __init__(self, *args, **kwargs):
    super(GraphicsScene, self).__init__(*args, **kwargs)

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
    
    ### create container for view + layer buttons and controls
    self.container = PyQt4.QtGui.QWidget()

    ### create container for view + layer buttons
    self.viewWidget = PyQt4.QtGui.QWidget()
    self.viewWidgetVBox = PyQt4.QtGui.QVBoxLayout()

    # add checkbox panel to view widget
    self.viewWidgetVBox.addWidget(ViewCheckboxPanel(self))

    # add graphics view to view widget
    self.viewWidgetVBox.addWidget(self.qView)

    # set layout of view widget to the layout manager
    self.viewWidget.setLayout(self.viewWidgetVBox)
    
    ### create and populate layout
    self.hBox = PyQt4.QtGui.QHBoxLayout()
    
    # add qView to layout
    self.hBox.addWidget(self.viewWidget, stretch=3)
    
    # add controls to layout
    self.hBox.addWidget(self.controls, stretch=1)
    
    ### finish up
    
    # set container's layout
    self.container.setLayout(self.hBox)
    
    # add container to main window and set as central element
    self.qMainWindow.setCentralWidget(self.container)
    
    # set fixed size for view
    self.qView.setMinimumSize(self.size.x, self.size.y)

    return

class ViewCheckboxPanel(PyQt4.QtGui.QGroupBox):
  def __init__(self, canvas, *args, **kwargs):
    super(ViewCheckboxPanel, self).__init__(*args, **kwargs)

    self.canvas = canvas

    self.setTitle('Layers')

    # create horizontal layout
    self.hBox = PyQt4.QtGui.QHBoxLayout()

    # create buttons
    self.button1 = PyQt4.QtGui.QCheckBox("Components")
    self.button1.setChecked(self.canvas.showFlags & AbstractCanvas.SHOW_COMPONENTS)
    self.button1.stateChanged.connect(self.showCheckBoxChanged)
    self.button2 = PyQt4.QtGui.QCheckBox("Links")
    self.button2.setChecked(self.canvas.showFlags & AbstractCanvas.SHOW_LINKS)
    self.button2.stateChanged.connect(self.showCheckBoxChanged)
    self.button3 = PyQt4.QtGui.QCheckBox("Labels")
    self.button3.setChecked(self.canvas.showFlags & AbstractCanvas.SHOW_LABELS)
    self.button3.stateChanged.connect(self.showCheckBoxChanged)

    # add buttons to layout
    self.hBox.addWidget(self.button1)
    self.hBox.addWidget(self.button2)
    self.hBox.addWidget(self.button3)

    # set layout of widget
    self.setLayout(self.hBox)

  def showCheckBoxChanged(self, *args, **kwargs):
    # just rebuild the show bitfield using all checkboxes
    self.canvas.showFlags = (self.button1.isChecked() << 0) | (self.button2.isChecked() << 1) | (self.button3.isChecked() << 2)

    # redraw canvas
    self.canvas.draw()

  @property
  def canvas(self):
    return self.__canvas
  
  @canvas.setter
  def canvas(self, canvas):
    self.__canvas = canvas

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
    
    markerLayout.addWidget(startMarkersCheckBox, alignment=PyQt4.QtCore.Qt.AlignHCenter)
    markerLayout.addWidget(endMarkersCheckBox, alignment=PyQt4.QtCore.Qt.AlignHCenter)
    
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

class AbstractCanvasItem(object):
  """
  Class to represent an item that can be drawn on the canvas (e.g. component, link, label).
  """
  
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, item, *args, **kwargs):
    self.item = item
  
  @abc.abstractmethod
  def draw(self, *args, **kwargs):
    return

class CanvasComponent(AbstractCanvasItem):  
  def __init__(self, component, clickedCallback=None, *args, **kwargs):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type AbstractComponent')
    
    self.clickedCallback = clickedCallback
    
    super(CanvasComponent, self).__init__(item=component, *args, **kwargs)
  
  def draw(self, qScene):
    print "[GUI] Drawing component {0} at {1}".format(self.item, self.item.position)
    
    # Create full system path from filename and SVG directory.
    path = os.path.join(self.item.svgDir, self.item.filename)
    
    # Create graphical representation of SVG image at path.
    svgItem = OptivisSvgItem(path)
    
    if self.item.tooltip is not None:
        svgItem.setToolTip(self.item.tooltip)
    
    # Add callback, if necessary
    if self.clickedCallback is not None:
      # FIXME: check clickedCallback is a valid callable
      svgItem.connect(svgItem, PyQt4.QtCore.SIGNAL('clicked()'), self.clickedCallback)
    
    # Set position of top-left corner.
    # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
    svgItem.setPos(self.item.position.x - self.item.size.x / 2, self.item.position.y - self.item.size.y / 2)
    
    # Rotate clockwise.
    # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
    svgItem.translate(self.item.size.x / 2, self.item.size.y / 2)
    svgItem.rotate(self.item.azimuth)
    svgItem.translate(-self.item.size.x / 2, -self.item.size.y / 2)
    
    qScene.addItem(svgItem)

class OptivisSvgItem(PyQt4.QtSvg.QGraphicsSvgItem):
  def __init__(self, *args, **kwargs):
    # initialise this as a QObject (QGraphicsSvgItem is not a descendent of QObject and so can't send signals by default)
    PyQt4.QtCore.QObject.__init__(self)
    
    # call other constructor (order is important)
    super(OptivisSvgItem, self).__init__(*args, **kwargs)
  
  def mousePressEvent(self, event, *args, **kwargs):
    """
    This method does nothing but accept the event, but this behaviour
    is required for mouseReleaseEvent() to work below.
    """
    event.accept()
  
  def mouseReleaseEvent(self, event, *args, **kwargs):
    # emit clicked signal with no arguments
    self.emit(PyQt4.QtCore.SIGNAL('clicked()'))
    
    # this is the default, but we'll call it anyway
    event.accept()

class CanvasLink(AbstractCanvasItem):
  def __init__(self, link, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    super(CanvasLink, self).__init__(item=link, *args, **kwargs)

  def draw(self, qScene, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    print "[GUI] Drawing link {0}".format(self.item)
    
    pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.item.color), self.item.width, PyQt4.QtCore.Qt.SolidLine)
    line = PyQt4.QtGui.QGraphicsLineItem(self.item.start.x, self.item.start.y, self.item.end.x, self.item.end.y)
    line.setPen(pen)

    # add line to graphics scene
    qScene.addItem(line)
    
    # add markers if necessary
    if startMarkers:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.item.start.x - startMarkerRadius, self.item.start.y - startMarkerRadius, startMarkerRadius * 2, startMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(startMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)
      
    if endMarkers:
      circle = PyQt4.QtGui.QGraphicsEllipseItem(self.item.end.x - endMarkerRadius, self.item.end.y - endMarkerRadius, endMarkerRadius * 2, endMarkerRadius * 2)
      pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(endMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine)
      circle.setPen(pen)
      
      qScene.addItem(circle)

class CanvasLabel(object):
  def __init__(self, canvasItem, *args, **kwargs):
    if not isinstance(canvasItem, AbstractCanvasItem):
      raise Exception('Specified canvas item is not of type AbstractCanvasItem')
    
    self.canvasItem = canvasItem
    
    super(CanvasLabel, self).__init__(*args, **kwargs)

  def draw(self, qScene):
    print "[GUI] Drawing label {0}".format(self.canvasItem.item.label)

    # create label
    labelItem = PyQt4.QtGui.QGraphicsTextItem(self.canvasItem.item.label.text)

    # position next to object
    labelItem.setPos(50, 50)

    ## calculate size
    #labelSize = optivis.geometry.Coordinates(labelItem.boundingRect().width(), labelItem.boundingRect().height())
    #  
    # get link length on GUI
    #linkLength = optivis.geometry.Coordinates(self.drawable.end.x - self.drawable.start.x, self.drawable.end.y - self.drawable.start.y)
    #
    #if linkLength.y != 0:
    #  linkAzimuth = math.degrees(math.atan2(linkLength.y, linkLength.x)) + 90
    #else:
    #  # avoid division by zero
    #  linkAzimuth = 90
    #
    #linkCentralPosition = (self.link.end - self.link.start) / 2
    #offset = optivis.geometry.Coordinates(self.link.label.offset, 0).rotate(linkAzimuth)
    #labelPosition = self.link.start.translate(linkCentralPosition).translate(offset)
    #
    ## position label
    #labelItem.setPos(labelPosition.x, labelPosition.y)
    #
    ## rotate text
    #labelItem.setRotation(linkAzimuth)

    qScene.addItem(labelItem)