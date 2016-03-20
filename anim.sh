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
output_file2="${game}_anim_a.gif"
recreate=0

for i in `ls plot/${game}*_c.data | sed 's/plot\///' | sed 's/_c\.data//'`; do
	echo "plotting $i";
    recreate=1
    commonSrc="plot/${i}_c.data";
	avgSrc="plot/${i}_avg.data";
	primSrc="plot/${i}_p.data";
	addsSrc="plot/${i}_a.data";
    primTarget="png/${i}_p.png"
    addsTarget="png/${i}_a.png"
    if [ "${game}" == "LOTTO" ]; then
        [ -f png/${i}.png ] && continue;
        gnuplot -e "sourcefn=\"$commonSrc\"; avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"png/${i}.png\"" ${game}_plot.gnuplot;
    else # EJACKPOT
        [ -f $primTarget ] && continue;
        gnuplot -e "avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"$primTarget\"" ${game}_plot_prim.gnuplot;
        gnuplot -e "addsfn=\"$addsSrc\"; targetfn=\"$addsTarget\"" ${game}_plot_adds.gnuplot;
    fi
done;

if [ "x$recreate" == "x1" ]; then
    [ -f $output_file ] && rm $output_file
    if [ "${game}" == "LOTTO" ]; then
        echo "creating new animated gif: $output_file"
        convert -delay 5 png/${game}*png $output_file
    else # EJACKPOT
        echo "creating new animated gif: $output_file"
        convert -delay 5 png/${game}*_p.png $output_file
        echo "creating new animated gif: $output_file2"
        convert -delay 5 png/${game}*_a.png $output_file2
    fi
fi

echo "Done"
