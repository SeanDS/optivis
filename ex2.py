"""
Demonstration of beam splitter's inputs and outputs.
"""

import Optivis
import Optivis.Gui

bench = Optivis.Bench(title="Example 2")

l1 = Optivis.BenchObjects.Laser(name="L1")
bs1 = Optivis.BenchObjects.BeamSplitter(name="BS", aoi=45)
m1 = Optivis.BenchObjects.CavityMirror(name="M1", aoi=45)
m2 = Optivis.BenchObjects.CavityMirror(name="M2", aoi=45)
m3 = Optivis.BenchObjects.CavityMirror(name="M3", aoi=45)

bench.addComponent(l1)
bench.addComponent(bs1)
bench.addComponent(m1)
bench.addComponent(m2)
bench.addComponent(m3)

bench.addLink(Optivis.BenchObjects.Link(l1.getOutputNode('out'), bs1.getInputNode('frA'), 100))
bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkA'), m1.getInputNode('fr'), 50))
bench.addLink(Optivis.BenchObjects.Link(m1.getOutputNode('fr'), m2.getInputNode('fr'), 50))
bench.addLink(Optivis.BenchObjects.Link(m2.getOutputNode('fr'), m3.getInputNode('fr'), 58))
bench.addLink(Optivis.BenchObjects.Link(m3.getOutputNode('fr'), bs1.getInputNode('frA'), 42.5))

gui = Optivis.Gui.Qt(bench=bench, azimuth=180, startMarker=True, endMarker=True)
gui.show()