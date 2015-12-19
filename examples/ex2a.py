"""
Demonstration of subgroups joined together
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas

scene = scene.Scene(title="Example 2a")

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

# first group
scene.link(laser.getOutputNode('out'), wp1.getInputNode('fr'), length=40)
scene.link(wp1.getOutputNode('bk'), wp2.getInputNode('fr'), length=10)
scene.link(wp2.getOutputNode('bk'), isol.getInputNode('fr'), length=30)
scene.link(isol.getOutputNode('bk'), lens1.getInputNode('fr'), length=30)

# second group
scene.link(lens2.getOutputNode('bk'), eom.getInputNode('fr'), length=30)
scene.link(eom.getOutputNode('bk'), mirror1.getInputNode('fr'), length=100)
scene.link(mirror1.getOutputNode('fr'), mirror2.getInputNode('fr'), length=100)
scene.link(mirror2.getOutputNode('fr'), mirror3.getInputNode('fr'), length=150)
scene.link(mirror3.getOutputNode('fr'), pd.getInputNode('in'), length=65)

# link groups
scene.link(lens1.getOutputNode('bk'), lens2.getInputNode('fr'), length=10)

gui = canvas.Simple(scene)
gui.show()