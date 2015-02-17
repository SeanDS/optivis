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
scene.link(m1.getOutputNode("fr"), d1.getInputNode("in"), 50)
scene.link(m1.getOutputNode("bk"), d2.getInputNode("in"), 100)

scene.reference = m1

gui = canvas.Simple(scene=scene)
gui.show()