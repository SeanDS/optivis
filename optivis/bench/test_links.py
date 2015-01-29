from __future__ import unicode_literals, division

from unittest import TestCase
import optivis.scene
import components
import links

class TestLinkInstantiation(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()
    self.componentC = components.CavityMirror()
  
  def test_invalid_components(self):
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can't create link with components not yet added to scene
    self.assertRaises(Exception, self.scene.addLink, link)
  
  def test_invalid_node(self):
    # add components
    self.scene.addComponent(self.componentB)
    self.scene.addComponent(self.componentC)
    
    # can't link input node to input node
    self.assertRaises(Exception, links.Link, self.componentB.getInputNode('fr'), self.componentC.getInputNode('fr'), 10)
    
    # can't link output node to output node
    self.assertRaises(Exception, links.Link, self.componentB.getOutputNode('fr'), self.componentC.getOutputNode('fr'), 10)
    
    # can't swap input with output node
    self.assertRaises(Exception, links.Link, self.componentB.getInputNode('fr'), self.componentC.getOutputNode('fr'), 10)
    
    # can't link component to self
    self.assertRaises(Exception, links.Link, self.componentB.getOutputNode('fr'), self.componentB.getInputNode('fr'), 10)
  
  def test_invalid_length(self):
    # add components
    self.scene.addComponent(self.componentA)
    self.scene.addComponent(self.componentB)
    
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
    self.scene = optivis.scene.Scene()
    
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()
    
    self.scene.addComponent(self.componentA)
    self.scene.addComponent(self.componentB)
    
    self.link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    self.scene.addLink(self.link)
    
  def test_invalid_width(self):
    # negative number
    self.assertRaises(Exception, setattr, self.link, 'width', -2)
    
    # negative numeric string
    self.assertRaises(Exception, setattr, self.link, 'width', '-2')
    
    # can't be interpreted as float
    self.assertRaises(Exception, setattr, self.link, 'width', str('invalid'))
    
    # invalid
    self.assertRaises(Exception, setattr, self.link, 'width', None)
    
  def test_invalid_marker_radius(self):
    # negative number
    self.assertRaises(Exception, setattr, self.link, 'startMarkerRadius', -2)
    self.assertRaises(Exception, setattr, self.link, 'endMarkerRadius', -2)
    
    # negative numeric string
    self.assertRaises(Exception, setattr, self.link, 'startMarkerRadius', '-2')
    self.assertRaises(Exception, setattr, self.link, 'endMarkerRadius', '-2')
    
    # can't be interpreted as float
    self.assertRaises(ValueError, setattr, self.link, 'startMarkerRadius', str('invalid'))
    self.assertRaises(ValueError, setattr, self.link, 'endMarkerRadius', str('invalid'))
    
    # invalid
    self.assertRaises(TypeError, setattr, self.link, 'startMarkerRadius', None)
    self.assertRaises(TypeError, setattr, self.link, 'endMarkerRadius', None)
    
  def test_invalid_color(self):
    # FIXME: verify valid colours are actually colours!
    
    # int
    self.assertRaises(Exception, setattr, self.link, 'color', int(10))
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', int(10))
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', int(10))
    
    # float
    self.assertRaises(Exception, setattr, self.link, 'color', float(10))
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', float(10))
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', float(10))
    
    # invalid
    self.assertRaises(Exception, setattr, self.link, 'color', None)
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', None)
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', None)