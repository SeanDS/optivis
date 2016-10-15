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

scene.link(outputNode=l1.getOutputNode("out"), inputNode=m1.getInputNode("fr"), length=50)

gui = canvas.Simple(scene=scene)
gui.show()
