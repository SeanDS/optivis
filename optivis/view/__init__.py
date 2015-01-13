from __future__ import unicode_literals, division

import abc

import optivis.geometry
import optivis.scene
import optivis.bench.components
import optivis.bench.links

class AbstractDrawable(object):
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, scene, size=None, zoom=1.0, startMarker=False, endMarker=False, startMarkerRadius=5, endMarkerRadius=3, startMarkerColor=None, endMarkerColor=None):
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
    self.startMarker = startMarker
    self.endMarker = endMarker
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