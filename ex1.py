"""
Demonstration of scaling.
"""

import Optivis
import Optivis.Gui

bench = Optivis.Bench(title="Example 1")

l1 = Optivis.BenchObjects.Laser(name="L1")
m1 = Optivis.BenchObjects.CavityMirror(name="M1")

bench.addComponent(l1)
bench.addComponent(m1)

bench.addLink(Optivis.BenchObjects.Link(l1.getOutputNode('out'), m1.getInputNode('fr'), 50))

gui = Optivis.Gui.Qt(bench=bench, size=Optivis.Coordinates(500, 500), zoom=1, azimuth=0, startMarker=False, endMarker=False)
gui.show()