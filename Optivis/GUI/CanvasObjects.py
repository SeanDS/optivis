from __future__ import division
import Tkinter as Tk
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
    canvas.create_image(int(self.position.x), int(self.position.y), image=self.getImage(), anchor=Tk.CENTER)

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
  
  def getImage(self):
    self.image = self.component.toImage(size=self.size, azimuth=self.azimuth)
    
    return self.image
  
  @property
  def azimuth(self):
    return self.__azimuth
  
  @azimuth.setter
  def azimuth(self, azimuth):
    self.__azimuth = azimuth
    
  def getBoundingBox(self):
    """
    Returns the top left and bottom right coordinates of the box bounding this component
    """
    
    topLeft = self.position.translate(self.size.flip() / 2).rotate(self.azimuth)
    topRight = self.position.translate(Optivis.Coordinates(self.size.x, -self.size.y) / 2).rotate(self.azimuth)
    bottomLeft = self.position.translate(Optivis.Coordinates(-self.size.x, self.size.y) / 2).rotate(self.azimuth)
    bottomRight = self.position.translate(self.size.x / 2).rotate(self.azimuth)
    
    minPos = topLeft
    maxPos = topLeft
    
    # find maximum position
    if topRight.x > maxPos.x: maxPos.x = topRight.x
    if topRight.y > maxPos.y: maxPos.y = topRight.y
    if bottomLeft.x > maxPos.x: maxPos.x = bottomLeft.x
    if bottomLeft.y > maxPos.y: maxPos.y = bottomLeft.y
    if bottomRight.x > maxPos.x: maxPos.x = bottomRight.x
    if bottomRight.y > maxPos.y: maxPos.y = bottomRight.y
    
    # find minimum position
    if topRight.x < minPos.x: minPos.x = topRight.x
    if topRight.y < minPos.y: minPos.y = topRight.y
    if bottomLeft.x < minPos.x: minPos.x = bottomLeft.x
    if bottomLeft.y < minPos.y: minPos.y = bottomLeft.y
    if bottomRight.x < minPos.x: minPos.x = bottomRight.x
    if bottomRight.y < minPos.y: minPos.y = bottomRight.y
    
    return minPos, maxPos
    
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