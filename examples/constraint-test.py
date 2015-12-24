from __future__ import unicode_literals, division

import os
import os.path
import sys

import PyQt4.Qt
import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtSvg
from PyQt4.QtGui import QGraphicsLineItem as QLine

class Canvas(object):  
  qApplication = None
  qMainWindow = None
  qScene = None
  qView = None
  lines = []
  
  def __init__(self, *args, **kwargs):
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
    self.qMainWindow.setWindowTitle('Optivis')
  def initialise(self):
    # set view antialiasing
    self.qView.setRenderHints(PyQt4.QtGui.QPainter.Antialiasing | PyQt4.Qt.QPainter.TextAntialiasing | PyQt4.Qt.QPainter.SmoothPixmapTransform | PyQt4.QtGui.QPainter.HighQualityAntialiasing)
    
    # set central widget to be the view
    self.qMainWindow.setCentralWidget(self.qView)
    
    # resize main window to fit content
    self.qMainWindow.setFixedSize(500, 500)
  
  def calibrateView(self):
    self.qView.setSceneRect(self.qScene.itemsBoundingRect())

  def draw(self):
    for line in self.lines:
        thisLine = QLine()
        thisLine.setLine(line.startx, line.starty, line.endx, line.endy)
        self.qScene.addItem(thisLine)
  
  def show(self):
    # draw scene
    self.draw()
    
    self.calibrateView()

    # show on screen
    self.qMainWindow.show()
    
    sys.exit(self.qApplication.exec_())
    
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

class Line(object):
  def __init__(self, startx, starty, endx, endy):
      self.startx = startx
      self.starty = starty
      self.endx = endx
      self.endy = endy

if __name__ == '__main__':
    canvas = Canvas()
    
    canvas.lines.append(Line(0, 0, 50, 50))
    canvas.lines.append(Line(50, 50, 0, 100))
    
    canvas.show()