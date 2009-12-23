import sys
import logging

from optparse import OptionParser
from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parsers import PackagesParser
from export import Triplifier, Serializer
from errors import MissingMandatoryFieldException 
from errors import NoFilesException, NoBaseURIException

VERSION = "0.1alpha"

class Launcher():
  """ Application entrypoint """
  def __init__(self):
    self.opts = None

  def run(self):
    self.configLogger()
    try:
      self.parseArgs()
    except NoFilesException:
      logging.info("Nothing to do, did you forget -p and/or -s?")
      exit(0)
    except NoBaseURIException:
      logging.error("Required base URI is missing, did you forget '-b'?")
      exit(-1)

    if self.opts.packages:
        logging.info("Trying to convert metadata from %s to %s..." % \
                      (self.opts.packages, self.opts.packagesOutput))
        try:
          (packagesno, triplesno) = self.processPackages()
          logging.info("Done! %s binary packages processed and %s triples extracted" % \
                      (packagesno,triplesno))
        except:
          logging.error("%s will not be processed, check application log" % self.opts.packages)

    if self.opts.sources:
      pass # FIXME

  def configLogger(self):
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

  def parseArgs(self):
    parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
    parser.add_option("-p", "--packages", dest="packages",\
                      metavar="FILE", help="read Packages from FILE")
    parser.add_option("-s", "--sources", dest="sources",\
                      metavar="FILE", help="read Sources from FILE")
    parser.add_option("-b", "--baseURI", dest="baseURI",\
                      metavar="URI", help="use URI as base URI for all resources")
    parser.add_option("-P", "--packages-output", dest="packagesOutput",\
                      default="Packages.rdf",\
                      metavar="FILE", help="dump rdfized Packages to FILE [default: %default]")
    parser.add_option("-S", "--sources-output", dest="sourcesOutput",\
                      default="Sources.rdf",\
                      metavar="FILE", help="dump rdfized Sources to FILE [default: %default]")
    (self.opts, args) = parser.parse_args()

    # FIXME: Add more checks
    if not self.opts.packages and not self.opts.sources:
      raise NoFilesException()
    elif (self.opts.packages or self.opts.packages) and not self.opts.baseURI:
      raise NoBaseURIException()

  def processPackages(self):

    try:
      inputFile = open(self.opts.packages, "r")
      outputFile = open(self.opts.packagesOutput, "w")
    except IOError, e:
      logging.error("Unable to open input and/or output Packages streams (%s)." % str(e))
      raise Exception()
   
    counter = 0
    graph = ConjunctiveGraph()
    parser = PackagesParser()
    triplifier = Triplifier(graph, self.opts.baseURI)
    serializer = Serializer()

    rawPackages = deb822.Packages.iter_paragraphs(inputFile)

    for p in rawPackages:
      # Parse
      try:
        parsedPackage = parser.parseBinaryPackage(p)
        counter += 1
      except MissingMandatoryFieldException, e:
        logging.error("Unable to parse package (%s). Skipping this." % str(e))
        continue

      # Triplify
      triplifier.triplifyBinaryPackage(parsedPackage)

    # Serialize all packages
    serializer.serializeToFile(graph, outputFile)

    inputFile.close()
    outputFile.close()
    return (counter, len(graph))

if __name__ == "__main__":
  Launcher().run()
