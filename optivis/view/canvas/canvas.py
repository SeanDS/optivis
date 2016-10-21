# -*- coding: utf-8 -*-

"""Canvas classes"""

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

from optivis.view.view import View
import optivis.view.svg
import optivis.layout
import optivis.bench.components
import optivis.bench.links
import optivis.geometry

class Canvas(View):
    __metaclass__ = abc.ABCMeta

    qApplication = None
    qMainWindow = None
    qScene = None
    qView = None

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)

        # create empty lists for canvas stuff
        self.canvasLinks = []
        self.canvasComponents = []
        self.canvasLabels = []

        # create and initialise GUI
        self.create()
        self.initialise()

    def create(self):
        # create application
        self.qApplication = PyQt4.Qt.QApplication(sys.argv)
        self.qMainWindow = MainWindow()

        # set close behaviour to prevent zombie processes
        self.qMainWindow.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose, True)

        # create drawing area
        self.qScene = GraphicsScene()

        # create view
        self.qView = GraphicsView(self.qScene, self.qMainWindow)

        # set window title
        self.qMainWindow.setWindowTitle('Optivis - {0}'.format(self.scene.title))

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
        # set view antialiasing
        self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing | PyQt4.Qt.QPainter.TextAntialiasing | PyQt4.Qt.QPainter.SmoothPixmapTransform | PyQt4.QtGui.QPainter.HighQualityAntialiasing)

    def calibrateView(self):
        """
        Sets the view box and other rendering gubbins.
        """

        # Set view rectangle to be equal to the rectangle enclosing the items in the scene.
        #
        # This is necessary because QGraphicsView uses QGraphicsScene's sceneRect() method to obtain the size of the scene,
        # and this is always set to the LARGEST scene rectangle EVER present on the scene since its creation. Since we don't
        # want to recreate the scene object, we just have to instead do the following.
        #
        # see http://permalink.gmane.org/gmane.comp.lib.qt.user/2150
        self.qView.setSceneRect(self.qScene.itemsBoundingRect())

        # set zoom
        self.qView.setScale(self.zoom)

    def draw(self):
        # draw links
        for canvasLink in self.canvasLinks:
            canvasLink.draw(self.qScene, \
            startMarkerRadius=self.start_marker_radius, \
            endMarkerRadius=self.end_marker_radius, \
            startMarkerColor=self.start_marker_color, \
            endMarkerColor=self.end_marker_color)

            if self.show_flags & Canvas.SHOW_LINKS:
                # set visibility
                canvasLink.graphicsItem.setVisible(True)
            else:
                canvasLink.graphicsItem.setVisible(False)

            # show start and end markers?
            startMarker = self.show_flags & Canvas.SHOW_START_MARKERS
            endMarker = self.show_flags & Canvas.SHOW_END_MARKERS

            canvasLink.startMarker.setVisible(startMarker)
            canvasLink.endMarker.setVisible(endMarker)

        # draw components
        for canvasComponent in self.canvasComponents:
            canvasComponent.draw(self.qScene)

            if self.show_flags & Canvas.SHOW_COMPONENTS:
                canvasComponent.graphicsItem.setVisible(True)
            else:
                canvasComponent.graphicsItem.setVisible(False)

        # draw labels
        for canvasLabel in self.canvasLabels:
            canvasLabel.draw(self.qScene, self.labelFlags)

            if self.show_flags & Canvas.SHOW_LABELS:
                canvasLabel.graphicsItem.setVisible(True)
            else:
                canvasLabel.graphicsItem.setVisible(False)

    def redraw(self, *args, **kwargs):
        # update links
        for canvasLink in self.canvasLinks:
            if self.show_flags & Canvas.SHOW_LINKS:
                canvasLink.redraw(startMarkerRadius=self.startMarkerRadius, endMarkerRadius=self.endMarkerRadius, startMarkerColor=self.startMarkerColor, endMarkerColor=self.endMarkerColor)

                # set visibility
                canvasLink.graphicsItem.setVisible(True)
            else:
                canvasLink.graphicsItem.setVisible(False)

            # show start and end markers?
            startMarker = self.show_flags & Canvas.SHOW_START_MARKERS
            endMarker = self.show_flags & Canvas.SHOW_END_MARKERS

            canvasLink.startMarker.setVisible(startMarker)
            canvasLink.endMarker.setVisible(endMarker)

        # update components
        for canvasComponent in self.canvasComponents:
            if self.show_flags & Canvas.SHOW_COMPONENTS:
                canvasComponent.redraw()
                canvasComponent.graphicsItem.setVisible(True)
            else:
                canvasComponent.graphicsItem.setVisible(False)

        # update labels
        for canvasLabel in self.canvasLabels:
            if self.show_flags & Canvas.SHOW_LABELS:
                canvasLabel.redraw(self.labelFlags)
                canvasLabel.graphicsItem.setVisible(True)
            else:
                canvasLabel.graphicsItem.setVisible(False)

    def layout(self):
        # instantiate layout manager and arrange objects
        layout = self.layout_manager(self.scene)
        layout.arrange()

    def show(self):
        # layout scene
        self.layout()

        # create canvas items
        self.createCanvasLinks()
        self.createCanvasComponents()
        self.createCanvasLabels()

        # draw scene
        self.draw()

        # draw GUI
        self.initialise()

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

        for component in self.scene.components:
            # Add component to list of canvas components.
            self.canvasComponents.append(CanvasComponent(component))

    def createCanvasLabels(self):
        self.canvasLabels = []

        for canvasLink in self.canvasLinks:
            if canvasLink.item.labels is not None:
                # Add labels to list of canvas labels.
                for label in canvasLink.item.labels:
                    self.canvasLabels.append(CanvasLabel(label))

        for canvasComponent in self.canvasComponents:
            if canvasComponent.item.labels is not None:
                # Add labels to list of canvas labels.
                for label in canvasComponent.item.labels:
                    self.canvasLabels.append(CanvasLabel(label))

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
        svgView = optivis.view.svg.Svg(self.scene, layoutManager=self.layoutManager)
        svgView.export(*args, **kwargs)

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

