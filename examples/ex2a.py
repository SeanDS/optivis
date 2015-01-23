"""
Demonstration of components with non-zero angles of incidence.
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

scene.addComponent(laser)
scene.addComponent(wp1)
scene.addComponent(wp2)
scene.addComponent(isol)
scene.addComponent(eom)
scene.addComponent(lens1)
scene.addComponent(lens2)
scene.addComponent(mirror1)
scene.addComponent(mirror2)
scene.addComponent(mirror3)
scene.addComponent(pd)

scene.addLink(links.Link(laser.getOutputNode('out'), wp1.getInputNode('fr'), 40))
scene.addLink(links.Link(wp1.getOutputNode('bk'), wp2.getInputNode('fr'), 10))
scene.addLink(links.Link(wp2.getOutputNode('bk'), isol.getInputNode('fr'), 30))
scene.addLink(links.Link(isol.getOutputNode('bk'), lens1.getInputNode('fr'), 30))
scene.addLink(links.Link(lens1.getOutputNode('bk'), lens2.getInputNode('fr'), 10))
scene.addLink(links.Link(lens2.getOutputNode('bk'), eom.getInputNode('fr'), 30))
scene.addLink(links.Link(eom.getOutputNode('bk'), mirror1.getInputNode('fr'), 100))
scene.addLink(links.Link(mirror1.getOutputNode('fr'), mirror2.getInputNode('fr'), 100))
scene.addLink(links.Link(mirror2.getOutputNode('fr'), mirror3.getInputNode('fr'), 150))
scene.addLink(links.Link(mirror3.getOutputNode('fr'), pd.getInputNode('in'), 65))

gui = canvas.Simple(scene)
gui.show()