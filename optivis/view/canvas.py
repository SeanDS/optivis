from __future__ import unicode_literals, division

# custom signals
# https://stackoverflow.com/questions/4523006/pyqt-signal-with-arguments-of-arbitrary-type-pyqt-pyobject-equivalent-for-new

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
  
  def __init__(self, layoutManagerClass=None, showFlags=None, showLabelFlags=0, *args, **kwargs):
    super(AbstractCanvas, self).__init__(*args, **kwargs)

    # create empty lists for canvas stuff
    self.canvasLinks = []
    self.canvasComponents = []
    self.canvasLabels = []

    if layoutManagerClass is None:
      layoutManagerClass = optivis.layout.StandardLayout

    if showFlags is None:
      showFlags = AbstractCanvas.SHOW_MAX

    self.layoutManagerClass = layoutManagerClass
    self.showFlags = showFlags
    self.showLabelFlags = showLabelFlags

    self.create()
    self.initialise()

  @property
  def layoutManagerClass(self):
    return self.__layoutManagerClass

  @layoutManagerClass.setter
  def layoutManagerClass(self, layoutManagerClass):
    if not issubclass(layoutManagerClass, optivis.layout.AbstractLayout):
      raise Exception('Specified layout manager class is not of type AbstractLayout')

    self.__layoutManagerClass = layoutManagerClass

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
    
    # create view
    self.qView = GraphicsView(self.qScene, self.qMainWindow)
    
    # set window title
    self.qMainWindow.setWindowTitle(self.title)
    
    ### add menu and menu items
    self.menuBar = self.qMainWindow.menuBar()
    self.fileMenu = self.menuBar.addMenu('&File')
    
    exportAction = PyQt4.QtGui.QAction('Export', self.qMainWindow)
    exportAction.setShortcut('Ctrl+E')
    exportAction.triggered.connect(self.export)
    
    self.fileMenu.addAction(exportAction)
    
    exitAction = PyQt4.QtGui.QAction('Exit', self.qMainWindow)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.triggered.connect(self.qApplication.quit)
    
    self.fileMenu.addAction(exitAction)
    
  def initialise(self):
    """
    Lays out the GUI after all of the main widgets have been created by create()
    """

    self.initialiseView()

  def initialiseView(self):
    # Set view rectangle to be equal to the rectangle enclosing the items in the scene.
    #
    # This is necessary because QGraphicsView uses QGraphicsScene's sceneRect() method to obtain the size of the scene,
    # and this is always set to the LARGEST scene rectangle EVER present on the scene since its creation. Since we don't
    # want to recreate the scene object, we just have to instead do the following.
    #
    # see http://permalink.gmane.org/gmane.comp.lib.qt.user/2150
    self.qView.setSceneRect(self.qScene.itemsBoundingRect())
    
    # set transformation anchor to reference the mouse position, for mouse zooming
    self.qView.setTransformationAnchor(PyQt4.QtGui.QGraphicsView.AnchorUnderMouse)
    
    # set zoom
    self.qView.setScale(self.zoom)

    # set view antialiasing
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing | PyQt4.Qt.QPainter.TextAntialiasing | PyQt4.Qt.QPainter.SmoothPixmapTransform | PyQt4.QtGui.QPainter.HighQualityAntialiasing)
      
  def draw(self):
    # create canvas stuff
    self.createCanvasLinks()
    self.createCanvasComponents()
    self.createCanvasLabels()
    
    # draw links
    if self.showFlags & AbstractCanvas.SHOW_LINKS:
      for canvasLink in self.canvasLinks:
	# draw
        canvasLink.draw(self.qScene, startMarkers=self.startMarkers, endMarkers=self.endMarkers, startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor)

    # draw components
    if self.showFlags & AbstractCanvas.SHOW_COMPONENTS:
      for canvasComponent in self.canvasComponents:
	# draw
        canvasComponent.draw(self.qScene)

    # draw labels
    if self.showFlags & AbstractCanvas.SHOW_LABELS:
      for canvasLabel in self.canvasLabels:
	canvasLabel.draw(self.qScene)

  def redraw(self, *args, **kwargs):
    # empty the qScene
    self.qScene.clear()

    # draw the scene again
    self.draw(*args, **kwargs)

    # reset the view
    self.initialiseView()

  def layout(self):
    # instantiate layout manager and arrange objects
    layout = self.layoutManagerClass(self.scene)
    layout.arrange()
  
  def show(self):
    # layout scene
    self.layout()
    
    # draw scene
    self.draw()

    # show on screen
    self.qMainWindow.show()
    
    # if IPython is being used, don't block the terminal
    try:
        if __IPYTHON__:
            from IPython.lib.inputhook import enable_gui
            app = enable_gui('qt4')
        else:
            raise ImportError
            
    except (ImportError, NameError):
        sys.exit(self.qApplication.exec_())

  def createCanvasLinks(self):
    self.canvasLinks = []
    
    for link in self.scene.links:
      # Add link to list of canvas links.
      self.canvasLinks.append(CanvasLink(link))

  def createCanvasComponents(self):
    self.canvasComponents = []
    
    for component in self.scene.getComponents():
      # Add component to list of canvas components.
      self.canvasComponents.append(CanvasComponent(component))
  
  def createCanvasLabels(self):
    self.canvasLabels = []
    
    for canvasLink in self.canvasLinks:
      if canvasLink.item.labels is not None:
	# Add labels to list of canvas labels.
	for label in canvasLink.item.labels:
	  self.canvasLabels.append(CanvasLabel(label, canvasLabelFlags=self.canvasLabelFlags))
	
    for canvasComponent in self.canvasComponents:
      if canvasComponent.item.labels is not None:
	# Add labels to list of canvas labels.
	for label in canvasComponent.item.labels:
	  self.canvasLabels.append(CanvasLabel(label, canvasLabelFlags=self.canvasLabelFlags))
  
  def setZoom(self, zoom):
    self.zoom = zoom
    
    self.qView.setScale(self.zoom)
  
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

  def getLayoutManagerClasses(self):
    def getSubclasses(subclass):
      """
      http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
      """

      subclasses = []

      for thisSubclass in subclass.__subclasses__():
        subclasses.append(thisSubclass)
        subclasses.extend(getSubclasses(thisSubclass))

      return subclasses

    return getSubclasses(optivis.layout.AbstractLayout)

