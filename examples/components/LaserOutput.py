from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene()

# laser
l1 = components.Laser(name="L1", azimuth=45)

# mirror
m1 = components.SteeringMirror(name="M1")

scene.link(l1.getOutputNode("out"), m1.getInputNode("fr"), 50)

gui = canvas.Simple(scene=scene)
gui.show()