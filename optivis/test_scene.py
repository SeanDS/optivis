from __future__ import unicode_literals, division

from unittest import TestCase
import optivis.scene
import optivis.bench.components as components
import optivis.bench.links as links

class TestSceneInstantiation(TestCase):
  def test_invalid_titles(self):
    self.assertRaises(Exception, optivis.scene.Scene, title=int(1))
    self.assertRaises(Exception, optivis.scene.Scene, title=float(1))
    self.assertRaises(Exception, optivis.scene.Scene, title=dict(one=1, two=2, three=3))
    self.assertRaises(Exception, optivis.scene.Scene, title=list('abc'))
    self.assertRaises(Exception, optivis.scene.Scene, title=set('abc'))
    self.assertRaises(Exception, optivis.scene.Scene, title=frozenset('abc'))
    self.assertRaises(Exception, optivis.scene.Scene, title=tuple('abc'))
    
  def test_valid_titles(self):
    self.assertIsInstance(optivis.scene.Scene(title=None), optivis.scene.Scene)
    self.assertIsInstance(optivis.scene.Scene(title=unicode('Title')), optivis.scene.Scene)
    self.assertIsInstance(optivis.scene.Scene(title=str('Title')), optivis.scene.Scene)

  def test_valid_init(self):
    self.assertIsInstance(optivis.scene.Scene(), optivis.scene.Scene)
    self.assertIsInstance(optivis.scene.Scene(title=None), optivis.scene.Scene)

class TestSceneSetReference(TestCase):
  def setUp(self):
    self.scene = optivis.scene.Scene()
    
  def test_set_valid_reference(self):
    component = components.Laser()
    
    # can set reference component of type laser
    self.assertIsNone(setattr(self.scene, 'reference', component))
  
  def test_set_invalid_reference(self):
    componentA = components.Laser()
    componentB = components.CavityMirror()

    link = links.Link(componentA.getOutputNode('out'), componentB.getInputNode('fr'), 10)
    
    # can't add a component of type link
    self.assertRaises(Exception, setattr, self.scene, 'reference', link)

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
    
  def test_add_valid_link(self):
    # add components to scene
    self.scene.addComponent(self.componentA)
    self.scene.addComponent(self.componentB)
    
    link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), 10)
    
    # can add a link of type Link
    self.assertIsNone(self.scene.addLink(link))
  
  def test_add_invalid_link(self):    
    # can't add a link of type Laser
    self.assertRaises(Exception, self.scene.addLink, self.componentA)