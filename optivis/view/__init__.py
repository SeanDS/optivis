from __future__ import unicode_literals, division

import abc

import optivis.geometry
import optivis.scene
import optivis.bench.components
import optivis.bench.links

class AbstractView(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, scene, size=None, zoom=1.0, startMarkers=False, endMarkers=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
    if not isinstance(scene, optivis.scene.Scene):
      raise Exception('Specified scene is not of type optivis.scene.Scene')
    
    title = "Optivis - {0}".format(scene.title)
    
    if size is None:
      size = optivis.geometry.Coordinates(500, 500)
      
    if startMarkerColor is None:
      startMarkerColor = "red"
    
    if endMarkerColor is None:
      endMarkerColor = "blue"
    
    self.scene = scene
    self.size = size
    self.zoom = zoom
    self.title = title
    self.startMarkers = startMarkers
    self.endMarkers = endMarkers
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerColor = startMarkerColor
    self.endMarkerColor = endMarkerColor
    
    return

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
  def startMarkers(self):
    return self.__startMarkers
  
  @startMarkers.setter
  def startMarkers(self, startMarkers):
    self.__startMarkers = bool(startMarkers)
    
  @property
  def endMarkers(self):
    return self.__endMarkers
  
  @endMarkers.setter
  def endMarkers(self, endMarkers):
    self.__endMarkers = bool(endMarkers)
    
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