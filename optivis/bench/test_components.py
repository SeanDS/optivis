from __future__ import unicode_literals, division

from unittest import TestCase
import optivis.scene
import components
import links

class TestComponentAttributes(TestCase):
  def setUp(self):
    self.componentA = components.Laser()
  
  def test_invalid_filename(self):    
    # filename must be string
    
    # can't be number
    self.assertRaises(Exception, setattr, self.componentA, 'filename', int(10))
    self.assertRaises(Exception, setattr, self.componentA, 'filename', float(10))
    
    # can't be None
    self.assertRaises(Exception, setattr, self.componentA, 'filename', None)
    
  def test_invalid_name(self):
    # name must be string
    
    # can't be number
    self.assertRaises(Exception, setattr, self.componentA, 'name', int(10))
    self.assertRaises(Exception, setattr, self.componentA, 'name', float(10))
    
    # can't be None
    self.assertRaises(Exception, setattr, self.componentA, 'name', None)