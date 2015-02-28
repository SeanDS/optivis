from __future__ import unicode_literals, division

import abc

import optivis.bench
import optivis.geometry

class AbstractLabel(object):
  def __init__(self, *args, **kwargs):
    super(AbstractLabel, self).__init__(*args, **kwargs)

class Label(AbstractLabel):
  def __init__(self, text, position=None, item=None, azimuth=0, offset=None, content=None, *args, **kwargs):
    """
    Instantiate label.
    
    Azimuth denotes the rotation of the label with respect to the item it is
    attached to's absolute azimuth, so an azimuth of zero will draw the label
    in the same direction as the item.
    """
    
    super(Label, self).__init__(*args, **kwargs)
    
    if position is None:
      position = optivis.geometry.Coordinates(0, 0)
    
    if offset is None:
      offset = optivis.geometry.Coordinates(0, 0)
    
    if content is None:
      content = {}

    self.text = text
    self.position = position
    self.item = item
    self.azimuth = azimuth
    self.offset = offset
    self.content = content

  def __str__(self):
    return "\"{0}\"".format(self.text)

  @property
  def text(self):
    return self.__text
  
  @text.setter
  def text(self, text):
    if not isinstance(text, basestring):
      raise Exception('Specified label text is not of type basestring')

    self.__text = text
  
  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):    
    # check position is valid object
    if not isinstance(position, optivis.geometry.Coordinates):
      raise Exception('Specified position is not of type Coordinates')
    
    self.__position = position
    
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    # raises TypeError if input is invalid, or ValueError if a string input can't be interpreted
    azimuth = float(azimuth)
    
    self.__azimuth = azimuth

  @property
  def item(self):
    return self.__item

  @item.setter
  def item(self, item):
    if item is not None and not isinstance(item, optivis.bench.AbstractBenchItem):
      raise Exception('Specified item is not of type AbstractBenchItem')

    self.__item = item

  @property
  def offset(self):
    return self.__offset

  @offset.setter
  def offset(self, offset):
    if not isinstance(offset, optivis.geometry.Coordinates):
      raise Exception('Specified offset is not of type Coordinates')

    self.__offset = offset
