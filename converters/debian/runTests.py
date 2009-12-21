import unittest

from test.unit import modelsTest, parserTest

def launchTests():
  suite = unittest.TestLoader().loadTestsFromModule(modelsTest)
  suite.addTests(unittest.TestLoader().loadTestsFromModule(parserTest))
  unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    launchTests()
