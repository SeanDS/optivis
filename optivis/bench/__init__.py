from __future__ import unicode_literals, division

import abc

import labels

class AbstractBenchItem(object):
  """
  Abstract class for any bench item (e.g. component, link) to subclass. This does not include labels.
  """
  
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, label=None, *args, **kwargs):
    self.label = label

  @abc.abstractmethod
  def getLabelOrigin(self):
    pass
  
  @abc.abstractmethod
  def getLabelAzimuth(self):
    pass
  
  @abc.abstractmethod
  def getSize(self):
    pass
    
  @property
  def label(self):
    return self.__label

  @label.setter
  def label(self, label):
    if label is not None and not isinstance(label, labels.Label):
      raise Exception('Specified label is not of type Label')

    self.__label = label