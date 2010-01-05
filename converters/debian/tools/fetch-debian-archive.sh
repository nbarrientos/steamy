#!/bin/bash

DISTS="slick potato woody sarge"
ARCHS="i386"
AREAS="main non-free contrib"
BASE_URL="http://ftp.de.debian.org/archive/debian/dists"
OUTPUT_DIR="dists"

for dist in $DISTS; do
	echo "Voy a descargarme todo sobre $dist"
	for area in $AREAS; do
	    echo "Entramos en el area $area"
	    SOURCES_URL="$BASE_URL/$dist/$area/source/Sources.gz"
	    echo "Descargando sources: $SOURCES_URL"
	    mkdir -p $OUTPUT_DIR/$dist/$area/source
	    wget $SOURCES_URL -O $OUTPUT_DIR/$dist/$area/source/Sources.gz
	    for arch in $ARCHS; do
	        ARCH_URL="$BASE_URL/$dist/$area/binary-$arch/Packages.gz"
	        echo "Descargando arquitectura $ARCH_URL"
	        mkdir -p $OUTPUT_DIR/$dist/$area/binary-$arch
	        wget $ARCH_URL -O $OUTPUT_DIR/$dist/$area/binary-$arch/Packages.gz
        done
	done
done