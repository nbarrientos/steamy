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

  def triplifyBinaryPackage(self, package):
    packageURI = URIRef(package.asURI(self.baseURI))
    self.g.add((packageURI, RDF.type, DEB['Binary']))

    self.triplifyBinaryPackageBuild(package.build, package.asURI(self.baseURI))
    
    # Package - Build
    buildURI = URIRef(package.build.asURI(package.asURI(self.baseURI)))
    self.g.add((packageURI, DEB['build'], buildURI))

  def triplifyBinaryPackageBuild(self, build, base):
    buildURI = URIRef(build.asURI(base))
    self.g.add((buildURI, RDF.type, DEB['Build']))
   
    # Architecture
    self.triplifyArchitecture(build.architecture)
    self.g.add((buildURI, DEB['architecture'], URIRef(build.architecture.asURI(self.baseURI))))

  def triplifyArchitecture(self, arch):
    self.g.add((URIRef(arch.asURI(self.baseURI)), RDF.type, DEB['Architecture']))
    

class Serializer():
  def __init__(self):
    pass

  def serializeToFile(self, graph, file):
    file.write(graph.serialize())
