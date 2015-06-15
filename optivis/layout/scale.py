from __future__ import unicode_literals, division

class ScaleFunction(object):  
  def __init__(self, powers=None, coefficients=None):
    if powers is None:
      powers = [1]
    
    if coefficients is None:
      coefficients = [1]
    
    self.powers = powers
    self.coefficients = coefficients
    
    if len(self.powers) != len(self.coefficients):
      raise Exception('Specified powers and coefficients lists have different lengths')
  
  def getScaledLength(self, length):
    scaledLength = 0
    
    for i in range(0, len(self.powers)):
      scaledLength += self.coefficients[i] * length ** self.powers[i]
    
    return scaledLength
    
  @property
  def powers(self):
    return self.__powers

  @powers.setter
  def powers(self, powers):
    if not isinstance(powers, (list, tuple)):
      raise Exception('Specified powers is not a list or tuple')
    
    self.__powers = powers
    
  @property
  def coefficients(self):
    return self.__coefficients

  @coefficients.setter
  def coefficients(self, coefficients):
    if not isinstance(coefficients, (list, tuple)):
      raise Exception('Specified coefficients is not a list or tuple')
    
    self.__coefficients = coefficients