class CanvasItem(object):
    """
    Class to represent an item that can be drawn on the canvas (e.g. component, link, label).
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, item, *args, **kwargs):
        self.item = item
        self.graphicsItem = None

    @property
    def graphicsItem(self):
        return self.__graphicsItem

    @graphicsItem.setter
    def graphicsItem(self, graphicsItem):
        if not isinstance(graphicsItem, (type(None), PyQt4.QtGui.QGraphicsItem, PyQt4.QtGui.QWidget, OptivisItemContainer)):
            raise Exception('Specified graphics item is not a QGraphicsItem, QWidget, OptivisItemContainer or None')

        self.__graphicsItem = graphicsItem

    @abc.abstractmethod
    def draw(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def redraw(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def setGraphicsFromItem(self):
        """
        Set graphics item information based on data from item, e.g. position, rotation, start of line, end of line, etc.
        """
        pass

class CanvasComponent(CanvasItem):
    def __init__(self, component, *args, **kwargs):
        if not isinstance(component, optivis.bench.components.Component):
            raise Exception('Specified component is not of type Component')

        super(CanvasComponent, self).__init__(item=component, *args, **kwargs)

    def draw(self, qScene):
        print "[GUI] Drawing component {0} at {1}".format(self.item, self.item.position)

        # Create full system path from filename and SVG directory.
        path = os.path.join(self.item.svg_dir, self.item.filename)

        # Create graphical representation of SVG image at path.
        self.graphicsItem = OptivisSvgItem(path)

        # reference this CanvasComponent in the data payload
        self.graphicsItem.data = self

        # set graphics information
        self.setGraphicsFromItem()

        qScene.addItem(self.graphicsItem)

    def redraw(self):
        print "[GUI] Redrawing component {0} at {1}".format(self.item, self.item.position)

        self.setGraphicsFromItem()

    def setGraphicsFromItem(self):
        # Reset transforms and rotations
        self.graphicsItem.resetTransform()

        # Set position of top-left corner.
        # self.position.{x, y} are relative to the centre of the component, so we need to compensate for this.
        self.graphicsItem.setPos(self.item.position.x - self.item.size.x / 2, self.item.position.y - self.item.size.y / 2)

        # Rotate clockwise.
        # Qt rotates with respect to the component's origin, i.e. top left, so to rotate around the centre we need to translate it before and after rotating it.
        self.graphicsItem.translate(self.item.size.x / 2, self.item.size.y / 2)
        self.graphicsItem.rotate(self.item.azimuth)
        self.graphicsItem.translate(-self.item.size.x / 2, -self.item.size.y / 2)

        # Set tooltip.
        if self.item.tooltip is not None:
            if hasattr(self.item.tooltip, "__call__"):
                self.graphicsItem.setToolTip(str(self.item.tooltip()))
            else:
                self.graphicsItem.setToolTip(str(self.item.tooltip))

class CanvasLink(CanvasItem):
    def __init__(self, link, *args, **kwargs):
        if not isinstance(link, optivis.bench.links.Link):
            raise Exception('Specified link is not of type Link')

        self.startMarker = None
        self.endMarker = None

        super(CanvasLink, self).__init__(item=link, *args, **kwargs)

    def draw(self, qScene, *args, **kwargs):
        print "[GUI] Drawing link {0}".format(self.item)

        # create graphics object(s)
        container = OptivisItemContainer()

        # reference this CanvasLink in the data payload
        container.comms.data = self

        for spec in self.item.specs:
            lineItem = OptivisLineItem()

            container.addItem(lineItem)

        self.graphicsItem = container

        # create start and end markers
        self.startMarker = PyQt4.QtGui.QGraphicsEllipseItem()
        self.endMarker = PyQt4.QtGui.QGraphicsEllipseItem()

        # add markers to graphics scene
        qScene.addItem(self.startMarker)
        qScene.addItem(self.endMarker)

        # set graphics information
        self.setGraphicsFromItem(*args, **kwargs)

        container.draw(qScene)

    def redraw(self, *args, **kwargs):
        print "[GUI] Redrawing link {0}".format(self.item)

        self.setGraphicsFromItem(*args, **kwargs)

    def setGraphicsFromItem(self, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
        for i in range(0, len(self.item.specs)):
            # create an offset coordinate
            linePos = optivis.geometry.Vector(self.item.end_pos.x \
            - self.item.start_pos.x, self.item.end_pos.y \
            - self.item.start_pos.y)
            azimuth = linePos.azimuth

            offsetPos = optivis.geometry.Vector(0, self.item.specs[i].offset)
            offsetPos = offsetPos.rotate(azimuth)

            # set start/end
            self.graphicsItem.getItem(i).setLine(self.item.start_pos.x \
            + offsetPos.x, self.item.start_pos.y + offsetPos.y, \
            self.item.end_pos.x + offsetPos.x, \
            self.item.end_pos.y + offsetPos.y)

            # create pen
            pen = PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(self.item.specs[i].color), self.item.specs[i].width, PyQt4.QtCore.Qt.SolidLine)

            # set pattern
            pen.setDashPattern(self.item.specs[i].pattern)

            # set pen
            self.graphicsItem.getItem(i).setPen(pen)

        # set markers
        self.startMarker.setRect(self.item.start_pos.x - startMarkerRadius, \
        self.item.start_pos.y - startMarkerRadius, startMarkerRadius * 2, \
        startMarkerRadius * 2)
        self.startMarker.setPen(PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(startMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine))

        self.endMarker.setRect(self.item.end_pos.x - endMarkerRadius, \
        self.item.end_pos.y - endMarkerRadius, endMarkerRadius * 2, \
        endMarkerRadius * 2)
        self.endMarker.setPen(PyQt4.QtGui.QPen(PyQt4.QtGui.QColor(endMarkerColor), 1, PyQt4.QtCore.Qt.SolidLine))

class CanvasLabel(CanvasItem):
    def __init__(self, label, *args, **kwargs):
        if not isinstance(label, optivis.bench.labels.AbstractLabel):
            raise Exception('Specified label is not of type AbstractLabel')

        super(CanvasLabel, self).__init__(item=label, *args, **kwargs)

    def draw(self, qScene, *args, **kwargs):
        print "[GUI] Drawing label {0}".format(self.item)

        # create label
        self.graphicsItem = OptivisLabelItem()

        # reference this CanvasLabel in the data payload
        self.graphicsItem.comms.data = self

        # set graphics information
        self.setGraphicsFromItem()

        # add to scene
        qScene.addItem(self.graphicsItem)

    def redraw(self, *args, **kwargs):
        print "[GUI] Redrawing label {0}".format(self.item)

        # Update graphical representation.
        self.setGraphicsFromItem(*args, **kwargs)

    def setGraphicsFromItem(self, labelFlags=None):
        ### Set label text.
        # Label text is set first so we can calculate the label's boundingRect() below.

        content = []

        # Create label sub-content
        if labelFlags is not None:
            for kv in self.item.content.items():
                if kv[0] in labelFlags.keys():
                    if labelFlags[kv[0]]:
                        # label is turned on
                        content.append("{0} = {1}".format(kv[0], kv[1]))

        # Set text
        self.graphicsItem.setText(self.item.text + "\n" + "\n".join(content))

        ### Calculate label size and azimuth.
        labelSize = optivis.geometry.Vector(self.graphicsItem.boundingRect().width(), self.graphicsItem.boundingRect().height())
        labelAzimuth = self.item.item.getLabelAzimuth() + self.item.azimuth

        ### Draw label at the correct position and orientation.

        # get nominal position
        labelPosition = self.item.item.getLabelOrigin()

        # translate to user-defined position
        labelPosition = labelPosition.translate((self.item.position * self.item.item.getSize()).rotate(self.item.item.getLabelAzimuth()))

        # move label such that the text is y-centered
        labelPosition = labelPosition.translate(optivis.geometry.Vector(0, labelSize.y / 2).flip().rotate(labelAzimuth))

        # add user-defined offset
        labelPosition = labelPosition.translate(self.item.offset.rotate(self.item.item.getLabelAzimuth()))

        # set position and angle
        self.graphicsItem.setPos(labelPosition.x, labelPosition.y)
        self.graphicsItem.setRotation(labelAzimuth)

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
        # Accept the event.
        # this is the default, but we'll call it anyway
        event.accept()

        # emit event as a signal
        self.comms.mousePressed.emit(event)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        # Accept the event.
        # this is the default, but we'll call it anyway
        event.accept()

        # emit event as a signal
        self.comms.mouseReleased.emit(event)

class OptivisLabelItemCommunicator(PyQt4.QtCore.QObject):
    """
    Qt Signals communication class for OptivisLabelItem
    """

    mousePressed = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
    mouseMoved = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
    mouseReleased = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)

class OptivisLabelItem(PyQt4.QtGui.QGraphicsSimpleTextItem):
    def __init__(self, *args, **kwargs):
        # Create a communicator.
        # This is necessary because QGraphicsSimpleTextItem does not inherit from QObject, so it does
        # not inherit signalling functionality. Instead, we do our signalling via a separate
        # communicator class which DOES inherit QObject.
        self.comms = OptivisLabelItemCommunicator()

        super(OptivisLabelItem, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event, *args, **kwargs):
        # Accept the event.
        # this is the default, but we'll call it anyway
        event.accept()

        # emit event as a signal
        self.comms.mousePressed.emit(event)

    def mouseMoveEvent(self, event, *args, **kwargs):
        # Accept the event.
        # this is the default, but we'll call it anyway
        event.accept()

        # emit event as a signal
        self.comms.mouseMoved.emit(event)

    def mouseReleaseEvent(self, event, *args, **kwargs):
        # Accept the event.
        # this is the default, but we'll call it anyway
        event.accept()

        # emit event as a signal
        self.comms.mouseReleased.emit(event)

class OptivisItemContainerCommunicator(PyQt4.QtCore.QObject):
    """
    Qt Signals communication class for OptivisItemContainer
    """

    mousePressed = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)
    mouseReleased = PyQt4.QtCore.pyqtSignal(PyQt4.QtGui.QGraphicsSceneMouseEvent)

class OptivisItemContainer(object):
    """
    Generic container for other OptivisItem objects. Supports draw().
    """

    def __init__(self):
        self.items = []

        # Create a communicator.
        self.comms = OptivisItemContainerCommunicator()

    def addItem(self, item):
        if not isinstance(item, (PyQt4.QtGui.QGraphicsItem, PyQt4.QtGui.QWidget)):
            raise Exception('Specified item is not of type QGraphicsItem or QWidget')

        item.comms.mousePressed.connect(self.comms.mousePressed)
        item.comms.mouseReleased.connect(self.comms.mouseReleased)

        self.items.append(item)

    def getItem(self, index):
        # FIXME: check index is valid and raise an exception if not (and make test)
        return self.items[index]

    def draw(self, qScene):
        for item in self.items:
            qScene.addItem(item)

    def setVisible(self, visibility):
        for item in self.items:
            item.setVisible(visibility)

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, items):
        self.__items = items

class OptivisItemDataType(object):
    """
    Class to define data types for editable parameters of bench items.
    """

    TEXTBOX = 1
    CHECKBOX = 2
    SPINBOX = 3

class OptivisCanvasItemDataType(OptivisItemDataType):
    """
    Factory class for Qt objects associated with data types defined in OptivisItemDataType.
    """

    @staticmethod
    def getCanvasWidget(itemParamName, itemDataType, *args, **kwargs):

        if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
            widget = PyQt4.QtGui.QLineEdit()

            return widget
        elif itemDataType == OptivisCanvasItemDataType.SPINBOX:
            widget = PyQt4.QtGui.QDoubleSpinBox()

            # set range and increment
            acceptRange = kwargs['acceptRange']
            increment = kwargs['increment']

            widget.setMinimum(acceptRange[0])
            widget.setMaximum(acceptRange[1])

            widget.setSingleStep(increment)

            return widget
        else:
            raise Exception('Specified item data type is invalid')

    @staticmethod
    def getCanvasWidgetValue(widget, itemDataType):
        if itemDataType == OptivisCanvasItemDataType.TEXTBOX:
            return str(widget.text())
        elif itemDataType == OptivisCanvasItemDataType.SPINBOX:
            return float(widget.value())
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
        elif itemDataType == OptivisCanvasItemDataType.SPINBOX:
            widget.setValue(float(itemValue))
        else:
            raise Exception('Specified item data type is invalid')
