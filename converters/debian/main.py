import sys

from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parser import Parser
from export import Triplifier, Serializer

# FIMXE: Use a class instead
def run(packagesFile):

  # FIXME: Refactor to init
  graph = ConjunctiveGraph()

  inputFile = openInputFile(packagesFile)
  outputFile = openOutputFile("Packages.rdf") # FIXME

  parser = Parser()
  triplifier = Triplifier(graph, "http://debian.org") # FIXME: as user input
  serializer = Serializer()

  rawPackages = deb822.Packages.iter_paragraphs(inputFile)

  for p in rawPackages:
    # Parse
    parsedPackage = parser.parseBinaryPackage(p)

    # Triplify
    triplifier.triplifyBinaryPackage(parsedPackage)

  # Serialize all packages
  serializer.serializeToFile(graph, outputFile)

  inputFile.close()
  outputFile.flush()
  outputFile.close()

def openInputFile(path):
  try:
    return open(path, "r")
  except:
    print 'Error opening input file for reading.'

def openOutputFile(path):
  try:
    return open(path, "w+")
  except:
    print 'Error opening output file for writting.'

if __name__ == "__main__":
  args = sys.argv[1:]
  run(args[0]) # FIXME: Usage and parameters parsing
