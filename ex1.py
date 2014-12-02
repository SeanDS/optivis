"""
Demonstration of angles of incidence.
"""

import Optivis
import Optivis.GUI

bench = Optivis.Bench(title="Example 1")

laser = Optivis.BenchObjects.Laser(name="Laser")
wp1 = Optivis.BenchObjects.QuarterWavePlate(name="Quarter Wave Plate")
wp2 = Optivis.BenchObjects.HalfWavePlate(name="Half Wave Plate")
isol = Optivis.BenchObjects.FaradayIsolator(name="Faraday Isolator")
eom = Optivis.BenchObjects.ElectroopticModulator(name="EOM")
lens1 = Optivis.BenchObjects.ConvexLens(name="Lens 1")
lens2 = Optivis.BenchObjects.ConcaveLens(name="Lens 2")
mirror1 = Optivis.BenchObjects.CavityMirror(name="Mirror 1", aoi=30)
mirror2 = Optivis.BenchObjects.CavityMirror(name="Mirror 2", aoi=15)
mirror3 = Optivis.BenchObjects.CavityMirror(name="Mirror 3", aoi=15)
#pd = Optivis.BenchObjects.Photodiode(name="Photodiode")

bench.addComponent(laser)
bench.addComponent(wp1)
bench.addComponent(wp2)
bench.addComponent(isol)
bench.addComponent(eom)
bench.addComponent(lens1)
bench.addComponent(lens2)
bench.addComponent(mirror1)
bench.addComponent(mirror2)
bench.addComponent(mirror3)
#bench.addComponent(pd)

bench.addLink(Optivis.BenchObjects.Link(laser.getOutputNode('out'), wp1.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(wp1.getOutputNode('bk'), wp2.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(wp2.getOutputNode('bk'), isol.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(isol.getOutputNode('bk'), lens1.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(lens1.getOutputNode('bk'), lens2.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(lens2.getOutputNode('bk'), eom.getInputNode('fr'), 10))
bench.addLink(Optivis.BenchObjects.Link(eom.getOutputNode('bk'), mirror1.getInputNode('fr'), 100))
bench.addLink(Optivis.BenchObjects.Link(mirror1.getOutputNode('fr'), mirror2.getInputNode('fr'), 100))
bench.addLink(Optivis.BenchObjects.Link(mirror2.getOutputNode('fr'), mirror3.getInputNode('fr'), 150))
#bench.addLink(Optivis.BenchObjects.Link(mirror3.getOutputNode('fr'), pd.getInputNode('in'), 150))

gui = Optivis.GUI.Tkinter(bench)
gui.show()