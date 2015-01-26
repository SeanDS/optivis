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
Optivis is pretty straightforward to use. You start off with importing a bunch of Optivis modules:

```python
import sys

sys.path.append('path/to/optivis')

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

The title is optional. Next, you can add a bunch of components to your scene:

```python
l1 = components.Laser(name="L1")
bs1 = components.BeamSplitter(name="BS", aoi=45)
m1 = components.CavityMirror(name="M1", aoi=45)
m2 = components.CavityMirror(name="M2", aoi=45)
m3 = components.CavityMirror(name="M3", aoi=45)

scene.addComponent(l1)
scene.addComponent(bs1)
scene.addComponent(m1)
scene.addComponent(m2)
scene.addComponent(m3)
```

Note that the beam splitter and mirrors have an `aoi` parameter - this specifies the angle of incidence of the component relative to its primary input.

Next, link your components to each other:

```python
scene.addLink(l1.getOutputNode('out'), bs1.getInputNode('frA'), 100)
scene.addLink(bs1.getOutputNode('bkA'), m1.getInputNode('fr'), 50)
scene.addLink(m1.getOutputNode('fr'), m2.getInputNode('fr'), 50)
scene.addLink(m2.getOutputNode('fr'), m3.getInputNode('fr'), 58)
scene.addLink(m3.getOutputNode('fr'), bs1.getInputNode('frA'), 42.5)
```

Note that the components have outputs and inputs with different names. These are names specific to each component - look up the component syntax to learn which inputs/outputs correspond to which ports.

Finally, draw the scene! You can either write the scene into a file...

```python
view = svg.Svg(scene)
view.export('scene.svg', fileFormat='svg')
```

...or open the GUI:

```python
gui = canvas.Simple(scene)
gui.show()
```

Take a look at the examples directory for a set of scripts demonstrating the abilities of Optivis.

## Coordinate System ##
Optivis uses a left-handed coordinate system in line with almost all computer graphics applications. Positive angle rotations are clockwise. All geometrical transforms are performed with the coordinate class contained in `optivis.geometry`.

## Adding New Components ##
Optivis uses scalable vector graphics (SVGs) as a basis for its optical components. To add a new component, you must provide an SVG file describing the component's looks. Please use one of the existing files as a basis for your design - Optivis expects SVG files to have a specific format:
 * The root element should be an `<svg>` item (this is standard for the SVG file format anyway).
 * Elements and element attributes should not use namespaces (such as `i:midPoint="value"`), because namespaces are not defined in the header. This is to keep the files clean of program-specific crud, and ensure that generated SVG files are [valid](http://validator.w3.org/).
 * The use of ID attributes should be restricted to definitions of IDs in elements (such as `<g id="this-id">`) and URLs (such as `fill="url(#gradient-id)"`). This is because Optivis replaces IDs in SVG files with unique strings, to allow multiple versions of the same component to be grouped together in a generated scene. The use of IDs in any other form may result in display issues.

The SVG file should be given an appropriate filename and placed in the `assets` directory within the `optivis` package. Then, in `optivis.bench.components` you should subclass the `AbstractComponent` class and write a constructor - see the existing components for details of how to do this. You will have to define nodes for your component's inputs and outputs. Nodes are places where links can originate or terminate, and must be positioned on the component's normalised coordinate system, where the origin is in the centre of the component. Again, see existing components for details.

## Planned Features ##
There are a number of features planned for future releases. See the [issue tracker](https://github.com/SeanDS/optivis/labels/enhancement) for more information.

## Tests ##
Optivis contains some basic tests to validate and verify inputs to its various objects. You can check that the tests pass or fail by running

`python optivis test`

from the root Optivis directory (the same directory as this readme).

Sean Leavey  
https://github.com/SeanDS/
