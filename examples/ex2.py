"""
Demonstration of components with non-zero angles of incidence.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.bench.labels as labels
import optivis.view.canvas as canvas
import optivis.geometry

scene = scene.Scene(title="Example 2")

laser = components.Laser(name="Laser")
wp1 = components.QuarterWavePlate(name="Quarter Wave Plate")
wp2 = components.HalfWavePlate(name="Half Wave Plate")
isol = components.FaradayIsolator(name="Faraday Isolator")
eom = components.ElectroopticModulator(name="EOM")
lens1 = components.ConvexLens(name="Lens 1")
lens2 = components.ConcaveLens(name="Lens 2")
mirror1 = components.CavityMirror(name="Mirror 1", aoi=30)
mirror2 = components.CavityMirror(name="Mirror 2", aoi=15)
mirror3 = components.CavityMirror(name="Mirror 3", aoi=-45)
pd = components.Photodiode(name="Photodiode")

scene.link(laser.getOutputNode('out'), wp1.getInputNode('fr'), 40, label=labels.Label(0.5, text="laser->wp1", offset=10))
scene.link(wp1.getOutputNode('bk'), wp2.getInputNode('fr'), 10)
scene.link(wp2.getOutputNode('bk'), isol.getInputNode('fr'), 30)
scene.link(isol.getOutputNode('bk'), lens1.getInputNode('fr'), 30)
scene.link(lens1.getOutputNode('bk'), lens2.getInputNode('fr'), 10)
scene.link(lens2.getOutputNode('bk'), eom.getInputNode('fr'), 30)
scene.link(eom.getOutputNode('bk'), mirror1.getInputNode('fr'), 100)
scene.link(mirror1.getOutputNode('fr'), mirror2.getInputNode('fr'), 100, label=labels.Label(0.5, text="mirror1->mirror2", offset=10))
scene.link(mirror2.getOutputNode('fr'), mirror3.getInputNode('fr'), 150, label=labels.Label(0.5, text="mirror2->mirror3", offset=10))
scene.link(mirror3.getOutputNode('fr'), pd.getInputNode('in'), 65)

gui = canvas.Full(scene)
gui.show()
