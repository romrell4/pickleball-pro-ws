# These lines allows us to import the src module
import os
import sys

sys.path.append(os.path.abspath(__file__ + "/../../"))
sys.path.append(os.path.abspath(__file__ + "/../../src/"))

import unittest

import da_test
import bl_test

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromTestCase(da_test.Test))
suite.addTests(loader.loadTestsFromTestCase(bl_test.Test))

result = unittest.TextTestRunner(verbosity=3).run(suite)
exit(0 if result.wasSuccessful() else 1)
