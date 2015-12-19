"""
Demonstration of constraints.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.layout.constraints as constraints
import optivis.view.canvas as canvas
import optivis.layout

scene = scene.Scene(title="Example 7")

l = components.Laser(name="L1")
bs = components.BeamSplitter(name="BS")
m1 = components.SteeringMirror(name="Mirror 1")
m2 = components.SteeringMirror(name="Mirror 2")

scene.link(outputNode=l.getOutputNode('out'), inputNode=bs.getInputNode('bkB'), length=100, startMarker=True, endMarker=True)
scene.link(outputNode=bs.getOutputNode('bkB'), inputNode=m1.getInputNode('fr'), length=50, startMarker=True, endMarker=True)
scene.link(outputNode=m1.getOutputNode('fr'), inputNode=m2.getInputNode('fr'), length=100, startMarker=True, endMarker=True)
scene.link(outputNode=m2.getOutputNode('fr'), inputNode=bs.getInputNode('frA'), startMarker=True, endMarker=True)

scene.reference = l

gui = canvas.Full(scene=scene, startMarkers=True, endMarkers=True)
gui.show()