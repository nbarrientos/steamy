#!/bin/bash
# fetch-debian-archive.sh
#
# Diego Berrueta <diego@berrueta.net>
# Nacho Barrientos Arias <nacho@debian.org>

# License: MIT

AREAS="main non-free contrib"
OUTPUT_DIR=$1

if [ -z $1 ]
then
  echo "Usage $0 <dest_dir>"
  exit -1
fi

function processDist {
  # $1: Distname
  echo "Will download $1 (arches: $ARCHS)"
  for area in $AREAS; do
      echo "Area: $area"
      mkdir -p $OUTPUT_DIR/$1/$area/source
      SOURCES_URL="$BASE_URL/$1/$area/source/Sources.gz"
      OUTPUT_PATH="$OUTPUT_DIR/$1/$area/source/Sources.gz"
      processFile $SOURCES_URL $OUTPUT_PATH
      for arch in $ARCHS; do
          mkdir -p $OUTPUT_DIR/$1/$area/binary-$arch
          PACKAGES_URL="$BASE_URL/$1/$area/binary-$arch/Packages.gz"
          OUTPUT_PATH="$OUTPUT_DIR/$1/$area/binary-$arch/Packages.gz"
          processFile $PACKAGES_URL $OUTPUT_PATH
        done
  done
}

function processFile {
  # $1: Download URL $2: Output file
  echo "Downloading file: $1..."
  wget $1 -O $2 &> /dev/null
  OUTPUT_PATH_UNZIPPED=$(echo $2 |sed -e "s/.gz//")
  echo "Gunzipping and recoding $2 to $OUTPUT_PATH_UNZIPPED..."
  gzip -d $2 -c > $OUTPUT_PATH_UNZIPPED
  iconv -f "ISO-8859-1" -t "UTF-8" $OUTPUT_PATH_UNZIPPED > $OUTPUT_PATH_UNZIPPED.u
  mv $OUTPUT_PATH_UNZIPPED.u $OUTPUT_PATH_UNZIPPED
}

# Old distributions

BASE_URL="http://ftp.nl.debian.org/debian-archive/dists"
ARCHS="i386 m68k"
processDist "hamm"

ARCHS="i386 m68k sparc"
processDist "slink"

ARCHS="i386"
processDist "potato"

ARCHS="i386"
processDist "woody"

ARCHS="i386"
processDist "sarge"

# Current ones

BASE_URL="http://ftp.de.debian.org/debian/dists"
ARCHS="i386 amd64 powerpc"
processDist "etch"

ARCHS="i386 amd64 powerpc"
processDist "lenny"
