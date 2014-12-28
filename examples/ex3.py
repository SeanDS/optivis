"""
Demonstration of beam splitter's inputs and outputs.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.gui.canvas as canvas

scene = scene.Scene(title="Example 3")

l1 = components.Laser(name="L1")
bs1 = components.BeamSplitter(name="BS", aoi=45)
m1 = components.CavityMirror(name="M1", aoi=45)
m2 = components.CavityMirror(name="M2", aoi=45)
m3 = components.CavityMirror(name="M3", aoi=45)

scene.addComponent(l1)
scene.addComponent(bs1)
scene.addComponent(m1)
scene.addComponent(m2)
scene.addComponent(m3)

scene.addLink(links.Link(l1.getOutputNode('out'), bs1.getInputNode('frA'), 100))
scene.addLink(links.Link(bs1.getOutputNode('bkA'), m1.getInputNode('fr'), 50))
scene.addLink(links.Link(m1.getOutputNode('fr'), m2.getInputNode('fr'), 50))
scene.addLink(links.Link(m2.getOutputNode('fr'), m3.getInputNode('fr'), 58))
scene.addLink(links.Link(m3.getOutputNode('fr'), bs1.getInputNode('frA'), 42.5))

gui = canvas.Simple(scene=scene, azimuth=180, startMarker=True, endMarker=True)
gui.show()