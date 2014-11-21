import Optivis

bench = Optivis.Bench()

l1 = Optivis.BenchObjects.Laser(name="L1")
m1 = Optivis.BenchObjects.CavityMirror(name="M1", aoi=30)
m2 = Optivis.BenchObjects.CavityMirror(name="M2", aoi=15)
m3 = Optivis.BenchObjects.CavityMirror(name="M3", aoi=0)

bench.addComponent(l1)
bench.addComponent(m1)
bench.addComponent(m2)
bench.addComponent(m3)

bench.addLink(Optivis.BenchObjects.Link(l1.outputNodes[0], m1.inputNodes[0], 100))
bench.addLink(Optivis.BenchObjects.Link(m1.outputNodes[0], m2.inputNodes[0], 100))
bench.addLink(Optivis.BenchObjects.Link(m2.outputNodes[0], m3.inputNodes[0], 150))

bench.draw()
