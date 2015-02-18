"""
Demonstration of laser and mirror.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 1")

l1 = components.Laser(name="L1", tooltip="This is a laser")
m1 = components.SteeringMirror(name="M1", tooltip="This is a mirror")

scene.addLink(links.Link(l1.getOutputNode('out'), m1.getInputNode('fr'), 50))

scene.reference = l1

gui = canvas.Simple(scene=scene)
gui.show()