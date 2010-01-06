#!/bin/bash
# process-distributions.sh
#
# Nacho Barrientos Arias <nacho@debian.org>

# License: MIT


BASEURI="http://rdf.debian.net"
DEAR="./dear" # FIXME

AREAS="non-free contrib main"
ARCHS="i386"
ABC="a b c d e f g h i j k l m n o p q r s t u v w x y z"

function processPackages {
  mkdir -p $DISTOUT/$1/binary-$arch
  local filename=$DISTDIR/$1/binary-$2/Packages
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  #echo "Area: $1 Architecture: $2 Prefix: $3 File: $filename"

  $DEAR -p $filename -P $DISTOUT/$1/binary-$2/Packages.$3.rdf \
  -a -t -b $BASEURI -r "^$3.*" \
  -d $DISTRIBUTION
  
  if [ ! -z "$t" ]
  then
    rm $t
  fi
}

function processSources {
  mkdir -p $DISTOUT/$1/sources
  local filename=$DISTDIR/$1/source/Sources
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  #echo "Area: $1 Prefix: $2 File: $filename"

  $DEAR -s $filename -S $DISTOUT/$1/sources/Sources.$2.rdf \
  -a -t -b $BASEURI -r "^$2.*" \
  -d $DISTRIBUTION

  if [ ! -z "$t" ]
  then
    rm $t
  fi
}

if [ $# -lt 2 ]
then
  echo "Usage: $0 <dists_dir> <output_dir> [distribution names list]"
  exit -1
fi

DATADIR=$1
shift
BASEOUT=$1
shift
DISTRIBUTIONS=$@

for dist in $DISTRIBUTIONS;
do
  if [ ! -e $DATADIR/$dist ]
  then
    echo "Directory '$DATADIR/$dist' does not exist. Skipping distribution '$dist'..."
    continue
  fi

  DISTDIR=$DATADIR/$dist
  DISTOUT=$BASEOUT/$dist
  DISTRIBUTION="$BASEURI/distribution/$dist"

  echo -e "\nProcessing distribution '$dist'"

  for area in $AREAS
  do
    # Packages
    for arch in $ARCHS
    do
      for initial in $ABC
      do
        processPackages $area $arch $initial
      done
    done
    # Sources
    for initial in $ABC
    do
      processSources $area $initial
    done
  done
done