class MainWindow(PyQt4.Qt.QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

class GraphicsScene(PyQt4.QtGui.QGraphicsScene):
  def __init__(self, *args, **kwargs):
    super(GraphicsScene, self).__init__(*args, **kwargs)

class GraphicsView(PyQt4.QtGui.QGraphicsView):
  wheel = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QWheelEvent)
  
  def __init__(self, *args, **kwargs):
    # initialise this as a QObject (QGraphicsView is not a descendent of QObject and so can't send signals by default)
    PyQt4.QtCore.QObject.__init__(self)
    
    # now initialise as normal
    super(GraphicsView, self).__init__(*args, **kwargs)
    
  def wheelEvent(self, event):
    # accept the event
    event.accept()
    
    # emit event as a signal
    self.wheel.emit(event)
  
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
    super(Simple, self).initialise()

    # set central widget to be the view
    self.qMainWindow.setCentralWidget(self.qView)
    
    # resize main window to fit content
    self.qMainWindow.resize(self.size.x, self.size.y)

    return
    
class Full(AbstractCanvas):
  zoomRange = (0.1, 10)
  zoomStep = 0.1
  
  def __init__(self, *args, **kwargs):    
    super(Full, self).__init__(*args, **kwargs)
  
  def create(self, *args, **kwargs):
    super(Full, self).create(*args, **kwargs)
    
    # Add label menu.
    self.labelMenu = self.menuBar.addMenu('&Labels')
  
  def draw(self, *args, **kwargs):
    super(Full, self).draw(*args, **kwargs)
    
    # attach link click signals to handlers
    for canvasLink in self.canvasLinks:
      canvasLink.optivisLineItem.comms.mouseReleased.connect(self.canvasLinkMouseReleasedHandler)

    # attach component click signals to handlers
    for canvasComponent in self.canvasComponents:   
      canvasComponent.optivisSvgItem.mouseReleased.connect(self.canvasComponentMouseReleasedHandler)
  
  def redraw(self, refreshMenu=True, *args, **kwargs):
    super(Full, self).redraw(*args, **kwargs)
    
    if refreshMenu:
      # Now that all labels have been created the dictionary of
      # label content options should be available.
      self.labelMenu.clear()
    
      for kv in self.canvasLabelFlags.items():
        a = PyQt4.QtGui.QAction(kv[0], self.qMainWindow, checkable=True)
        a.data = kv[0]
        a.toggled.connect(self.toggleLabelContent)
        self.labelMenu.addAction(a)
        # This doesn't work!
        # checkableAction = PyQt4.QtGui.QWidgetAction(self.qMainWindow)
        # checkBox = PyQt4.QtGui.QCheckBox(kv[0], self.qMainWindow)
        # checkableAction.setDefaultWidget(checkBox)
        # self.labelMenu.addAction(checkableAction)
        
      self.labelMenu.addSeparator()
      self.labelMenu.addAction(PyQt4.QtGui.QAction("Clear all...", self.qMainWindow))
  
  def initialise(self):
    super(Full, self).initialise()

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

    ### set up signal handling

    # set mouse wheel listener for view scrolling
    self.qView.wheel.connect(self.wheelHandler)
    
    ### finish up
    
    # set container's layout
    self.container.setLayout(self.hBox)
    
    # add container to main window and set as central element
    self.qMainWindow.setCentralWidget(self.container)
    
    # set fixed size for view
    self.qView.setMinimumSize(self.size.x, self.size.y)

    return
  
  def setZoom(self, zoom):
    # calculate rounded zoom level
    zoom = round(zoom / Full.zoomStep) * Full.zoomStep
    
    # clamp zoom level to bounds
    if zoom < Full.zoomRange[0]:
      zoom = Full.zoomRange[0]
    elif zoom > Full.zoomRange[1]:
      zoom = Full.zoomRange[1]
    
    # call parent
    super(Full, self).setZoom(zoom)
    
    # update zoom slider
    self.controls.zoomSlider.setSliderPosition(self.zoom / Full.zoomStep)
    
    # update zoom spin box
    self.controls.zoomSpinBox.setValue(self.zoom)
  
  def canvasLinkMouseReleasedHandler(self, event):
    # Get clicked canvas link.
    canvasLink = self.qMainWindow.sender().data
    
    # open edit controls
    self.controls.openEditControls(canvasLink)
    
  def canvasComponentMouseReleasedHandler(self, event):
    # Get clicked canvas component.
    canvasComponent = self.qMainWindow.sender().data
    
    # open edit controls
    self.controls.openEditControls(canvasComponent)

  def toggleLabelContent(self, checked):
    sender = self.qMainWindow.sender()
    label = sender.data
    self.canvasLabelFlags[label] = checked
    self.redraw(refreshMenu=False)
    
  def wheelHandler(self, event):
    # get wheel delta, dividing by 120 (to represent 15 degrees of rotation -
    # see http://qt-project.org/doc/qt-4.8/qwheelevent.html#delta)
    delta = event.delta() / 120
    
    # calculate new zoom level
    zoom = self.zoom + delta * self.zoomStep
    
    # set zoom
    self.setZoom(zoom)

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
    self.canvas.redraw()

  @property
  def canvas(self):
    return self.__canvas
  
  @canvas.setter
  def canvas(self, canvas):
    self.__canvas = canvas

