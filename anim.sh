#!/bin/bash

GAME='unknown'
QUIET=
TOTAL=0

function printUsage {
    echo "Usage: $0 -g <lotto|ejackpot> [-q]"
    echo -e "\t-g\tgame to create graphs for"
    echo -e "\t-q\tbe quiet"
    exit 1
}

[ -d plot ] || mkdir plot
[ -d png ] || mkdir png
[ $# -lt 1 ] && printUsage

while [ $# -ne 0 ];
do
    case $1 in
        -q)
        QUIET="quet"
        shift
        ;;
        -g)
        GAME=$(echo "$2" | awk '{print toupper($0)}')
        shift 2
        ;;
        *)
        echo "unknown parameter: $1"
        usage
        ;;
    esac
done

if [ "$GAME" != "lotto" ] && [ "${GAME}" != "ejackpot" ]; then
    printUsage
fi

output_file="${GAME}_anim.gif"
output_file2="${GAME}_anim_a.gif"
recreate=0

for i in `ls plot/${GAME}*_c.data | sed 's/plot\///' | sed 's/_c\.data//'`; do
	[ -z "${QUIET}" ] && echo "plotting $i";
    commonSrc="plot/${i}_c.data";
	avgSrc="plot/${i}_avg.data";
	primSrc="plot/${i}_p.data";
	addsSrc="plot/${i}_a.data";
    primTarget="png/${i}_p.png"
    addsTarget="png/${i}_a.png"
    if [ "${GAME}" == "lotto" ]; then
        [ -f "png/${i}.png" ] && continue;
        recreate=1
        gnuplot -e "sourcefn=\"$commonSrc\"; avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"png/${i}.png\"" "${GAME}_plot.gnuplot";
        TOTAL=$((TOTAL + 1))
    else # ejackpot
        [ -f "$primTarget" ] && continue;
        recreate=1
        gnuplot -e "avgfn=\"$avgSrc\"; primfn=\"$primSrc\"; targetfn=\"$primTarget\"" "${GAME}_plot_prim.gnuplot";
        gnuplot -e "addsfn=\"$addsSrc\"; targetfn=\"$addsTarget\"" "${GAME}_plot_adds.gnuplot";
        TOTAL=$((TOTAL + 1))
    fi
done;

echo "Total: $TOTAL"

if [ "x$recreate" == "x1" ]; then
    [ -f "$output_file" ] && rm "$output_file"
    if [ "${GAME}" == "lotto" ]; then
        [ -z "${QUIET}" ] && echo "creating new animated gif: $output_file"
        convert -delay 5 "png/${GAME}*png" "$output_file"
    else # ejackpot
        [ -z "${QUIET}" ] && echo "creating new animated gif: $output_file"
        convert -delay 5 "png/${GAME}*_p.png" "$output_file"
        [ -z "${QUIET}" ] && echo "creating new animated gif: $output_file2"
        convert -delay 5 "png/${GAME}*_a.png" "$output_file2"
    fi
fi

echo "Done"
