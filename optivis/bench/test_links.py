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
  
  def test_valid_components(self):
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # add components to scene
    self.scene.addComponent(self.componentA)
    self.scene.addComponent(self.componentB)
    
    # can create link with components in scene
    self.assertIsNone(self.scene.addLink(link))
  
  def test_invalid_components(self):
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can't create link with components not yet added to scene
    self.assertRaises(Exception, self.scene.addLink, link)