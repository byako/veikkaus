#!/bin/bash

LAST_RESULT=$(tail -1 latest_EJACKPOT.json |sed 's/},$/}/')
WEEKN=$(date +%V)
YEARN=$(date +%Y)
LAST_WEEK=$(echo $LAST_RESULT | jq ".week" | sed 's/"//g')
LAST_YEAR=$(echo $LAST_RESULT | jq ".year" | sed 's/"//g')

echo "last fetched week:$LAST_WEEK"
echo "current week:$WEEKN"

if [ "$LAST_YEAR" -ne "$YEARN" ]; then
    echo "year mismatch, do update manually"
    exit 1;
fi

if [ "$LAST_WEEK" -lt "$WEEKN" ]; then # fetch new result
    for i in `seq $((LAST_WEEK+1)) $WEEKN`; do
        echo "./fetch-results.py -y $YEARN -g ejackpot  -w $i"
        ./fetch-results.py -y $YEARN -g ejackpot  -w $i
    done
    # update pictures
    echo "./gen_plot_source.py -g ejackpot -q"
    ./gen_plot_source.py -g ejackpot -q
    echo "./anim.sh ejackpot"
    ./anim.sh ejackpot
else
    echo "No new results needed"
fi
