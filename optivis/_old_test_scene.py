from __future__ import unicode_literals, division

from unittest import TestCase

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

        self.link = links.Link(self.componentA.getOutputNode('out'), self.componentB.getInputNode('fr'), length=10)

    def test_set_invalid_reference_link(self):
        self.scene.addLink(self.link)

        # can't add a component of type link
        self.assertRaises(Exception, setattr, self.scene, 'reference', self.link)

class TestSceneAddLink(TestCase):
    def setUp(self):
        self.scene = optivis.scene.Scene()
        self.componentA = components.Laser()
        self.componentB = components.CavityMirror()

    def test_add_invalid_link(self):
        # can't add a link of type Laser
        self.assertRaises(Exception, self.scene.addLink, self.componentA)