class ControlPanel(PyQt4.QtGui.QWidget):  
  def __init__(self, canvas, *args, **kwargs):
    super(ControlPanel, self).__init__(*args, **kwargs)
  
    self.canvas = canvas
    
    self.addControls()
  
  def openEditControls(self, canvasItem):
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

    ### layout chooser
    layoutGroupBox = PyQt4.QtGui.QGroupBox(title="Layout")
    layoutGroupBox.setFixedHeight(100)

    # layout label and combo box
    layoutLabel = PyQt4.QtGui.QLabel("Manager")
    self.layoutComboBox = PyQt4.QtGui.QComboBox()

    # populate combo box
    layoutManagerClasses = self.canvas.getLayoutManagerClasses()

    for i in range(0, len(layoutManagerClasses)):
      layoutManagerClass = layoutManagerClasses[i]

      # add this layout to the combobox, setting the userData to the class name of this layout
      self.layoutComboBox.addItem(layoutManagerClass.title, i)

    # set selected layout
    self.layoutComboBox.setCurrentIndex(self.layoutComboBox.findText(self.canvas.layoutManagerClass.title))

    # connect signal to slot to listen for changes
    self.layoutComboBox.currentIndexChanged[int].connect(self.layoutComboBoxChangeHandler)

    # add combo box to group box
    layoutLayout = PyQt4.QtGui.QHBoxLayout()
    
    layoutLayout.addWidget(layoutLabel)
    layoutLayout.addWidget(self.layoutComboBox)
    
    layoutGroupBox.setLayout(layoutLayout)
    
    # add layout chooser controls to control box layout
    controlLayout.addWidget(layoutGroupBox)
    
    ### zoom controls
    
    # group box for slider
    zoomSliderGroupBox = PyQt4.QtGui.QGroupBox(title="Zoom")
    zoomSliderGroupBox.setFixedHeight(100)
    
    # zoom slider
    self.zoomSlider = PyQt4.QtGui.QSlider(PyQt4.QtCore.Qt.Horizontal)
    self.zoomSlider.setFocusPolicy(PyQt4.QtCore.Qt.NoFocus)
    self.zoomSlider.setRange(self.canvas.zoomRange[0] / self.canvas.zoomStep, self.canvas.zoomRange[1] / self.canvas.zoomStep)
    self.zoomSlider.setSingleStep(1)
    self.zoomSlider.setSliderPosition(self.canvas.zoom / self.canvas.zoomStep)
    self.zoomSlider.valueChanged[int].connect(self.zoomSliderChanged)
    
    # zoom spin box
    self.zoomSpinBox = PyQt4.QtGui.QDoubleSpinBox()
    self.zoomSpinBox.setDecimals(1)
    self.zoomSpinBox.setRange(*self.canvas.zoomRange)
    self.zoomSpinBox.setSingleStep(self.canvas.zoomStep)
    self.zoomSpinBox.setValue(self.canvas.zoom) # TODO: check this is a valid step
    self.zoomSpinBox.valueChanged[float].connect(self.zoomSpinBoxChanged)
    
    # add zoom controls to zoom group box
    sliderLayout = PyQt4.QtGui.QHBoxLayout()
    
    sliderLayout.addWidget(self.zoomSlider)
    sliderLayout.addWidget(self.zoomSpinBox)
    
    zoomSliderGroupBox.setLayout(sliderLayout)
    
    # add zoom group box to control box layout
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
    
    # add marker check box group box to control box layout
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

    # add group box to control box layout
    controlLayout.addWidget(self.itemEditGroupBox)
    
    ### add layout to control widget
    self.setLayout(controlLayout)
  
  def layoutComboBoxChangeHandler(self):
    # get combo box
    layoutComboBox = self.sender()

    # get layout manager classes
    layoutManagerClasses = self.canvas.getLayoutManagerClasses()

    # get selected item's data (which is the index of the selected layout in layoutManagerClasses)
    # The toInt() returns a tuple with the data in first position and a 'status' in the second. We don't need the second one.
    layoutIndex, ok = layoutComboBox.itemData(layoutComboBox.currentIndex()).toInt()

    # update canvas layout
    self.canvas.layoutManagerClass = layoutManagerClasses[layoutIndex]

    # re-layout
    self.canvas.layout()

    # redraw
    self.canvas.redraw()

  def zoomSliderChanged(self, value):
    # scale value by zoom step (sliders only support int increments)
    self.canvas.setZoom(float(value * self.canvas.zoomStep))
  
  def zoomSpinBoxChanged(self, value):
    self.canvas.setZoom(float(value))
  
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
    self.canvas.redraw()
    
  def setEndMarkers(self, value):
    self.canvas.endMarkers = value
    self.canvas.redraw()

