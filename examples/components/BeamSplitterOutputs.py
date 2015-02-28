from __future__ import unicode_literals, division

import sys

sys.path.append('../..')

import optivis.scene as scene
import optivis.bench.components as components
import optivis.bench.labels as labels
import optivis.geometry as geometry
import optivis.view.canvas as canvas

scene = scene.Scene()

# beam splitter
bs = components.BeamSplitter(name="BS", azimuth=180+45, aoi=45)

# mirrors
mPR = components.SteeringMirror(name="PR")
mSR = components.SteeringMirror(name="SR")
mIX = components.SteeringMirror(name="IX")
mIY = components.SteeringMirror(name="IY")

# link OUTPUTS of beam splitter to mirrors
scene.link(outputNode=bs.getOutputNode("frB"), inputNode=mPR.getInputNode("fr"), length=150, labels=[
    labels.Label(text="BS->frB --> fr<-PR", position=geometry.Coordinates(-0.3, 0))
  ])
scene.link(outputNode=bs.getOutputNode("bkB"), inputNode=mSR.getInputNode("fr"), length=150, labels=[
    labels.Label(text="BS->bkB --> fr<-SR", position=geometry.Coordinates(-0.3, 0))
  ])
scene.link(outputNode=bs.getOutputNode("bkA"), inputNode=mIX.getInputNode("fr"), length=300, labels=[
    labels.Label(text="BS->bkA --> fr<-IX", position=geometry.Coordinates(-0.3, 0))
  ])
scene.link(outputNode=bs.getOutputNode("frA"), inputNode=mIY.getInputNode("fr"), length=300, labels=[
    labels.Label(text="BS->frA --> fr<-IY", position=geometry.Coordinates(-0.3, 0))
  ])

scene.reference = bs

gui = canvas.Simple(scene=scene, size=geometry.Coordinates(700, 700))
gui.show()