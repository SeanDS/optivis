"""
Demonstration of insane double links
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas
import optivis.view.svg as svg

scene = scene.Scene(title="Example 4a")

l1 = components.Laser(name="L1")
bs1 = components.BeamSplitter(name="BS1", aoi=22.5)
m2 = components.CavityMirror(name="M2", aoi=-23)
bs2 = components.BeamSplitter(name="BS2", aoi=10)
m4 = components.CavityMirror(name="M4")
m5 = components.SteeringMirror(name="M5")

scene.reference = l1

scene.link(bs2.getOutputNode('bkA'), m5.getInputNode('fr'), length=100)
scene.link(l1.getOutputNode('out'), bs1.getInputNode('bkA'), length=50)
scene.link(bs1.getOutputNode('frB'), m2.getInputNode('fr'), length=50)
scene.link(bs1.getOutputNode('frA'), bs2.getInputNode('frA'), length=50)
scene.link(bs1.getOutputNode('bkA'), m4.getInputNode('fr'), length=50)
scene.link(m2.getOutputNode('fr'), bs2.getInputNode('frB'), length=35)

#view = svg.Svg(scene)
#view.export('scene.png', fileFormat='png')

gui = canvas.Simple(scene=scene)
gui.show()