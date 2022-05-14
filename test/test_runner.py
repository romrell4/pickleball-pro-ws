# These lines allows us to import the src module
import os
import sys

sys.path.append(os.path.abspath(__file__ + "/../../"))
sys.path.append(os.path.abspath(__file__ + "/../../src/"))

import unittest

import domain_test
import da_test
import bl_test
import handler_test
import firebase_client_test

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromTestCase(domain_test.GameScoreTest))
suite.addTests(loader.loadTestsFromTestCase(domain_test.StatTest))
suite.addTests(loader.loadTestsFromTestCase(domain_test.MatchTest))
suite.addTests(loader.loadTestsFromTestCase(domain_test.PlayerTest))
suite.addTests(loader.loadTestsFromTestCase(da_test.Test))
suite.addTests(loader.loadTestsFromTestCase(bl_test.Test))
suite.addTests(loader.loadTestsFromTestCase(handler_test.Test))
suite.addTests(loader.loadTestsFromTestCase(firebase_client_test.Test))

result = unittest.TextTestRunner(verbosity=3).run(suite)
exit(0 if result.wasSuccessful() else 1)
