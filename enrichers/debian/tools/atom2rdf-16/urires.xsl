<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <!-- URI Reference resolver -->
  

  <!-- $Id: urires.xsl,v 1.4 2006/05/01 22:41:24 Dave Exp $ -->

  <!-- resolve a uri reference -->
  <xsl:template name="resolveRef">
    <xsl:param name="base" />
    <xsl:param name="ref" />
    <xsl:param name="strict" select="'true'" />

    <xsl:variable name="refScheme">
      <xsl:call-template name="urires_getScheme">
	<xsl:with-param name="ref" select="$ref" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refNoScheme">
      <xsl:call-template name="urires_getSchemeRest">
	<xsl:with-param name="ref" select="$ref" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refAuth">
      <xsl:call-template name="urires_getAuthority">
	<xsl:with-param name="ref" select="$refNoScheme" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refNoAuth">
      <xsl:call-template name="urires_getAuthorityRest">
	<xsl:with-param name="ref" select="$refNoScheme" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refPath">
      <xsl:call-template name="urires_getPath">
	<xsl:with-param name="ref" select="$refNoAuth" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refNoPath">
      <xsl:call-template name="urires_getPathRest">
	<xsl:with-param name="ref" select="$refNoAuth" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refQuery">
      <xsl:call-template name="urires_getQuery">
	<xsl:with-param name="ref" select="$refNoPath" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="refNoQuery">
      <xsl:call-template name="urires_getQueryRest">
	<xsl:with-param name="ref" select="$refNoPath" />
      </xsl:call-template>
    </xsl:variable>
    
    <xsl:variable name="refFrag">
      <xsl:call-template name="urires_getFragment">
	<xsl:with-param name="ref" select="$refNoQuery" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseScheme">
      <xsl:call-template name="urires_getScheme">
	<xsl:with-param name="ref" select="$base" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseNoScheme">
      <xsl:call-template name="urires_getSchemeRest">
	<xsl:with-param name="ref" select="$base" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseAuth">
      <xsl:call-template name="urires_getAuthority">
	<xsl:with-param name="ref" select="$baseNoScheme" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseNoAuth">
      <xsl:call-template name="urires_getAuthorityRest">
	<xsl:with-param name="ref" select="$baseNoScheme" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="basePath">
      <xsl:call-template name="urires_getPath">
	<xsl:with-param name="ref" select="$baseNoAuth" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseNoPath">
      <xsl:call-template name="urires_getPathRest">
	<xsl:with-param name="ref" select="$baseNoAuth" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseQuery">
      <xsl:call-template name="urires_getQuery">
	<xsl:with-param name="ref" select="$baseNoPath" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="baseNoQuery">
      <xsl:call-template name="urires_getQueryRest">
	<xsl:with-param name="ref" select="$baseNoPath" />
      </xsl:call-template>
    </xsl:variable>
    
    <xsl:variable name="baseFrag">
      <xsl:call-template name="urires_getFragment">
	<xsl:with-param name="ref" select="$baseNoQuery" />
      </xsl:call-template>
    </xsl:variable>

    <!-- uses '&lt;&gt;' as a marker for UNDEFINED - which can't occur
         in scheme, authority, query, or fragment -->

    <xsl:choose>
      <xsl:when test="($refScheme = '&lt;&gt;') or (not($strict = 'true') and ($refScheme = $baseScheme))" >
	<xsl:choose>
	  <xsl:when test="not($refAuth = '&lt;&gt;')">	    
	    <xsl:variable name="targetScheme" select="$baseScheme" />
	    <xsl:variable name="targetAuth" select="$refAuth" />
	    <xsl:variable name="targetPath">
	      <xsl:call-template name="urires_removeDotSegments">
		<xsl:with-param name="in" select="$refPath" />
	      </xsl:call-template>
	    </xsl:variable>
	    <xsl:variable name="targetQuery" select="$refQuery" />
	    <xsl:variable name="targetFrag" select="$refFrag" />
	    <xsl:call-template name="urires_composeUri">
	      <xsl:with-param name="scheme" select="$targetScheme" />
	      <xsl:with-param name="authority" select="$targetAuth" />
	      <xsl:with-param name="path" select="$targetPath" />
	      <xsl:with-param name="query" select="$targetQuery" />
	      <xsl:with-param name="fragment" select="$targetFrag" />
	    </xsl:call-template>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:choose>
	      <xsl:when test="$refPath = ''">
		<xsl:choose>
		  <xsl:when test="not($refQuery = '&lt;&gt;')">
		    <xsl:variable name="targetScheme" select="$baseScheme" />
		    <xsl:variable name="targetAuth" select="$baseAuth" />
		    <xsl:variable name="targetPath" select="$basePath" />
		    <xsl:variable name="targetQuery" select="$refQuery" />
		    <xsl:variable name="targetFrag" select="$refFrag" />
		    <xsl:call-template name="urires_composeUri">
		      <xsl:with-param name="scheme" select="$targetScheme" />
		      <xsl:with-param name="authority" select="$targetAuth" />
		      <xsl:with-param name="path" select="$targetPath" />
		      <xsl:with-param name="query" select="$targetQuery" />
		      <xsl:with-param name="fragment" select="$targetFrag" />
		    </xsl:call-template>
		  </xsl:when>
		  <xsl:otherwise>
		    <xsl:variable name="targetScheme" select="$baseScheme" />
		    <xsl:variable name="targetAuth" select="$baseAuth" />
		    <xsl:variable name="targetPath" select="$basePath" />
		    <xsl:variable name="targetQuery" select="$baseQuery" />
		    <xsl:variable name="targetFrag" select="$refFrag" />
		    <xsl:call-template name="urires_composeUri">
		      <xsl:with-param name="scheme" select="$targetScheme" />
		      <xsl:with-param name="authority" select="$targetAuth" />
		      <xsl:with-param name="path" select="$targetPath" />
		      <xsl:with-param name="query" select="$targetQuery" />
		      <xsl:with-param name="fragment" select="$targetFrag" />
		    </xsl:call-template>
		  </xsl:otherwise>
		</xsl:choose>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:choose>
		  <xsl:when test="starts-with($refPath, '/')">
		    <xsl:variable name="targetScheme" select="$baseScheme" />
		    <xsl:variable name="targetAuth" select="$baseAuth" />
		    <xsl:variable name="targetPath">
		      <xsl:call-template name="urires_removeDotSegments">
			<xsl:with-param name="in" select="$refPath" />
		      </xsl:call-template>
		    </xsl:variable>
		    <xsl:variable name="targetQuery" select="$refQuery" />
		    <xsl:variable name="targetFrag" select="$refFrag" />
		    <xsl:call-template name="urires_composeUri">
		      <xsl:with-param name="scheme" select="$targetScheme" />
		      <xsl:with-param name="authority" select="$targetAuth" />
		      <xsl:with-param name="path" select="$targetPath" />
		      <xsl:with-param name="query" select="$targetQuery" />
		      <xsl:with-param name="fragment" select="$targetFrag" />
		    </xsl:call-template>
		  </xsl:when>
		  <xsl:otherwise>
		    <xsl:variable name="targetScheme" select="$baseScheme" />
		    <xsl:variable name="targetAuth" select="$baseAuth" />
		    <xsl:variable name="targetPath">
		      <xsl:call-template name="urires_removeDotSegments">
			<xsl:with-param name="in">
			  <xsl:call-template name="urires_mergePaths">
			    <xsl:with-param name="baseAuth" select="$baseAuth" />
			    <xsl:with-param name="basePath" select="$basePath" />
			    <xsl:with-param name="refPath" select="$refPath" />
			  </xsl:call-template>
			</xsl:with-param>
		      </xsl:call-template>
		    </xsl:variable>
		    <xsl:variable name="targetQuery" select="$refQuery" />
		    <xsl:variable name="targetFrag" select="$refFrag" />
		    <xsl:call-template name="urires_composeUri">
		      <xsl:with-param name="scheme" select="$targetScheme" />
		      <xsl:with-param name="authority" select="$targetAuth" />
		      <xsl:with-param name="path" select="$targetPath" />
		      <xsl:with-param name="query" select="$targetQuery" />
		      <xsl:with-param name="fragment" select="$targetFrag" />
		    </xsl:call-template>
		  </xsl:otherwise>
		</xsl:choose>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="targetScheme" select="$refScheme" />
	<xsl:variable name="targetAuth" select="$refAuth" />
	<xsl:variable name="targetPath">
	  <xsl:call-template name="urires_removeDotSegments">
	    <xsl:with-param name="in" select="$refPath" />
	  </xsl:call-template>
	</xsl:variable>
	<xsl:variable name="targetQuery" select="$refQuery" />
	<xsl:variable name="targetFrag" select="$refFrag" />
	<xsl:call-template name="urires_composeUri">
	  <xsl:with-param name="scheme" select="$targetScheme" />
	  <xsl:with-param name="authority" select="$targetAuth" />
	  <xsl:with-param name="path" select="$targetPath" />
	  <xsl:with-param name="query" select="$targetQuery" />
	  <xsl:with-param name="fragment" select="$targetFrag" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_composeUri">
    <xsl:param name="scheme" />
    <xsl:param name="authority" />
    <xsl:param name="path" />
    <xsl:param name="query" />
    <xsl:param name="fragment" />

    <xsl:if test="not($scheme = '&lt;&gt;')" >
      <xsl:value-of select="$scheme" />
      <xsl:text>:</xsl:text>
    </xsl:if>

    <xsl:if test="not($authority = '&lt;&gt;')" >
      <xsl:text>//</xsl:text>
      <xsl:value-of select="$authority" />
    </xsl:if>

    <xsl:value-of select="$path" />

    <xsl:if test="not($query = '&lt;&gt;')" >
      <xsl:text>?</xsl:text>
      <xsl:value-of select="$query" />
    </xsl:if>

    <xsl:if test="not($fragment = '&lt;&gt;')" >
      <xsl:text>#</xsl:text>
      <xsl:value-of select="$fragment" />
    </xsl:if>

  </xsl:template>


  <!-- internal use only -->
  <!-- (#(.*))? -->
  <xsl:template name="urires_getFragment">
    <xsl:param name="ref" />
    <xsl:choose>
      <xsl:when test="substring($ref, 1, 1) = '#'">
	<xsl:value-of select="substring($ref, 2)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>&lt;&gt;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- (\?([^#]*))? -->
  <xsl:template name="urires_getQuery">
    <xsl:param name="ref" />
    <xsl:choose>
      <xsl:when test="substring($ref, 1, 1) = '?'">
	<xsl:variable name="ref2" select="substring($ref, 2)" />
	<xsl:variable name="pos">
	  <xsl:call-template name="urires_findQueryEnd">
	    <xsl:with-param name="head" select="$ref2" />
	  </xsl:call-template>
	</xsl:variable>
	<xsl:value-of select="substring($ref2, 1, $pos - 1)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>&lt;&gt;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- (\?([^#]*))? -->
  <xsl:template name="urires_getQueryRest">
    <xsl:param name="ref" />
    <xsl:choose>
      <xsl:when test="substring($ref, 1, 1) = '?'">
	<xsl:variable name="ref2" select="substring($ref, 2)" />
	<xsl:variable name="pos">
	  <xsl:call-template name="urires_findQueryEnd">
	    <xsl:with-param name="head" select="$ref2" />
	  </xsl:call-template>
	</xsl:variable>
	<xsl:value-of select="substring($ref2, $pos)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$ref" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ([^?#]*) -->
  <xsl:template name="urires_getPath">
    <xsl:param name="ref" />
    <xsl:variable name="pos">
      <xsl:call-template name="urires_findPathEnd">
	<xsl:with-param name="head" select="$ref" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:value-of select="substring($ref, 1, $pos - 1)" />
  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_getPathRest">
    <xsl:param name="ref" />
    <xsl:variable name="pos">
      <xsl:call-template name="urires_findPathEnd">
	<xsl:with-param name="head" select="$ref" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:value-of select="substring($ref, $pos)" />
  </xsl:template>

  <!-- internal use only -->
  <!-- (//([^/?#]*))? -->
  <xsl:template name="urires_getAuthority">
    <xsl:param name="ref" />
    <xsl:choose>
      <xsl:when test="substring($ref, 1, 2) = '//'">
	<xsl:variable name="ref2" select="substring($ref, 3)" />
	<xsl:variable name="pos">
	  <xsl:call-template name="urires_findAuthorityEnd">
	    <xsl:with-param name="head" select="$ref2" />
	  </xsl:call-template>
	</xsl:variable>
	<xsl:value-of select="substring($ref2, 1, $pos - 1)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>&lt;&gt;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- (//([^/?#]*))? -->
  <xsl:template name="urires_getAuthorityRest">
    <xsl:param name="ref" />
    <xsl:choose>
      <xsl:when test="substring($ref, 1, 2) = '//'">
	<xsl:variable name="ref2" select="substring($ref, 3)" />
	<xsl:variable name="pos">
	  <xsl:call-template name="urires_findAuthorityEnd">
	    <xsl:with-param name="head" select="$ref2" />
	  </xsl:call-template>
	</xsl:variable>
	<xsl:value-of select="substring($ref2, $pos)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$ref" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ^(([^:/?#]+):)? -->
  <xsl:template name="urires_getScheme">
    <xsl:param name="ref" />
    <xsl:variable name="pos">
      <xsl:call-template name="urires_findSchemeEnd">
	<xsl:with-param name="head" select="$ref" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:choose>
      <xsl:when test="$pos != -1">
	<xsl:choose>
	  <xsl:when test="substring($ref, $pos, 1) = ':'">
	    <xsl:value-of select="substring($ref, 1, $pos - 1)" />
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:text>&lt;&gt;</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>&lt;&gt;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_getSchemeRest">
    <xsl:param name="ref" />
    <xsl:variable name="pos">
      <xsl:call-template name="urires_findSchemeEnd">
	<xsl:with-param name="head" select="$ref" />
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$pos != -1">
	<xsl:choose>
	  <xsl:when test="substring($ref, $pos, 1) = ':'">
	    <xsl:value-of select="substring($ref, $pos + 1)" />
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="$ref" />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$ref" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ([^:/?#]+) -->
  <xsl:template name="urires_findSchemeEnd">
    <xsl:param name="head" />
    <xsl:param name="i" select="1" />

    <xsl:variable name="c" select="substring($head, 1, 1)" />
    <xsl:variable name="tail" select="substring($head, 2)" />

    <xsl:choose>
      <xsl:when test="string-length($head) = 0">
	<!-- no scheme -->
	<xsl:value-of select="-1" />
      </xsl:when>
      <xsl:when test="($c = ':') or ($c = '/') or ($c = '?') or ($c = '#')">
	<xsl:choose>
	  <xsl:when test="number($i) = 1">
	    <!-- no scheme -->
	    <xsl:value-of select="-1" />
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="$i" />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="newi" select="number($i) + 1" />

	<xsl:call-template name="urires_findSchemeEnd">
	  <xsl:with-param name="head" select="$tail" />
	  <xsl:with-param name="i" select="$newi" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ([^#]*) -->
  <xsl:template name="urires_findQueryEnd">
    <xsl:param name="head" />
    <xsl:param name="i" select="1" />

    <xsl:variable name="c" select="substring($head, 1, 1)" />
    <xsl:variable name="tail" select="substring($head, 2)" />

    <xsl:choose>
      <xsl:when test="string-length($head) = 0">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:when test="($c = '#')">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="newi" select="number($i) + 1" />

	<xsl:call-template name="urires_findQueryEnd">
	  <xsl:with-param name="head" select="$tail" />
	  <xsl:with-param name="i" select="$newi" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ([^?#]*) -->
  <xsl:template name="urires_findPathEnd">
    <xsl:param name="head" />
    <xsl:param name="i" select="1" />

    <xsl:variable name="c" select="substring($head, 1, 1)" />
    <xsl:variable name="tail" select="substring($head, 2)" />

    <xsl:choose>
      <xsl:when test="string-length($head) = 0">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:when test="($c = '?') or ($c = '#')">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="newi" select="number($i) + 1" />

	<xsl:call-template name="urires_findPathEnd">
	  <xsl:with-param name="head" select="$tail" />
	  <xsl:with-param name="i" select="$newi" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- ([^/?#]*) -->
  <xsl:template name="urires_findAuthorityEnd">
    <xsl:param name="head" />
    <xsl:param name="i" select="1" />

    <xsl:variable name="c" select="substring($head, 1, 1)" />
    <xsl:variable name="tail" select="substring($head, 2)" />

    <xsl:choose>
      <xsl:when test="string-length($head) = 0">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:when test="($c = '/') or ($c = '?') or ($c = '#')">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="newi" select="number($i) + 1" />

	<xsl:call-template name="urires_findAuthorityEnd">
	  <xsl:with-param name="head" select="$tail" />
	  <xsl:with-param name="i" select="$newi" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_mergePaths">
    <xsl:param name="baseAuth" />    
    <xsl:param name="basePath" />
    <xsl:param name="refPath" />

    <xsl:choose>
      <xsl:when test="not($baseAuth = '&lt;&gt;') and ($basePath = '')">
	<xsl:value-of select="concat('/', $refPath)" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:choose>
	  <xsl:when test="contains($basePath, '/')" >
	    <xsl:variable name="baseNoLast">
	      <xsl:call-template name="urires_removeLastPathSegment">
		<xsl:with-param name="path" select="$basePath" />
	      </xsl:call-template>
	    </xsl:variable>
	    <xsl:value-of select="concat($baseNoLast, '/', $refPath)" />
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="$refPath" />
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_findLastPathSegmentEnd">
    <xsl:param name="tail" />
    <xsl:param name="i" select="string-length($tail)" />

    <xsl:variable name="c" select="substring($tail, $i, 1)" />
    <xsl:variable name="head" select="substring($tail, 1, $i - 1)" />

    <xsl:choose>
      <xsl:when test="string-length($tail) = 0">
	<xsl:value-of select="1" />
      </xsl:when>
      <xsl:when test="($c = '/')">
	<xsl:value-of select="$i" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:variable name="newi" select="number($i) - 1" />

	<xsl:call-template name="urires_findLastPathSegmentEnd">
	  <xsl:with-param name="tail" select="$head" />
	  <xsl:with-param name="i" select="$newi" />
	</xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <!-- used by merge paths -->
  <xsl:template name="urires_removeLastPathSegment">
    <xsl:param name="path" />

    <xsl:variable name="pos">
      <xsl:call-template name="urires_findLastPathSegmentEnd">
	<xsl:with-param name="tail" select="$path" />
      </xsl:call-template>
    </xsl:variable>

    <xsl:value-of select="substring($path, 1, $pos - 1)" />
  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_removeDotSegments">
    <xsl:param name="in" />
    <xsl:param name="out" select="''" />
    
    <xsl:choose>
      <xsl:when test="$in = ''">
	<xsl:value-of select="$out" />
      </xsl:when>
      <xsl:when test="starts-with($in, '../')">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="substring($in, 4)" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="starts-with($in, './')">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="substring($in, 3)" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="starts-with($in, '/./')">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="substring($in, 3)" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="$in = '/.'">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="'/'" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="starts-with($in, '/../')">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="substring($in, 4)" />
	  <xsl:with-param name="out">
	    <xsl:call-template name="urires_removeLastSegment">
	      <xsl:with-param name="head" select="$out" />
	    </xsl:call-template>
	  </xsl:with-param>
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="$in = '/..'">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="'/'" />
	  <xsl:with-param name="out">
	    <xsl:call-template name="urires_removeLastSegment">
	      <xsl:with-param name="head" select="$out" />
	    </xsl:call-template>
	  </xsl:with-param>
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="$in = '.'">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="''" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:when test="$in = '..'">
	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="''" />
	  <xsl:with-param name="out" select="$out" />
	</xsl:call-template>
      </xsl:when>
      <xsl:otherwise>

	<xsl:variable name="segout" >
	  <xsl:choose>
	    <xsl:when test="starts-with($in, '/')" >
	      <xsl:choose>
		<xsl:when test="substring-before(substring($in, 2), '/')" >
		  <xsl:value-of select="concat('/', substring-before(substring($in, 2), '/'))" />
		</xsl:when>
		<xsl:otherwise>
		  <xsl:value-of select="$in" />
		</xsl:otherwise>
	      </xsl:choose>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:choose>
		<xsl:when test="contains($in, '/')" >
		  <xsl:value-of select="substring-before($in, '/')" />
		</xsl:when>
		<xsl:otherwise>
		  <xsl:value-of select="$in" />
		</xsl:otherwise>
	      </xsl:choose>
	    </xsl:otherwise>
	  </xsl:choose>
	</xsl:variable>

	<xsl:variable name="segin" select="substring($in, string-length($segout) + 1)" />

	<xsl:call-template name="urires_removeDotSegments">
	  <xsl:with-param name="in" select="$segin" />
	  <xsl:with-param name="out" select="concat($out, $segout)" />
	</xsl:call-template>
	
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- internal use only -->
  <xsl:template name="urires_removeLastSegment" >
    <xsl:param name="head" />
    <xsl:param name="i" select="'0'" />

    <xsl:variable name="nhead" select="substring-before($head, '/')" />

    <xsl:if test="$head">
      <xsl:if test="not($i = '0') and $nhead" >
	<xsl:text>/</xsl:text>
      </xsl:if>

      <xsl:value-of select="$nhead" />

      <xsl:variable name="ntail" select="substring-after($head, '/')" />
      <xsl:if test="$ntail">
	<xsl:call-template name="urires_removeLastSegment">
	  <xsl:with-param name="head" select="$ntail" />
	  <xsl:with-param name="i" select="number($i) + 1" />	  
	</xsl:call-template>
      </xsl:if>
      
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
