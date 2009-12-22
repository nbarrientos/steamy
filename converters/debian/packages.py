import sys
import logging

from optparse import OptionParser
from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parser import Parser
from export import Triplifier, Serializer

def init():
  configLogger()
  parseArgs()

def configLogger():
  logging.basicConfig(level=logging.DEBUG)

def parseArgs():
  usage = "usage: %prog [options]"
  parser = OptionParser(usage)
  parser.add_option("-p", "--packages", dest="packages", help="read Packages from FILENAME")
  parser.add_option("-s", "--source", dest="sources", help="read Sources from FILENAME")

  (options, args) = parser.parse_args()

  if options.packages:
    logging.debug("Parsing package data from %s" % options.packages)
    processPackages(options.packages)

# FIMXE: Use a class instead
def processPackages(packagesFile):

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
  init()
