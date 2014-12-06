"""
Demonstration of scaling.
"""

import Optivis
import Optivis.Gui

bench = Optivis.Bench(title="Example 5")

l1 = Optivis.BenchObjects.Laser(name="L1")
m1 = Optivis.BenchObjects.CavityMirror(name="M1")
bs1 = Optivis.BenchObjects.BeamSplitter(name="BS", aoi=-22.5)
m2 = Optivis.BenchObjects.CavityMirror(name="M2")
m3 = Optivis.BenchObjects.CavityMirror(name="M3", aoi=33.75)
m4 = Optivis.BenchObjects.CavityMirror(name="M4", aoi=-33.75)

bench.addComponent(l1)
bench.addComponent(bs1)
bench.addComponent(m1)
bench.addComponent(m2)
bench.addComponent(m3)
bench.addComponent(m4)

bench.addLink(Optivis.BenchObjects.Link(l1.getOutputNode('out'), m1.getInputNode('bk'), 50))
bench.addLink(Optivis.BenchObjects.Link(m1.getOutputNode('fr'), bs1.getInputNode('frA'), 50))
bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('frA'), m2.getInputNode('fr'), 50))
bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkA'), m3.getInputNode('fr'), 50))
bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkB'), m4.getInputNode('fr'), 50))
bench.addLink(Optivis.BenchObjects.Link(m3.getOutputNode('fr'), m4.getInputNode('fr'), 38.27))

gui = Optivis.Gui.Qt(bench=bench, size=Optivis.Coordinates(1000, 700), zoom=3, azimuth=180, startMarker=False, endMarker=False)
gui.show()