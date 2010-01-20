<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dct="http://purl.org/dc/terms/"
                xmlns:content="http://purl.org/rss/1.0/modules/content/"
                xmlns:rss="http://purl.org/rss/1.0/"
                xmlns:RSS2COMPAT="tag:djpowell.net,2005:ns-rss-compat/"
                
                exclude-result-prefixes="atom rdf dc dct content rss RSS2COMPAT"
                >

  <!-- Common utilities -->
  <!-- $Id: atom2rdf-16-common.xsl,v 1.1 2006/05/08 19:37:37 Dave Exp $ -->

<!--
NOTES

Part of the problem with mixing Atom and RSS, or even RSS with DC, is
deciding whether all the information needs to be combined, or whether
some properties just hold redundant duplicate information.

Eg: copyright + dc:rights are likely to be redundant;
    link and atom:link are likely to be relevant

-->  
  
  <xsl:import href="atom2rdf-16-extensions.xsl" />
  <xsl:import href="baselangutils.xsl" />
  <xsl:import href="rssdates.xsl" />

  <xsl:param name="contentbase" />
  <xsl:param name="contentlang" />

  <xsl:variable name="NS_ATOMRDF" select="'http://djpowell.net/schemas/atomrdf/0.3/'" />
  <xsl:variable name="NS_RSS2COMPAT" select="'tag:djpowell.net,2005:ns-rss-compat/'" />

  <!-- FUTURE perhaps allow option of per-site preprocessing stylesheets -->

  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>

  <!-- OTHERS -->
  <xsl:template match="*">
    <xsl:message terminate="yes">Unsupported feed format: {<xsl:value-of select="namespace-uri()" />}<xsl:value-of select="local-name()" /></xsl:message>
  </xsl:template>

  <xsl:template mode="feed-title" match="dc:title">
    <!-- should be plain text -->
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="feed-subtitle" match="dc:description">
    <!-- should be plain text -->
    <atomrdf:summary>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:summary>
  </xsl:template>

  <xsl:template mode="feed-language" match="dc:language">
    <dc:language>
      <xsl:value-of select="text()" />
    </dc:language>
  </xsl:template>

  <xsl:template mode="feed-author" match="dc:creator">
    <atomrdf:author>
      <xsl:call-template name="FreePerson" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="feed-rights" match="dc:rights">
    <atomrdf:rights>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="feed-updated" match="dc:date">
    <atomrdf:updated>
      <xsl:call-template name="convertW3CDateTimeDate">
        <xsl:with-param name="in" select="text()" />
      </xsl:call-template>
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="feed-category" match="dc:subject">
    <atomrdf:category>
      <atomrdf:Category>

        <!-- set category id -->
        <xsl:attribute name="rdf:nodeID">
          <xsl:text>cat-</xsl:text>
          <xsl:value-of select="generate-id()" />
        </xsl:attribute>
        
        <atomrdf:categoryTerm>
          <xsl:value-of select="text()" />
        </atomrdf:categoryTerm>
      </atomrdf:Category>
    </atomrdf:category>   
  </xsl:template>

  <xsl:template mode="feed" match="dc:contributor">
    <atomrdf:random>
      <xsl:call-template name="FreePerson" />
    </atomrdf:random>
  </xsl:template>

  <!-- ALTERNATE ENTRY PROPERTIES -->

  <xsl:template mode="entry-author" match="dc:creator">
    <atomrdf:author>
      <xsl:call-template name="FreePerson" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="entry-rights" match="dc:rights">
    <atomrdf:rights>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="entry-title" match="dc:title">
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="entry-summary" match="dc:description">
    <atomrdf:summary>
      <xsl:call-template name="AmbiguousRSS2Text" />
    </atomrdf:summary>
  </xsl:template>

  <xsl:template mode="entry-content" match="content:encoded">
    <atomrdf:content>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'HtmlText'" />
      </xsl:call-template>
    </atomrdf:content>
  </xsl:template>

  <xsl:template mode="entry-content" match="xhtml:div">
    <atomrdf:content>
      <xsl:call-template name="XhtmlRSS2Text" />
    </atomrdf:content>
  </xsl:template>

  <xsl:template mode="entry-content" match="xhtml:body">
    <atomrdf:content>
      <xsl:call-template name="XhtmlRSS2Text" />
    </atomrdf:content>
  </xsl:template>

  <xsl:template mode="entry-updated" match="dc:date">
    <atomrdf:updated>
      <xsl:call-template name="convertW3CDateTimeDate">
        <xsl:with-param name="in" select="text()" />
      </xsl:call-template>
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="entry-category" match="dc:subject">
    <atomrdf:category>
      <atomrdf:Category>

        <!-- set category id -->
        <xsl:attribute name="rdf:nodeID">
          <xsl:text>cat-</xsl:text>
          <xsl:value-of select="generate-id()" />
        </xsl:attribute>
        
        <atomrdf:categoryTerm>
          <xsl:value-of select="text()" />
        </atomrdf:categoryTerm>
      </atomrdf:Category>
    </atomrdf:category>   
  </xsl:template>

  <xsl:template mode="entry" match="dc:contributor">
    <atomrdf:contributor>
      <xsl:call-template name="FreePerson" />
    </atomrdf:contributor>
  </xsl:template>

  <xsl:template mode="entry-language" match="dc:language">
    <dc:language>
      <xsl:value-of select="text()" />
    </dc:language>
  </xsl:template>

  <!-- FUNCTIONS -->
  
  <!--
      YYYY (eg 1997)
      YYYY-MM (eg 1997-07)
      YYYY-MM-DD (eg 1997-07-16)
      YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
      YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)
      YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)
      
      We probably only need to support the form used by Atom, the
      others are probably quite rare.
  -->
  <xsl:template name="convertW3CDateTimeDate">
    <xsl:param name="in" />
    <xsl:value-of select="$in" />
  </xsl:template>

  <!-- OVERRIDES -->
  
  <xsl:template mode="feed" match="*" />
  <xsl:template mode="entry" match="*" />

</xsl:stylesheet>