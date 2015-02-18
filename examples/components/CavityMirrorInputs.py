from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# lasers
l1 = components.Laser()
l2 = components.Laser()

# mirror
m1 = components.CavityMirror(azimuth=0, aoi=45)

# link lasers to INPUTS of mirror
scene.link(outputNode=l1.getOutputNode("out"), inputNode=m1.getInputNode("fr"), length=50)
scene.link(outputNode=l2.getOutputNode("out"), inputNode=m1.getInputNode("bk"), length=100)

scene.reference = m1

gui = canvas.Simple(scene=scene)
gui.show()