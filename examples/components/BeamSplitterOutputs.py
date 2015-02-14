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

# link OUTPUTS of beam splitter to mirrors
scene.link(bs.getOutputNode("frB"), mPR.getInputNode("fr"), 25)
scene.link(bs.getOutputNode("bkB"), mSR.getInputNode("fr"), 50)
scene.link(bs.getOutputNode("bkA"), mIX.getInputNode("fr"), 75)
scene.link(bs.getOutputNode("frA"), mIY.getInputNode("fr"), 100)

gui = canvas.Simple(scene=scene)
gui.show()