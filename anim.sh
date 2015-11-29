#!/bin/bash

game='unknown'

function printUsage {
    echo "Usage: $0 <lotto|ejackpot>"
    exit -1
}

[ -d plot ] || mkdir plot
[ -d png ] || mkdir png
[ $# -lt 1 ] && printUsage

[ "$1" == 'lotto' ] && game='LOTTO'
[ "$1" == 'ejackpot' ] && game='EJACKPOT'

[ "$game" == "unknown" ] && printUsage

output_file="${game}_anim.gif"
recreate=0

for i in `ls plot/${game}*_c.data | sed 's/plot\///' | sed 's/_c\.data//'`; do
    [ -f png/${game}_${i}_p.png ] && continue;
	echo "plotting $i";
    recreate=1
    commonSrc="plot/${i}_c.data";
	avgSrc="plot/${i}_avg.data";
	primSrc="plot/${i}_p.data";
	addsSrc="plot/${i}_a.data";
    primTarget="png/${i}_p.png"
    addsTarget="png/${i}_a.png"
    if [ "${game}" == "LOTTO" ]; then
        gnuplot -e "sourcefn=\"$commonSrc\"; avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"png/${game}_${i}.png\"" ${game}_plot.gnuplot;
    else # EJACKPOT
        gnuplot -e "avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"$primTarget\"" ${game}_plot_prim.gnuplot;
        gnuplot -e "addsfn=\"$addsSrc\"; targetfn=\"$addsTarget\"" ${game}_plot_adds.gnuplot;
    fi
done;

if [ "x$recreate" == "x1" ]; then
    [ -f $output_file ] && rm $output_file
    echo "creating new animated gif: $output_file"
 #   convert -delay 20 png/* $output_file
fi

echo "Done"
