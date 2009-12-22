from rdflib import Namespace, URIRef, BNode, Literal

RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class Triplifier():
  def __init__(self, graph, baseURI):
    self.g = graph
    self.baseURI = baseURI
    
    # Namespace Binding
    self.g.bind("rdf", RDF)
    self.g.bind("deb", DEB)

  def triplifySourcePackage(self, package):
    pass # FIMXE

  def triplifyBinaryPackage(self, package):
    ref = URIRef(package.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Binary']))

    # Package
    self.g.add((ref, DEB['packageName'], Literal(str(package.package))))

    # Version
    versionRef = self.triplifyVersionNumber(package.version)
    self.g.add((ref, DEB['versionNumber'], versionRef))

    # Build
    buildRef = self.triplifyBinaryPackageBuild(package.build, package.asURI(self.baseURI))
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

  def triplifyBinaryPackageBuild(self, build, base):
    ref = URIRef(build.asURI(base))
    self.g.add((ref, RDF.type, DEB['Build']))
   
    # Architecture
    archRef = self.triplifyArchitecture(build.architecture)
    self.g.add((ref, DEB['architecture'], archRef))

    return ref

  def triplifyArchitecture(self, arch):
    ref = URIRef(arch.asURI(self.baseURI))
    self.g.add((ref, RDF.type, DEB['Architecture']))
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

    self.g.add((ref, DEB['packageName'], Literal(str(constraint.package))))

    if constraint.operator and constraint.version:
      self.g.add((ref, DEB['constraintOperator'], Literal(str(constraint.operator))))
      versionRef = self.triplifyVersionNumber(constraint.version)
      self.g.add((ref, DEB['versionNumber'], versionRef))

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


class Serializer():
  def __init__(self):
    pass

  def serializeToFile(self, graph, file):
    file.write(graph.serialize())
