<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                
                xmlns:wfw="http://wellformedweb.org/CommentAPI/"
                xmlns:pingback="http://madskills.com/public/xml/rss/module/pingback/"   
                xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/" 
                xmlns:slash="http://purl.org/rss/1.0/modules/slash/" 

                exclude-result-prefixes="xsl rdf wfw pingback trackback slash"
                >

  <!--
NOTES

Supports all rss and atom formats.

Part of the problem with mixing Atom and RSS, or even RSS with DC, is
deciding whether all the information needs to be combined, or whether
some properties just hold redundant duplicate information.

Eg: copyright + dc:rights are likely to be redundant;
    link and atom:link are likely to be relevant

-->  
  
  <xsl:include href="atom2rdf-16-atom.xsl" />
  <xsl:include href="atom2rdf-16-atom03.xsl" />
  <xsl:include href="atom2rdf-16-rss10.xsl" />
  <xsl:include href="atom2rdf-16-rss20.xsl" /> <!-- also supports 0.91 -->

  <xsl:output method="xml" encoding="utf-8" indent="yes" media-type="application/rdf+xml" />

<!--
  <xsl:template mode="query-pluggable-extension" match="wfw:comment">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="wfw:comment">
    <wfw:comment rdf:resource="{normalize-space(text())}" />
  </xsl:template>

  <xsl:template mode="query-pluggable-extension" match="wfw:commentRss">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="wfw:commentRss">
    <wfw:commentRss rdf:resource="{normalize-space(text())}" />
  </xsl:template>

  <xsl:template mode="query-pluggable-extension" match="pingback:target">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="pingback:target">
    <pingback:target rdf:resource="{normalize-space(text())}" />
  </xsl:template>

  <xsl:template mode="query-pluggable-extension" match="pingback:server">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="pingback:server">
    <pingback:target rdf:resource="{normalize-space(text())}" />
  </xsl:template>

  <xsl:template mode="query-pluggable-extension" match="trackback:ping">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="trackback:ping">
    <trackback:ping rdf:resource="{normalize-space(text())}" />
  </xsl:template>

  <xsl:template mode="query-pluggable-extension" match="slash:comments">plugin</xsl:template>
  <xsl:template mode="pluggable-extension" match="slash:comments">
    <slash:comments>
      <xsl:value-of select="normalize-space(text())" />
    </slash:comments>
  </xsl:template>
-->

<!-- TODO temp to test support of extensions -->
<xsl:template mode="query-pluggable-extension" match="*">generic</xsl:template>

</xsl:stylesheet>
