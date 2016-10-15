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

# link mirrors to INPUTS of beam splitter
scene.link(outputNode=mPR.getOutputNode("fr"), inputNode=bs.getInputNode("frA"), length=150,   labels=[
    labels.Label(text="PR->fr --> frA<-BS", position=geometry.Coordinates(-0.3, 0))
  ])
scene.link(outputNode=mSR.getOutputNode("fr"), inputNode=bs.getInputNode("bkA"), length=150, labels=[
    labels.Label(text="SR->fr --> bkA<-BS", position=geometry.Coordinates(-0.3, 0))
  ])
scene.link(outputNode=mIX.getOutputNode("fr"), inputNode=bs.getInputNode("bkB"), length=300, labels=[
    labels.Label(text="IX->fr --> bkB<-BS", position=geometry.Coordinates(-0.2, 0))
  ])
scene.link(outputNode=mIY.getOutputNode("fr"), inputNode=bs.getInputNode("frB"), length=300, labels=[
    labels.Label(text="IY->fr --> frB<-BS", position=geometry.Coordinates(-0.2, 0))
  ])

scene.reference = bs

gui = canvas.Simple(scene=scene, size=geometry.Coordinates(700, 700))
gui.show()
