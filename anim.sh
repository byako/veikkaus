#!/bin/bash

[ -d plot ] || mkdir plot
[ -d png ] || mkdir png

output_file=anim.gif
recreate=0

echo "creating new png files"
for i in `ls plot/*c.data | sed 's/plot\///'`; do
    [ -f png/$i.png ] && continue;
	echo "starting $i";
    recreate=1
	avg=`echo $i | sed 's/_c/_avg/'`;
	prim=`echo $i | sed 's/_c/_p/'`;
	echo "avg=$avg";
	gnuplot -e "sourcefn=\"plot/$i\"; avgfn=\"plot/$avg\"; primfn=\"plot/$prim\"; targetfn=\"png/$i.png\"" plot.gnuplot;
done;

if [ "x$recreate" == "x1" ]; then
    [ -f $output_file ] && rm $output_file
    echo "creating new animated gif: $output_file"
    convert -delay 20 png/* $output_file
fi

echo "Done"
