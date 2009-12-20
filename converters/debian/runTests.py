import unittest

from test.unit import modelsTest

def launchTests():
  suite = unittest.TestLoader().loadTestsFromModule(modelsTest)
  unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    launchTests()
