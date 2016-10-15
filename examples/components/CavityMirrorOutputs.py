from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# mirror
m1 = components.CavityMirror(azimuth=0, aoi=45)

# dumps
d1 = components.Dump()
d2 = components.Dump()

# link OUTPUTS of mirror to dumps
scene.link(outputNode=m1.getOutputNode("fr"), inputNode=d1.getInputNode("in"), length=50)
scene.link(outputNode=m1.getOutputNode("bk"), inputNode=d2.getInputNode("in"), length=100)

scene.reference = m1

gui = canvas.Simple(scene=scene)
gui.show()
