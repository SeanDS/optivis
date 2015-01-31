from __future__ import unicode_literals, division

from unittest import TestCase
import copy

import optivis.scene
import optivis.bench.components as components
import optivis.bench.links as links

class TestSceneSetTitle(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
  
  def test_invalid_titles(self):
    self.assertRaises(Exception, setattr, self.scene, 'title', int(10))
    self.assertRaises(Exception, setattr, self.scene, 'title', float(1))
    self.assertRaises(Exception, setattr, self.scene, 'title', dict(one=1, two=2, three=3))
    self.assertRaises(Exception, setattr, self.scene, 'title', list('abc'))
    self.assertRaises(Exception, setattr, self.scene, 'title', set('abc'))
    self.assertRaises(Exception, setattr, self.scene, 'title', frozenset('abc'))
    self.assertRaises(Exception, setattr, self.scene, 'title', tuple('abc'))

class TestSceneSetReference(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
    
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()

    self.link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
  
  def test_set_invalid_reference_link(self):
    self.scene.addComponent(self.componentA)
    self.scene.addComponent(self.componentB)
    self.scene.addLink(self.link)
    
    # can't add a component of type link
    self.assertRaises(Exception, setattr, self.scene, 'reference', self.link)
    
  def test_set_invalid_reference_component(self):    
    # can't add a component reference if it is not in the scene
    self.assertRaises(Exception, setattr, self.scene, 'reference', self.componentA)

class TestSceneAddComponent(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
    
  def test_add_valid_component(self):
    component = components.Laser()
    
    # can add a component of type laser
    self.assertIsNone(self.scene.addComponent(component))
  
  def test_add_invalid_component(self):
    componentA = components.Laser()
    componentB = components.CavityMirror()

    link = links.Link(componentA.getOutputNode('out'), componentB.getInputNode('fr'), 10)
    
    # can't add a component of type link
    self.assertRaises(Exception, self.scene.addComponent, link)
    
class TestSceneAddLink(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
    self.componentA = components.Laser()
    self.componentB = components.CavityMirror()
  
  def test_add_invalid_link(self):    
    # can't add a link of type Laser
    self.assertRaises(Exception, self.scene.addLink, self.componentA)
  
  def test_add_link_components_not_in_scene_A(self):
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can't create link with components not yet added to scene
    self.assertRaises(Exception, self.scene.addLink, link)
    
  def test_add_link_components_not_in_scene_B(self):
    # add only one of the two linked components
    self.scene.addComponent(self.componentA)
    
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can't create link with other component not in scene
    self.assertRaises(Exception, self.scene.addLink, link)
    
  def test_add_link_components_not_in_scene_C(self):
    # add only one of the two linked components
    self.scene.addComponent(self.componentB)
    
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can't create link with other component not in scene
    self.assertRaises(Exception, self.scene.addLink, link)