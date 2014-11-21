from __future__ import division
import Tkinter as Tk

class GUI(object):
  master = None
  canvas = None

  def __init__(self, width=500, height=500, title="Optivis", svgDir="svg"):
    self.width = width
    self.height = height
    self.title = title
    self.svgDir = svgDir

    # create canvas
    self.master = Tk.Tk()
    self.canvas = Tk.Canvas(self.master, width=self.width, height=self.height)

    self.initialise()

  def initialise(self):
    # set title
    # TODO: make this user-settable
    self.master.title(self.title)

    # add menu
    menuBar = Tk.Menu(self.master)
    menuBar.add_command(label="Exit", command=self.quit)

    self.master.config(menu=menuBar)

  def quit(self):
    self.master.destroy()

  def draw(self, canvasComponents):
    for canvasComponent in canvasComponents:
      canvasComponent.draw(self.canvas, self.svgDir)

    # force redraw
    self.canvas.pack()

    # run GUI loop
    self.master.mainloop()
  
  #def addMarker(self, (xPos, yPos), radius=2, *args, **kwargs):
  #  self.canvas.create_oval(xPos - radius, yPos - radius, xPos + radius, yPos + radius, *args, **kwargs)

  @property
  def width(self):
    return self.__width

  @width.setter
  def width(self, width):
    self.__width = width

  @property
  def height(self):
    return self.__height

  @height.setter
  def height(self, height):
    self.__height = height

  @property
  def title(self):
    return self.__title

  @title.setter
  def title(self, title):
    self.__title = title

  @property
  def svgDir(self):
    return self.__svgDir

  @svgDir.setter
  def svgDir(self, svgDir):
    self.__svgDir = svgDir