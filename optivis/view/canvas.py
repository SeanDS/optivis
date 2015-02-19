from __future__ import unicode_literals, division

import os
import os.path
import sys

import abc
import math
import weakref

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

from collections import OrderedDict

class AbstractCanvas(optivis.view.AbstractView):
  __metaclass__ = abc.ABCMeta
  
  qApplication = None
  qMainWindow = None
  qScene = None
  qView = None

  SHOW_COMPONENTS = 1 << 0
  SHOW_LINKS = 1 << 1
  SHOW_LABELS = 1 << 2

  canvasLabelFlags = OrderedDict()

  # 'show all', 2^(n+1)-1 where n is the number of significant bits above
  SHOW_MAX = (1 << 3) - 1
  
  def __init__(self, clickedCallback=None, showFlags=None, showLabelFlags=0, *args, **kwargs):
    super(AbstractCanvas, self).__init__(*args, **kwargs)

    if showFlags is None:
      showFlags = AbstractCanvas.SHOW_MAX

    self.clickedCallback = clickedCallback
    self.showFlags = showFlags
    self.showLabelFlags = showLabelFlags

    self.create()
    self.initialise()

  @property
  def clickedCallback(self):
    return self.__clickedCallback

  @clickedCallback.setter
  def clickedCallback(self, clickedCallback):
    # FIXME: check clickedCallback is a valid callable
    self.__clickedCallback = clickedCallback
  
  def clickHandler(self, canvasItem, event, *args, **kwargs):
    if self.clickedCallback is not None:
      self.clickedCallback(canvasItem, event)

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
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing | PyQt4.Qt.QPainter.TextAntialiasing | PyQt4.Qt.QPainter.SmoothPixmapTransform | PyQt4.QtGui.QPainter.HighQualityAntialiasing)
    
    # set window title
    self.qMainWindow.setWindowTitle(self.title)
    
    ### add menu and menu items
    menubar = self.qMainWindow.menuBar()
    fileMenu = menubar.addMenu('&File')
    self.labelMenu = menubar.addMenu('&Labels')
    
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

    # draw components
    if self.showFlags & AbstractCanvas.SHOW_COMPONENTS:
      for canvasComponent in canvasComponents:
        canvasComponent.draw(self.qScene)

    # draw labels
    if self.showFlags & AbstractCanvas.SHOW_LABELS:
      for canvasLink in canvasLinks:
	if canvasLink.item.labels is not None:
	  # Add labels to list of canvas labels.
          for label in canvasLink.item.labels:
            canvasLabels.append(CanvasLabel(label, canvasLabelFlags=self.canvasLabelFlags))
	  
      for canvasComponent in canvasComponents:
        if canvasComponent.item.labels is not None:
	  # Add labels to list of canvas labels.
          for label in canvasComponent.item.labels:
            canvasLabels.append(CanvasLabel(label, canvasLabelFlags=self.canvasLabelFlags))
	  
      for canvasLabel in canvasLabels:
	canvasLabel.draw(self.qScene)
    
    # Now that all labels have been created the dictionary of
    # label content options should be available.
    self.labelMenu.clear()
    
    for kv in self.canvasLabelFlags.items():
        checkBox = PyQt4.QtGui.QCheckBox(kv[0], self.qMainWindow)
        checkableAction = PyQt4.QtGui.QWidgetAction(self.qMainWindow)
        checkableAction.setDefaultWidget(checkBox)
        
        #self.labelMenu.addAction(checkableAction)
    
    self.labelMenu.addSeparator()
    self.labelMenu.addAction(PyQt4.QtGui.QAction("Clear all...", self.qMainWindow))
      
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
      canvasComponents.append(CanvasComponent(component, clickedCallback=self.clickHandler))
    
    return canvasComponents
  
  def getCanvasLinks(self):
    canvasLinks = []
    
    for link in self.scene.links:
      # Add link to list of canvas links.
      canvasLinks.append(CanvasLink(link, clickedCallback=self.clickHandler))
    
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

    # hook into AbstractCanvas's click callback
    self.canvas.clickedCallback = self.clickHandler
  
  def clickHandler(self, canvasItem, event):
    print canvasItem.item
    self.itemEditPanel.setContentFromCanvasItem(canvasItem)

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
    zoomSliderGroupBox.setFixedHeight(100)
    
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
    
    # add zoom group box to layout
    controlLayout.addWidget(zoomSliderGroupBox)
    
    ### marker controls
    
    # group box for marker controls
    markerCheckBoxGroupBox = PyQt4.QtGui.QGroupBox(title="Markers")
    markerCheckBoxGroupBox.setFixedHeight(100)
    
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
    
    # add marker check box group box to layout
    controlLayout.addWidget(markerCheckBoxGroupBox)

    ### item edit controls

    # group box for item edit controls
    self.itemEditGroupBox = PyQt4.QtGui.QGroupBox(title="Attributes")

    # edit panel within scroll area within group box
    self.itemEditScrollArea = PyQt4.QtGui.QScrollArea()
    self.itemEditPanel = OptivisItemEditPanel()
    self.itemEditScrollArea.setWidget(self.itemEditPanel)
    self.itemEditScrollArea.setWidgetResizable(True)
    itemEditGroupBoxLayout = PyQt4.QtGui.QVBoxLayout()
    itemEditGroupBoxLayout.addWidget(self.itemEditScrollArea)
    self.itemEditGroupBox.setLayout(itemEditGroupBoxLayout)

    # add group box to layout
    controlLayout.addWidget(self.itemEditGroupBox)
    
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

