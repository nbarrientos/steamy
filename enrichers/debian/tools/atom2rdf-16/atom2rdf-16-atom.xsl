<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:arlex="http://djpowell.net/schemas/atomrdf-lex/0.1/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                
                exclude-result-prefixes="atom"
                >

  <!-- Atom 1.0 support for Atom/RDF -->
  <!-- $Id: atom2rdf-16-atom.xsl,v 1.4 2006/08/09 20:26:21 Dave Exp $ -->

  <!--
NOTES

Part of the problem with mixing Atom and RSS, or even RSS with DC, is
deciding whether all the information needs to be combined, or whether
some properties just hold redundant duplicate information.

Eg: copyright + dc:rights are likely to be redundant;
    link and atom:link are likely to be relevant

-->  
  
  <xsl:import href="atom2rdf-16-common.xsl" />

  <xsl:output method="xml" encoding="utf-8" indent="yes" media-type="application/rdf+xml" />
  
  <!-- FUTURE perhaps allow option of per-site preprocessing stylesheets -->

  <xsl:variable name="NS_ATOM" select="'http://www.w3.org/2005/Atom'" />

  <!-- ATOM 1.0 -->
  <xsl:template match="/atom:feed">
    <rdf:RDF>
      <xsl:call-template name="AtomFeed" />

      <xsl:for-each select="/atom:feed/atom:entry/atom:source">
        <xsl:call-template name="AtomFeed" />
      </xsl:for-each>

      <xsl:call-template name="AtomLex" />
    </rdf:RDF>
  </xsl:template>

  <xsl:template name="AtomLex">
    <arlex:State>
      <arlex:feedInstance rdf:nodeID="fi-{generate-id()}" />
      <arlex:entryInstances rdf:parseType="Collection">
        <xsl:for-each select="/atom:feed/atom:entry">
          <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}" />
        </xsl:for-each>
      </arlex:entryInstances>
    </arlex:State>
  </xsl:template>
  
  <!-- === FEED === -->
  <xsl:template name="AtomFeed">
    <xsl:variable name="format" select="'atom10'" />

          <atomrdf:FeedInstance rdf:nodeID="fi-{generate-id()}">

            <atomrdf:feed>
      <atomrdf:Feed>

        <!-- set feed id -->
        <xsl:choose>
          <xsl:when test="atom:id">
            <xsl:attribute name="rdf:about">
              <xsl:value-of select="atom:id" />
            </xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="rdf:nodeID">
              <xsl:text>feed-</xsl:text>
              <xsl:value-of select="generate-id()" />
            </xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
      </atomrdf:Feed>
            </atomrdf:feed>

            <xsl:apply-templates mode="feed" />

            <!-- feed extensions -->
            <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM]">
              <xsl:with-param name="context" select="'feed'" />
              <xsl:with-param name="format" select="$format" />
            </xsl:apply-templates>

          </atomrdf:FeedInstance>

      <xsl:apply-templates mode="entries" select="atom:entry">
        <xsl:with-param name="format" select="$format" />
      </xsl:apply-templates>
          
  </xsl:template>


  <xsl:template mode="entries" match="atom:entry">
    <xsl:param name="format" />
    
        <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}">
        
          <atomrdf:entry>
    <atomrdf:Entry>
      <!-- entry id -->
      <xsl:if test="atom:id">
        <xsl:attribute name="rdf:about">
          <xsl:value-of select="atom:id" />
        </xsl:attribute>
      </xsl:if>
    </atomrdf:Entry>
          </atomrdf:entry>

          <xsl:variable name="containingFeedId">
            <xsl:value-of select="/atom:feed/atom:id" />
          </xsl:variable>

          <atomrdf:containingFeed rdf:resource="{$containingFeedId}" />

          <xsl:choose>
            <xsl:when test="not(atom:source)">
              <atomrdf:sourceFeed rdf:resource="{$containingFeedId}" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates mode="source" select="atom:source" />
            </xsl:otherwise>
          </xsl:choose>

          <!-- entry author -->
          <xsl:choose>
            <xsl:when test="atom:author">
              <xsl:apply-templates mode="entry-author" select="atom:author" />
            </xsl:when>
            <xsl:when test="atom:source/atom:author">
              <xsl:apply-templates mode="entry-author" select="atom:source/atom:author" />
            </xsl:when>
            <xsl:when test="/atom:feed/atom:author">
              <xsl:apply-templates mode="entry-author" select="/atom:feed/atom:author" />
            </xsl:when>
          </xsl:choose>

          <!-- entry rights -->
          <xsl:choose>
            <xsl:when test="atom:rights">
              <xsl:apply-templates mode="entry-rights" select="atom:rights" />
            </xsl:when>
            <xsl:when test="atom:source/atom:rights">
              <xsl:apply-templates mode="entry-rights" select="atom:source/atom:rights" />
            </xsl:when>
            <xsl:when test="/atom:feed/atom:rights">
              <xsl:apply-templates mode="entry-rights" select="/atom:feed/atom:rights" />
            </xsl:when>
          </xsl:choose>

          <xsl:apply-templates mode="entry" />
          
          <!-- entry extensions -->
          <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM]">
            <xsl:with-param name="context" select="'entry'" />
            <xsl:with-param name="format" select="$format" />
          </xsl:apply-templates>

        </atomrdf:EntryInstance>

  </xsl:template>

  <!-- FEED PROPERTIES -->

  <xsl:template mode="feed" match="atom:title">
    <atomrdf:title>
      <xsl:call-template name="Text" />
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="feed" match="atom:subtitle">
    <atomrdf:subtitle>
      <xsl:call-template name="Text" />
    </atomrdf:subtitle>
  </xsl:template>

  <xsl:template mode="feed" match="atom:author">
    <atomrdf:author>
      <xsl:call-template name="Person" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="feed" match="atom:rights">
    <atomrdf:rights>
      <xsl:call-template name="Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="feed" match="atom:updated">
    <atomrdf:updated>
      <xsl:value-of select="." />
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="feed" match="atom:category">
    <xsl:call-template name="Category" />
  </xsl:template>

  <xsl:template mode="feed" match="atom:generator">
    <atomrdf:generator>
      <atomrdf:Generator>
        
        <atomrdf:generatorName>
          <xsl:value-of select="." />
        </atomrdf:generatorName>
          
        <xsl:if test="@uri">
          <atomrdf:generatorUri>
            <xsl:attribute name="rdf:resource">
              <xsl:call-template name="resolveRef">
                <xsl:with-param name="base">
                  <xsl:call-template name="getXmlBase">
                    <xsl:with-param name="element" select="." />
                    <xsl:with-param name="default" select="$contentbase" />
                  </xsl:call-template>
                </xsl:with-param>
                <xsl:with-param name="ref" select="@uri" />
              </xsl:call-template>
            </xsl:attribute>
          </atomrdf:generatorUri>
        </xsl:if>
          
        <xsl:if test="@version">
          <atomrdf:generatorVersion>
            <xsl:value-of select="@version" />
          </atomrdf:generatorVersion>
        </xsl:if>

      </atomrdf:Generator>
    </atomrdf:generator>
  </xsl:template>

  <xsl:template mode="feed" match="atom:logo">
    <atomrdf:logo>
      <atomrdf:Image>
        <atomrdf:imageUri>
          <xsl:attribute name="rdf:resource">
            <!-- resolve atom:logo IRIRef -->
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="node()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:imageUri>
      </atomrdf:Image>
    </atomrdf:logo>
  </xsl:template>

  <xsl:template mode="feed" match="atom:link">
    <xsl:call-template name="Link" />
  </xsl:template>

  <xsl:template mode="feed" match="atom:contributor">
    <atomrdf:contributor>
      <xsl:call-template name="Person" />
    </atomrdf:contributor>
  </xsl:template>

  <!-- ATOM SPECIFIC FEED PROPERTIES -->

  <xsl:template mode="feed" match="atom:icon">
    <atomrdf:icon>
      <atomrdf:Image>
        <atomrdf:imageUri>
          <xsl:attribute name="rdf:resource">
            <!-- resolve atom:logo IRIRef -->
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="node()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:imageUri>
      </atomrdf:Image>
    </atomrdf:icon>
  </xsl:template>


  <!-- ENTRY PROPERTIES -->

  <xsl:template mode="entry-author" match="atom:author">
    <atomrdf:author>
      <xsl:call-template name="Person" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="entry-rights" match="atom:rights">
    <atomrdf:rights>
      <xsl:call-template name="Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="entry" match="atom:title">
    <atomrdf:title>
      <xsl:call-template name="Text" />
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="entry" match="atom:summary">
    <atomrdf:summary>
      <xsl:call-template name="Text" />
    </atomrdf:summary>
  </xsl:template>

  <xsl:template mode="entry" match="atom:content">
    <xsl:variable name="ltype" select="translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />
    <atomrdf:content>
      <xsl:choose>
        <!-- process external content -->
        <xsl:when test="@src">

          <atomrdf:ExternalContent>
            <atomrdf:contentSource>
              <xsl:attribute name="rdf:resource">
                <xsl:call-template name="resolveRef">
                  <xsl:with-param name="base">
                    <xsl:call-template name="getXmlBase">
                      <xsl:with-param name="element" select="." />
                      <xsl:with-param name="default" select="$contentbase" />
                    </xsl:call-template>
                  </xsl:with-param>
                  <xsl:with-param name="ref" select="@src" />
                </xsl:call-template>
              </xsl:attribute>
            </atomrdf:contentSource>
            <xsl:if test="@type">
              <atomrdf:mimeType>
                <xsl:value-of select="$ltype" />
              </atomrdf:mimeType>
            </xsl:if>
          </atomrdf:ExternalContent>
        </xsl:when>

        <!-- process text content -->
        <xsl:when test="not(@type) or $ltype='text'">
          <atomrdf:PlainText>
            <!-- preserve xml:lang context -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>
            
            <atomrdf:textValue>
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:textValue>
          </atomrdf:PlainText>
        </xsl:when>
        
        <!-- process html content -->
        <xsl:when test="$ltype='html'">
          <atomrdf:HtmlText>
            <!-- preserve xml:lang context -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>
            
            <!-- preserve xml:base context -->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:variable>

            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>
            
            <atomrdf:textValue>
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:textValue>
          </atomrdf:HtmlText>
        </xsl:when>

        <!-- process xhtml content -->
        <xsl:when test="$ltype='xhtml'">
          <atomrdf:XhtmlText>
            <!-- preserve xml:lang context -->
            <!-- get lang from the xhtml:div -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="xhtml:div" />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>

            <!-- preserve xml:base context from xhtml:div -->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="xhtml:div" />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>

            <atomrdf:xmlValue rdf:parseType="Literal">
              <!-- don't include div container -->	
              <xsl:apply-templates mode="copyXhtml" select="xhtml:div/node()" />
            </atomrdf:xmlValue>
          </atomrdf:XhtmlText>
        </xsl:when>

        <!-- process XML content -->
        <xsl:when test="(substring($ltype, string-length($ltype) - 3) = '+xml') or (substring($ltype, string-length($ltype) - 3) = '/xml')">
          <atomrdf:XmlContent>
            <!-- preserve xml:lang context -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>

            <!-- preserve xml:base context -->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>

            <atomrdf:xmlValue rdf:parseType="Literal">
              <!-- don't include containing element -->
              <xsl:copy-of select="node()" />
            </atomrdf:xmlValue>
            <atomrdf:mimeType>
              <xsl:value-of select="$ltype" />
            </atomrdf:mimeType>
          </atomrdf:XmlContent>
        </xsl:when>

        <!-- process text/* content -->
        <xsl:when test="starts-with($ltype, 'text/')">
          <atomrdf:TextContent>
            <!-- preserve xml:lang context -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>

            <atomrdf:textValue>
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:textValue>
            <atomrdf:mimeType>
              <xsl:value-of select="$ltype" />
            </atomrdf:mimeType>
          </atomrdf:TextContent>
        </xsl:when>
        
        <!-- process inline binary content -->
        <xsl:otherwise>
          <atomrdf:BinaryContent>
            <!-- preserve xml:base context -->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>
            <atomrdf:base64Value>
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:base64Value>
            <atomrdf:mimeType>
              <xsl:value-of select="$ltype" />
            </atomrdf:mimeType>
          </atomrdf:BinaryContent>
        </xsl:otherwise>
      </xsl:choose>
    </atomrdf:content>
  </xsl:template>

  <xsl:template mode="entry" match="atom:updated">
    <atomrdf:updated>
      <xsl:value-of select="." />
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="entry" match="atom:category">
    <xsl:call-template name="Category" />
  </xsl:template>

  <xsl:template mode="entry" match="atom:link">
    <xsl:call-template name="Link" />
  </xsl:template>

  <xsl:template mode="entry" match="atom:contributor">
    <atomrdf:contributor>
      <xsl:call-template name="Person" />
    </atomrdf:contributor>
  </xsl:template>

  <!-- ATOM SPECIFIC ENTRY PROPERTIES -->

  <xsl:template mode="entry" match="atom:published">
    <atomrdf:published>
      <xsl:value-of select="." />
    </atomrdf:published>
  </xsl:template>

  <!-- SOURCE PROPERTIES -->

  <xsl:template mode="source" match="atom:source">
    <!-- TODO this needs to point to a Feed, and a FeedInstance needs
         to point to that seperately -->
    <atomrdf:sourceFeed>
      <xsl:choose>
        <xsl:when test="atom:id">
          <atomrdf:Feed rdf:resource="{atom:id/text()}" />
        </xsl:when>
        <xsl:otherwise>
          <atomrdf:Feed rdf:nodeID="feed-{generate-id()}" />
        </xsl:otherwise>
      </xsl:choose>
    </atomrdf:sourceFeed>
  </xsl:template>

  <!-- FUNCTIONS -->
  
  <!-- process text constructs -->
  <xsl:template name="Text">
    <xsl:param name="nodeId" select="''" />
    <xsl:variable name="ltype" select="translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />

    <xsl:choose>
      <!-- process text content -->
      <xsl:when test="not(@type) or $ltype='text'">

        <atomrdf:PlainText>
          <!-- set nodeId if a shared Text node (used by atom:rights only) -->
          <xsl:if test="$nodeId != ''">
            <xsl:attribute name="rdf:nodeID">
              <xsl:value-of select="$nodeId" />
            </xsl:attribute>
          </xsl:if>

          <!-- preserve xml:lang context -->
          <xsl:variable name="lang">
            <xsl:call-template name="getXmlLang">
              <xsl:with-param name="element" select="." />
              <xsl:with-param name="default" select="$contentlang" />
            </xsl:call-template>
          </xsl:variable>
          <xsl:if test="$lang != ''">
            <atomrdf:contentLang>
              <xsl:value-of select="$lang" />
            </atomrdf:contentLang>
          </xsl:if>

          <atomrdf:textValue>
            <xsl:value-of select="." />
          </atomrdf:textValue>
        </atomrdf:PlainText>
      </xsl:when>

        <!-- process html content -->
        <xsl:when test="$ltype='html'">

          <atomrdf:HtmlText>
            <!-- set nodeId if a shared Text node (used by atom:rights only) -->
            <xsl:if test="$nodeId != ''">
              <xsl:attribute name="rdf:nodeID">
                <xsl:value-of select="$nodeId" />
              </xsl:attribute>
            </xsl:if>

            <!-- preserve xml:lang context -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
            </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>

            <!-- preserve xml:base context -->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>
            <atomrdf:textValue>
              <xsl:value-of select="." />
            </atomrdf:textValue>
          </atomrdf:HtmlText>
        </xsl:when>

        <!-- process xhtml content -->
        <xsl:when test="$ltype='xhtml'">

          <atomrdf:XhtmlText>
            <!-- set nodeId if a shared Text node (used by atom:rights only) -->
            <xsl:if test="$nodeId != ''">
              <xsl:attribute name="rdf:nodeID">
                <xsl:value-of select="$nodeId" />
              </xsl:attribute>
            </xsl:if>

            <!-- preserve xml:lang context -->
            <!-- get lang from the xhtml:div -->
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="xhtml:div" />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <atomrdf:contentLang>
                <xsl:value-of select="$lang" />
              </atomrdf:contentLang>
            </xsl:if>

            <!-- preserve xml:base context from xhtml:div-->
            <xsl:variable name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="xhtml:div" />
                <xsl:with-param name="default" select="$contentbase" />
            </xsl:call-template>
            </xsl:variable>
            <xsl:if test="not($base='')">
              <atomrdf:contentBase rdf:resource="{$base}" />
            </xsl:if>
            <atomrdf:xmlValue rdf:parseType="Literal">
              <!-- don't include containing element -->	
              <xsl:apply-templates mode="copyXhtml" select="xhtml:div/node()" />
            </atomrdf:xmlValue>
          </atomrdf:XhtmlText>
        </xsl:when>
      </xsl:choose>	
  </xsl:template>

  <!-- process atom:link -->
  <xsl:template name="Link">
    <xsl:variable name="ltype" select="translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />

    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel>
          <xsl:attribute name="rdf:resource">
            <xsl:choose>

              <!-- default rel is 'alternate' -->
              <xsl:when test="not(@rel)">
                <xsl:text>http://www.iana.org/assignments/relation/alternate</xsl:text>
              </xsl:when>

              <!-- if a URI -->
              <xsl:when test="contains(., ':')">
                <xsl:value-of select="@rel" />
              </xsl:when>

              <!-- otherwise use IANA namespace -->
              <xsl:otherwise>
                <xsl:text>http://www.iana.org/assignments/relation/</xsl:text><xsl:value-of select="@rel" />
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </atomrdf:linkRel>
        
        <xsl:variable name="linkType" select="$ltype" />
        <xsl:if test="$linkType">
          <atomrdf:linkType>
            <xsl:value-of select="$linkType" />
          </atomrdf:linkType>
        </xsl:if>
        
        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="@href" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
        <xsl:variable name="linkHrefLang" select="@hreflang" />
        <xsl:if test="$linkHrefLang">
          <atomrdf:linkHrefLang>
            <xsl:value-of select="$linkHrefLang" />
          </atomrdf:linkHrefLang>
        </xsl:if>

        <xsl:variable name="linkTitle" select="@title" />
        <xsl:if test="$linkTitle">
          <atomrdf:linkTitle>
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <xsl:attribute name="xml:lang">
                <xsl:value-of select="$lang" />
              </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="$linkTitle" />
          </atomrdf:linkTitle>
        </xsl:if>

        <xsl:variable name="linkLength" select="@length" />
        <xsl:if test="$linkLength">
          <atomrdf:linkLength>
            <xsl:value-of select="$linkLength" />
          </atomrdf:linkLength>
        </xsl:if>

      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <!-- process Category constructs -->
  <xsl:template name="Category">

    <atomrdf:category>
      <atomrdf:Category>
        
        <atomrdf:categoryTerm>
          <xsl:value-of select="@term" />
        </atomrdf:categoryTerm>

        <xsl:variable name="categoryScheme" select="@scheme" />
        <xsl:if test="$categoryScheme">	      
          <atomrdf:categoryScheme>
            <xsl:attribute name="rdf:resource">
              <xsl:value-of select="$categoryScheme" />
            </xsl:attribute>
          </atomrdf:categoryScheme>
        </xsl:if>

        <xsl:variable name="categoryLabel" select="@label" />
        <xsl:if test="$categoryLabel">	      
          <atomrdf:categoryLabel>
            <xsl:variable name="lang">
              <xsl:call-template name="getXmlLang">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentlang" />
              </xsl:call-template>
            </xsl:variable>
            <xsl:if test="$lang != ''">
              <xsl:attribute name="xml:lang">
                <xsl:value-of select="$lang" />
              </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="$categoryLabel" />
          </atomrdf:categoryLabel>
        </xsl:if>

      </atomrdf:Category>
    </atomrdf:category>
  </xsl:template>

  <!-- process author and contributor -->
  <xsl:template name="Person">
    <atomrdf:Person>
      <xsl:attribute name="rdf:nodeID">
        <xsl:text>person-</xsl:text>
        <xsl:value-of select="generate-id()" />
      </xsl:attribute>

      <!-- process 0 or 1 atom:uri -->
      <xsl:for-each select="atom:uri" >
        <atomrdf:personUri>
          <!-- resolve atom:uri IRIRef -->
          <xsl:call-template name="resolveRef">
            <xsl:with-param name="base">	
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="ref" select="." />
          </xsl:call-template>
        </atomrdf:personUri>
      </xsl:for-each>

      <!-- process 1 atom:name -->
      <xsl:for-each select="atom:name" >
        <atomrdf:personName>
          <!-- add the xml:lang of atom:name -->
          <xsl:variable name="lang">
            <xsl:call-template name="getXmlLang">
              <xsl:with-param name="element" select="." />
              <xsl:with-param name="default" select="$contentlang" />
            </xsl:call-template>
          </xsl:variable>
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="." />
        </atomrdf:personName>
      </xsl:for-each>

      <!-- process 0 or 1 atom:email -->
      <xsl:for-each select="atom:email" >
        <atomrdf:personEmail>
          <xsl:value-of select="." />
        </atomrdf:personEmail>
      </xsl:for-each>
      
      <!-- person extensions -->
      <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM]">
        <xsl:with-param name="context" select="'person'" />
        <xsl:with-param name="format" select="'atom10'" />        
        <xsl:with-param name="defaultBehaviour" select="'generic'" />
      </xsl:apply-templates>
      <!-- always atom10, even if this was found in an rss20 feed -
           probably best not to think about that :) -->

    </atomrdf:Person>
  </xsl:template>

</xsl:stylesheet>