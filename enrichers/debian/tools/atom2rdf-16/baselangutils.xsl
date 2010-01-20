<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- xml:base / xml:lang resolver -->
  <!-- $Id: baselangutils.xsl,v 1.4 2006/05/01 19:44:09 Dave Exp $ -->


  <xsl:include href="urires.xsl" />


  <xsl:template name="getXmlLang">
    <xsl:param name="element" />
    <xsl:param name="default" />

    <xsl:choose>
      <xsl:when test="$element/@xml:lang">
	<xsl:value-of select="$element/@xml:lang" />
      </xsl:when>
      <xsl:otherwise>

	<xsl:choose>
	  <xsl:when test="$element/..">

	    <xsl:call-template name="getXmlLang">
	      <xsl:with-param name="element" select="$element/.." />
	      <xsl:with-param name="default" select="$default" />
	    </xsl:call-template>

	  </xsl:when>
	  <xsl:otherwise>

	    <xsl:value-of select="$default" />
	      
	  </xsl:otherwise>
	</xsl:choose>

      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>


  <xsl:template name="getXmlBase">
    <xsl:param name="element" />
    <xsl:param name="default" />
    <xsl:param name="strict" select="'true'" />

    <xsl:variable name="pathString">
      <xsl:value-of select="$default" />
      <xsl:call-template name="blu_getXmlBaseQueue">
	<xsl:with-param name="element" select="$element" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:call-template name="blu_splitPath">
      <xsl:with-param name="h" select="$default" />
      <xsl:with-param name="path" select="normalize-space($pathString)" />
      <xsl:with-param name="strict" select="$strict" />
    </xsl:call-template>

  </xsl:template>


  <xsl:template name="blu_splitPath">
    <xsl:param name="h" select="''" />
    <xsl:param name="path" />
    <xsl:param name="strict" select="'true'" />

    <xsl:variable name="p1" select="substring-before($path, ' ')" />
    <xsl:variable name="tail" select="substring-after($path, ' ')" />

    <xsl:choose>
      <xsl:when test="$p1">
	<xsl:variable name="res">
	  <xsl:call-template name="blu_splitPath">
	    <xsl:with-param name="h" select="$p1" />
	    <xsl:with-param name="path" select="$tail" />
	  </xsl:call-template>
	</xsl:variable>

	<xsl:call-template name="resolveRef">
	  <xsl:with-param name="base" select="$h" />
	  <xsl:with-param name="ref" select="$res" />
	  <xsl:with-param name="strict" select="$strict" />
	</xsl:call-template>

      </xsl:when>
      <xsl:otherwise>

	<xsl:if test="$path">
	  <xsl:call-template name="resolveRef">
	    <xsl:with-param name="base" select="$h" />
	    <xsl:with-param name="ref" select="$path" />
	    <xsl:with-param name="strict" select="$strict" />
	  </xsl:call-template>
	</xsl:if>

      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>

  <xsl:template name="blu_getXmlBaseQueue">
    <xsl:param name="element" />

    <xsl:if test="$element/..">
      
      <xsl:call-template name="blu_getXmlBaseQueue">
	<xsl:with-param name="element" select="$element/.." />
      </xsl:call-template>
      
    </xsl:if>

    <xsl:if test="$element/..">

      <xsl:if test="$element/@xml:base">
	<xsl:text> </xsl:text>
	<xsl:value-of select="$element/@xml:base" />
      </xsl:if>

    </xsl:if>
	
  </xsl:template>



</xsl:stylesheet>

