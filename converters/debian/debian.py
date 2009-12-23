import sys
import logging

from optparse import OptionParser
from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parser import PackagesParser
from export import Triplifier, Serializer

VERSION = "0.1alpha"

def init():
  configLogger()
  parseArgs()

def configLogger():
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def parseArgs():
  parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
  parser.add_option("-p", "--packages", dest="packages",\
                    metavar="FILE", help="read Packages from FILE")
  parser.add_option("-s", "--sources", dest="sources",\
                    metavar="FILE", help="read Sources from FILE")
  parser.add_option("-b", "--baseURI", dest="baseURI",\
                    metavar="URI", help="use URI as base URI for all resources")
  parser.add_option("-P", "--packages-output", dest="packagesOutput",\
                    default="Packages.rdf",\
                    metavar="FILE", help="print rdflized Packages to FILE [default: %default]")
  parser.add_option("-S", "--sources-output", dest="sourcesOutput",\
                    default="Sources.rdf",\
                    metavar="FILE", help="print rdflized Sources to FILE [default: %default]")
  (options, args) = parser.parse_args()

  # FIXME: Add more checks
  if not options.packages and not options.sources:
    logging.info("Nothing to do, did you forget -p and/or -s?")

  if options.packages:
    if options.baseURI:
      logging.debug("Converting packages metadata from %s to %s" % \
                    (options.packages, options.packagesOutput))
      processPackages(options.packages, options.packagesOutput, options.baseURI)
    else:
      logging.error("Base URI is missing, did you forget '-b'?")
      exit(-1)

  if options.sources:
    pass # FIXME

# FIMXE: Use a class instead
def processPackages(src, out, baseURI):

  # FIXME: Refactor to init
  graph = ConjunctiveGraph()

  inputFile = openInputFile(src)
  outputFile = openOutputFile(out)

  parser = PackagesParser()
  triplifier = Triplifier(graph, baseURI)
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
  outputFile.close()

def openInputFile(path):
  try:
    return open(path, "r")
  except:
    log.error("Error opening input file for reading")

def openOutputFile(path):
  try:
    # TODO: does the file already exist?
    return open(path, "w+")
  except:
    log.error("Error opening output file for writting")

if __name__ == "__main__":
  init()
