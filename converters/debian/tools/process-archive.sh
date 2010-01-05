DISTDIR=$1
OUTDIR=$2
DISTRIBUTIONS="slink potato woody sarge etch lenny"
for d in $DISTRIBUTIONS;
do
	bash process-distribution.sh $DISTDIR $d $OUTDIR;
done