class OptivisItemEditPanel(PyQt4.QtGui.QWidget):
  def __init__(self, *args, **kwargs):
    super(OptivisItemEditPanel, self).__init__(*args, **kwargs)

    # create layout to use for edit controls (empty by default)
    self.vBox = PyQt4.QtGui.QVBoxLayout()
    self.vBox.setAlignment(PyQt4.QtCore.Qt.AlignTop)

    # set layout
    self.setLayout(self.vBox)

  def setEditWidgetValidity(self, widget, validity):
    if validity:
      # clear background on widget
      widget.setStyleSheet("")
    else:
      # yellow background
      widget.setStyleSheet("background-color: yellow;")    

  def paramEditWidgetTextChanged(self, *args, **kwargs):
    sender = self.sender()

    # get parameters from sender
    paramName, itemDataType, canvasItem = sender.data

    # get the canvas item associated with this edit widget
    if hasattr(canvasItem, "__call__"):
      # reference the weakref by calling it like a function
      canvasItem = canvasItem()

    if not isinstance(canvasItem, AbstractCanvasItem):
      raise Exception('Specified canvas item is not of type AbstractCanvasItem')

    ### send edit to externally linked item

    # get external object
    pykatObject = canvasItem.item.pykatObject

    # set the updated value
    try:
      setattr(pykatObject, paramName, OptivisCanvasItemDataType.getCanvasWidgetValue(sender, itemDataType))

      self.setEditWidgetValidity(sender, True)
    except AttributeError, e:
      self.setEditWidgetValidity(sender, False)
      raise Exception('Error setting attribute {0} on {1}: {2}'.format(paramName, canvasItem.item, e))
    except Exception, e:
      self.setEditWidgetValidity(sender, False)
      raise Exception('Error setting attribute {0} on {1}: {2}'.format(paramName, canvasItem.item, e))

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

    # loop over attributes from external object and create
    for paramName in attributes:
      dataType = attributes[paramName]

      # get attribute value
      paramValue = getattr(pykatObject, paramName)

      # get widget for this parameter
      try:
        paramEditWidget = OptivisCanvasItemDataType.getCanvasWidget(paramName, dataType, canvasItem)

        # give the edit widget knowledge of its canvas item
        # use a weak reference to avoid making the canvas item a zombie if it is deleted
        paramEditWidget.data = (paramName, dataType, weakref.ref(canvasItem))
      except AttributeError, e:
        print "[GUI] WARNING: the value of a parameter specified in the parameter list with this object is not available. Skipping."
        continue

      # connect edit widget text change signal to a slot that deals with it
      self.connect(paramEditWidget, PyQt4.QtCore.SIGNAL("textChanged(QString)"), self.paramEditWidgetTextChanged)
          
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
  def __init__(self, component, *args, **kwargs):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type AbstractComponent')
    
    self.optivisSvgItem = None
    
    super(CanvasComponent, self).__init__(item=component, *args, **kwargs)
  
  def draw(self, qScene):
    print "[GUI] Drawing component {0} at {1}".format(self.item, self.item.position)
    
    # Create full system path from filename and SVG directory.
    path = os.path.join(self.item.svgDir, self.item.filename)
    
    # Create graphical representation of SVG image at path.
    self.optivisSvgItem = OptivisSvgItem(path)
    
    # reference this CanvasComponent in the data payload
    self.optivisSvgItem.data = self
    
    if self.item.tooltip is not None:
      if hasattr(self.item.tooltip, "__call__"):
	self.optivisSvgItem.setToolTip(str(self.item.tooltip()))
      else:
	self.optivisSvgItem.setToolTip(str(self.item.tooltip))
    
    # Set position of top-left corner.
    # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
    self.optivisSvgItem.setPos(self.item.position.x - self.item.size.x / 2, self.item.position.y - self.item.size.y / 2)
    
    # Rotate clockwise.
    # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
    self.optivisSvgItem.translate(self.item.size.x / 2, self.item.size.y / 2)
    self.optivisSvgItem.rotate(self.item.azimuth)
    self.optivisSvgItem.translate(-self.item.size.x / 2, -self.item.size.y / 2)
    
    qScene.addItem(self.optivisSvgItem)
    
  @property
  def optivisSvgItem(self):
    return self.__optivisSvgItem
  
  @optivisSvgItem.setter
  def optivisSvgItem(self, optivisSvgItem):
    # FIXME: check type (but allow None)
    self.__optivisSvgItem = optivisSvgItem

