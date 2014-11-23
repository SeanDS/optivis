"""
Demonstration of angles of incidence.
"""

import Optivis
import Optivis.GUI

bench = Optivis.Bench(title="Example 1")

l1 = Optivis.BenchObjects.Laser(name="L1")
m1 = Optivis.BenchObjects.CavityMirror(name="M1", aoi=30)
m2 = Optivis.BenchObjects.CavityMirror(name="M2", aoi=15)
m3 = Optivis.BenchObjects.CavityMirror(name="M3", aoi=0)

bench.addComponent(l1)
bench.addComponent(m1)
bench.addComponent(m2)
bench.addComponent(m3)

bench.addLink(Optivis.BenchObjects.Link(l1.getOutputNode('out'), m1.getInputNode('fr'), 100))
bench.addLink(Optivis.BenchObjects.Link(m1.getOutputNode('fr'), m2.getInputNode('fr'), 100))
bench.addLink(Optivis.BenchObjects.Link(m2.getOutputNode('fr'), m3.getInputNode('fr'), 150))

gui = Optivis.GUI.Tkinter(bench)
gui.show()