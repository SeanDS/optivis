import Optivis

bench = Optivis.Bench(azimuth=0)

l1 = Optivis.BenchObjects.Laser(name="L1")
bs1 = Optivis.BenchObjects.BeamSplitter(name="BS", aoi=0)
m1 = Optivis.BenchObjects.CavityMirror(name="M1", aoi=45)
m2 = Optivis.BenchObjects.CavityMirror(name="M2", aoi=45)
m3 = Optivis.BenchObjects.CavityMirror(name="M3", aoi=45)

bench.addComponent(l1)
bench.addComponent(bs1)
bench.addComponent(m1)
bench.addComponent(m2)
bench.addComponent(m3)

bench.addLink(Optivis.BenchObjects.Link(l1.outputNodes[0], bs1.inputNodes[0], 100))
bench.addLink(Optivis.BenchObjects.Link(bs1.outputNodes[2], m1.inputNodes[0], 50))
bench.addLink(Optivis.BenchObjects.Link(m1.outputNodes[0], m2.inputNodes[0], 50))
bench.addLink(Optivis.BenchObjects.Link(m2.outputNodes[0], m3.inputNodes[0], 61.5))
bench.addLink(Optivis.BenchObjects.Link(m3.outputNodes[0], bs1.inputNodes[2], 38.5))

bench.draw()
