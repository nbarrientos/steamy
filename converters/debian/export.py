#!/usr/bin/python
# -*- coding: utf8 -*-

from rdflib import Namespace, URIRef, BNode, Literal

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/#")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
NFO = Namespace(u"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")
TAG = Namespace(u"http://www.holygoat.co.uk/owl/redwood/0.1/tags#")

class Triplifier():
  def __init__(self, graph, baseURI):
    self.g = graph
    self.baseURI = baseURI
    
    # Namespace Binding
    self.g.bind("rdf", RDF)
    self.g.bind("deb", DEB)
    self.g.bind("rdfs", RDFS)
    self.g.bind("foaf", FOAF)
    self.g.bind("nfo", NFO)
    self.g.bind("tag", TAG)

  ### Sources ###

  def triplifySourcePackage(self, package):
    ref = URIRef(package.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Source']))
    self.g.add((ref, RDFS.label, Literal(package.asLabel())))

    # Package
    self.g.add((ref, DEB['packageName'], Literal(str(package.package))))

    # Version
    versionRef = self.triplifyVersionNumber(package.version)
    self.g.add((ref, DEB['versionNumber'], versionRef))

    # Binary
    if package.binary:
      for binary in package.binary:
        binaryRef = self.triplifyBinaryPackageLite(binary)
        self.g.add((ref, DEB['binary'], binaryRef))

    # Build-Depends
    if package.buildDepends:
      for ord in package.buildDepends:
        node = self.triplifyOrConstraint(ord)
        self.g.add((ref, DEB['build-depends'], node))

    # Build-Depends-Indep
    if package.buildDependsIndep:
      for ord in package.buildDependsIndep:
        node = self.triplifyOrConstraint(ord)
        self.g.add((ref, DEB['build-depends-indep'], node))

    # Architecture
    if package.architecture:
      for arch in package.architecture:
        archRef = self.triplifyArchitecture(arch)
        self.g.add((ref, DEB['shouldBuildIn'], archRef))

    # Directory
    directoryRef = self.triplifyDirectory(package.directory)
    self.g.add((ref, DEB['container'], directoryRef))

    # Files
    for file in package.files:
      fileRef = self.triplifyFile(file)
      self.g.add((fileRef, NFO['belongsToContainer'], directoryRef))
      self.g.add((fileRef, DEB['productOf'], ref))

    # Section
    sectionRef = self.triplifySection(package.section)
    self.g.add((ref, DEB['section'], sectionRef))

    # Priority
    if package.priority:
      priorityRef = self.triplifyPriority(package.priority)
      self.g.add((ref, DEB['priority'], priorityRef))

    # Maintainer
    maintainerRef = self.triplifyContributor(package.maintainer)
    self.g.add((ref, DEB['maintainer'], maintainerRef))

    # Uploaders
    if package.uploaders:
      for uploader in package.uploaders:
        uploaderRef = self.triplifyContributor(uploader)
        self.g.add((ref, DEB['uploader'], uploaderRef))

  def triplifyBinaryPackageLite(self, package):
    ref = URIRef(package.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Binary']))
    self.g.add((ref, RDFS.label, Literal(package.asLabel())))

    # Package
    self.g.add((ref, DEB['packageName'], Literal(str(package.package))))

    # Version
    versionRef = self.triplifyVersionNumber(package.version)
    self.g.add((ref, DEB['versionNumber'], versionRef))

    return ref

  ### Packages ###

  def triplifyBinaryPackage(self, package):
    ref = self.triplifyBinaryPackageLite(package)

    # Build
    buildRef = self.triplifyBinaryPackageBuild(package.build)
    self.g.add((ref, DEB['build'], buildRef))

    # Depends
    if package.depends:
      for ord in package.depends:
        node = self.triplifyOrConstraint(ord)
        self.g.add((ref, DEB['depends'], node))

    # Recommends
    if package.recommends:
      for orr in package.recommends:
        node = self.triplifyOrConstraint(orr)
        self.g.add((ref, DEB['recommends'], node))

    # Filename
    fileRef = self.triplifyFile(package.filename)
    directoryRef = self.triplifyDirectory(package.filename.ancestor)
    self.g.add((ref, DEB['container'], directoryRef))
    self.g.add((fileRef, NFO['belongsToContainer'], directoryRef))
    self.g.add((fileRef, DEB['productOf'], buildRef))

    # Tag
    if package.tag:
      for tag in package.tag:
        node = self.triplifyTag(tag)
        self.g.add((ref, TAG['taggedWithTag'], node))
        self.g.add((node, TAG['isTagOf'], ref))

    # Section
    sectionRef = self.triplifySection(package.section)
    self.g.add((ref, DEB['section'], sectionRef))

    # Priority
    if package.priority:
      priorityRef = self.triplifyPriority(package.priority)
      self.g.add((ref, DEB['priority'], priorityRef))

  def triplifyBinaryPackageBuild(self, build):
    ref = URIRef(build.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['BinaryBuild']))
    self.g.add((ref, RDFS.label, Literal(build.asLabel())))

    # Architecture
    archRef = self.triplifyArchitecture(build.architecture)
    self.g.add((ref, DEB['architecture'], archRef))

    # Installed-Size
    self.g.add((ref, DEB['installed-size'], Literal(str(build.installedSize))))

    return ref

  def triplifyArchitecture(self, arch):
    if arch.hasInstance():
      return DEB[arch.name]
    else:
      ref = URIRef(arch.asURI(self.baseURI))
      self.g.add((ref, RDF.type, DEB['Architecture']))
      self.g.add((ref, RDFS.label, Literal(arch.asLabel())))
      return ref

  def triplifyOrConstraint(self, orconstraint):
    ref = BNode()
    self.g.add((ref, RDF.type, DEB['DisjunctivePackageConstraint']))

    for constraint in orconstraint.constraints:
      node = self.triplifyConstraint(constraint)
      self.g.add((ref, DEB['alternative'], node))

    return ref

  def triplifyConstraint(self, constraint):
    ref = URIRef(constraint.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['SimplePackageConstraint']))
    self.g.add((ref, RDFS.label, Literal(constraint.asLabel())))

    self.g.add((ref, DEB['packageName'], Literal(str(constraint.package))))

    if constraint.operator and constraint.version:
      self.g.add((ref, DEB['constraintOperator'], Literal(str(constraint.operator))))
      versionRef = self.triplifyVersionNumber(constraint.version)
      self.g.add((ref, DEB['versionNumber'], versionRef))

    for arch in constraint.exceptin:
      archRef = self.triplifyArchitecture(arch)
      self.g.add((ref, DEB['exceptInArchitecture'], archRef))

    for arch in constraint.onlyin:
      archRef = self.triplifyArchitecture(arch)
      self.g.add((ref, DEB['onlyInArchitecture'], archRef))

    return ref

  def triplifyVersionNumber(self, version):
    ref = URIRef(version.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['VersionNumber']))
    
    if version.epoch:
      self.g.add((ref, DEB['epoch'], Literal(str(version.epoch))))

    self.g.add((ref, DEB['upstreamVersion'], Literal(str(version.upstream_version))))
    
    if version.debian_version:
      self.g.add((ref, DEB['debianRevision'], Literal(str(version.debian_version))))
    
    return ref

  def triplifyFile(self, file):
    ref = URIRef(file.asURI(self.baseURI))
    self.g.add((ref, RDF.type, NFO['FileDataObject']))
    self.g.add((ref, RDFS.label, Literal(file.asLabel())))

    self.g.add((ref, NFO['fileName'], Literal(file.name)))

    hash = BNode()
    self.g.add((hash, RDF.type, NFO['FileHash']))
    self.g.add((hash, NFO['hashAlgorithm'], Literal("MD5")))
    self.g.add((hash, NFO['hashValue'], Literal(file.md5sum)))
    self.g.add((ref, NFO['hasHash'], hash))

    self.g.add((ref, NFO['fileSize'], Literal(file.size)))

    return ref

  def triplifyDirectory(self, dir):
    ref = URIRef(dir.asURI(self.baseURI))
    self.g.add((ref, RDF.type, NFO['Folder']))
    self.g.add((ref, RDFS.label, Literal(dir.asLabel())))

    return ref

  def triplifyTag(self, tag):
    ref = URIRef(tag.asURI(self.baseURI))
    self.g.add((ref, RDF.type, TAG['Tag']))
    self.g.add((ref, RDFS.label, Literal(tag.asLabel())))
    self.g.add((ref, DEB['facet'], Literal(tag.facet)))
    self.g.add((ref, TAG['name'], Literal(tag.tag)))

    return ref

  def triplifySection(self, section):
    ref = URIRef(section.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Section']))
    self.g.add((ref, RDFS.label, Literal(section.asLabel())))
    self.g.add((ref, DEB['sectionName'], Literal(section.name)))

    return ref
 
  def triplifyPriority(self, priority):
    ref = URIRef(priority.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Priority']))
    self.g.add((ref, RDFS.label, Literal(priority.asLabel())))
    self.g.add((ref, DEB['priorityName'], Literal(priority.name)))

    return ref

  def triplifyContributor(self, contributor):
    ref = URIRef(contributor.asURI(self.baseURI))
    self.g.add((ref, RDF.type, FOAF[contributor.rdfType()]))
    self.g.add((ref, RDFS.label, Literal(contributor.asLabel())))

    self.g.add((ref, FOAF['name'], Literal(contributor.name)))
    self.g.add((ref, FOAF['mbox'], Literal(contributor.email)))

    return ref
    
 
class Serializer():
  def __init__(self):
    pass

  def serializeToFile(self, graph, file):
    file.write(graph.serialize())