class OptivisSvgItem(PyQt4.QtSvg.QGraphicsSvgItem):
  mousePressed = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
  mouseReleased = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
  
  def __init__(self, *args, **kwargs):
    super(OptivisSvgItem, self).__init__(*args, **kwargs)

  def mousePressEvent(self, event, *args, **kwargs):
    # accept the event
    # this is the default, but we'll call it anyway
    event.accept()
    
    # emit event as a signal
    self.mousePressed.emit(event)
  
  def mouseReleaseEvent(self, event, *args, **kwargs):
    # accept the event
    # this is the default, but we'll call it anyway
    event.accept()
    
    # emit event as a signal
    self.mouseReleased.emit(event)

class CanvasLink(AbstractCanvasItem):
  def __init__(self, link, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.optivisLineItem = None

    super(CanvasLink, self).__init__(item=link, *args, **kwargs)

  def draw(self, qScene, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    print "[GUI] Drawing link {0}".format(self.item)
    
    # create graphics object
    self.optivisLineItem = OptivisLineItem()
    
    # reference this CanvasLink in the data payload
    self.optivisLineItem.comms.data = self
    
    # set start/end
    self.optivisLineItem.setLine(self.item.start.x, self.item.start.y, self.item.end.x, self.item.end.y)
    
    # set pen
    self.optivisLineItem.setPen(PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.item.color), self.item.width, PyQt4.QtCore.Qt.SolidLine))

    # add line to graphics scene
    qScene.addItem(self.optivisLineItem)
    
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

  @property
  def optivisLineItem(self):
    return self.__optivisLineItem
  
  @optivisLineItem.setter
  def optivisLineItem(self, optivisLineItem):
    # FIXME: check type (but allow None)
    self.__optivisLineItem = optivisLineItem

