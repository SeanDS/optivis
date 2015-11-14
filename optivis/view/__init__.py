from __future__ import unicode_literals, division

import abc
import inspect
from collections import OrderedDict

import optivis.geometry
import optivis.scene
import optivis.bench.components
import optivis.bench.links
import optivis.layout

class AbstractView(object):
  __metaclass__ = abc.ABCMeta
  
  SHOW_COMPONENTS = 1 << 0
  SHOW_LINKS = 1 << 1
  SHOW_LABELS = 1 << 2
  SHOW_START_MARKERS = 1 << 3
  SHOW_END_MARKERS = 1 << 4

  # 'show all'
  SHOW_MAX = (1 << 5) - 1
  
  labelFlags = OrderedDict()
  
  def __init__(self, scene, size=None, zoom=1.0, layoutManager=None, showFlags=None, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    if size is None:
      size = optivis.geometry.Coordinates(500, 500)
      
    if layoutManager is None:
      layoutManager = optivis.layout.StandardLayout
      
    if showFlags is None:
      showFlags = AbstractView.SHOW_MAX
      
    if startMarkerColor is None:
      startMarkerColor = "red"
    
    if endMarkerColor is None:
      endMarkerColor = "blue"
    
    self.scene = scene
    self.size = size
    self.zoom = zoom
    self.layoutManager = layoutManager
    self.showFlags = showFlags
    self.startMarkers = startMarkers
    self.endMarkers = endMarkers
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    return
  
  def getLayoutManagerClasses(self):    
    managers = []
    
    # http://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    for name, obj in inspect.getmembers(optivis.layout):
      if inspect.isclass(obj):
        managers.append(obj)
    
    return managers

  @property
  def scene(self):
    return self.__scene

  @scene.setter
  def scene(self, scene):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    self.__scene = scene
  
  @property
  def size(self):
    return self.__size

  @size.setter
  def size(self, size):
    if not isinstance(size, optivis.geometry.Coordinates):
      raise Exception('Specified size is not of type optivis.geometry.Coordinates')
    
    self.__size = size
    
  @property
  def zoom(self):
    return self.__zoom
  
  @zoom.setter
  def zoom(self, zoom):
    self.__zoom = zoom
    
  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title
    
  @property
  def layoutManager(self):
    return self.__layoutManager

  @layoutManager.setter
  def layoutManager(self, layoutManager):
    if not issubclass(layoutManager, optivis.layout.AbstractLayout):
      raise Exception('Specified layout manager class is not of type AbstractLayout')

    self.__layoutManager = layoutManager
    
  @property
  def showFlags(self):
    return self.__showFlags

  @showFlags.setter
  def showFlags(self, showFlags):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    showFlags = int(showFlags)

    if showFlags < 0 or showFlags > AbstractView.SHOW_MAX:
      raise Exception('Specified show flags are not valid. Show flags value must be between 0 and {0}'.format(AbstractView.SHOW_MAX))

    self.__showFlags = showFlags
    
  @property
  def startMarkers(self):
    return self.showFlags & AbstractView.SHOW_START_MARKERS
  
  @startMarkers.setter
  def startMarkers(self, startMarkers):
    if bool(startMarkers):
      self.showFlags |= 1 << 3
    else:
      self.showFlags &= ~(1 << 3)
    
  @property
  def endMarkers(self):
    return self.showFlags & AbstractView.SHOW_END_MARKERS
  
  @endMarkers.setter
  def endMarkers(self, endMarkers):
    if bool(endMarkers):
      self.showFlags |= 1 << 4
    else:
      self.showFlags &= ~(1 << 4)
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    startMarkerRadius = float(startMarkerRadius)
    
    if startMarkerRadius < 0:
      raise Exception('Start marker radius must be >= 0')
    
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    endMarkerRadius = float(endMarkerRadius)
    
    if endMarkerRadius < 0:
      raise Exception('Start marker radius must be >= 0')
    
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerColor(self):
    return self.__startMarkerColor
  
  @startMarkerColor.setter
  def startMarkerColor(self, startMarkerColor):
    if not isinstance(startMarkerColor, basestring):
      raise Exception('Specified start marker color is not of type basestring')
    
    #FIXME: check for valid colors here
    self.__startMarkerColor = startMarkerColor
    
  @property
  def endMarkerColor(self):
    return self.__endMarkerColor
  
  @endMarkerColor.setter
  def endMarkerColor(self, endMarkerColor):
    if not isinstance(endMarkerColor, basestring):
      raise Exception('Specified end marker color is not of type basestring')
    
    #FIXME: check for valid colors here
    self.__endMarkerColor = endMarkerColor