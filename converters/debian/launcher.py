import sys
import logging
import re
import time, rfc822, datetime

from optparse import OptionParser
from debian_bundle import deb822
from rdflib.Graph import ConjunctiveGraph

from parsers import PackagesParser, SourcesParser
from export import Triplifier, Serializer
from errors import PackageDoesNotMatchRegularExpressionException
from errors import ParsingErrorException
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
      except Exception, e:
        logging.error("%s will not be processed, check application log" % self.opts.packages)
        logging.debug(str(e))

    if self.opts.sources:
      logging.info("Trying to convert metadata from %s to %s..." % \
                    (self.opts.sources, self.opts.sourcesOutput))
      try:
        self.processSources()
      except Exception, e:
        logging.error("%s will not be processed, check application log" % self.opts.sources)
        logging.debug(str(e))

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
    parser.add_option("-b", "--base", dest="baseURI",\
                      metavar="URI", help="use URI as base URI for all resources\
                      (e.g. 'http://rdf.debian.net')")
    parser.add_option("-d", "--distribution", dest="distribution",\
                      metavar="URI", help="attach distribution pointed by URI\
                      to every source package processed\
                      (e.g. 'http://rdf.debian.net/distribution/lenny')")
    parser.add_option("-D", "--distribution-release-date", dest="distdate",\
                      metavar="DATE", help="set distribution release date to\
                      DATE (RFC822) (e.g. 'Mon, 20 Nov 1995 13:12:08 -0500')")
    parser.add_option("-P", "--packages-output", dest="packagesOutput",\
                      default="Packages.rdf",\
                      metavar="FILE", help="dump rdfized Packages to FILE [default: %default]")
    parser.add_option("-S", "--sources-output", dest="sourcesOutput",\
                      default="Sources.rdf",\
                      metavar="FILE", help="dump rdfized Sources to FILE [default: %default]")
    parser.add_option("-f", "--output-format", dest="format",\
                      default="xml", choices=["xml", "nt", "n3"],\
                      metavar="FORMAT", help="use FORMAT as graph serialization\
                      format [options: xml, n3, nt] [default: %default]")
    parser.add_option("-r", "--regex", dest="regex",\
                      metavar="REGEX", help="skip source and binary packages not matching REGEX")
    parser.add_option("-t", "--guess-team", action="store_true", dest="team",\
                      default=False,\
                      help="team membership heuristic: every human uploader\
                      will be added as team member if maintainer is classified as a team")
    parser.add_option("-a", "--guess-area", action="store_true", dest="area",\
                      default=False,\
                      help="package area heuristic: attach source package to an\
                      area according to the content of directory field")
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
    elif self.opts.distribution and \
         re.match(r"^%s.+" % self.opts.baseURI, self.opts.distribution) == None:
      raise OptsParsingException("Distribution (-d) is not prefixed by base URI (-b)")
    elif self.opts.regex:
      try:
        self.opts.cRegex = re.compile(self.opts.regex)
      except:
        raise OptsParsingException("The Regular expression you provided is not valid")
    elif self.opts.distdate and not self.opts.distribution:
      raise OptsParsingException("No distribution provided, did you forget -d?")

    if self.opts.distdate:
      date = rfc822.parsedate(self.opts.distdate)
      if date is not None:
        stamp = time.mktime(date)
        self.opts.parsedDistDate = datetime.date.fromtimestamp(stamp)
      else:
        raise OptsParsingException("'%s' is not a valid RFC822 date" % \
        self.opts.distdate)


  def processPackages(self):
    try:
      inputFile = open(self.opts.packages)
    except IOError, e:
      logging.error("Unable to open Packages input stream (%s)." % str(e))
      raise e
   
    counter = 0
    graph = ConjunctiveGraph()
    parser = PackagesParser(self.opts)
    triplifier = Triplifier(graph, self.opts)
    triplifier.pushInitialTriples()
    serializer = Serializer(self.opts)

    rawPackages = deb822.Packages.iter_paragraphs(inputFile)

    for p in rawPackages:
      # Parse
      try:
        parsedPackage = parser.parseBinaryPackage(p)
        counter += 1
      except PackageDoesNotMatchRegularExpressionException, e:
        logging.debug("Won't process this package (reason: '%s')." % str(e))
        continue
      except ParsingErrorException, e:
        logging.error("Won't process this package (reason: '%s')." % str(e))
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
    parser = SourcesParser(self.opts)
    triplifier = Triplifier(graph, self.opts)
    triplifier.pushInitialTriples()
    serializer = Serializer(self.opts)

    rawPackages = deb822.Sources.iter_paragraphs(inputFile)

    for p in rawPackages:
      # Parse
      try:
        parsedPackage = parser.parseSourcePackage(p)
        counter += 1
      except PackageDoesNotMatchRegularExpressionException, e:
        logging.debug("Won't process this package (reason: '%s')." % str(e))
        continue
      except ParsingErrorException, e:
        logging.error("Won't process this package (reason: '%s')." % str(e))
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
