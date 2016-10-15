from __future__ import unicode_literals, division

import datetime

from optivis.geometry import Coordinates

class Scene(object):
    def __init__(self, title=None, reference=None):
        if title is None:
            # use default title
            title = Scene.get_default_title()

        # set title and reference component
        self.title = str(title)
        self.reference = reference
        
        # create empty component and link lists
        self.components = []
        self.links = []

    def link(self, *args, **kwargs):
        link = bench.links.Link(*args, **kwargs)

        self._add_link(link)

    def _add_link(self, link):
        self.links.append(link)

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
        return datetime.datetime.now().strftime('%Y-%M-%d %H:%M')