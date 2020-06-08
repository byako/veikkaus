#!/bin/bash

GAME='ejackpot'
QUIET=false
TOTAL=0

function printUsage {
    echo "Usage: $0 -g <lotto|ejackpot> [-q]"
    echo -e "\t-q\tbe quiet"
    exit 1
}

[ -d plot ] || mkdir plot
[ -d png ] || mkdir png
[ $# -lt 1 ] && {
    echo "ERROR: Not enough arguments";
    printUsage
}

while [ $# -ne 0 ];
do
    case $1 in
        -q)
        QUIET=true
        shift
        ;;
        *)
        echo "unknown parameter: $1"
        usage
        ;;
    esac
done

output_file="${GAME}_anim.gif"
output_file2="${GAME}_anim_a.gif"
recreate=false

for i in `ls plot/${GAME}*_c.data | sed 's/plot\///' | sed 's/_c\.data//'`; do
	${QUIET} && echo "plotting $i";
	avgSrc="plot/${i}_avg.data";
	primSrc="plot/${i}_p.data";
	addsSrc="plot/${i}_a.data";
    primTarget="png/${i}_p.png"
    addsTarget="png/${i}_a.png"
    [ -f "$primTarget" ] && continue;
    recreate=true
    gnuplot -e "avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"$primTarget\"" "${GAME}_plot_prim.gnuplot";
    gnuplot -e "addsfn=\"$addsSrc\"; targetfn=\"$addsTarget\"" "${GAME}_plot_adds.gnuplot";
    TOTAL=$((TOTAL + 1))
done;

echo "Total: $TOTAL"

if $recreate; then
    [ -f "$output_file" ] && rm "$output_file"
    ${QUIET} && echo "creating new animated gif: $output_file"
    convert -delay 5 "png/${GAME}*_p.png" "$output_file"
    ${QUIET} && echo "creating new animated gif: $output_file2"
    convert -delay 5 "png/${GAME}*_a.png" "$output_file2"
fi

echo "Done"
