from __future__ import unicode_literals, division

from optivis.geometry import Vector

class Label(object):
    def __init__(self, text, item=None, azimuth=0, offset=None):
        """Instantiates a label

        :param text: text to show
        :param item: item this label is attached to
        :param azimuth: the angle of the label with respect to the attached \
        item's absolute azimuth
        :param offset: offset of this label with respect to the item
        """

        if offset is None:
            offset = Vector(0, 0)

        self.text = text
        self.item = item
        self.azimuth = azimuth
        self.offset = offset

    def __unicode__(self):
        """String representation of this label"""

        return "\"{0}\"".format(self.text)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        """Representation of this label"""

        return unicode(self)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = unicode(text)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        self._azimuth = float(azimuth)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        self._offset = Vector(offset)
