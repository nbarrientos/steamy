#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import random

from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace

DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
XHV = Namespace(u"http://www.w3.org/1999/xhtml/vocab#")
EARL = Namespace(u"http://www.w3.org/ns/earl#")


class GraphPool():
  def __init__(self, size, prefix, base):
    self.prefix = "%s/%s" % (base, prefix)
    self.pool = [ConjunctiveGraph() for i in range(int(size))]
    for graph in self.pool:
      graph.bind("deb", DEB)
      graph.bind("xhv", XHV)
      graph.bind("earl", EARL)

  def add_triple(self, triple):
    self.pool[self._random_graphno()].add(triple)

  def merge_graph(self, graph):
    self.pool[self._random_graphno()] += graph

  def count_triples(self):
    return sum([len(i) for i in self.pool])

  def serialize(self):
    for i in range(len(self.pool)): # I'm sorry :(    
      try:
        f = open("%s-%d.rdf" % (self.prefix, i), "w")
        f.write(self.pool[i].serialize())
        f.close()
      except IOError, e:
        logging.error("Serialization failed: %s (does base dir exist?)", e)

  def _random_graphno(self):
    return int(random.uniform(0, len(self.pool)))
