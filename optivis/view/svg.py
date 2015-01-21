from __future__ import unicode_literals, division

import os
import os.path
import sys
from xml.etree import ElementTree as et

import optivis.geometry
import optivis.bench.components
import optivis.bench.links
import optivis.layout

class Svg(optivis.view.AbstractDrawable):
  def __init__(self, *args, **kwargs):
    super(Svg, self).__init__(*args, **kwargs)
  
  def getDrawableComponents(self):
    drawableComponents = []
    
    for component in self.scene.components:
      # Add component to list of SVG components.
      drawableComponents.append(SvgComponent(component))
    
    return drawableComponents
  
  def getDrawableLinks(self):
    drawableLinks = []
    
    for link in self.scene.links:
      # Add link to list of SVG links.
      drawableLinks.append(SvgLink(link))
    
    return drawableLinks
  
  def layout(self):
    layout = optivis.layout.SimpleLayout(self.scene)
    layout.arrange()
    
    return
  
  def export(self, path):
    # check path is valid
    try:
      open(path, 'w').close()
      os.unlink(path)
    except OSError:
      raise Exception('The specified filename is invalid')
    except IOError:
      raise Exception('You do not have permission to save the file to the specified location.')
    
    # lay things out before doing anything else
    self.layout()
    
    # get scene size
    (lowerBounds, upperBounds) = self.scene.getBoundingBox()
    size = upperBounds.translate(lowerBounds.flip())
    offset = lowerBounds.flip()
    
    document = et.Element('svg', width='{0}'.format(size.x), height='{0}'.format(size.y), version='1.1', xmlns='http://www.w3.org/2000/svg')
    
    for svgLink in self.getDrawableLinks():
      svgLink.draw(document, offset)
    
    for svgComponent in self.getDrawableComponents():
      # draw component with offset applied to centre everything in the SVG canvas
      svgComponent.draw(document, offset)
    
    f = open(path, 'w')
    f.write('<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n')
    f.write('<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n')
    f.write('\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n')
    f.write(et.tostring(document))
    f.close()
    
    return

class SvgComponent(optivis.bench.components.AbstractDrawableComponent):  
  def __init__(self, component, *args, **kwargs):
    if not isinstance(component, optivis.bench.components.AbstractComponent):
      raise Exception('Specified component is not of type AbstractComponent')
    
    self.component = component
    
    super(SvgComponent, self).__init__(*args, **kwargs)
  
  def draw(self, document, offset=None):
    if not isinstance(document, et.Element):
      raise Exception('Specified document is not of type ElementTree')
    
    if offset is None:
      offset = optivis.geometry.Coordinates(0, 0)
    
    # create full path to SVG file
    path = os.path.join(self.component.svgDir, self.component.filename)
    
    # parse SVG file into an element tree
    svgFile = et.parse(path)
    
    # get root element from tree
    svgElement = svgFile.getroot()
    
    # make sure we've got an SVG element as root
    if svgElement.tag != 'svg':
      raise Exception('Root element of SVG file %s is not an \'svg\' tag'.format(path))
    
    # put contents of SVG element in new group to keep it unaltered
    graphicGroup = et.Element('g')
    
    for child in svgElement:
      graphicGroup.append(child)
    
    # map of unique IDs
    uniqueIds = {}

    # loop over all subelements of the root, replacing ID with a unique string (this allows the same SVG images to be used multiple times in a document)
    for element in list(graphicGroup.iter()):
      if 'id' in element.attrib:
	# element has an ID associated with it - check if it's been seen already	
	currentId = element.attrib['id']
	
	if currentId in uniqueIds:
	  raise Exception('Found duplicate ID in SVG file %s'.format(path))
	
	# current ID has not yet been seen - generate a unique alternative
	uniqueId = 'e{0}'.format(id(element))
	
	# map unique ID to current ID
	uniqueIds[currentId] = uniqueId

    # loop over all subelements again, replacing IDs with unique equivalents
    for element in list(graphicGroup.iter()):
      if 'id' in element.attrib:
	element.attrib['id'] = uniqueIds[element.attrib['id']]
      
      # check any attributes for references to IDs
      for (attrKey, attrVal) in element.attrib.iteritems():
	# loop over all entries of map
	for thisId in uniqueIds:
	  # form string with hash at beginning to search for references to IDs
	  needle = 'url(#{0})'.format(thisId)
	  if needle in attrVal:
	    # found reference to ID - create replacement
	    newNeedle = 'url(#{0})'.format(uniqueIds[thisId])
	  
	    # replace with unique ID
	    element.attrib[attrKey] = attrVal.replace(needle, newNeedle)

    # now graphicGroup contains content with unique IDs, ready to be combined with other SVG markup.
    # create a new group to control this SVG image's global position (accounting for centre of rotation)
    group1 = et.Element('g', transform='translate({0} {1})'.format(self.component.position.x - self.component.size.x / 2 + offset.x, self.component.position.y - self.component.size.y / 2 + offset.y))

    # check if we also need to rotate the component
    if self.component.azimuth != 0:
      # rotation group
      group2 = et.Element('g', transform='rotate({0} {1} {2})'.format(self.component.azimuth, self.component.size.x / 2, self.component.size.y / 2))
      group2.append(graphicGroup)
      
      group1.append(group2)
    else:
      group1.append(graphicGroup)
    
    # add this graphic to the document
    document.append(group1)
    
    return

class SvgLink(optivis.bench.links.AbstractDrawableLink):
  def __init__(self, link, *args, **kwargs):
    if not isinstance(link, optivis.bench.links.AbstractLink):
      raise Exception('Specified link is not of type AbstractLink')
    
    self.link = link
    
    super(SvgLink, self).__init__(*args, **kwargs)

  def draw(self, document, offset=None):
    if not isinstance(document, et.Element):
      raise Exception('Specified document is not of type ElementTree')
    
    if offset is None:
      offset = optivis.geometry.Coordinates(0, 0)
    
    line = et.SubElement(document, 'line', x1=str(self.link.start.x + offset.x), x2=str(self.link.end.x + offset.x), y1=str(self.link.start.y + offset.y), y2=str(self.link.end.y + offset.y), style='stroke: {0}; stroke-width: {1}'.format(self.link.color, self.link.width))