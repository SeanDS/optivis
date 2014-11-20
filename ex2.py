from vis import *

table = Optivis(azimuth=0)

l1 = Laser(name="L1")
bs1 = BeamSplitter(name="BS", aoi=0)
m1 = CavityMirror(name="M1", aoi=45)
m2 = CavityMirror(name="M2", aoi=45)
m3 = CavityMirror(name="M3", aoi=45)

table.addComponent(l1)
table.addComponent(bs1)
table.addComponent(m1)
table.addComponent(m2)
table.addComponent(m3)

table.addLink(Link(l1.outputNodes[0], bs1.inputNodes[0], 100))
table.addLink(Link(bs1.outputNodes[2], m1.inputNodes[0], 50))
table.addLink(Link(m1.outputNodes[0], m2.inputNodes[0], 50))
table.addLink(Link(m2.outputNodes[0], m3.inputNodes[0], 61.5))
table.addLink(Link(m3.outputNodes[0], bs1.inputNodes[2], 38.5))

table.draw()
