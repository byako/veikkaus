#!/bin/bash

for i in `seq 2012 2020`; do
    for j in `seq 00 53`; do
        if [ $i == 2012 -a $j -lt 13 ]; then continue; fi;
        ./fetch_results.py -g ejackpot -y $i -w $j
        sleep 1
    done;
done;