class OptivisItemEditPanel(PyQt4.QtGui.QWidget):
  def __init__(self, *args, **kwargs):
    super(OptivisItemEditPanel, self).__init__(*args, **kwargs)

    # create layout to use for edit controls (empty by default)
    self.vBox = PyQt4.QtGui.QVBoxLayout()
    self.vBox.setAlignment(PyQt4.QtCore.Qt.AlignTop)

    # set layout
    self.setLayout(self.vBox)

  def tmp(self, *args, **kwargs):
    print self.sender()

  def setContentFromCanvasItem(self, canvasItem):
    # empty current contents
    # from http://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    for i in reversed(range(self.vBox.count())): 
      self.vBox.itemAt(i).widget().setParent(None)

    if canvasItem.item.paramList is None:
      # no edit controls provided
      return

    # get attributes and external item
    attributes = canvasItem.item.paramList
    pykatObject = canvasItem.item.pykatObject

    # references to external items should be made using weakref, so if they are deleted after the reference is made, the reference will be None
    if pykatObject is None:
      raise Exception('External item is deleted')

    # handle weak references
    if isinstance(pykatObject, weakref.ReferenceType):
      pykatObject = pykatObject()

    # loop over attributes from external object and create
    for paramName in attributes:
      dataType = attributes[paramName]

      # get attribute value
      paramValue = getattr(pykatObject, paramName)

      # get widget for this parameter
      try:
        paramEditWidget = OptivisCanvasItemDataType.getCanvasWidget(paramName, dataType, canvasItem)

        self.connect(paramEditWidget, PyQt4.QtCore.SIGNAL("textChanged(QString)"), self.tmp)
      except AttributeError, e:
        print "[GUI] WARNING: the value of a parameter specified in the parameter list with this object is not available. Skipping."
        continue

      # set its value
      OptivisCanvasItemDataType.setCanvasWidgetValue(paramEditWidget, dataType, paramValue)

      # create a container for this edit widget
      container = PyQt4.QtGui.QWidget()
      containerLayout = PyQt4.QtGui.QHBoxLayout()

      # remove padding between widgets
      containerLayout.setContentsMargins(0, 0, 0, 0)

      # create label
      label = PyQt4.QtGui.QLabel(text=paramName)

      # add label and edit widget to layout
      containerLayout.addWidget(label)
      containerLayout.addWidget(paramEditWidget)

      # set layout of container
      container.setLayout(containerLayout)

      # set container height
      #container.setFixedHeight(50)

      # add container to edit panel
      self.vBox.addWidget(container)

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

    # set callback
    svgItem.clickedCallback = self.svgItemClicked
    
    if self.item.tooltip is not None:
        if hasattr(self.item.tooltip, "__call__"):
            svgItem.setToolTip(str(self.item.tooltip()))
        else:
            svgItem.setToolTip(str(self.item.tooltip))
    
    # Set position of top-left corner.
    # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
    svgItem.setPos(self.item.position.x - self.item.size.x / 2, self.item.position.y - self.item.size.y / 2)
    
    # Rotate clockwise.
    # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
    svgItem.translate(self.item.size.x / 2, self.item.size.y / 2)
    svgItem.rotate(self.item.azimuth)
    svgItem.translate(-self.item.size.x / 2, -self.item.size.y / 2)
    
    qScene.addItem(svgItem)

  def svgItemClicked(self, event, *args, **kwargs):
    if self.clickedCallback is not None:
      self.clickedCallback(self, event, *args, **kwargs)

class OptivisSvgItem(PyQt4.QtSvg.QGraphicsSvgItem):
  def __init__(self, *args, **kwargs):
    # TODO: is there a way to send the clickCallback into this consturctor without screwing up Qt? (Right now any extra arguments in the __init__ above seems to make the SvgItem silently fail to draw...)
    super(OptivisSvgItem, self).__init__(*args, **kwargs)

    # default callback value (can't set it within __init__ for some reason, see above)
    self.clickedCallback = None
  
  @property
  def clickedCallback(self):
    return self.__clickedCallback

  @clickedCallback.setter
  def clickedCallback(self, clickedCallback):
    # FIXME: check that clickedCallback is a valid callable
    self.__clickedCallback = clickedCallback

  def mousePressEvent(self, event, *args, **kwargs):
    """
    This method does nothing but accept the event, but this behaviour
    is required for mouseReleaseEvent() to work below.
    """
    event.accept()
  
  def mouseReleaseEvent(self, event, *args, **kwargs):
    if self.clickedCallback is not None:
      # call callback
      self.clickedCallback(event, *args, **kwargs)
    
    # this is the default, but we'll call it anyway
    event.accept()

