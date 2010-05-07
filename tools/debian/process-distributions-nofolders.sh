#!/bin/bash
# process-distributions.sh
#
# Nacho Barrientos Arias <nacho@debian.org>

# License: MIT


BASEURI="http://linkeddata.debian.net/resource"
DEAR="./dear" # FIXME

AREAS="non-free contrib main"
ARCHS="i386"
ABC="a b c d e f g h i j k l m n o p q r s t u v w x y z"

function processPackages {
  local filename=$DISTDIR/$1/binary-$2/Packages
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  $DEAR -p $filename -P $BASEOUT/$4_$1_binary-$2_Packages.$5.rdf \
  -a -t -b $BASEURI -r $3 \
  -d $DISTRIBUTION
  
  if [ ! -z "$t" ]
  then
    rm $t
  fi
}

function processSources {
  local filename=$DISTDIR/$1/source/Sources
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  $DEAR -s $filename -S $BASEOUT/$3_$1_sources_Sources.$4.rdf \
  -a -t -b $BASEURI -r $2 \
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

mkdir -p $BASEOUT

for dist in $DISTRIBUTIONS;
do
  if [ ! -e $DATADIR/$dist ]
  then
    echo "Directory '$DATADIR/$dist' does not exist. Skipping distribution '$dist'..."
    continue
  fi

  DISTDIR=$DATADIR/$dist
  DISTRIBUTION="$BASEURI/distribution/$dist"

  echo -e "\nProcessing distribution '$dist'"

  for area in $AREAS
  do
    # Packages
    for arch in $ARCHS
    do
      processPackages $area $arch "\d.*" $dist "#"
      for initial in $ABC
      do
        if [ $initial == "l" -a $area == "main" ]
        then
          processPackages $area $arch "l(?!ib).*" $dist "l"
          processPackages $area $arch "lib\d.*" $dist "lib#"
          for subinitial in $ABC
          do
            processPackages $area $arch "lib$subinitial.*" $dist "lib$subinitial"
          done
        else
          processPackages $area $arch "$initial.*" $dist $initial
        fi
      done
    done
    # Sources
    processSources $area "\d.*" $dist "#"
    for initial in $ABC
    do
      if [ $initial == "l" -a $area == "main" ]
      then
        processSources $area "l(?!ib).*" $dist "l"
        processSources $area "lib\d.*" $dist "lib#"
        for subinitial in $ABC
        do
          processSources $area "lib$subinitial.*" $dist "lib$subinitial"
        done
      else
        processSources $area "$initial.*" $dist $initial
      fi
    done
  done
done
