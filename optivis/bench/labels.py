from __future__ import unicode_literals, division

import optivis.geometry

class Label(object):
  def __init__(self, position, text="", offset=10):
    self.position = position
    self.text = text
    self.offset = offset

  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):
    # check position is valid object
    if not isinstance(position, float) and not isinstance(position, int):
      raise Exception('Specified position is not an integer or float')
    
    # check position is normalised
    if position < 0 or position > 1:
      raise Exception('Position should be between 0 and 1')
    
    self.__position = position

  @property
  def text(self):
    return self.__text

  @text.setter
  def text(self, text):
    if not isinstance(text, basestring):
      raise Exception('Specified label text is not of type basestring')

    self.__text = text

  @property
  def offset(self):
    return self.__offset

  @offset.setter
  def offset(self, offset):
    if not isinstance(offset, float) and not isinstance(offset, int):
      raise Exception('Specified offset is not an integer or float')

    self.__offset = offset
