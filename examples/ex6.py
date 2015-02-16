"""
Demonstration of full GUI.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 6")

l = components.Laser(name="L1")
bs = components.BeamSplitter(name="BS", aoi=45)
mTopRight = components.SteeringMirror(name="Top Right", aoi=45)
mBottomRight = components.SteeringMirror(name="Bottom Right", aoi=45)
mBottomLeft = components.SteeringMirror(name="Bottom Left", aoi=45)

scene.link(l.getOutputNode('out'), bs.getInputNode('bkB'), 100, startMarker=True, endMarker=True)
scene.link(bs.getOutputNode('frB'), mTopRight.getInputNode('fr'), 50, startMarker=True, endMarker=True)
scene.link(mTopRight.getOutputNode('fr'), mBottomRight.getInputNode('fr'), 50, startMarker=True, endMarker=True)
scene.link(mBottomRight.getOutputNode('fr'), mBottomLeft.getInputNode('fr'), 50, startMarker=True, endMarker=True)
scene.link(mBottomLeft.getOutputNode('fr'), bs.getInputNode('frB'), 42.5, startMarker=True, endMarker=True)

scene.reference = l

gui = canvas.Full(scene=scene, startMarkers=True, endMarkers=True)
gui.show()