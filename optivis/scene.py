# -*- coding: utf-8 -*-

"""Scene classes"""

from __future__ import unicode_literals, division

import datetime

from optivis.geometry import Coordinates
from optivis.bench.links import Link

class Scene(object):
    def __init__(self, title=None, reference=None):
        if title is None:
            # use default title
            title = Scene.get_default_title()

        # set title and reference component
        self.title = title
        self.reference = reference

        # create empty component and link lists
        self.components = []
        self.links = []

    def __unicode__(self):
        """String representation of the scene"""

        return "Scene \"{0}\" with {1} component(s), {2} link(s)".format( \
        self.title, len(self.components), len(self.links))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of the scene"""

        return unicode(self)

    def get_description(self):
        """Description of the scene"""

        # component and link descriptions
        components = [unicode(component) for component in self.components]
        links = [unicode(link) for link in self.links]

        return "{0}\n\tComponents:\n\t\t{1}\n\tLinks:\n\t\t{2}".format(self, \
        "\n\t\t".join(components), "\n\t\t".join(links))

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = unicode(title)

    def add_component(self, component):
        """Adds the specified component to the scene

        :param component: component to add
        """

        if component in self.components:
            raise Exception("Specified component is already in the scene")

        # check if component has a name
        if len(component.name) == 0:
            # get a unique name
            component.name = self.get_unique_name(component)
        elif component.name in self.get_component_names():
            raise Exception("Component name clashes with existing component")

        self.components.append(component)

    def add_link(self, *args, **kwargs):
        link = Link(*args, **kwargs)

        self.links.append(link)

    def get_unique_name(self, item):
        """Gets a unique name for the specified item"""

        # get name of class (e.g. Mirror)
        class_name = unicode(item.__class__.__name__)

        # default counter
        counter = 1

        # names of components already in scene
        component_names = self.get_component_names()

        # loop until we find a unique name
        while True:
            proposal = "{0} {1}".format(class_name, counter)

            if proposal not in component_names:
                return proposal

            # increment counter
            counter += 1

    def get_component_names(self):
        """Gets a list of names of components in this scene"""

        return [component.name for component in self.components]

    def get_bounding_box(self):
        # list of component coordinates
        x = []
        y = []

        # loop over components to find actual bounds
        for component in self.components:
            # get the coordinates for lower and upper bounds of the component
            (this_lower_bound, this_upper_bound) = component.get_bounding_box()

            # add coordinates to lists
            x.append(this_lower_bound.x)
            x.append(this_upper_bound.x)
            y.append(this_lower_bound.y)
            y.append(this_upper_bound.y)

        # create global bounds
        lower_bound = Coordinates(min(x), min(y))
        upper_bound = Coordinates(max(x), max(y))

        return (lower_bound, upper_bound)

    def get_size(self):
        (lower_bound, upper_bound) = self.get_bounding_box()

        # subtract coordinates to obtain size
        return upper_bound - lower_bound

    @staticmethod
    def get_default_title():
        # use the current local time
        return datetime.datetime.now().strftime("%Y-%M-%d %H:%M")
