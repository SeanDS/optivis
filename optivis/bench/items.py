# -*- coding: utf-8 -*-

"""Item classes"""

from __future__ import unicode_literals, division

import abc

from optivis.bench.labels import Label

class BenchItem(object):
    """Abstract class for bench items (e.g. components, links)"""

    # set abstract class
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        # default labels
        self.labels = []

    @abc.abstractmethod
    def get_label_origin(self):
        """Coordinates labels should be placed with respect to"""
        pass

    @abc.abstractmethod
    def get_label_azimuth(self):
        """Azimuth labels should be placed with respect to"""
        pass

    @abc.abstractmethod
    def get_bounding_box(self):
        """Coordinates of item's edges closest to and furthest away from \
        origin

        :return: (lower, upper) bounds
        """
        pass

    def get_size(self):
        """Size of bench item

        :return: coordinates representing size with respect to origin
        """

        # get bounding box
        (lower_bound, upper_bound) = self.get_bounding_box()

        # return the difference
        return upper_bound - lower_bound

    def add_label(self, *args, **kwargs):
        """Adds a label to the item

        Accepts arguments for Label
        """

        # add new node, setting the node's component to this
        self.labels.append(Label(*args, item=self, **kwargs))
