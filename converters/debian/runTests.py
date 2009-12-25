import unittest

from test.unit import modelsTest, parserTest, exportTest

def launchTests():
  suite = unittest.TestLoader().loadTestsFromModule(modelsTest)
  suite.addTests(unittest.TestLoader().loadTestsFromModule(parserTest))
  suite.addTests(unittest.TestLoader().loadTestsFromModule(exportTest))
  unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    launchTests()
