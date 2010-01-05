#!/bin/bash

DATADIR=$1
BASEOUT=$3

BASEURI="http://rdf.debian.net"
DISTRIBUTION="http://rdf.debian.net/distributions/$2"
DEAR="./dear" # FIXME

AREAS="non-free contrib"
#AREAS="non-free contrib main"
ARCHES="i386 amd64 powerpc"
#ABC="a b c d e f g h i j k l m n o p q r s t u v w x y z"
ABC="a b"

function processPackages {
  local filename=$DATADIR/$1/binary-$2/Packages
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  #echo "Area: $1 Architecture: $2 Prefix: $3 File: $filename"

  $DEAR -p $filename -P $BASEOUT/$1/binary-$2/Packages.$3.rdf \
  -a -t -b $BASEURI -r "^$3.*" \
  -d $DISTRIBUTION
  
  if [ ! -z "$t" ]
  then
    rm $t
  fi
}

function processSources {
  local filename=$DATADIR/$1/source/Sources
  if [ ! -e $filename ]
  then
    local t=$(mktemp)
    gzip -d $filename.gz -c > $t
    local filename=$t
  fi
  
  #echo "Area: $1 Prefix: $2 File: $filename"

  $DEAR -s $filename -S $BASEOUT/$1/sources/Sources.$2.rdf \
  -a -t -b $BASEURI -r "^$2.*" \
  -d $DISTRIBUTION

  if [ ! -z "$t" ]
  then
    rm $t
  fi
}

if [ $# -ne 3 ]
then
  echo "Usage: $0 <dists_dir> <distribution> <output_dir>"
  exit -1
fi

if [ ! -e $DATADIR/$2 ]
then
  echo "Directory $DATADIR/$2 does not exist"
  exit -1
else
  DATADIR=$DATADIR/$2
  BASEOUT=$BASEOUT/$2
fi

mkdir -p $BASEOUT

for y in $AREAS
do
  mkdir -p $BASEOUT/$y
  # Packages
  for a in $ARCHES
  do
    mkdir -p $BASEOUT/$y/binary-$a
    for l in $ABC
    do
      processPackages $y $a $l
    done
  done
  # Sources
  mkdir -p $BASEOUT/$y/sources
  for l in $ABC
  do
    processSources $y $l
  done
done
