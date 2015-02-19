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

# link OUTPUTS of beam splitter to mirrors
scene.link(outputNode=bs.getOutputNode("frB"), inputNode=mPR.getInputNode("fr"), length=25)
scene.link(outputNode=bs.getOutputNode("bkB"), inputNode=mSR.getInputNode("fr"), length=50)
scene.link(outputNode=bs.getOutputNode("bkA"), inputNode=mIX.getInputNode("fr"), length=75)
scene.link(outputNode=bs.getOutputNode("frA"), inputNode=mIY.getInputNode("fr"), length=100)

gui = canvas.Simple(scene=scene)
gui.show()