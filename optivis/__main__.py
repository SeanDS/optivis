from __future__ import unicode_literals, division

import sys

if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        import unittest

        loader = unittest.TestLoader()
        suite = loader.discover('.')

        runner = unittest.runner.TextTestRunner()
        runner.run(suite)
