from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# mirror
m1 = components.SteeringMirror(azimuth=0, aoi=45)

# dump
d1 = components.Dump()

# link OUTPUT of mirror to dump
scene.link(outputNode=m1.getOutputNode("fr"), inputNode=d1.getInputNode("in"), length=50)

scene.reference = m1

gui = canvas.Simple(scene=scene)
gui.show()