import sys
import logging

from optparse import OptionParser
from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parsers import PackagesParser, SourcesParser
from export import Triplifier, Serializer
from errors import ParsingException 
from errors import OptsParsingException

VERSION = "0.1alpha"

class Launcher():
  """ Application entrypoint """
  def __init__(self):
    self.opts = None

  def run(self):
    try:
      self.parseArgs()
    except OptsParsingException, e:
      print >> sys.stderr, str(e)
      sys.exit(2)

    self.configLogger()

    if self.opts.packages:
      logging.info("Trying to convert metadata from %s to %s..." % \
                    (self.opts.packages, self.opts.packagesOutput))
      try:
        self.processPackages()
      except:
        logging.error("%s will not be processed, check application log" % self.opts.packages)

    if self.opts.sources:
      logging.info("Trying to convert metadata from %s to %s..." % \
                    (self.opts.sources, self.opts.sourcesOutput))
      try:
        self.processSources()
      except:
        logging.error("%s will not be processed, check application log" % self.opts.sources)

  def configLogger(self):
    if self.opts.verbose:
      lvl = logging.DEBUG
    elif self.opts.quiet:
      lvl = logging.ERROR
    else:
      lvl = logging.INFO

    logging.basicConfig(level=lvl, format='%(message)s')

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
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",\
                      default=False, help="increases debug level")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",\
                      default=False,\
                      help="decreases debug level (only errors are shown)")

    (self.opts, args) = parser.parse_args()

    # FIXME: Add more checks
    if not self.opts.packages and not self.opts.sources:
      raise OptsParsingException("Nothing to do, did you forget -p and/or -s?")
    elif (self.opts.packages or self.opts.packages) and not self.opts.baseURI:
      raise OptsParsingException("Required base URI is missing, did you forget -b?")
    elif self.opts.verbose and self.opts.quiet:
      raise OptsParsingException("Verbose (-v) and Quiet (-q) are mutually exclusive")

  def processPackages(self):
    try:
      inputFile = open(self.opts.packages)
    except IOError, e:
      logging.error("Unable to open Packages input stream (%s)." % str(e))
      raise e
   
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
      except ParsingException, e:
        logging.error("Unable to parse package (%s). Skipping this." % str(e))
        continue

      # Triplify
      triplifier.triplifyBinaryPackage(parsedPackage)

      logging.debug("Processed binary package %s." % parsedPackage.package)
      if counter % 500 == 0:
        logging.info("Processed %s binary packages." % counter)

    # Serialize all packages
    try:
      outputFile = open(self.opts.packagesOutput, "w")
    except IOError, e:
      logging.error("Unable to open Packages output stream (%s)." % str(e))
      raise e

    serializer.serializeToFile(graph, outputFile)
    logging.debug("Graph serialization completed.")

    inputFile.close()
    outputFile.close()

    logging.info("Done! %s binary packages processed and %s triples extracted" % \
                (counter, len(graph)))

  def processSources(self):
    try:
      inputFile = open(self.opts.sources)
    except IOError, e:
      logging.error("Unable to open Sources input stream (%s)." % str(e))
      raise Exception()
   
    counter = 0
    graph = ConjunctiveGraph()
    parser = SourcesParser()
    triplifier = Triplifier(graph, self.opts.baseURI)
    serializer = Serializer()

    rawPackages = deb822.Sources.iter_paragraphs(inputFile)

    for p in rawPackages:
      # Parse
      try:
        parsedPackage = parser.parseSourcePackage(p)
        counter += 1
      except ParsingException, e:
        logging.error("Unable to parse package (%s). Skipping this." % str(e))
        continue

      # Triplify
      triplifier.triplifySourcePackage(parsedPackage)

      logging.debug("Processed source package %s." % parsedPackage.package)
      if counter % 500 == 0:
        logging.info("Processed %s source packages." % counter)
    
    # Serialize all packages
    try:
      outputFile = open(self.opts.sourcesOutput, "w")
    except IOError, e:
      logging.error("Unable to open Sources output stream (%s)." % str(e))
      raise Exception()
    
    serializer.serializeToFile(graph, outputFile)
    logging.debug("Graph serialization completed.")

    inputFile.close()
    outputFile.close()

    logging.info("Done! %s source packages processed and %s triples extracted" % \
                (counter, len(graph)))

if __name__ == "__main__":
  Launcher().run()
