#!/bin/bash

LAST_RESULT=$(tail -1 latest_ejackpot.json |sed 's/},$/}/')
WEEKN=$(date +%V)
YEARN=$(date +%Y)
LAST_WEEK=$(echo "$LAST_RESULT" | jq ".week" | sed 's/"//g')
LAST_YEAR=$(echo "$LAST_RESULT" | jq ".year" | sed 's/"//g')

echo "last fetched week:$LAST_WEEK"
echo "current week:$WEEKN"

gnuplot --version > /dev/null 2>&1 || {
    echo "Install gnuplot"
    return 1
}

jq --version > /dev/null 2>&1 || {
    echo "Install jq"
    return 1
}


if [[ "$LAST_WEEK" -lt "$WEEKN" ]] || [[ "$LAST_YEAR" -ne "$YEARN" ]]; then # fetch new result
    LOOP_YEAR=$LAST_YEAR
    while [[ "$LOOP_YEAR" -ne "$YEARN" ]]; do
        LOOP_WEEK=1
        while [[ $LOOP_WEEK -lt 54 ]]; do
            echo "./fetch_results.py -y $LOOP_YEAR -w $LOOP_WEEK"
            ./fetch_results.py -y $((LOOP_YEAR)) -w $LOOP_WEEK
            LOOP_WEEK=$(( LOOP_WEEK + 1 ))
        done
        LOOP_YEAR=$(( LOOP_YEAR + 1 ))
    done

    if [[ "$LAST_YEAR" -ne "$YEARN" ]]; then # fetch new result
        LOOP_WEEK=1
    else
        LOOP_WEEK=$LAST_WEEK
    fi

    while [[ $LOOP_WEEK -lt $WEEKN ]]; do
        echo "./fetch_results.py -y $YEARN -w $LOOP_WEEK"
        ./fetch_results.py -y $YEARN -w $LOOP_WEEK
        LOOP_WEEK=$(( LOOP_WEEK + 1 ))
    done

    # update pictures
    echo "./gen_plot_source.py -g ejackpot -q"
    ./gen_plot_source.py -g ejackpot -q
    echo "./anim.sh -q -g ejackpot"
    ./anim.sh -q -g ejackpot
else
    echo "No new results needed"
fi
