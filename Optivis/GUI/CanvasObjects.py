from __future__ import division

import os
import Tkinter as Tk
import Image
import ImageTk
import rsvg
import cairo

import Optivis
import Optivis.GUI
import Optivis.BenchObjects

class CanvasObject(object):
  def __init__(self):
    return None

  def draw(self, canvas):
    if not isinstance(canvas, Tk.Canvas):
      raise Exception('Specified canvas is not of type Tk.Canvas')
    
    self._draw(canvas)

class CanvasComponent(CanvasObject):
  def __init__(self, component, size, azimuth=0, position=None):
    if not isinstance(component, Optivis.BenchObjects.Component):
      raise Exception('Specified component is not of type Optivis.BenchObjects.Component')
    
    if position is None:
      position = Optivis.Coordinates(0, 0)
    
    self.image = None

    self.component = component
    self.size = size
    self.azimuth = azimuth
    self.position = position

    super(CanvasComponent, self).__init__()
  
  def _draw(self, canvas):    
    # store image in object (NOTE: this is necessary for Tkinter to correctly draw the image)
    self.image = self.getImage()
    
    canvas.create_image(int(self.position.x), int(self.position.y), image=self.image, anchor=Tk.CENTER)

  @property
  def size(self):
    return self.__size
  
  @size.setter
  def size(self, size):
    self.__size = size

  @property
  def position(self):
    return self.__position
  
  @position.setter
  def position(self, position):
    if not isinstance(position, Optivis.Coordinates):
      raise Exception('Specified position is not of type Optivis.Coordinates')
    
    self.__position = position
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
  
  def getImage(self):
    """
    Returns a ImageTk.PhotoImage object represeting the svg file
    """
    
    filepath = os.path.join(self.component.svgDir, self.component.filename)
    
    svg = rsvg.Handle(file=filepath)
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.size.x), int(self.size.y))
    context = cairo.Context(surface)
    
    # scale svg
    context.scale(self.size.x / self.component.size.x, self.size.y / self.component.size.y)
    
    # render as bitmap
    svg.render_cairo(context)
    
    tkImage = ImageTk.PhotoImage('RGBA')
    image = Image.frombuffer('RGBA', (int(self.size.x), int(self.size.y)), surface.get_data(), 'raw', 'BGRA', 0, 1)
    image = image.rotate(-self.azimuth, expand=True) # -azimuth used because we have a left handed coordinate system
    tkImage.paste(image)
    
    return(tkImage)
    
  def __str__(self):
    # return component's __str__
    return self.component.__str__()

class CanvasLink(CanvasObject):
  def __init__(self, start, end, width, fill="red", startMarker=True, endMarker=True, startMarkerRadius=3, endMarkerRadius=2, startMarkerOutline="red", endMarkerOutline="blue"):
    if width < 0:
      raise Exception('Specified width is invalid')
    
    self.start = start
    self.end = end
    self.width = width
    self.fill = fill
    self.startMarker = startMarker
    self.endMarker = endMarker
    self.startMarkerRadius = startMarkerRadius
    self.endMarkerRadius = endMarkerRadius
    self.startMarkerOutline = startMarkerOutline
    self.endMarkerOutline = endMarkerOutline
    
    super(CanvasLink, self).__init__()

  def _draw(self, canvas):
    canvas.create_line(int(self.start.x), int(self.start.y), int(self.end.x), int(self.end.y), width=self.width, fill=self.fill)
    
    # add markers if necessary
    if self.startMarker: canvas.create_oval(int(self.start.x - self.startMarkerRadius), int(self.start.y - self.startMarkerRadius), int(self.start.x + self.startMarkerRadius), int(self.start.y + self.startMarkerRadius), outline=self.startMarkerOutline, tags="startmarker")
    if self.endMarker: canvas.create_oval(int(self.end.x - self.endMarkerRadius), int(self.end.y - self.endMarkerRadius), int(self.end.x + self.endMarkerRadius), int(self.end.y + self.endMarkerRadius), outline=self.endMarkerOutline, tags="endmarker")

  @property
  def start(self):
    return self.__start

  @start.setter
  def start(self, start):
    if not isinstance(start, Optivis.Coordinates):
      raise Exception('Specified start is not of type Optivis.Coordinates')
    
    self.__start = start

  @property
  def end(self):
    return self.__end

  @end.setter
  def end(self, end):
    if not isinstance(end, Optivis.Coordinates):
      raise Exception('Specified end is not of type Optivis.Coordinates')
    
    self.__end = end
    
  @property
  def width(self):
    return self.__width

  @width.setter
  def width(self, width):
    self.__width = width

  @property
  def fill(self):
    return self.__fill

  @fill.setter
  def fill(self, fill):
    self.__fill = fill
    
  @property
  def startMarker(self):
    return self.__startMarker
  
  @startMarker.setter
  def startMarker(self, startMarker):
    self.__startMarker = startMarker
    
  @property
  def endMarker(self):
    return self.__endMarker
  
  @endMarker.setter
  def endMarker(self, endMarker):
    self.__endMarker = endMarker
    
  @property
  def startMarkerRadius(self):
    return self.__startMarkerRadius
  
  @startMarkerRadius.setter
  def startMarkerRadius(self, startMarkerRadius):
    self.__startMarkerRadius = startMarkerRadius
    
  @property
  def endMarkerRadius(self):
    return self.__endMarkerRadius
  
  @endMarkerRadius.setter
  def endMarkerRadius(self, endMarkerRadius):
    self.__endMarkerRadius = endMarkerRadius
    
  @property
  def startMarkerOutline(self):
    return self.__startMarkerOutline
  
  @startMarkerOutline.setter
  def startMarkerOutline(self, startMarkerOutline):
    self.__startMarkerOutline = startMarkerOutline
    
  @property
  def endMarkerOutline(self):
    return self.__endMarkerOutline
  
  @endMarkerOutline.setter
  def endMarkerOutline(self, endMarkerOutline):
    self.__endMarkerOutline = endMarkerOutline