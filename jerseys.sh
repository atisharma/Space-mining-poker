#!/bin/bash
# bash because of associative arrays

LOGDIR=/home/prospector/logs
PLAYERS="Peploe Sivyer Simpson Peploe Comerford Freckelton Lovelock Sharma Wittig SpongeBob AlwaysLauncher PassiveLauncher AgressiveLauncher Observer Evie"
COUNT=7
TMP=$(mktemp /tmp/jersey.XXXXXX)
TMP1=$(mktemp /tmp/jersey.XXXXXX)

# find all daily logs (for yellow jersey count)
DAILYLOGS=$(ls -1t $LOGDIR/201?-*)

declare -A YCOUNT
rm "$TMP"
for P in $PLAYERS
do
    YCOUNT[$P]=$(cat $DAILYLOGS | grep "Top player at end of game: $P" | wc -l)
    echo "${YCOUNT[$P]} $P" >> $TMP
done

echo "Yellow Jersey (all time leader in wins)"
cat $TMP | sort -k 1,1nr
echo

# find the COUNT last daily logs (for polka dot jersey count)
DAILYLOGS=$(ls -1t $LOGDIR/201?-* | head -n $COUNT)

declare -A SCOUNT
rm "$TMP"
for P in $PLAYERS
do
    SCOUNT[$P]=$(cat $DAILYLOGS | grep "Top player at end of game: $P" | wc -l)
    echo "${YCOUNT[$P]} $P" >> $TMP
done

echo "Polka Dot Jersey (recent leader in wins)"
cat $TMP | sort -k 1,1nr
echo

# find number of non-bankruptcies (not playing does not count) and total amount of money made overall
declare -A NBCOUNT
declare -A MCOUNT
rm "$TMP"
rm "$TMP1"
REGEXP='"bankroll": ([0-9]+)'
for P in $PLAYERS
do
    MCOUNT[$P]=0
    NBCOUNT[$P]=0
    for L in $LOGDIR/$P/201?-*
    do
        LINE=$(tail -n1 "$L")
        if [[ $LINE =~ $REGEXP ]]; then
            M=${BASH_REMATCH[1]}
            if [ "$M" -gt 0 ]; then
                NBCOUNT[$P]=$(expr "${NBCOUNT[$P]}" + 1)
                MCOUNT[$P]=$(expr "${MCOUNT[$P]}" + "$M")
            fi
        fi
    done
    echo "${NBCOUNT[$P]} $P" >> $TMP
    echo "${MCOUNT[$P]} $P" >> $TMP1
done

echo "White Jersey (most non-bankruptcies)"
cat $TMP | sort -k 1,1nr
echo

echo "Green Jersey (most money made)"
cat $TMP1 | sort -k 1,1nr
echo

rm "$TMP"
rm "$TMP1"
