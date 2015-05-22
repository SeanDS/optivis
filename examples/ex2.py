"""
Demonstration of components with non-zero angles of incidence.
"""

import sys

sys.path.append('..')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.bench.labels as labels
import optivis.view.canvas as canvas
import optivis.geometry as geometry

scene = scene.Scene(title="Example 2")

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

# dashed pattern to indicate sidebands
pat = [5, 5]

scene.link(
  outputNode=laser.getOutputNode('out'),
  inputNode=wp1.getInputNode('bk'),
  length=40,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ],
  labels=[
    labels.Label(text="laser->wp1", position=geometry.Coordinates(0, 0), azimuth=90),
    labels.Label(text="p=1W", position=geometry.Coordinates(-0.5, 0), azimuth=90),
    labels.Label(text="g=23+3i", position=geometry.Coordinates(0.5, 0), azimuth=90)
  ]
)

scene.link(
  outputNode=wp1.getOutputNode('fr'),
  inputNode=wp2.getInputNode('bk'),
  length=10,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ]
)

scene.link(
  outputNode=wp2.getOutputNode('fr'),
  inputNode=isol.getInputNode('bk'),
  length=30,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ]
)

scene.link(
  outputNode=isol.getOutputNode('fr'),
  inputNode=lens1.getInputNode('bk'),
  length=30,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ]
)

scene.link(
  outputNode=lens1.getOutputNode('fr'),
  inputNode=lens2.getInputNode('bk'),
  length=10,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ]
)

scene.link(
  outputNode=lens2.getOutputNode('fr'),
  inputNode=eom.getInputNode('bk'),
  length=30,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0)
  ]
)

scene.link(
  outputNode=eom.getOutputNode('fr'),
  inputNode=mirror1.getInputNode('fr'),
  length=100,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=-3),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=3)
  ]
)

scene.link(
  outputNode=mirror1.getOutputNode('fr'),
  inputNode=mirror2.getInputNode('fr'),
  length=100,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=-3),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=3)
  ],
  labels=[
    labels.Label(text="mirror1->mirror2", position=geometry.Coordinates(0, 0), azimuth=90, offset=geometry.Coordinates(0, 0))
  ]
)

scene.link(
  outputNode=mirror2.getOutputNode('fr'),
  inputNode=mirror3.getInputNode('fr'),
  length=150,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=-3),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=3)
  ],
  labels=[
    labels.Label(text="mirror2->mirror3", position=geometry.Coordinates(0, 0), azimuth=90, offset=geometry.Coordinates(0, 0))
  ]
)

scene.link(
  outputNode=mirror3.getOutputNode('fr'),
  inputNode=pd.getInputNode('in'),
  length=65,
  specs=[
    links.LinkSpec(width=3, color="red", pattern=None, offset=0),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=-3),
    links.LinkSpec(width=2, color="green", pattern=pat, offset=3)
  ],
)

gui = canvas.Full(scene=scene)
gui.show()
