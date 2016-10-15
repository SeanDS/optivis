from __future__ import unicode_literals, division

from unittest import TestCase
import optivis.scene
import optivis.geometry
import components
import links

class TestComponentAttributes(TestCase):
  def setUp(self):
    self.componentA = components.Laser()
  
  def test_invalid_name(self):
    # name must be string
    
    # can't be number
    self.assertRaises(Exception, setattr, self.componentA, 'name', int(10))
    self.assertRaises(Exception, setattr, self.componentA, 'name', float(10))
    
    # can't be None
    self.assertRaises(Exception, setattr, self.componentA, 'name', None)
  
  def test_invalid_filename(self):    
    # filename must be string
    
    # can't be number
    self.assertRaises(Exception, setattr, self.componentA, 'filename', int(10))
    self.assertRaises(Exception, setattr, self.componentA, 'filename', float(10))
    
    # can't be None
    self.assertRaises(Exception, setattr, self.componentA, 'filename', None)

  def test_invalid_size(self):
    # size must be of class Coordinates
    self.assertRaises(Exception, setattr, self.componentA, 'size', None)
    self.assertRaises(Exception, setattr, self.componentA, 'size', int(5))
    self.assertRaises(Exception, setattr, self.componentA, 'size', float(5))
    self.assertRaises(Exception, setattr, self.componentA, 'size', [5, 5])
    self.assertRaises(Exception, setattr, self.componentA, 'size', (5, 5))
    self.assertRaises(Exception, setattr, self.componentA, 'size', '(5, 5)')
    
    # size must be positive coordinates
    self.assertRaises(Exception, setattr, self.componentA, 'size', optivis.geometry.Coordinates(-5, -5))
    self.assertRaises(Exception, setattr, self.componentA, 'size', optivis.geometry.Coordinates(-5, 5))
    self.assertRaises(Exception, setattr, self.componentA, 'size', optivis.geometry.Coordinates(5, -5))
    
  def test_invalid_azimuth(self):
    # can't be interpreted as float
    self.assertRaises(ValueError, setattr, self.componentA, 'azimuth', str('invalid'))
    
    # invalid
    self.assertRaises(TypeError, setattr, self.componentA, 'azimuth', None)
    
  def test_invalid_position(self):
    # position must be of class Coordinates
    self.assertRaises(Exception, setattr, self.componentA, 'position', None)
    self.assertRaises(Exception, setattr, self.componentA, 'position', int(5))
    self.assertRaises(Exception, setattr, self.componentA, 'position', float(5))
    self.assertRaises(Exception, setattr, self.componentA, 'position', [5, 5])
    self.assertRaises(Exception, setattr, self.componentA, 'position', (5, 5))
    self.assertRaises(Exception, setattr, self.componentA, 'position', '(5, 5)')
    
# TODO: tests for getInputNode/getOutputNode (checks whether specified node search term is string), tests for inputNodes/outputNodes setters
# TODO: test for getBoundingBox() ?