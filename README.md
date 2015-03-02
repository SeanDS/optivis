# Optivis #

![example](https://cloud.githubusercontent.com/assets/5225190/5718217/570c509a-9b03-11e4-8e4a-65114fb75d43.png)

Script to visualise optical environments. Uses the fantastic SVG optical components created by Alexander Franzen (http://www.gwoptics.org/ComponentLibrary/).  

## Requirements ##
Optivis requires Python 2.7+ or higher. For extra functionality, you must also install additional packages:

* `python-qt4` for the GUI
* `python-cairosvg` for PDF, PostScript and PNG export capability

On Ubuntu/Debian you should be able to install all of these with the following command:

`$ sudo apt-get install python python-qt4 python-cairosvg`

## How To ##
Optivis is pretty straightforward to use. You start off by importing a bunch of Optivis modules:

```python
import sys

sys.path.append('/path/to/optivis')

import optivis.scene as scene
import optivis.bench.links as links
import optivis.bench.components as components
import optivis.view.canvas as canvas
import optivis.view.svg as svg
```

Make sure you replace `/path/to/optivis` with the location of Optivis so that Python knows where to look.

Next, define your scene:

```python
scene = scene.Scene(title="My Scene")
```

The title is optional. Next, create a bunch of components:

```python
l1 = components.Laser(name="L1")
bs1 = components.BeamSplitter(name="BS", aoi=45)
m1 = components.CavityMirror(name="M1", aoi=45)
m2 = components.CavityMirror(name="M2", aoi=45)
m3 = components.CavityMirror(name="M3", aoi=45)
```

Note that the beam splitter and mirrors have an `aoi` parameter - this specifies the angle of incidence of the component relative to its primary input.

Next, link your components to each other:

```python
scene.link(l1.getOutputNode('out'), bs1.getInputNode('frA'), 100)
scene.link(bs1.getOutputNode('bkA'), m1.getInputNode('fr'), 50)
scene.link(m1.getOutputNode('fr'), m2.getInputNode('fr'), 50)
scene.link(m2.getOutputNode('fr'), m3.getInputNode('fr'), 58)
scene.link(m3.getOutputNode('fr'), bs1.getInputNode('frA'), 42.5)
```

Note that the components have outputs and inputs with different names. These are names specific to each component - look up the component syntax to learn which inputs/outputs correspond to which ports.

Next, set the reference component for your scene. This is the component which will be placed first, and all links will be drawn using this component as an absolute reference of position and azimuth. If you don't define a reference, then the component corresponding to the output node of the first link added to the scene will be used. In this example, we'll set the reference to be the laser:

```python
scene.reference = l1
```

Finally, draw the scene! You can either write the scene into a file...

```python
view = svg.Svg(scene)
view.export('scene.svg')
```

...or open the GUI:

```python
gui = canvas.Simple(scene)
gui.show()
```

This is what you'll see:

![scene](https://cloud.githubusercontent.com/assets/5225190/6220519/3e1e10b8-b62f-11e4-982a-c8941c1d1168.png)

Take a look at the `examples` directory for a set of scripts demonstrating the abilities of Optivis.

## Coordinate System ##
Optivis uses a left-handed coordinate system in line with almost all computer graphics applications. Positive angle rotations are **clockwise**. All geometrical transforms are performed with the coordinate class contained in `optivis.geometry`.

## Adding New Components ##

### Graphic Format ###
Optivis uses scalable vector graphics (SVGs) as a basis for its optical components. To add a new component, you must provide an SVG file describing the component's looks. Please use one of the existing files as a basis for your design - Optivis expects SVG files to have a specific format:
 * The root element should be an `<svg>` item (this is standard for the SVG file format anyway).
 * Elements and element attributes should not use namespaces (such as `i:midPoint="value"`), because namespaces are not defined in the header. This is to keep the files clean of program-specific crud, and ensure that generated SVG files are [valid](http://validator.w3.org/).
 * The use of ID attributes should be restricted to definitions of IDs in elements (such as `<g id="this-id">`) and URLs (such as `fill="url(#gradient-id)"`). This is because Optivis replaces IDs in SVG files with unique strings, to allow multiple versions of the same component to be grouped together in a generated scene. The use of IDs in any other form may result in display issues.

The SVG file should be given an appropriate filename and placed in the `assets` directory within the `optivis` package. Then, in `optivis.bench.components` you should subclass the `AbstractComponent` class and write a constructor - see the existing components for details of how to do this. You will have to define nodes for your component's inputs and outputs - see the next section for details.

### Input/Output Node Conventions ###
Take a look at existing components for an idea of how input/output nodes work. The beam splitter is a good example, because it has four inputs and four outputs.

There are a number of conventions that Optivis follows in order to avoid chaos when it comes to figuring out how to link components together. In general, Optivis follows the same form as [Optickle2](https://github.com/Optickle/Optickle/tree/Optickle2).

* The position of the component's input and output nodes are defined with respect to the component. The position is defined using an `optivis.geometry.Coordinates` object which represents the *normalised* position of the node with respect to the centre of the component. That means that if you wish to place a node on the middle-right edge of a component, you would give it coordinates `(0.5, 0)`.

* The azimuth of the node is defined with respect to the component's normal.
  * For output nodes, the azimuth should represent the direction light **leaves** the component
  * For input nodes, the azimuth should represent the direction light **enters** the component

### Angles of Incidence Convention ###
For the purposes of defining angles of incidence, it is necessary to designate a particular input and output as the primary input or output. This is done implicitly by defining the azimuth of each input or output node with respect to an `aoi` parameter (representing the user-defined angle of incidence of that component). Nodes in Optivis follow these conventions:

* For output nodes, the angle between the normal and the primary output is **positive** (for clockwise rotations):
![bs-outputs](https://cloud.githubusercontent.com/assets/5225190/6199972/aab69baa-b459-11e4-9a5f-f9ed437e538c.png)
* For input nodes, the angle between the normal and the primary input is **negative** (for clockwise rotations):
![bs-inputs](https://cloud.githubusercontent.com/assets/5225190/6199973/b2b8a474-b459-11e4-9362-5df434d5425e.png)
* A node's azimuth is determined by three numbers: the component's angle of incidence (`aoi` parameter), the node's `aoiMultiplier` factor and its `aoiOffset` factor. For example, a beam splitter's reflected back output has an `aoiMultiplier` of `-1` and an `aoiOffset` of `180`, so for an angle of incidence of `45`, the node's azimuth would be `-1 * 45 + 180 = 135`.

The primary output is typically designated the name `fr` or `frA`. On a beam splitter, for example, the azimuth of the output node `frA` is just the component's `aoi` parameter. Other outputs have modifiers such as `aoiMultiplier = -1` or `aoiOffset = 180`.

This is a design choice, not a rule, so you are free to define new components using whatever convention you like. However, for the sake of clarity, consider following this convention.

## Planned Features ##
There are a number of features planned for future releases. See the [issue tracker](https://github.com/SeanDS/optivis/labels/enhancement) for more information.

## Tests ##
Optivis contains some basic tests to validate and verify inputs to its various objects. You can check that the tests pass or fail by running

`python optivis test`

from the root Optivis directory (the same directory as this readme).

Sean Leavey  
https://github.com/SeanDS/