class OptivisLineItemCommunicator(PyQt4.QtCore.QObject):
  """
  Qt Signals communication class for OptivisLineItem
  """
  
  mousePressed = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
  mouseReleased = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)

class OptivisLineItem(PyQt4.QtGui.QGraphicsLineItem):  
  def __init__(self, *args, **kwargs):
    # Create a communicator.
    # This is necessary because QGraphicsLineItem does not inherit from QObject, so it does
    # not inherit signalling functionality. Instead, we do our signalling via a separate
    # communicator class which DOES inherit QObject.
    self.comms = OptivisLineItemCommunicator()
    
    super(OptivisLineItem, self).__init__(*args, **kwargs)
    
  def mousePressEvent(self, event, *args, **kwargs):
    # accept the event
    # this is the default, but we'll call it anyway
    event.accept()
    
    # emit event as a signal
    self.comms.mousePressed.emit(event)
  
  def mouseReleaseEvent(self, event, *args, **kwargs):
    # accept the event
    # this is the default, but we'll call it anyway
    event.accept()
    
    # emit event as a signal
    self.comms.mouseReleased.emit(event)

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
                text += "\n%s" % kv[1]

    labelItem = PyQt4.QtGui.QGraphicsSimpleTextItem(text)
    
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
  def getCanvasWidgetValue(widget, itemDataType):
    if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
      return str(widget.text())
    else:
      raise Exception('Specified item data type is invalid')

  @staticmethod
  def setCanvasWidgetValue(widget, itemDataType, itemValue):
    # FIXME: check inputs are valid
    if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
      itemValue = str(itemValue)

      if itemValue == 'None':
        itemValue = ''

      widget.setText(itemValue)
    else:
      raise Exception('Specified item data type is invalid')
