from __future__ import unicode_literals, division

import abc

import labels

class AbstractBenchItem(object):
  """
  Abstract class for any bench item (e.g. component, link) to subclass. This does not include labels.
  """
  
  __metaclass__ = abc.ABCMeta
  
  def __init__(self, labels=None, *args, **kwargs):
    self.labels = labels

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
  def labels(self):
    return self.__labels

  @labels.setter
  def labels(self, theseLabels):
    processedLabels = []

    if theseLabels is not None:
      for label in theseLabels:
        if not isinstance(label, labels.Label):
          raise Exception('Specified label is not of type Label')

        # tell label what its attached item is
        label.item = self

        processedLabels.append(label)

    self.__labels = processedLabels
