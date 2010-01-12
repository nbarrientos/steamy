from rdflib.sparql.bison.Query import SelectQuery, WhereClause
from rdflib.sparql.bison.GraphPattern import ParsedGroupGraphPattern, GraphPattern
from rdflib.sparql.bison.Resource import Resource
from rdflib.sparql.bison.Triples import PropertyValue

from rdflib import Variable

from sparql.miniast import *

class QueryStringVisitor():
    def visit(self, node, *args):
        className = node.__class__.__name__
        implementation = getattr(self, 'visit_' + className)
        return implementation(node, *args)

    def visit_Optional(self, node):
        return "OPTIONAL { %s } ." % self.visit(node.stmt)

    def visit_Variable(self, node):
        return "?%s" % str(node)

    def visit_URIRef(self, node):
        return "<%s>" % str(node)

    def visit_Literal(self, node):
        return '"%s"' % str(node)

    def visit_Triple(self, node):
        out = [self.visit(node.subject), " ", self.visit(node.property), " ",\
                self.visit(node.object), "."]
        return ''.join(out)

    def visit_Optional(self, node):
        triples = [self.visit(triple) for triple in node.stmts]
        return "OPTIONAL{%s}" % ''.join(triples)

    def visit_Filter(self, node):
        return "FILTER(%s)" % self.visit(node.expr)

    def visit_BinaryExpression(self, node):
        return "%s%s%s" % (self.visit(node.lhs), node.operator,\
                            self.visit(node.rhs))

    def visit_FunCall(self, node):
        args = [self.visit(arg) for arg in node.args]
        return "%s(%s)" % (node.function, ','.join(args))

    def visit_Union(self, node):
        strs = []
        for graphpattern in node.graphpatterns:
            merged_graphpattern = ''.join([self.visit(triple) for triple in graphpattern])
            strs.append(merged_graphpattern)
        return '{' + '}UNION{'.join(strs) + '}'

    def visit_SelectQuery(self, node):
        variables = ''.join(map(self.visit, node.variables))
        where = ''.join(map(self.visit, node.whereclause.stmts))
        query = ["SELECT", variables, " WHERE{", where, "}"] 
        return ''.join(query)

    # Tools

    def visit_str(self, node):
        return node
