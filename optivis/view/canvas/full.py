# -*- coding: utf-8 -*-

"""Canvas classes"""

from __future__ import unicode_literals, division

class FullCanvas(Canvas):
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
            canvasLink.graphicsItem.comms.mouseReleased.connect(self.canvasLinkMouseReleasedHandler)

        # attach component click signals to handlers
        for canvasComponent in self.canvasComponents:
            canvasComponent.graphicsItem.mouseReleased.connect(self.canvasComponentMouseReleasedHandler)

        # attach link click signals to handlers
        for canvasLabel in self.canvasLabels:
            canvasLabel.graphicsItem.comms.mousePressed.connect(self.canvasLabelMousePressedHandler)
            canvasLabel.graphicsItem.comms.mouseMoved.connect(self.canvasLabelMouseMovedHandler)
            canvasLabel.graphicsItem.comms.mouseReleased.connect(self.canvasLabelMouseReleasedHandler)

    def redraw(self, refreshLabelMenu=True, *args, **kwargs):
        # Refresh label flags
        for canvasLabel in self.canvasLabels:
            if canvasLabel.item.content is not None:
                for kv in canvasLabel.item.content.items():
                    if kv[0] not in self.labelFlags.keys():
                        # add label to list of labels, but set it off by default
                        self.labelFlags[kv[0]] = False

        if refreshLabelMenu:
            # Now that all labels have been created the dictionary of
            # label content options should be available.
            self.labelMenu.clear()

            for kv in self.labelFlags.items():
                a = PyQt4.QtGui.QAction(kv[0], self.qMainWindow, checkable=True)

                # set widget data to the label key
                a.data = kv[0]

                # set toggled status
                a.setChecked(kv[1])

                # connect signal to handler
                a.toggled.connect(self.toggleLabelContent)

                # add to menu
                self.labelMenu.addAction(a)

            self.labelMenu.addSeparator()
            self.labelMenu.addAction(PyQt4.QtGui.QAction("Clear all...", self.qMainWindow))

        # call parent redraw
        super(Full, self).redraw(*args, **kwargs)

        # update scene to avoid graphical artifacts
        self.qScene.update()

    def initialise(self):
        super(Full, self).initialise()

        ### create controls

        # add control widgets
        self.controls = ControlPanel(self)
        self.controls.setFixedWidth(300)

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

        # set transformation anchor to reference the mouse position, for mouse zooming
        self.qView.setTransformationAnchor(PyQt4.QtGui.QGraphicsView.AnchorUnderMouse)

        # set view box, etc.
        self.calibrateView()

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

    def canvasLabelMousePressedHandler(self, event):
        # Get clicked canvas label.
        canvasLabel = self.qMainWindow.sender().data

        # Set position of mouse, in case this press becomes a drag
        self.canvasLabelMousePosition = self.qView.mapFromScene(event.scenePos())

    def canvasLabelMouseMovedHandler(self, event):
        canvasItem = self.qMainWindow.sender()

        # Get moved canvas label.
        canvasLabel = canvasItem.data

        # event position
        eventPos = self.qView.mapFromScene(event.scenePos())

        # difference
        difference = eventPos - self.canvasLabelMousePosition

        # set canvas label position to original position plus the difference
        projection = optivis.geometry.Coordinates(difference.x(), 0).rotate(canvasLabel.item.azimuth)

        # set label offset
        canvasLabel.item.offset = canvasLabel.item.offset + projection

        # redraw scene
        self.redraw()

        # update mouse position
        self.canvasLabelMousePosition = eventPos

    def canvasLabelMouseReleasedHandler(self, event):
        # Get clicked canvas label.
        canvasLabel = self.qMainWindow.sender().data

        # open edit controls
        self.controls.openEditControls(canvasLabel)

    def toggleLabelContent(self, checked):
        sender = self.qMainWindow.sender()
        label = sender.data
        self.labelFlags[label] = checked
        self.redraw(refreshLabelMenu=False)

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
        self.button4 = PyQt4.QtGui.QCheckBox("Start Markers")
        self.button4.setChecked(self.canvas.showFlags & AbstractCanvas.SHOW_START_MARKERS)
        self.button4.stateChanged.connect(self.showCheckBoxChanged)
        self.button5 = PyQt4.QtGui.QCheckBox("End Markers")
        self.button5.setChecked(self.canvas.showFlags & AbstractCanvas.SHOW_END_MARKERS)
        self.button5.stateChanged.connect(self.showCheckBoxChanged)

        # add buttons to layout
        self.hBox.addWidget(self.button1)
        self.hBox.addWidget(self.button2)
        self.hBox.addWidget(self.button3)
        self.hBox.addWidget(self.button4)
        self.hBox.addWidget(self.button5)

        # set layout of widget
        self.setLayout(self.hBox)

    def showCheckBoxChanged(self, *args, **kwargs):
        # just rebuild the show bitfield using all checkboxes
        self.canvas.showFlags = (self.button1.isChecked() << 0) | (self.button2.isChecked() << 1) | (self.button3.isChecked() << 2) | (self.button4.isChecked() << 3) | (self.button5.isChecked() << 4)

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

        ### scene controls group (layout and reference component)
        sceneControlsGroupBox = PyQt4.QtGui.QGroupBox(title="Scene")
        sceneControlsGroupBox.setFixedHeight(100)

        sceneControlsGroupBoxLayout = PyQt4.QtGui.QVBoxLayout()

        ## layout controls

        # create a container for this edit widget
        layoutContainer = PyQt4.QtGui.QWidget()
        layoutContainerLayout = PyQt4.QtGui.QHBoxLayout()

        # remove padding between widgets
        layoutContainerLayout.setContentsMargins(0, 0, 0, 0)

        layoutLabel = PyQt4.QtGui.QLabel("Manager")
        self.layoutComboBox = PyQt4.QtGui.QComboBox()

        # populate combo box
        layoutManagerClasses = self.canvas.getLayoutManagerClasses()

        for i in range(0, len(layoutManagerClasses)):
            # instantiate layout manager correctly
            layoutManager = layoutManagerClasses[i](self.canvas.scene)

            # add this layout to the combobox, setting the userData to the class name of this layout
            self.layoutComboBox.addItem(layoutManager.title, i)

        # set selected layout
        self.layoutComboBox.setCurrentIndex(self.layoutComboBox.findText(self.canvas.layoutManager.title))

        # connect signal to slot to listen for changes
        self.layoutComboBox.currentIndexChanged[int].connect(self.layoutComboBoxChangeHandler)

        # create layout edit button
        layoutEditButton = PyQt4.QtGui.QPushButton("Edit")
        layoutEditButton.clicked.connect(self.layoutEditButtonClickHandler)

        # add combo box to group box
        layoutContainerLayout.addWidget(layoutLabel, 1)
        layoutContainerLayout.addWidget(self.layoutComboBox, 4)
        layoutContainerLayout.addWidget(layoutEditButton, 1)

        # set layout container layout
        layoutContainer.setLayout(layoutContainerLayout)

        # add container to scene controls group
        sceneControlsGroupBoxLayout.addWidget(layoutContainer)

        ## scene reference controls

        # create a container for this edit widget
        referenceContainer = PyQt4.QtGui.QWidget()
        referenceContainerLayout = PyQt4.QtGui.QHBoxLayout()

        # remove padding between widgets
        referenceContainerLayout.setContentsMargins(0, 0, 0, 0)

        # reference label combo box
        referenceLabel = PyQt4.QtGui.QLabel("Reference")
        self.referenceComboBox = PyQt4.QtGui.QComboBox()

        # populate combo box
        canvasComponents = self.canvas.canvasComponents

        # add 'Default'
        self.referenceComboBox.addItem('Default', 0)

        for i in range(0, len(canvasComponents)):
            canvasComponent = canvasComponents[i]

            # add this layout to the combobox, setting the userData to the class name of this layout
            self.referenceComboBox.addItem(str(canvasComponent.item), i)

        # set selected layout
        if self.canvas.scene.reference is None:
            # default value
            self.referenceComboBox.setCurrentIndex(0)
        else:
            self.referenceComboBox.setCurrentIndex(self.referenceComboBox.findText(str(self.canvas.scene.reference)))

        # connect signal to slot to listen for changes
        self.referenceComboBox.currentIndexChanged[int].connect(self.referenceComboBoxChangeHandler)

        # add combo box to group box
        referenceContainerLayout.addWidget(referenceLabel, 1)
        referenceContainerLayout.addWidget(self.referenceComboBox, 2)

        referenceContainer.setLayout(referenceContainerLayout)

        sceneControlsGroupBoxLayout.addWidget(referenceContainer)

        # set scene controls layout
        sceneControlsGroupBox.setLayout(sceneControlsGroupBoxLayout)

        # add all to control box
        controlLayout.addWidget(sceneControlsGroupBox)

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

        ### item edit controls

        # group box for item edit controls
        self.itemEditGroupBox = PyQt4.QtGui.QGroupBox(title="Attributes")

        # edit panel within scroll area within group box
        self.itemEditScrollArea = PyQt4.QtGui.QScrollArea()
        self.itemEditPanel = OptivisItemEditPanel()
        self.itemEditPanel.parameterEdited.connect(self.parameterEditedHandler)
        self.itemEditScrollArea.setWidget(self.itemEditPanel)
        self.itemEditScrollArea.setWidgetResizable(True)
        itemEditGroupBoxLayout = PyQt4.QtGui.QVBoxLayout()
        itemEditGroupBoxLayout.addWidget(self.itemEditScrollArea)
        self.itemEditGroupBox.setLayout(itemEditGroupBoxLayout)

        # add group box to control box layout
        controlLayout.addWidget(self.itemEditGroupBox)

        ### add layout to control widget
        self.setLayout(controlLayout)

    def parameterEditedHandler(self):
        """
        Handles signals from edit panel showing that a parameter has been edited.
        """

        # an edited parameter might have changed the look of the view, so lay it out again and redraw
        self.canvas.layout()
        self.canvas.redraw()

    def layoutComboBoxChangeHandler(self):
        # get combo box
        layoutComboBox = self.sender()

        # get layout manager classes
        layoutManagerClasses = self.canvas.getLayoutManagerClasses()

        # get selected item's data (which is the index of the selected layout in layoutManagerClasses)
        # The toInt() returns a tuple with the data in first position and a 'status' in the second. We don't need the second one.
        layoutIndex, ok = layoutComboBox.itemData(layoutComboBox.currentIndex()).toInt()

        # update canvas layout
        self.canvas.layoutManager = layoutManagerClasses[layoutIndex]

        # re-layout
        self.canvas.layout()

        # redraw
        self.canvas.redraw()

        # reset view
        self.canvas.calibrateView()

    def layoutEditButtonClickHandler(self):
        print self.canvas.layoutManager.title
        layoutEditWindow = CanvasScaleFunctionEditor(self.canvas.qMainWindow, self.canvas.layoutManager)
        layoutEditWindow.show()

    def referenceComboBoxChangeHandler(self):
        # get combo box
        referenceComboBox = self.sender()

        # get components
        canvasComponents = self.canvas.canvasComponents

        # get selected item's data (which is the index of the selected component in canvasComponents)
        # The toInt() returns a tuple with the data in first position and a 'status' in the second. We don't need the second one.
        componentIndex, ok = referenceComboBox.itemData(referenceComboBox.currentIndex()).toInt()

        # update scene reference
        if componentIndex == 0:
            # 'None'
            self.canvas.scene.reference = None
        else:
            self.canvas.scene.reference = canvasComponents[componentIndex].item

        # re-layout
        self.canvas.layout()

        # redraw
        self.canvas.redraw()

        # reset view
        self.canvas.calibrateView()

    def zoomSliderChanged(self, value):
        # scale value by zoom step (sliders only support int increments)
        self.canvas.setZoom(float(value * self.canvas.zoomStep))

    def zoomSpinBoxChanged(self, value):
        self.canvas.setZoom(float(value))

