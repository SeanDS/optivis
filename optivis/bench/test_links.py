from __future__ import unicode_literals, division

from unittest import TestCase
import optivis.scene
import components
import links

class TestLinkInstantiation(TestCase):
  def setUp(self):
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()
    self.componentC = components.CavityMirror()
  
  def test_invalid_node(self):    
    # can't link input node to input node
    self.assertRaises(Exception, links.Link, self.componentB.getInputNode('fr'), self.componentC.getInputNode('fr'), 10)
    
    # can't link output node to output node
    self.assertRaises(Exception, links.Link, self.componentB.getOutputNode('fr'), self.componentC.getOutputNode('fr'), 10)
    
    # can't swap input with output node
    self.assertRaises(Exception, links.Link, self.componentB.getInputNode('fr'), self.componentC.getOutputNode('fr'), 10)
    
    # can't link component to self
    self.assertRaises(Exception, links.Link, self.componentB.getOutputNode('fr'), self.componentB.getInputNode('fr'), 10)
  
  def test_invalid_length(self):    
    # negative number
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), -10)
    
    # negative numeric string
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), '-10')
    
    # can't be interpreted as float
    self.assertRaises(ValueError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), str('invalid'))
    
    # invalid
    self.assertRaises(TypeError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), None)

class TestLinkAttributes(TestCase):
  def setUp(self):    
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()
    
    self.link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
  def test_invalid_width(self):
    # negative number
    self.assertRaises(Exception, setattr, self.link, 'width', -2)
    
    # negative numeric string
    self.assertRaises(Exception, setattr, self.link, 'width', '-2')
    
    # can't be interpreted as float
    self.assertRaises(Exception, setattr, self.link, 'width', str('invalid'))
    
    # invalid
    self.assertRaises(Exception, setattr, self.link, 'width', None)
  
  def test_invalid_pattern(self):
    # invalid type
    self.assertRaises(Exception, setattr, self.link, 'pattern', str('invalid'))
    self.assertRaises(Exception, setattr, self.link, 'pattern', None)
    
    # odd number of elements
    self.assertRaises(Exception, setattr, self.link, 'pattern', [1, 2, 3])
    
    # invalid elements
    self.assertRaises(Exception, setattr, self.link, 'pattern', [1, 2, 3, str('invalid')])