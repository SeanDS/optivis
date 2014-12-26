from __future__ import division

import datetime
import math

import BenchObjects

class Bench(object):
  ###
  # Optivis canvas components

  components = []
  links = []
  
  def __init__(self, title=None):
    if title is None:
      title = datetime.datetime.now().strftime('%Y-%M-%d %H:%M')
    
    self.title = title
    
    return
    
  def addComponent(self, component):
    if not isinstance(component, BenchObjects.Component):    
      raise Exception('Specified component is not of type BenchObjects.Component')
    
    self.components.append(component)
  
  def addLink(self, link):
    if not isinstance(link, BenchObjects.Link):
      raise Exception('Specified link is not of type BenchObjects.Link')
    
    if not link.inputNode.component in self.components:
      raise Exception('Input node component has not been added to table')
    
    if not link.outputNode.component in self.components:
      raise Exception('Output node component has not been added to table')
    
    self.links.append(link)

  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title

class Coordinates(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  @property
  def x(self):
    return self.__x
  
  @x.setter
  def x(self, x):
    self.__x = x
  
  @property
  def y(self):
    return self.__y
  
  @y.setter
  def y(self, y):
    self.__y = y
    
  def translate(self, *args):
    translation = Coordinates(0, 0)
    
    for arg in args:
      translation += arg
    
    return Coordinates(self.x + translation.x, self.y + translation.y)
  
  def rotate(self, azimuth):
    """
    Rotation of coordinates about the origin using a left-handed coordinate system.
    Azimuth is the angle in degrees to rotate in a clockwise direction.
    """
    
    # apply rotation matrix to x and y
    xRot = self.x * math.cos(math.radians(azimuth)) - self.y * math.sin(math.radians(azimuth))
    yRot = self.x * math.sin(math.radians(azimuth)) + self.y * math.cos(math.radians(azimuth))
    
    return Coordinates(xRot, yRot)
  
  def flip(self):
    return Coordinates(-self.x, -self.y)
  
  def __eq__(self, otherCoordinates):
    """
    Compare coordinate floats without precision errors. Based on http://code.activestate.com/recipes/577124-approximately-equal/.
    """
    
    # FIXME: move these settings somewhere user-setable
    tol=1e-18
    rel=1e-7
    
    if tol is rel is None:
      raise TypeError('Cannot specify both absolute and relative errors are None')
    
    xTests = []
    yTests = []
    
    if tol is not None:
      xTests.append(tol)
      yTests.append(tol)
      
    if rel is not None:
      xTests.append(rel * abs(self.x))
      yTests.append(rel * abs(self.y))
    
    assert xTests
    assert yTests
    
    return (abs(self.x - otherCoordinates.x) <= max(xTests)) and (abs(self.y - otherCoordinates.y) <= max(yTests))
  
  def __ne__(self, otherCoordinates):
    return not self.__eq__(otherCoordinates)
  
  def __gt__(self, otherCoordinates):
    if otherCoordinates.x > self.x and otherCoordinates.y > self.y:
      return True
    
    return False
  
  def __lt__(self, otherCoordinates):
    if otherCoordinates.x < self.x and otherCoordinates.y < self.y:
      return True
    
    return False
  
  def __mul__(self, factor):
    if isinstance(factor, Coordinates):
      return Coordinates(self.x * factor.x, self.y * factor.y)
    else:
      return Coordinates(self.x * factor, self.y * factor)
  
  def __truediv__(self, factor):
    if isinstance(factor, Coordinates):
      return Coordinates(self.x / factor.x, self.y / factor.y)
    else:
      return Coordinates(self.x / factor, self.y / factor)
  
  def __div__(self, factor):
    return self.__truediv__(factor)
    
  def __add__(self, factor):
    if isinstance(factor, Coordinates):
      return Coordinates(self.x + factor.x, self.y + factor.y)
    else:
      return Coordinates(self.x + factor, self.y + factor)
    
  def __sub__(self, factor):
    if isinstance(factor, Coordinates):
      return Coordinates(self.x - factor.x, self.y - factor.y)
    else:
      return Coordinates(self.x - factor, self.y - factor)