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

  def test_invalid_width(self):
    # negative number
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, -2)
    
    # negative numeric string
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, width='-2')
    
    # can't be interpreted as float
    self.assertRaises(ValueError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, width=str('invalid'))
    
    # invalid
    self.assertRaises(TypeError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, width=None)
    
  def test_invalid_marker_radius(self):
    # negative number
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerRadius=-2)
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerRadius=-2)
    
    # negative numeric string
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerRadius='-2')
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerRadius='-2')
    
    # can't be interpreted as float
    self.assertRaises(ValueError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerRadius=str('invalid'))
    self.assertRaises(ValueError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerRadius=str('invalid'))
    
    # invalid
    self.assertRaises(TypeError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerRadius=None)
    self.assertRaises(TypeError, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerRadius=None)
    
  def test_invalid_color(self):
    # FIXME: verify valid colours are actually colours!
    
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, color=int(10))
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, color=float(10))
    
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerColor=int(10))
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, startMarkerColor=float(10))
    
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerColor=int(10))
    self.assertRaises(Exception, links.Link, self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10, endMarkerColor=float(10))