class CanvasLink(AbstractCanvasItem):
  def __init__(self, link, clickedCallback=None, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.clickedCallback = clickedCallback

    super(CanvasLink, self).__init__(item=link, *args, **kwargs)

  def draw(self, qScene, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    print "[GUI] Drawing link {0}".format(self.item)
    
    line = OptivisLineItem(self.item.start, self.item.end, self.item.width, PyQt4.QtGui.QColor(self.item.color))

    # set callback
    line.clickedCallback = self.lineItemClicked

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

  def lineItemClicked(self, event, *args, **kwargs):
    if self.clickedCallback is not None:
      self.clickedCallback(self, event, *args, **kwargs)

class OptivisLineItem(PyQt4.QtGui.QGraphicsLineItem):
  def __init__(self, start, end, width, color, *args, **kwargs):
    # FIXME: check these are valid
    self.start = start
    self.end = end
    self.width = width
    self.color = color

    super(OptivisLineItem, self).__init__(self.start.x, self.start.y, self.end.x, self.end.y, *args, **kwargs)

    # set pen
    self.setPen(PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.color), self.width, PyQt4.QtCore.Qt.SolidLine))

    # default callback value (can't set it within __init__ for some reason, see above)
    self.clickedCallback = None

  @property
  def clickedCallback(self):
    return self.__clickedCallback

  @clickedCallback.setter
  def clickedCallback(self, clickedCallback):
    # FIXME: check that clickedCallback is a valid callable
    self.__clickedCallback = clickedCallback

  def mousePressEvent(self, event, *args, **kwargs):
    """
    This method does nothing but accept the event, but this behaviour
    is required for mouseReleaseEvent() to work below.
    """
    event.accept()
  
  def mouseReleaseEvent(self, event, *args, **kwargs):
    if self.clickedCallback is not None:
      # call callback
      self.clickedCallback(event, *args, **kwargs)
    
    # this is the default, but we'll call it anyway
    event.accept()

class CanvasLabel(object):
  def __init__(self, label, canvasLabelFlags=None, *args, **kwargs):
    if not isinstance(label, optivis.bench.labels.AbstractLabel):
      raise Exception('Specified label is not of type AbstractLabel')
    
    self.label = label
    self._canvasLabelFlags = canvasLabelFlags
    
    if canvasLabelFlags is not None:
        for kv in self.label.content.items():
            if kv[0] not in self._canvasLabelFlags:
                self._canvasLabelFlags[kv[0]] = False
                    
    super(CanvasLabel, self).__init__(*args, **kwargs)

  def draw(self, qScene):
    print "[GUI] Drawing label {0}".format(self.label)

    # create label
    text = self.label.text
    
    if self._canvasLabelFlags is not None:
        for kv in self.label.content.items():
            if self._canvasLabelFlags[kv[0]] == True:
                text += "\n%s: %2.2g" % kv

    labelItem = PyQt4.QtGui.QGraphicsTextItem(text)
    
    # calculate label size
    labelSize = optivis.geometry.Coordinates(labelItem.boundingRect().width(), labelItem.boundingRect().height())
    
    labelAzimuth = self.label.item.getLabelAzimuth() + self.label.azimuth
    
    ### calculate label position
    # get nominal position
    labelPosition = self.label.item.getLabelOrigin()
    
    # translate to user-defined position
    labelPosition = labelPosition.translate((self.label.position * self.label.item.getSize()).rotate(self.label.item.getLabelAzimuth()))
    
    # move label such that the text is y-centered
    labelPosition = labelPosition.translate(optivis.geometry.Coordinates(0, labelSize.y / 2).flip().rotate(labelAzimuth))
    
    # add user-defined offset
    labelPosition = labelPosition.translate(self.label.offset.rotate(self.label.item.getLabelAzimuth()))
    
    # set position and angle
    labelItem.setPos(labelPosition.x, labelPosition.y)
    labelItem.setRotation(labelAzimuth)

    # add to scene
    qScene.addItem(labelItem)

class OptivisItemDataType(object):
  """
  Class to define data types for editable parameters of bench items.
  """

  TEXTBOX = 1
  CHECKBOX = 2

class OptivisCanvasItemDataType(OptivisItemDataType):
  """
  Factory class for Qt objects associated with data types defined in OptivisItemDataType.
  """

  @staticmethod
  def getCanvasWidget(itemParamName, itemDataType, canvasItem):
    if not isinstance(canvasItem, AbstractCanvasItem):
      raise Exception('Specified canvas item is not of type AbstractCanvasItem')

    if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
      widget = PyQt4.QtGui.QLineEdit()

      return widget
    else:
      raise Exception('Specified item data type is invalid')

  @staticmethod
  def setCanvasWidgetValue(widget, itemDataType, itemValue):
    # FIXME: check inputs are valid
    if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
      widget.setText(str(itemValue))
    else:
      raise Exception('Specified item data type is invalid')
