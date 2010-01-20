<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom03="http://purl.org/atom/ns#"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:RSS2COMPAT="tag:djpowell.net,2005:ns-rss-compat/"
                xmlns:dct="http://purl.org/dc/terms/"
                xmlns:arlex="http://djpowell.net/schemas/atomrdf-lex/0.1/"
                
                exclude-result-prefixes="atom03 RSS2COMPAT dct"
                >

  <!-- Atom 0.3 support for Atom/RDF -->
  <!-- $Id: atom2rdf-16-atom03.xsl,v 1.2 2006/08/09 20:11:49 Dave Exp $ -->

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

  <xsl:variable name="NS_ATOM03" select="'http://purl.org/atom/ns#'" />

  <!-- ATOM 1.0 -->
  <xsl:template match="/atom03:feed[@version='0.3']">
    <rdf:RDF>
      <xsl:call-template name="Atom03Feed" />
      <xsl:call-template name="Atom03Lex" />
    </rdf:RDF>
  </xsl:template>

  <xsl:template name="Atom03Lex">
    <arlex:State>
      <arlex:feedInstance rdf:nodeID="fi-{generate-id()}" />
      <arlex:entryInstances rdf:parseType="Collection">
        <xsl:for-each select="/atom03:feed/atom03:entry">
          <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}" />
        </xsl:for-each>
      </arlex:entryInstances>
    </arlex:State>
  </xsl:template>
  
  <!-- === FEED === -->
  <xsl:template name="Atom03Feed">
    <xsl:variable name="format" select="'atom03'" />

          <atomrdf:FeedInstance rdf:nodeID="fi-{generate-id()}">         

            <atomrdf:feed>
      <atomrdf:Feed>

        <!-- NOTE feed id is optional -->
        <!-- set feed id -->
        <xsl:choose>
          <xsl:when test="atom03:id">
            <xsl:attribute name="rdf:about">
              <xsl:value-of select="atom03:id" />
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
            <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM03]">
              <xsl:with-param name="context" select="'feed'" />
              <xsl:with-param name="format" select="$format" />
            </xsl:apply-templates>

          </atomrdf:FeedInstance>

      <xsl:apply-templates mode="entries" select="atom03:entry">
        <xsl:with-param name="format" select="$format" />
      </xsl:apply-templates>
          
  </xsl:template>


  <xsl:template mode="entries" match="atom03:entry">
    <xsl:param name="format" />
    
        <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}">
        
          <atomrdf:entry>
    <atomrdf:Entry>

      <!-- entry id -->
      <xsl:attribute name="rdf:about">
        <xsl:value-of select="atom03:id" />
      </xsl:attribute>
    </atomrdf:Entry>
          </atomrdf:entry>

          <xsl:choose>
            <xsl:when test="/atom03:feed/atom03:id">
              <xsl:variable name="containingFeedId">
                <xsl:value-of select="/atom03:feed/atom03:id" />
              </xsl:variable>
              <atomrdf:containingFeed rdf:resource="{$containingFeedId}" />
              <atomrdf:sourceFeed rdf:resource="{$containingFeedId}" />
            </xsl:when>
           
            <xsl:otherwise>
              <xsl:variable name="containingFeedId">
                <xsl:text>feed-</xsl:text>
                <xsl:value-of select="generate-id( /atom03:feed )" />
              </xsl:variable>
              <atomrdf:containingFeed rdf:nodeID="{$containingFeedId}" />
              <atomrdf:sourceFeed rdf:nodeID="{$containingFeedId}" />
            </xsl:otherwise>
          </xsl:choose>

          <!-- entry author -->
          <xsl:choose>
            <xsl:when test="atom03:author">
              <xsl:apply-templates mode="entry-author" select="atom03:author" />
            </xsl:when>
            <xsl:when test="/atom03:feed/atom03:author">
              <xsl:apply-templates mode="entry-author" select="/atom03:feed/atom03:author" />
            </xsl:when>
          </xsl:choose>

          <!-- entry rights -->
          <xsl:apply-templates mode="entry-rights" select="/atom03:feed/atom03:copyright" />

          <xsl:apply-templates mode="entry" />
          
          <!-- entry extensions -->
          <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM03]">
            <xsl:with-param name="context" select="'entry'" />
            <xsl:with-param name="format" select="$format" />
          </xsl:apply-templates>

        </atomrdf:EntryInstance>

  </xsl:template>


  <!-- FEED PROPERTIES -->

  <xsl:template mode="feed" match="atom03:title">
    <atomrdf:title>
      <xsl:call-template name="Atom03Text" />
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="feed" match="atom03:tagline">
    <atomrdf:subtitle>
      <xsl:call-template name="Atom03Text" />
    </atomrdf:subtitle>
  </xsl:template>

  <xsl:template mode="feed" match="atom03:author">
    <atomrdf:author>
      <xsl:call-template name="Person03" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="feed" match="atom03:copyright">
    <atomrdf:rights>
      <xsl:call-template name="Atom03Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="feed" match="atom03:modified">
    <atomrdf:updated>
      <xsl:value-of select="." />
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="feed" match="atom03:generator">
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
                <xsl:with-param name="ref" select="@url" />
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

  <xsl:template mode="feed" match="atom03:link">
    <xsl:call-template name="Link03" />
  </xsl:template>

  <xsl:template mode="feed" match="atom03:contributor">
    <atomrdf:contributor>
      <xsl:call-template name="Person03" />
    </atomrdf:contributor>
  </xsl:template>

  <!-- NOTE don't bother handling atom03:info -->

  <!-- ENTRY PROPERTIES -->

  <xsl:template mode="entry-author" match="atom03:author">
    <atomrdf:author>
      <xsl:call-template name="Person03" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="entry-rights" match="atom03:copyright">
    <atomrdf:rights>
      <xsl:call-template name="Atom03Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:title">
    <atomrdf:title>
      <xsl:call-template name="Atom03Text" />
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:summary">
    <atomrdf:summary>
      <xsl:call-template name="Atom03Text" />
    </atomrdf:summary>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:content">
    <atomrdf:content>
      <xsl:call-template name="Atom03Content" />
    </atomrdf:content>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:modified">
    <atomrdf:updated>
      <xsl:value-of select="." />
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:link">
    <xsl:call-template name="Link03" />
  </xsl:template>

  <xsl:template mode="entry" match="atom03:contributor">
    <atomrdf:contributor>
      <xsl:call-template name="Person03" />
    </atomrdf:contributor>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:issued">
    <dct:issued>
      <xsl:value-of select="." />
    </dct:issued>
  </xsl:template>

  <xsl:template mode="entry" match="atom03:created">
    <dct:created>
      <xsl:value-of select="." />
    </dct:created>
  </xsl:template>

  <!-- FUNCTIONS -->
  <!-- process atom03:link -->
  <xsl:template name="Link03">
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

      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <!-- process author and contributor -->
  <xsl:template name="Person03">
    <atomrdf:Person>
      <xsl:attribute name="rdf:nodeID">
        <xsl:text>person-</xsl:text>
        <xsl:value-of select="generate-id()" />
      </xsl:attribute>

      <!-- process 0 or 1 atom03:uri -->
      <xsl:for-each select="atom03:url" >
        <atomrdf:personUri>
          <!-- resolve atom03:uri IRIRef -->
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

      <!-- process 1 atom03:name -->
      <xsl:for-each select="atom03:name" >
        <atomrdf:personName>
          <!-- add the xml:lang of atom03:name -->
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

      <!-- process 0 or 1 atom03:email -->
      <xsl:for-each select="atom03:email" >
        <atomrdf:personEmail>
          <xsl:value-of select="." />
        </atomrdf:personEmail>
      </xsl:for-each>
      
      <!-- person extensions -->
      <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_ATOM03]">
        <xsl:with-param name="context" select="'person'" />
        <xsl:with-param name="format" select="'atom03'" />        
        <xsl:with-param name="defaultBehaviour" select="'generic'" />
      </xsl:apply-templates>
      <!-- always atom03, even if this was found in an rss20 feed -
           probably best not to think about that :) -->

    </atomrdf:Person>
  </xsl:template>

  <xsl:template name="Atom03Content">
    <xsl:param name="nodeId" select="''" />
    <xsl:variable name="ltype" select="translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />

    <!-- select first alternate -->
    <xsl:for-each select="descendant-or-self::atom03:content[not(@type) or $ltype != 'multipart/alternative'][1]">
      <xsl:call-template name="Atom03Text">
        <xsl:with-param name="nodeId" select="$nodeId" />
      </xsl:call-template>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="Atom03Text">
    <xsl:param name="nodeId" select="''" />
    <xsl:variable name="ltype" select="translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />

      <xsl:choose>
        
        <xsl:when test="@mode = 'base64'">
          <atomrdf:BinaryContent>
            <!-- set nodeId if a shared Text node (used by atom:rights only) -->
            <xsl:if test="$nodeId != ''">
              <xsl:attribute name="rdf:nodeID">
                <xsl:value-of select="$nodeId" />
              </xsl:attribute>
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
            <atomrdf:base64Value>
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:base64Value>
            <atomrdf:mimeType>
              <xsl:value-of select="$ltype" />
            </atomrdf:mimeType>
          </atomrdf:BinaryContent>
        </xsl:when>

        <!-- process text content -->
        <xsl:when test="not(@type) or $ltype='text/plain'">
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
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:textValue>
          </atomrdf:PlainText>
        </xsl:when>
        
        <!-- process html content -->
        <xsl:when test="@mode='escaped'">
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
              <!-- don't include containing element -->
              <xsl:value-of select="text()" />
            </atomrdf:textValue>
          </atomrdf:HtmlText>
        </xsl:when>

        <!-- process xhtml content -->
        <xsl:when test="$ltype='text/html' or $ltype='application/xhtml+xml'">
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
        <xsl:otherwise>
          <atomrdf:XmlContent>
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

            <atomrdf:xmlValue rdf:parseType="Literal">
              <!-- don't include containing element -->
              <xsl:copy-of select="node()" />
            </atomrdf:xmlValue>
            <atomrdf:mimeType>
              <xsl:value-of select="$ltype" />
            </atomrdf:mimeType>
          </atomrdf:XmlContent>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>

  <!-- OVERRIDES -->
  
  <xsl:template mode="feed" match="*" />
  <xsl:template mode="entry" match="*" />

</xsl:stylesheet>