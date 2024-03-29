#!/bin/bash

echo "----- SETUP:\n"
echo "----- SETUP: load gcc/6.4.0\n"
module load gcc/6.4.0
echo "----- SETUP: load python"
module load python/3.5.2

echo "----- SETUP: load prun"
module load prun

prun -o wdps_group13 -v -np 1 -t 600000 runner.sh $1

sleep 10

while : ; do
    if ls runner.sh.* 1> /dev/null 2>&1; then
        sleep 5
    else
        break
    fi
done

cat final-output.tsv