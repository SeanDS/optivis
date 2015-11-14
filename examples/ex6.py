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

scene.link(outputNode=l.getOutputNode('out'), inputNode=bs.getInputNode('bkB'), length=100, startMarker=True, endMarker=True)
scene.link(outputNode=bs.getOutputNode('frB'), inputNode=mTopRight.getInputNode('fr'), length=50, startMarker=True, endMarker=True)
scene.link(outputNode=mTopRight.getOutputNode('fr'), inputNode=mBottomRight.getInputNode('fr'), length=50, startMarker=True, endMarker=True)
scene.link(outputNode=mBottomRight.getOutputNode('fr'), inputNode=mBottomLeft.getInputNode('fr'), length=50, startMarker=True, endMarker=True)
scene.link(outputNode=mBottomLeft.getOutputNode('fr'), inputNode=bs.getInputNode('bkA'), startMarker=True, endMarker=True)

scene.reference = l

print bs.getAoiForConstrainedNodeAngle(bs.getInputNode('bkB'), bs.getInputNode('bkA'), 45)

gui = canvas.Full(scene=scene, startMarkers=True, endMarkers=True)
gui.show()