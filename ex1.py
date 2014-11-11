from vis import *
import Tkinter as Tk

master = Tk.Tk()

canvas = Tk.Canvas(master, width=500, height=500)
#canvas.create_line(0, 100, 400, 500)
#canvas.create_line(0, 80, 420, 500)
#canvas.create_line(0, 60, 440, 500)
#canvas.create_line(0, 40, 460, 500)
#canvas.create_line(0, 20, 480, 500)
#canvas.create_line(0, 0, 500, 500)
#canvas.create_line(20, 0, 500, 480)
#canvas.create_line(40, 0, 500, 460)
#canvas.create_line(60, 0, 500, 440)
#canvas.create_line(80, 0, 500, 420)
#canvas.create_line(100, 0, 500, 400)

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

#table.addComponent(m1)
#table.addComponent(m2)
#table.addComponent(m3)

#table.addLink(Link(m1.outputNodes[0], m2.inputNodes[0], 100))
#table.addLink(Link(m2.outputNodes[0], m3.inputNodes[0], 100))
#table.addLink(Link(m3.outputNodes[0], m1.inputNodes[0], 100))

table.vis(canvas)