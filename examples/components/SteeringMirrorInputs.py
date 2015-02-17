from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# laser
l1 = components.Laser()

# mirror
m1 = components.SteeringMirror(azimuth=0, aoi=45)

# link laser to INPUT of mirror
scene.link(l1.getOutputNode("out"), m1.getInputNode("fr"), 50)

scene.reference = m1

gui = canvas.Simple(scene=scene)
gui.show()