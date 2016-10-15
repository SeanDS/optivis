"""
Demonstration of export functionality.
"""

import sys

sys.path.append('..')

import optivis.geometry as geometry
import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.svg as svg

scene = scene.Scene(title="Export Example")

laser = components.Laser(name="Laser")
wp1 = components.QuarterWavePlate(name="Quarter Wave Plate")
wp2 = components.HalfWavePlate(name="Half Wave Plate")
isol = components.FaradayIsolator(name="Faraday Isolator")
eom = components.ElectroopticModulator(name="EOM")
lens1 = components.ConvexLens(name="Lens 1")
lens2 = components.ConcaveLens(name="Lens 2")
mirror1 = components.CavityMirror(name="Mirror 1", aoi=30)
mirror2 = components.CavityMirror(name="Mirror 2", aoi=15)
mirror3 = components.CavityMirror(name="Mirror 3", aoi=-45)
pd = components.Photodiode(name="Photodiode")

scene.addLink(links.Link(laser.getOutputNode('out'), wp1.getInputNode('fr'), 40))
scene.addLink(links.Link(wp1.getOutputNode('bk'), wp2.getInputNode('fr'), 10))
scene.addLink(links.Link(wp2.getOutputNode('bk'), isol.getInputNode('fr'), 30))
scene.addLink(links.Link(isol.getOutputNode('bk'), lens1.getInputNode('fr'), 30))
scene.addLink(links.Link(lens1.getOutputNode('bk'), lens2.getInputNode('fr'), 10))
scene.addLink(links.Link(lens2.getOutputNode('bk'), eom.getInputNode('fr'), 30))
scene.addLink(links.Link(eom.getOutputNode('bk'), mirror1.getInputNode('fr'), 100))
scene.addLink(links.Link(mirror1.getOutputNode('fr'), mirror2.getInputNode('fr'), 100))
scene.addLink(links.Link(mirror2.getOutputNode('fr'), mirror3.getInputNode('fr'), 150))
scene.addLink(links.Link(mirror3.getOutputNode('fr'), pd.getInputNode('in'), 65))

view = svg.Svg(scene=scene)

kwargs = {}

# get a valid format
formats = svg.Svg._Svg__formats

while True:
    print 'Valid formats are: ' + ', '.join(formats)
    fileFormat = raw_input('Enter a format: ')

    if fileFormat in formats:
        break
    else:
        print 'Invalid format: {0}'.format(fileFormat)

# get a valid filename
while True:
    try:
        path = raw_input('Enter a filename: ')

        break
    except Exception, e:
        print('Invalid path: {0}'.format(e))

view.export(path, fileFormat=fileFormat)

print('Exported scene to {0}'.format(path))
