"""
Demonstration of scaling.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas
import optivis.geometry as geometry

scene = scene.Scene(title="Example 5")

l1 = components.Laser(name="L1")
m1 = components.CavityMirror(name="M1")
bs1 = components.BeamSplitter(name="BS", aoi=22.5)
m2 = components.CavityMirror(name="M2", aoi=-23)
m3 = components.CavityMirror(name="M3", aoi=-45)
m4 = components.CavityMirror(name="M4")

scene.link(l1.getOutputNode('out'), m1.getInputNode('bk'), 50)
scene.link(m1.getOutputNode('fr'), bs1.getInputNode('bkA'), 50)
scene.link(bs1.getOutputNode('frB'), m2.getInputNode('fr'), 50)
scene.link(bs1.getOutputNode('frA'), m3.getInputNode('fr'), 50)
scene.link(bs1.getOutputNode('bkA'), m4.getInputNode('fr'), 50)
scene.link(m2.getOutputNode('fr'), m3.getInputNode('fr'), 35)

gui = canvas.Simple(scene=scene, size=geometry.Coordinates(1000, 700), zoom=3)
gui.show()