# https://stackoverflow.com/questions/3295386/python-unittest-and-discovery
import os
import unittest

    
def runTest():
    # If live don't run
    if not os.environ.get('AWS_SAM_LOCAL'):
        return True
    loader = unittest.TestLoader()
    # Finds all test in test folder
    tests = loader.discover('test')
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)
    return True