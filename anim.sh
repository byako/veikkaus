#!/bin/bash

[ -d plot ] || mkdir plot
[ -d png ] || mkdir png

echo "cleaning graphics"
rm png/*
rm anim.gif

echo "creating new png files"
for i in `ls plot/*c.data | sed 's/plot\///'`; do
	echo "starting $i";
	avg=`echo $i | sed 's/_c/_avg/'`;
	prim=`echo $i | sed 's/_c/_p/'`;
	echo "avg=$avg";
	gnuplot -e "sourcefn=\"plot/$i\"; avgfn=\"plot/$avg\"; primfn=\"plot/$prim\"; targetfn=\"png/$i.png\"" plot.gnuplot;
done;

echo "creating new animated gif 'anim.gif'"
convert -delay 20 png/* anim.gif

echo "Done"
