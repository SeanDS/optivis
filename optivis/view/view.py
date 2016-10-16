# -*- coding: utf-8 -*-

"""View classes"""

from __future__ import unicode_literals, division

import abc
import inspect
from collections import OrderedDict

from optivis.geometry import Coordinates
import optivis.layout.layout as layout

class View(object):
    __metaclass__ = abc.ABCMeta

    # default view dimensions
    default_size_x = 500
    default_size_y = 500

    SHOW_COMPONENTS = 1 << 0
    SHOW_LINKS = 1 << 1
    SHOW_LABELS = 1 << 2
    SHOW_START_MARKERS = 1 << 3
    SHOW_END_MARKERS = 1 << 4

    # default show (all)
    SHOW_DEFAULT = (1 << 5) - 1

    # show all
    SHOW_MAX = (1 << 5) - 1

    label_flags = OrderedDict()

    def __init__(self, scene, size=None, zoom=1.0, layout_manager=None, \
    show_flags=None, start_markers=False, end_markers=False, \
    start_marker_radius=5, end_marker_radius=3, start_marker_color=None, \
    end_marker_color=None):
        if size is None:
            size = Coordinates(self.default_size_x, self.default_size_y)

        if layout_manager is None:
            layout_manager = layout.StandardLayout

        if show_flags is None:
            show_flags = View.SHOW_DEFAULT

        if start_marker_color is None:
            start_marker_color = "red"

        if end_marker_color is None:
            end_marker_color = "blue"

        self.scene = scene
        self.size = size
        self.zoom = zoom
        self.layout_manager = layout_manager
        self.show_flags = show_flags
        self.start_markers = start_markers
        self.end_markers = end_markers
        self.start_marker_radius = start_marker_radius
        self.end_marker_radius = end_marker_radius
        self.start_marker_color = start_marker_color
        self.end_marker_color = end_marker_color

    @staticmethod
    def get_layout_manager_classes(self):
        managers = []

        for name, obj in inspect.getmembers(layout):
            if inspect.isclass(obj) and not inspect.isabstract(obj):
                managers.append(obj)

        return managers

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = Coordinates(size)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        self._zoom = float(zoom)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = unicode(title)

    @property
    def show_flags(self):
        return self._show_flags

    @show_flags.setter
    def show_flags(self, show_flags):
        show_flags = int(show_flags)

        if show_flags < 0 or show_flags > View.SHOW_MAX:
            raise Exception("Specified show flags are not valid. Show flags \
value must be between 0 and {0}".format(View.SHOW_MAX))

        self._show_flags = show_flags

    @property
    def start_markers(self):
        return self.show_flags & View.SHOW_START_MARKERS

    @start_markers.setter
    def start_markers(self, start_markers):
        if bool(start_markers):
            self.show_flags |= 1 << 3
        else:
            self.show_flags &= ~(1 << 3)

    @property
    def end_markers(self):
        return self.show_flags & View.SHOW_END_MARKERS

    @end_markers.setter
    def end_markers(self, end_markers):
        if bool(end_markers):
            self.show_flags |= 1 << 4
        else:
            self.show_flags &= ~(1 << 4)

    @property
    def start_marker_radius(self):
        return self._start_marker_radius

    @start_marker_radius.setter
    def start_marker_radius(self, start_marker_radius):
        start_marker_radius = float(start_marker_radius)

        if start_marker_radius < 0:
            raise Exception("Start marker radius must be >= 0")

        self._start_marker_radius = start_marker_radius

    @property
    def end_marker_radius(self):
        return self._end_marker_radius

    @end_marker_radius.setter
    def end_marker_radius(self, end_marker_radius):
        end_marker_radius = float(end_marker_radius)

        if end_marker_radius < 0:
            raise Exception("End marker radius must be >= 0")

        self._end_marker_radius = end_marker_radius

    @property
    def start_marker_color(self):
        return self._start_marker_color

    @start_marker_color.setter
    def start_marker_color(self, start_marker_color):
        #FIXME: check for valid colors here
        self._start_marker_color = unicode(start_marker_color)

    @property
    def end_marker_color(self):
        return self._end_marker_color

    @end_marker_color.setter
    def end_marker_color(self, end_marker_color):
        #FIXME: check for valid colors here
        self._end_marker_color = unicode(end_marker_color)
