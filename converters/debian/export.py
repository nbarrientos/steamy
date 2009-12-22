from rdflib import Namespace, URIRef, BNode, Literal

RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class Triplifier():
  def __init__(self, graph, baseUri):
    self.g = graph
    self.baseUri = baseUri
    
    # Namespace Binding
    self.g.bind("rdf", RDF)
    self.g.bind("deb", DEB)

  def triplifyBinaryPackage(self, package):
    packageUri = URIRef(package.asUri(self.baseUri))
    self.g.add((packageUri, RDF.type, DEB['Binary']))

    self.triplifyBinaryPackageBuild(package.build, package.asUri(self.baseUri))
    
    # Package - Build
    buildUri = URIRef(package.build.asUri(package.asUri(self.baseUri)))
    self.g.add((packageUri, DEB['build'], buildUri))

  def triplifyBinaryPackageBuild(self, build, base):
    buildUri = URIRef(build.asUri(base))
    self.g.add((buildUri, RDF.type, DEB['Build']))
   
    # Architecture
    self.triplifyArchitecture(build.architecture)
    self.g.add((buildUri, DEB['architecture'], URIRef(build.architecture.asUri(self.baseUri))))

  def triplifyArchitecture(self, arch):
    self.g.add((URIRef(arch.asUri(self.baseUri)), RDF.type, DEB['Architecture']))
    

class Serializer():
  def __init__(self):
    pass

  def serializeToFile(self, graph, file):
    file.write(graph.serialize())
