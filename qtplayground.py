"""
Qt playground
"""

import os
import sys

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg

application = PyQt4.Qt.QApplication(sys.argv)
scene = PyQt4.QtGui.QGraphicsScene()
view = PyQt4.QtGui.QGraphicsView(scene)

view.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing)
view.resize(500, 500)
view.scale(2, 2)

path1 = os.path.join('svg', 'c-laser1.svg')
path2 = os.path.join('svg', 'c-laser2.svg')

item1 = PyQt4.QtSvg.QGraphicsSvgItem(path1)
item1.setPos(0, 0)
#transform = PyQt4.QtGui.QTransform()
#transform.translate(-100, -100)
#transform.rotate(45)
#item1.setTransform(transform)

item2 = PyQt4.QtSvg.QGraphicsSvgItem(path2)
item2.setPos(100, 100)
#item2.rotate(-45)

item3 = PyQt4.QtGui.QGraphicsLineItem(0, 0, 100, 100)

scene.addItem(item1)
scene.addItem(item2)
scene.addItem(item3)

view.show()
sys.exit(application.exec_())