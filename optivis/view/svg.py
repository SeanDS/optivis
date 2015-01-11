import os
import os.path
import sys

import optivis.view
import optivis.layout
import optivis.bench.components
import optivis.bench.links

class Svg(optivis.view.AbstractDrawable):
  def __init__(self, *args, **kwargs):
    super(Svg, self).__init__(*args, **kwargs)
  
  def export(self):
    return

class SvgComponent(optivis.bench.components.AbstractDrawableComponent):  
  def __init__(self, component, *args, **kwargs):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type AbstractComponent')
    
    self.component = component
    
    super(SvgComponent, self).__init__(*args, **kwargs)
  
  def draw(self, et):
    return

class SvgLink(optivis.bench.links.AbstractDrawableLink):
  def __init__(self, link, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.link = link
    
    super(SvgLink, self).__init__(*args, **kwargs)

  def draw(self, et):
    return