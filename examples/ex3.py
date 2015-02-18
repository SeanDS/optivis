"""
Demonstration of beam splitter's inputs and outputs.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 3")

l = components.Laser(name="L1")
bs = components.BeamSplitter(name="BS", aoi=45)
mTopRight = components.SteeringMirror(name="Top Right", aoi=45)
mBottomRight = components.SteeringMirror(name="Bottom Right", aoi=45)
mBottomLeft = components.SteeringMirror(name="Bottom Left", aoi=45)

scene.link(outputNode=l.getOutputNode('out'), inputNode=bs.getInputNode('bkB'), length=100)
scene.link(outputNode=bs.getOutputNode('frB'), inputNode=mTopRight.getInputNode('fr'), length=50)
scene.link(outputNode=mTopRight.getOutputNode('fr'), inputNode=mBottomRight.getInputNode('fr'), length=50)
scene.link(outputNode=mBottomRight.getOutputNode('fr'), inputNode=mBottomLeft.getInputNode('fr'), length=50)
scene.link(outputNode=mBottomLeft.getOutputNode('fr'), inputNode=bs.getInputNode('frB'), length=42.5)

scene.reference = l

gui = canvas.Simple(scene=scene, startMarkers=True, endMarkers=True)
gui.show()