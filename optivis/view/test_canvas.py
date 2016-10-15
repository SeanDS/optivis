"""
Not yet implemented, but here are the tests previously written for markers (taken from link() when it used to have markers defined)

  def test_invalid_marker_radius(self):
    # negative number
    self.assertRaises(Exception, setattr, self.link, 'startMarkerRadius', -2)
    self.assertRaises(Exception, setattr, self.link, 'endMarkerRadius', -2)

    # negative numeric string
    self.assertRaises(Exception, setattr, self.link, 'startMarkerRadius', '-2')
    self.assertRaises(Exception, setattr, self.link, 'endMarkerRadius', '-2')

    # can't be interpreted as float
    self.assertRaises(ValueError, setattr, self.link, 'startMarkerRadius', str('invalid'))
    self.assertRaises(ValueError, setattr, self.link, 'endMarkerRadius', str('invalid'))

    # invalid
    self.assertRaises(TypeError, setattr, self.link, 'startMarkerRadius', None)
    self.assertRaises(TypeError, setattr, self.link, 'endMarkerRadius', None)

  def test_invalid_color(self):
    # FIXME: verify valid colours are actually colours!

    # int
    self.assertRaises(Exception, setattr, self.link, 'color', int(10))
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', int(10))
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', int(10))

    # float
    self.assertRaises(Exception, setattr, self.link, 'color', float(10))
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', float(10))
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', float(10))

    # invalid
    self.assertRaises(Exception, setattr, self.link, 'color', None)
    self.assertRaises(Exception, setattr, self.link, 'startMarkerColor', None)
    self.assertRaises(Exception, setattr, self.link, 'endMarkerColor', None)
"""
