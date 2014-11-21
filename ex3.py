"""
Beam splitter test
"""

import Optivis

bench = Optivis.Bench(azimuth=180)

l1 = Optivis.BenchObjects.Laser(name="L1")
bs1 = Optivis.BenchObjects.BeamSplitter(name="BS", aoi=-22.5)
m1 = Optivis.BenchObjects.CavityMirror(name="M1")
m2 = Optivis.BenchObjects.CavityMirror(name="M2")
m3 = Optivis.BenchObjects.CavityMirror(name="M3")
m4 = Optivis.BenchObjects.CavityMirror(name="M4")

bench.addComponent(l1)
bench.addComponent(bs1)
bench.addComponent(m1)
#bench.addComponent(m2)
#bench.addComponent(m3)
#bench.addComponent(m4)

bench.addLink(Optivis.BenchObjects.Link(l1.getOutputNode('out'), bs1.getInputNode('frA'), 100))
bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkB'), m1.getInputNode('fr'), 25))
bench.addLink(Optivis.BenchObjects.Link(m1.getOutputNode('fr'), bs1.getInputNode('frA'), 25, colour="blue"))
#bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('frB'), m2.getInputNode('fr'), 50))
#bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkA'), m3.getInputNode('fr'), 75))
#bench.addLink(Optivis.BenchObjects.Link(bs1.getOutputNode('bkB'), m4.getInputNode('fr'), 100))

bench.draw()