from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# beam splitter
bs = components.BeamSplitter(azimuth=180+45, aoi=45)

# mirrors
mPR = components.SteeringMirror(name="PR")
mSR = components.SteeringMirror(name="SR")
mIX = components.SteeringMirror(name="IX")
mIY = components.SteeringMirror(name="IY")

# link mirrors to INPUTS of beam splitter
scene.link(outputNode=mPR.getOutputNode("fr"), inputNode=bs.getInputNode("frA"), length=25)
scene.link(outputNode=mSR.getOutputNode("fr"), inputNode=bs.getInputNode("bkA"), length=50)
scene.link(outputNode=mIX.getOutputNode("fr"), inputNode=bs.getInputNode("bkB"), length=75)
scene.link(outputNode=mIY.getOutputNode("fr"), inputNode=bs.getInputNode("frB"), length=100)

scene.reference = bs

gui = canvas.Simple(scene=scene)
gui.show()