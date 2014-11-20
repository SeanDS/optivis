from vis import *

table = Optivis()

l1 = Laser(name="L1")
m1 = CavityMirror(name="M1", aoi=30)
m2 = CavityMirror(name="M2", aoi=15)
m3 = CavityMirror(name="M3", aoi=0)

table.addComponent(l1)
table.addComponent(m1)
table.addComponent(m2)
table.addComponent(m3)

table.addLink(Link(l1.outputNodes[0], m1.inputNodes[0], 100))
table.addLink(Link(m1.outputNodes[0], m2.inputNodes[0], 100))
table.addLink(Link(m2.outputNodes[0], m3.inputNodes[0], 150))

table.vis()
