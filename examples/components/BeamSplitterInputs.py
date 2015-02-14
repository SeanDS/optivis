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

scene.addComponent(bs)
scene.addComponent(mPR)
scene.addComponent(mSR)
scene.addComponent(mIX)
scene.addComponent(mIY)

# link mirrors to INPUTS of beam splitter
scene.link(mPR.getOutputNode("fr"), bs.getInputNode("frA"), 25)
scene.link(mSR.getOutputNode("fr"), bs.getInputNode("bkA"), 50)
scene.link(mIX.getOutputNode("fr"), bs.getInputNode("bkB"), 75)
scene.link(mIY.getOutputNode("fr"), bs.getInputNode("frB"), 100)

scene.reference = bs

gui = canvas.Simple(scene=scene)
gui.show()