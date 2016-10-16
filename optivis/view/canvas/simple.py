# -*- coding: utf-8 -*-

"""Canvas classes"""

from __future__ import unicode_literals, division

from optivis.view.canvas.canvas import Canvas

class SimpleCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super(SimpleCanvas, self).__init__(*args, **kwargs)

    def initialise(self):
        super(SimpleCanvas, self).initialise()

        # set central widget to be the view
        self.qMainWindow.setCentralWidget(self.qView)

        # resize main window to fit content
        self.qMainWindow.setFixedSize(self.size.x, self.size.y)

        # set view box, etc.
        self.calibrateView()
