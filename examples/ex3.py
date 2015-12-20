"""
Demonstration of beam splitter's inputs and outputs.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.layout.constraints as constraints
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 3")

l = components.Laser(name="L1")
bs = components.BeamSplitter(name="BS", tooltip="BS")
mTopLeft = components.SteeringMirror(name="Top Left", tooltip="Top Left", aoi=-45)
mTopRight = components.SteeringMirror(name="Top Right", tooltip="Top Right", aoi=-45)
mBottomRight = components.SteeringMirror(name="Bottom Right", tooltip="Bottom Right", aoi=-45)

scene.link(outputNode=l.getOutputNode('out'), inputNode=bs.getInputNode('bkB'), length=100)
scene.link(outputNode=bs.getOutputNode('bkB'), inputNode=mTopLeft.getInputNode('fr'), length=50)
scene.link(outputNode=mTopLeft.getOutputNode('fr'), inputNode=mTopRight.getInputNode('fr'), length=50)
scene.link(outputNode=mTopRight.getOutputNode('fr'), inputNode=mBottomRight.getInputNode('fr'), length=50)
scene.link(outputNode=mBottomRight.getOutputNode('fr'), inputNode=bs.getInputNode('frB'))

#scene.addConstraint(constraints.NodeAngleConstraint(nodeA=mTopLeft.getInputNode('fr'), nodeB=mTopLeft.getOutputNode('fr'), angle=-90))
#scene.addConstraint(constraints.NodeAngleConstraint(nodeA=mTopRight.getInputNode('fr'), nodeB=mTopRight.getOutputNode('fr'), angle=-90))

scene.reference = l

gui = canvas.Simple(scene=scene, startMarkers=True, endMarkers=True)
gui.show()