class OptivisItemEditPanel(PyQt4.QtGui.QWidget):
    # signal to emit when item parameters are edited in the GUI
    parameterEdited = PyQt4.QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(OptivisItemEditPanel, self).__init__(*args, **kwargs)

        # create layout to use for edit controls (empty by default)
        self.vBox = PyQt4.QtGui.QVBoxLayout()
        self.vBox.setAlignment(PyQt4.QtCore.Qt.AlignTop)

        # set layout
        self.setLayout(self.vBox)

    def paramEditWidgetChanged(self, *args, **kwargs):
        # get widget that sent the signal
        sender = self.sender()

        # get parameter data associated with this widget
        paramName, paramType, target = self.extractParamEditWidgetPayload(sender)

        # get param value
        paramValue = OptivisCanvasItemDataType.getCanvasWidgetValue(sender, paramType)

        ### send new value to associated bench item
        self.setParamOnTarget(target, paramName, paramValue, sender)

        # emit signal
        self.parameterEdited.emit()

    def extractParamEditWidgetPayload(self, sender):
        # get parameters from sender
        paramName, paramType, target = sender.data

        # get the canvas item associated with this edit widget
        if hasattr(target, "__call__"):
            # reference the weakref by calling it like a function
            target = target()

        return (paramName, paramType, target)

    def setParamOnTarget(self, target, paramName, paramValue, widget):
        try:
            setattr(target, paramName, paramValue)

            self.setEditWidgetValidity(widget, True)
        except AttributeError, e:
            self.setEditWidgetValidity(widget, False)
            raise Exception('Error setting attribute {0} on {1}: {2}'.format(paramName, target, e))
        except Exception, e:
            self.setEditWidgetValidity(widget, False)
            raise Exception('Error setting attribute {0} on {1}: {2}'.format(paramName, target, e))

    def setEditWidgetValidity(self, widget, validity):
        if validity:
            # clear background on widget
            widget.setStyleSheet("")
        else:
            # yellow background
            widget.setStyleSheet("background-color: yellow;")

    def setContentFromCanvasItem(self, canvasItem):
        # empty current contents
        # from http://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
        for i in reversed(range(self.vBox.count())):
            self.vBox.itemAt(i).widget().setParent(None)

        ### Add built-in attributes.

        # Create a group box for built-in parameters
        parameterGroupBox = PyQt4.QtGui.QGroupBox(title=str(canvasItem.item))
        layout = PyQt4.QtGui.QVBoxLayout()
        layout.setAlignment(PyQt4.QtCore.Qt.AlignTop)

        # set layout
        parameterGroupBox.setLayout(layout)

        # Component specific controls.
        if isinstance(canvasItem.item, optivis.bench.components.AbstractComponent):
            # Add aoi control
            aoiEditWidget = OptivisCanvasItemDataType.getCanvasWidget('aoi', OptivisCanvasItemDataType.SPINBOX, acceptRange=[-360, 360], increment=1)

            # set data
            aoiEditWidget.data = ('aoi', OptivisCanvasItemDataType.SPINBOX, weakref.ref(canvasItem.item))

            # connect edit widget text change signal to a slot that deals with it
            aoiEditWidget.valueChanged[float].connect(self.paramEditWidgetChanged)

            OptivisCanvasItemDataType.setCanvasWidgetValue(aoiEditWidget, OptivisCanvasItemDataType.SPINBOX, getattr(canvasItem.item, 'aoi'))

            # create a container for this edit widget
            container = PyQt4.QtGui.QWidget()
            containerLayout = PyQt4.QtGui.QHBoxLayout()

            # remove padding between widgets
            containerLayout.setContentsMargins(0, 0, 0, 0)

            # create label
            label = PyQt4.QtGui.QLabel(text="{0} aoi".format(canvasItem.item))

            # add label and edit widget to layout
            containerLayout.addWidget(label, 2) # stretch 2
            containerLayout.addWidget(aoiEditWidget, 1) # stretch 1

            # set layout of container
            container.setLayout(containerLayout)

            # add container to edit panel
            layout.addWidget(container)

        # Link specific controls.
        if isinstance(canvasItem.item, optivis.bench.links.AbstractLink):
            # Add length control
            lengthEditWidget = OptivisCanvasItemDataType.getCanvasWidget('length', OptivisCanvasItemDataType.SPINBOX, acceptRange=[0, float('inf')], increment=1)

            # set data
            lengthEditWidget.data = ('length', OptivisCanvasItemDataType.SPINBOX, weakref.ref(canvasItem.item))

            # connect edit widget text change signal to a slot that deals with it
            lengthEditWidget.valueChanged[float].connect(self.paramEditWidgetChanged)

            OptivisCanvasItemDataType.setCanvasWidgetValue(lengthEditWidget, OptivisCanvasItemDataType.SPINBOX, getattr(canvasItem.item, 'length'))

            # create a container for this edit widget
            container = PyQt4.QtGui.QWidget()
            containerLayout = PyQt4.QtGui.QHBoxLayout()

            # remove padding between widgets
            containerLayout.setContentsMargins(0, 0, 0, 0)

            # create label
            label = PyQt4.QtGui.QLabel(text='Length')

            # add label and edit widget to layout
            containerLayout.addWidget(label, 2) # stretch 2
            containerLayout.addWidget(lengthEditWidget, 1) # stretch 1

            # set layout of container
            container.setLayout(containerLayout)

            # add container to edit panel
            layout.addWidget(container)

        # Label specific controls.
        elif isinstance(canvasItem.item, optivis.bench.labels.AbstractLabel):
            azimuthEditWidget = OptivisCanvasItemDataType.getCanvasWidget('azimuth', OptivisCanvasItemDataType.SPINBOX, acceptRange=[-360, 360], increment=1)

            # set data
            azimuthEditWidget.data = ('azimuth', OptivisCanvasItemDataType.SPINBOX, weakref.ref(canvasItem.item))

            # connect edit widget text change signal to a slot that deals with it
            azimuthEditWidget.valueChanged[float].connect(self.paramEditWidgetChanged)

            OptivisCanvasItemDataType.setCanvasWidgetValue(azimuthEditWidget, OptivisCanvasItemDataType.SPINBOX, getattr(canvasItem.item, 'azimuth'))

            # create a container for this edit widget
            container = PyQt4.QtGui.QWidget()
            containerLayout = PyQt4.QtGui.QHBoxLayout()

            # remove padding between widgets
            containerLayout.setContentsMargins(0, 0, 0, 0)

            # create label
            label = PyQt4.QtGui.QLabel(text='azimuth')

            # add label and edit widget to layout
            containerLayout.addWidget(label, 2) # stretch 2
            containerLayout.addWidget(azimuthEditWidget, 1) # stretch 1

            # set layout of container
            container.setLayout(containerLayout)

            # add container to edit panel
            layout.addWidget(container)

        # Now that we've added built-in edit controls, add the layout to the panel
        self.vBox.addWidget(parameterGroupBox)

        # Add external parameters, if available.
        # These are only available on AbstractBenchItems, so components and links (but not labels).
        if isinstance(canvasItem.item, optivis.bench.AbstractBenchItem):
            # Create a group box for these external parameters
            externalParameterGroupBox = PyQt4.QtGui.QGroupBox(title='External Parameters')
            externalLayout = PyQt4.QtGui.QVBoxLayout()
            externalLayout.setAlignment(PyQt4.QtCore.Qt.AlignTop)

            # set layout
            externalParameterGroupBox.setLayout(externalLayout)

            if canvasItem.item.paramList is not None:
                # external edit controls provided

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
                        paramEditWidget = OptivisCanvasItemDataType.getCanvasWidget(paramName, dataType)

                        # give the edit widget knowledge of its canvas item
                        # use a weak reference to avoid making the canvas item a zombie if it is deleted
                        paramEditWidget.data = (paramName, dataType, weakref.ref(pykatObject))
                    except AttributeError, e:
                        print "[GUI] WARNING: the value of a parameter specified in the parameter list with this object is not available. Skipping."
                        continue

                    # connect edit widget text change signal to a slot that deals with it
                    self.connect(paramEditWidget, PyQt4.QtCore.SIGNAL("textChanged(QString)"), self.paramEditWidgetChanged)

                    OptivisCanvasItemDataType.setCanvasWidgetValue(paramEditWidget, dataType, paramValue)

                    # create a container for this edit widget
                    container = PyQt4.QtGui.QWidget()
                    containerLayout = PyQt4.QtGui.QHBoxLayout()

                    # remove padding between widgets
                    containerLayout.setContentsMargins(0, 0, 0, 0)

                    # create label
                    label = PyQt4.QtGui.QLabel(text=paramName)

                    # add label and edit widget to layout
                    containerLayout.addWidget(label, 2) # stretch 2
                    containerLayout.addWidget(paramEditWidget, 1) # stretch 1

                    # set layout of container
                    container.setLayout(containerLayout)

                    # add container to edit panel
                    externalLayout.addWidget(container)

                # Now that we've added external edit controls, add the layout to the panel
                self.vBox.addWidget(externalParameterGroupBox)

class CanvasScaleFunctionEditor(PyQt4.Qt.QMainWindow):
    def __init__(self, layoutManager, *args, **kwargs):
        self.layoutManager = layoutManager

        super(CanvasScaleFunctionEditor, self).__init__(*args, **kwargs)

    @property
    def layoutManager(self):
        return self.__layoutManager

    @layoutManager.setter
    def layoutManager(self, layoutManager):
        if not isinstance(layoutManager, optivis.layout.AbstractLayout):
            raise Exception('Specified layout manager is not of type AbstractLayout')

        self.__layoutManager = layoutManager
