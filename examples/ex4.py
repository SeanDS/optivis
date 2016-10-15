"""
Demonstration of funky angles of incidence.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 4")

l1 = components.Laser(name="L1")
m1 = components.CavityMirror(name="M1")
bs1 = components.BeamSplitter(name="BS", aoi=22.5)
m2 = components.CavityMirror(name="M2", aoi=-23)
m3 = components.CavityMirror(name="M3", aoi=-45)
m4 = components.CavityMirror(name="M4")

scene.link(outputNode=l1.getOutputNode('out'), inputNode=m1.getInputNode('bk'), length=50)
scene.link(outputNode=m1.getOutputNode('fr'), inputNode=bs1.getInputNode('bkA'), length=50)
scene.link(outputNode=bs1.getOutputNode('frB'), inputNode=m2.getInputNode('fr'), length=50)
scene.link(outputNode=bs1.getOutputNode('frA'), inputNode=m3.getInputNode('fr'), length=50)
scene.link(outputNode=bs1.getOutputNode('bkA'), inputNode=m4.getInputNode('fr'), length=50, pattern=[1, 2])
scene.link(outputNode=m2.getOutputNode('fr'), inputNode=m3.getInputNode('fr'), length=35)

gui = canvas.Simple(scene=scene)
gui.show()
